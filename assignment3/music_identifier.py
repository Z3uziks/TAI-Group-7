import os
import numpy as np
import subprocess
import tempfile
from typing import List, Tuple, Dict
import json
from pathlib import Path
from audio_processor import get_max_frequencies, convert_to_wav

class MusicIdentifier:
    def __init__(self, compressor: str = 'gzip'):
        """
        Initialize the MusicIdentifier with a specific compressor.
        
        Args:
            compressor: The compression algorithm to use ('gzip', 'bzip2', 'lzma', 'zstd')
        """
        self.compressor = compressor
        self.database: Dict[str, str] = {}  # music_name -> signature
        
    def extract_signature(self, audio_path: str, n_freqs: int = 100) -> str:
        """
        Extract a signature from an audio file using GetMaxFreqs approach.
        
        Args:
            audio_path: Path to the audio file
            n_freqs: Number of most significant frequencies to keep
            
        Returns:
            String representation of the signature
        """
        # Convert to WAV if needed
        if not audio_path.endswith('.wav'):
            with tempfile.NamedTemporaryFile(suffix='.wav') as temp_wav:
                convert_to_wav(audio_path, temp_wav.name)
                freqs = get_max_frequencies(temp_wav.name, n_freqs)
        else:
            freqs = get_max_frequencies(audio_path, n_freqs)
        
        # Convert frequencies to string representation
        return ','.join(map(str, freqs))
    
    def compute_ncd(self, x: str, y: str) -> float:
        """
        Compute the Normalized Compression Distance between two signatures.
        
        Args:
            x: First signature
            y: Second signature
            
        Returns:
            NCD value between 0 and 1
        """
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as fx, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as fy, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as fxy:
            
            # Write signatures to files
            fx.write(x)
            fy.write(y)
            fxy.write(x + y)
            
            # Flush to ensure content is written
            fx.flush()
            fy.flush()
            fxy.flush()
            
            # Get compressed sizes
            cx = self._get_compressed_size(fx.name)
            cy = self._get_compressed_size(fy.name)
            cxy = self._get_compressed_size(fxy.name)
            
            # Compute NCD
            return (cxy - min(cx, cy)) / max(cx, cy)
    
    def _get_compressed_size(self, file_path: str) -> int:
        """Get the size of a compressed file in bytes."""
        if self.compressor == 'gzip':
            cmd = ['gzip', '-c', file_path]
        elif self.compressor == 'bzip2':
            cmd = ['bzip2', '-c', file_path]
        elif self.compressor == 'lzma':
            cmd = ['lzma', '-c', file_path]
        elif self.compressor == 'zstd':
            cmd = ['zstd', '-c', file_path]
        else:
            raise ValueError(f"Unsupported compressor: {self.compressor}")
        
        result = subprocess.run(cmd, capture_output=True)
        return len(result.stdout)
    
    def add_to_database(self, music_path: str, music_name: str):
        """Add a music to the database."""
        signature = self.extract_signature(music_path)
        self.database[music_name] = signature
    
    def identify(self, query_path: str) -> Tuple[str, float]:
        """
        Identify a music segment by finding the closest match in the database.
        
        Args:
            query_path: Path to the query audio segment
            
        Returns:
            Tuple of (music_name, ncd_value) for the best match
        """
        query_sig = self.extract_signature(query_path)
        
        best_match = None
        best_ncd = float('inf')
        
        for music_name, db_sig in self.database.items():
            ncd = self.compute_ncd(query_sig, db_sig)
            if ncd < best_ncd:
                best_ncd = ncd
                best_match = music_name
        
        return best_match, best_ncd
    
    def save_database(self, path: str):
        """Save the database to a file."""
        with open(path, 'w') as f:
            json.dump(self.database, f)
    
    def load_database(self, path: str):
        """Load the database from a file."""
        with open(path, 'r') as f:
            self.database = json.load(f) 