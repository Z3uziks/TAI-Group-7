#!/usr/bin/env python3
"""
Music Identification System using Normalized Compression Distance (NCD)
Main system for identifying music segments using frequency signatures and compression.
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd

from ncd_calculator import NCDCalculator
from audio_processor import AudioProcessor


@dataclass
class IdentificationResult:
    """Result of music identification."""
    query_file: str
    best_match: str
    noise_level: float
    ncd_value: float
    compressor: str
    all_matches: List[Tuple[str, float]]
    processing_time: float


class MusicIdentifier:
    """Main music identification system."""
    
    def __init__(self, database_dir: str, signatures_dir: str,
                 getmaxfreqs_path: str = "./GetMaxFreqs/bin/GetMaxFreqs"):
        """
        Initialize MusicIdentifier.
        
        Args:
            database_dir: Directory containing music database
            signatures_dir: Directory for storing signatures
            getmaxfreqs_path: Path to GetMaxFreqs executable
        """
        self.database_dir = Path(database_dir)
        self.signatures_dir = Path(signatures_dir)
        self.db_signatures_dir = self.signatures_dir / "database"
        self.query_signatures_dir = self.signatures_dir / "queries"
        
        # Create directories
        for dir_path in [self.signatures_dir, self.db_signatures_dir, self.query_signatures_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.audio_processor = AudioProcessor(getmaxfreqs_path)
        self.ncd_calculator = NCDCalculator()
        self.database_signatures = []
        self.music_database = {}
    
    def build_database(self, signature_params: Dict = None) -> bool:
        """
        Build signature database from audio files.
        
        Args:
            signature_params: Parameters for signature generation
            
        Returns:
            True if successful, False otherwise
        """
        if signature_params is None:
            signature_params = {
                'win_size': 1024,
                'shift': 256,
                'down_sampling': 4,
                'n_freqs': 4
            }
        
        print("Building signature database...")
        
        # Find all audio files
        audio_extensions = ['.wav', '.flac', '.mp3']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(list(self.database_dir.glob(f"*{ext}")))
            #audio_files.extend(list(self.database_dir.glob(f"**/*{ext}")))
        
        if len(audio_files) < 25:
            print(f"Warning: Only {len(audio_files)} audio files found. Need at least 25.")
        
        print(f"Found {len(audio_files)} audio files")
        
        # Generate signatures
        successful = 0
        temp_dir = self.signatures_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        for audio_file in audio_files:
            signature_file = self.db_signatures_dir / f"{audio_file.stem}.freqs"
            
            try:
                # Convert to stereo WAV if needed
                temp_wav = temp_dir / f"{audio_file.stem}_converted.wav"
                conversion_cmd = [
                    'sox', str(audio_file), '-c', '2',  # Force stereo
                    '-r', '44100',  # Standard sample rate
                    str(temp_wav)
                ]
                
                subprocess.run(conversion_cmd, check=True, capture_output=True)
                
                # Generate signature from converted file
                if self.audio_processor.generate_signature(
                    str(temp_wav), str(signature_file), **signature_params
                ):
                    self.database_signatures.append(str(signature_file))
                    self.music_database[audio_file.stem] = str(audio_file)
                    successful += 1
                    print(f"Generated signature for {audio_file.name}")
                else:
                    print(f"Failed to generate signature for {audio_file.name}")
                    
                # Clean up temp file
                temp_wav.unlink(missing_ok=True)
                
            except Exception as e:
                print(f"Error processing {audio_file.name}: {e}")
                continue
        
        # Clean up temp directory
        temp_dir.rmdir()
        
        print(f"Successfully generated {successful} signatures")
        
        # Save database info
        db_info = {
            'signatures': self.database_signatures,
            'music_files': self.music_database,
            'signature_params': signature_params
        }
        
        with open(self.signatures_dir / "database_info.json", 'w') as f:
            json.dump(db_info, f, indent=2)
        
        return successful > 0
    
    def load_database(self) -> bool:
        """Load existing signature database."""
        db_info_file = self.signatures_dir / "database_info.json"
        
        if not db_info_file.exists():
            print("Database info not found. Please build database first.")
            return False
        
        try:
            with open(db_info_file, 'r') as f:
                db_info = json.load(f)
            
            self.database_signatures = db_info['signatures']
            self.music_database = db_info['music_files']
            
            # Verify signatures exist
            existing_signatures = []
            for sig_file in self.database_signatures:
                if os.path.exists(sig_file):
                    existing_signatures.append(sig_file)
            
            self.database_signatures = existing_signatures
            print(f"Loaded {len(self.database_signatures)} signatures")
            return len(self.database_signatures) > 0
            
        except Exception as e:
            print(f"Error loading database: {e}")
            return False
    
    def standardize_audio(self, input_file: str, output_file: str) -> bool:
        """Convert audio to standard format (stereo, 44.1kHz)."""
        try:
            cmd = [
                'sox', str(input_file),
                '-c', '2',  # Force stereo
                '-r', '44100',  # Standard sample rate
                str(output_file)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Sox conversion failed: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Error converting audio: {e}")
            return False

    def identify_music(self, query_file: str, compressor: str = 'gzip',
                    signature_params: Dict = None, add_noise: bool = False,
                    noise_level: float = 0.05) -> IdentificationResult:
        """
        Identify music from query segment.
        """
        start_time = time.time()
        
        if signature_params is None:
            signature_params = {
                'win_size': 1024,
                'shift': 256,
                'down_sampling': 4,
                'n_freqs': 4
            }
        
        query_path = Path(query_file)
        temp_dir = self.query_signatures_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # First standardize the audio format
            temp_wav = temp_dir / f"{query_path.stem}_standardized.wav"
            if not self.standardize_audio(query_file, temp_wav):
                raise RuntimeError(f"Failed to standardize {query_file}")
            
            processed_query = str(temp_wav)
            
            # Add noise if requested
            if add_noise:
                noisy_file = temp_dir / f"{query_path.stem}_noisy.wav"
                if self.audio_processor.add_noise(processed_query, str(noisy_file), noise_level):
                    processed_query = str(noisy_file)
                    print(f"Added noise (level {noise_level}) to query")
            
            # Generate signature for query
            query_signature = self.query_signatures_dir / f"{query_path.stem}.freqs"
            
            if not self.audio_processor.generate_signature(
                processed_query, str(query_signature), **signature_params
            ):
                raise RuntimeError(f"Failed to generate signature for {query_file}")
            
            # Compare with database
            matches = self.ncd_calculator.batch_compare(
                str(query_signature), self.database_signatures, compressor
            )
            
            # Clean up temp files
            temp_wav.unlink(missing_ok=True)
            if add_noise and processed_query != str(temp_wav):
                Path(processed_query).unlink(missing_ok=True)
                
        except Exception as e:
            raise RuntimeError(f"Failed to process {query_file}: {e}")
        finally:
            # Clean up temp directory if empty
            try:
                temp_dir.rmdir()
            except:
                pass
        
        processing_time = time.time() - start_time
        
        best_match = matches[0] if matches else ("Unknown", 1.0)
        
        return IdentificationResult(
            query_file=query_file,
            noise_level=noise_level,
            best_match=best_match[0],
            ncd_value=best_match[1],
            compressor=compressor,
            all_matches=matches[:10],  # Top 10 matches
            processing_time=processing_time
        )
    
    def batch_identify(self, query_files: List[str], compressors: List[str] = None,
                      add_noise_levels: List[float] = None) -> List[IdentificationResult]:
        """
        Identify multiple music queries.
        
        Args:
            query_files: List of query file paths
            compressors: List of compressors to test
            add_noise_levels: List of noise levels to test
            
        Returns:
            List of IdentificationResult objects
        """
        if compressors is None:
            compressors = ['gzip', 'bzip2', 'lzma', 'zstd']
        
        if add_noise_levels is None:
            add_noise_levels = [0.0, 0.02, 0.05, 0.1]
        
        results = []
        total_tests = len(query_files) * len(compressors) * len(add_noise_levels)
        test_count = 0
        
        print(f"Running {total_tests} identification tests...")
        
        for query_file in query_files:
            for compressor in compressors:
                for noise_level in add_noise_levels:
                    test_count += 1
                    print(f"Test {test_count}/{total_tests} - {Path(query_file).name} - {compressor} - noise:{noise_level}")
                    
                    try:
                        result = self.identify_music(
                            query_file, compressor, 
                            add_noise=(noise_level > 0), 
                            noise_level=noise_level
                        )
                        results.append(result)
                    except Exception as e:
                        print(f"Error in test: {e}")
        
        return results
    
    def evaluate_results(self, results: List[IdentificationResult],
                        ground_truth: Dict[str, str] = None) -> pd.DataFrame:
        """
        Evaluate identification results.
        
        Args:
            results: List of identification results
            ground_truth: Dictionary mapping query names to correct answers
            
        Returns:
            DataFrame with evaluation metrics
        """
        data = []
        
        for result in results:
            query_name = Path(result.query_file).stem
            
            # Extract true song name from query filename if not provided
            true_song = None
            if ground_truth and query_name in ground_truth:
                true_song = ground_truth[query_name]
            else:
                # Assume query filename contains the song name
                if '_segment_' in query_name:
                    true_song = query_name.split('_segment_')[0]
                elif '_' in query_name:
                    true_song = query_name.split('_')[0]
                # if its a sample from professor, it might be like "sample1"
                elif query_name.startswith("sample"):
                    # sample01.wav: Rainbow - I Surrender
                    # sample02.wav: Carlos Paredes - Canção Verdes Anos [Official Audio]
                    # sample03.wav: Ultravox - All Stood Still
                    # sample04.wav: Mozart Requiem Sanctus
                    # sample05.wav: Beethoven / Karajan, Sinfonia nº 5, 1º Andamento (20 seg)
                    # sample06.wav: Vangelis - Spiral (Audio)
                    # sample07.wav: Metallica： The Memory Remains (Official Music Video)
                    if query_name == "sample01":
                        true_song = "Rainbow - I Surrender"
                    elif query_name == "sample02":
                        true_song = "Carlos Paredes - Canção Verdes Anos [Official Audio]"
                    elif query_name == "sample03":
                        true_song = "Ultravox - All Stood Still"
                    elif query_name == "sample04":
                        true_song = "Mozart Requiem Sanctus"
                    elif query_name == "sample05":
                        true_song = "Quinta Sinfonia - 1º movimento - Beethoven"
                    elif query_name == "sample06":
                        true_song = "Vangelis - Spiral (Audio)"
                    elif query_name == "sample07":
                        true_song = "Metallica： The Memory Remains (Official Music Video)"
                    else:
                        true_song = query_name
            
            correct = (true_song and true_song in result.best_match) if true_song else None
            
            data.append({
                'query': query_name,
                'true_song': true_song,
                'noise_level': result.noise_level if hasattr(result, 'noise_level') else None,
                'predicted': result.best_match,
                'ncd_value': result.ncd_value,
                'compressor': result.compressor,
                'correct': correct,
                'processing_time': result.processing_time,
                'top_5_matches': [match[0] for match in result.all_matches[:5]]
            })
        
        df = pd.DataFrame(data)
        
        # Calculate accuracy by compressor
        if 'correct' in df.columns and df['correct'].notna().any():
            accuracy_by_compressor = df.groupby('compressor')['correct'].mean()
            print("\nAccuracy by Compressor:")
            for comp, acc in accuracy_by_compressor.items():
                print(f"{comp:8s}: {acc:.3f}")
        
        return df
    
    def save_results(self, results: List[IdentificationResult], output_file: str):
        """Save results to JSON file."""
        results_data = []
        
        for result in results:
            results_data.append({
                'query_file': result.query_file,
                'best_match': result.best_match,
                'noise_level': result.noise_level if hasattr(result, 'noise_level') else None,
                'ncd_value': result.ncd_value,
                'compressor': result.compressor,
                'all_matches': result.all_matches,
                'processing_time': result.processing_time
            })
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Results saved to {output_file}")


def main():
    """Example usage of MusicIdentifier."""
    # Initialize system
    identifier = MusicIdentifier(
        database_dir="./database",
        signatures_dir="./signatures"
    )
    
    # Build or load database
    if not identifier.load_database():
        print("Building new database...")
        identifier.build_database()
    
    print(f"Database contains {len(identifier.database_signatures)} signatures")


if __name__ == "__main__":
    main()