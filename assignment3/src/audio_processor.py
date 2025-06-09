#!/usr/bin/env python3
"""
Audio Processing Utilities
Handles audio file manipulation, segment extraction, noise addition, and signature generation.
"""

import os
import subprocess
import tempfile
import random
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import librosa
import soundfile as sf


class AudioProcessor:
    """Handle audio file processing and manipulation."""
    
    def __init__(self, getmaxfreqs_path: str = "./GetMaxFreqs/bin/GetMaxFreqs"):
        """
        Initialize AudioProcessor.
        
        Args:
            getmaxfreqs_path: Path to GetMaxFreqs executable
        """
        self.getmaxfreqs_path = Path(getmaxfreqs_path)
        if not self.getmaxfreqs_path.exists():
            # Try Windows executable
            win_path = Path(str(getmaxfreqs_path).replace("GetMaxFreqs", "GetMaxFreqs.exe"))
            if win_path.exists():
                self.getmaxfreqs_path = win_path
            else:
                raise FileNotFoundError(f"GetMaxFreqs executable not found at {getmaxfreqs_path}")
    
    def extract_segment(self, input_file: str, output_file: str, 
                       start_time: float, duration: float) -> bool:
        """
        Extract a segment from audio file using sox.
        
        Args:
            input_file: Input audio file path
            output_file: Output audio file path
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                'sox', input_file, output_file,
                'trim', str(start_time), str(duration)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error extracting segment: {e}")
            return False
    
    def add_noise(self, input_file: str, output_file: str, 
                  noise_level: float = 0.05) -> bool:
        """
        Add white noise to audio file.
        
        Args:
            input_file: Input audio file path
            output_file: Output audio file path
            noise_level: Noise level (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load audio
            audio, sr = librosa.load(input_file, sr=None, mono=False)
            
            # Generate noise
            if len(audio.shape) == 1:
                # Mono
                noise = np.random.normal(0, noise_level, audio.shape)
            else:
                # Stereo
                noise = np.random.normal(0, noise_level, audio.shape)
            
            # Add noise
            noisy_audio = audio + noise
            
            # Ensure we don't clip
            max_val = np.max(np.abs(noisy_audio))
            if max_val > 1.0:
                noisy_audio = noisy_audio / max_val
            
            # Save
            sf.write(output_file, noisy_audio.T if len(noisy_audio.shape) > 1 else noisy_audio, sr)
            return True
            
        except Exception as e:
            print(f"Error adding noise: {e}")
            return False
    
    def convert_to_wav(self, input_file: str, output_file: str, 
                      sample_rate: int = 44100, channels: int = 2) -> bool:
        """
        Convert audio file to WAV format using sox.
        
        Args:
            input_file: Input audio file path
            output_file: Output WAV file path
            sample_rate: Target sample rate
            channels: Number of channels
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                'sox', input_file, 
                '-r', str(sample_rate),
                '-c', str(channels),
                '-b', '16',
                output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error converting to WAV: {e}")
            return False
    
    def generate_signature(self, audio_file: str, signature_file: str,
                          win_size: int = 1024, shift: int = 256,
                          down_sampling: int = 4, n_freqs: int = 4,
                          verbose: bool = False) -> bool:
        """
        Generate frequency signature using GetMaxFreqs.
        
        Args:
            audio_file: Input audio file path
            signature_file: Output signature file path
            win_size: Window size for frequency analysis
            shift: Shift between windows
            down_sampling: Down sampling factor
            n_freqs: Number of frequency components to retain
            verbose: Enable verbose output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [str(self.getmaxfreqs_path)]
            
            if verbose:
                cmd.append('-v')
            
            cmd.extend([
                '-w', signature_file,
                '-ws', str(win_size),
                '-sh', str(shift),
                '-ds', str(down_sampling),
                '-nf', str(n_freqs),
                audio_file
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"GetMaxFreqs error: {result.stderr}")
                return False
                
            return os.path.exists(signature_file)
            
        except Exception as e:
            print(f"Error generating signature: {e}")
            return False
    
    def generate_random_segments(self, audio_file: str, output_dir: str,
                               segment_duration: float = 10.0, 
                               num_segments: int = 5) -> List[str]:
        """
        Generate random segments from an audio file.
        
        Args:
            audio_file: Input audio file path
            output_dir: Output directory for segments
            segment_duration: Duration of each segment in seconds
            num_segments: Number of segments to generate
            
        Returns:
            List of generated segment file paths
        """
        segments = []
        
        try:
            # Get audio duration
            duration = librosa.get_duration(path=audio_file)
            
            if duration <= segment_duration:
                print(f"Audio file too short for {segment_duration}s segments")
                return segments
            
            os.makedirs(output_dir, exist_ok=True)
            base_name = Path(audio_file).stem
            
            for i in range(num_segments):
                # Random start time
                max_start = duration - segment_duration
                start_time = random.uniform(0, max_start)
                
                segment_file = os.path.join(output_dir, f"{base_name}_segment_{i+1:02d}.wav")
                
                if self.extract_segment(audio_file, segment_file, start_time, segment_duration):
                    segments.append(segment_file)
                    
        except Exception as e:
            print(f"Error generating random segments: {e}")
        
        return segments
    
    def batch_process_signatures(self, audio_files: List[str], 
                               signature_dir: str, **kwargs) -> List[str]:
        """
        Generate signatures for multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            signature_dir: Output directory for signatures
            **kwargs: Arguments passed to generate_signature
            
        Returns:
            List of generated signature file paths
        """
        signatures = []
        os.makedirs(signature_dir, exist_ok=True)
        
        for audio_file in audio_files:
            base_name = Path(audio_file).stem
            signature_file = os.path.join(signature_dir, f"{base_name}.freqs")
            
            if self.generate_signature(audio_file, signature_file, **kwargs):
                signatures.append(signature_file)
                print(f"Generated signature for {base_name}")
            else:
                print(f"Failed to generate signature for {base_name}")
        
        return signatures


def main():
    """Example usage of AudioProcessor."""
    processor = AudioProcessor()
    
    # Example: extract 10-second segment
    # processor.extract_segment("input.wav", "segment.wav", 30.0, 10.0)
    
    # Example: add noise
    # processor.add_noise("clean.wav", "noisy.wav", 0.05)
    
    # Example: generate signature
    # processor.generate_signature("audio.wav", "audio.freqs")
    
    print("AudioProcessor initialized successfully")


if __name__ == "__main__":
    main()