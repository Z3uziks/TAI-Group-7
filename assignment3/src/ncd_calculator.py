#!/usr/bin/env python3
"""
Normalized Compression Distance (NCD) Calculator
Implementation for music identification using various compression algorithms.
"""

import gzip
import bz2
import lzma
import zstandard as zstd
import os
import tempfile
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path


class NCDCalculator:
    """Calculate NCD using different compression algorithms."""
    
    def __init__(self):
        self.compressors = {
            'gzip': self._compress_gzip,
            'bzip2': self._compress_bzip2,
            'lzma': self._compress_lzma,
            'zstd': self._compress_zstd
        }
    
    def _compress_gzip(self, data: bytes) -> int:
        """Compress data using gzip and return compressed size."""
        return len(gzip.compress(data))
    
    def _compress_bzip2(self, data: bytes) -> int:
        """Compress data using bzip2 and return compressed size."""
        return len(bz2.compress(data))
    
    def _compress_lzma(self, data: bytes) -> int:
        """Compress data using lzma and return compressed size."""
        return len(lzma.compress(data))
    
    def _compress_zstd(self, data: bytes) -> int:
        """Compress data using zstandard and return compressed size."""
        cctx = zstd.ZstdCompressor()
        return len(cctx.compress(data))
    
    def read_signature(self, filepath: str) -> bytes:
        """Read frequency signature file and return as bytes."""
        with open(filepath, 'rb') as f:
            return f.read()
    
    def calculate_ncd(self, x_data: bytes, y_data: bytes, compressor: str = 'gzip') -> float:
        """
        Calculate NCD between two byte sequences.
        
        NCD(x,y) = [C(x,y) - min{C(x), C(y)}] / max{C(x), C(y)}
        
        Args:
            x_data: First data sequence
            y_data: Second data sequence
            compressor: Compression algorithm to use
            
        Returns:
            NCD value between 0 and 1
        """
        if compressor not in self.compressors:
            raise ValueError(f"Unsupported compressor: {compressor}")
        
        compress_func = self.compressors[compressor]
        
        # Calculate individual compressed sizes
        c_x = compress_func(x_data)
        c_y = compress_func(y_data)
        
        # Calculate joint compressed size
        xy_data = x_data + y_data
        c_xy = compress_func(xy_data)
        
        # Calculate NCD
        numerator = c_xy - min(c_x, c_y)
        denominator = max(c_x, c_y)
        
        if denominator == 0:
            return 0.0
        
        ncd = numerator / denominator
        return max(0.0, min(1.0, ncd))  # Clamp to [0, 1]
    
    def calculate_ncd_from_files(self, file1: str, file2: str, compressor: str = 'gzip') -> float:
        """Calculate NCD between two signature files."""
        data1 = self.read_signature(file1)
        data2 = self.read_signature(file2)
        return self.calculate_ncd(data1, data2, compressor)
    
    def compare_all_compressors(self, x_data: bytes, y_data: bytes) -> Dict[str, float]:
        """Compare NCD values across all available compressors."""
        results = {}
        for compressor in self.compressors:
            results[compressor] = self.calculate_ncd(x_data, y_data, compressor)
        return results
    
    def batch_compare(self, query_file: str, database_files: List[str], 
                     compressor: str = 'gzip') -> List[Tuple[str, float]]:
        """
        Compare query against database and return sorted results.
        
        Args:
            query_file: Path to query signature file
            database_files: List of database signature file paths
            compressor: Compression algorithm to use
            
        Returns:
            List of (filename, ncd_value) tuples sorted by NCD value
        """
        query_data = self.read_signature(query_file)
        results = []
        
        for db_file in database_files:
            db_data = self.read_signature(db_file)
            ncd_value = self.calculate_ncd(query_data, db_data, compressor)
            results.append((os.path.basename(db_file), ncd_value))
        
        # Sort by NCD value (ascending - lower is better)
        results.sort(key=lambda x: x[1])
        return results


def main():
    """Example usage of NCDCalculator."""
    calc = NCDCalculator()
    
    # Example with dummy data
    data1 = b"This is a test string for compression."
    data2 = b"This is another test string for compression."
    
    print("NCD Calculation Example:")
    print(f"Data 1: {data1}")
    print(f"Data 2: {data2}")
    print()
    
    # Compare across all compressors
    results = calc.compare_all_compressors(data1, data2)
    for compressor, ncd in results.items():
        print(f"{compressor:8s}: {ncd:.6f}")


if __name__ == "__main__":
    main()