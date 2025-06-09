#!/usr/bin/env python3
"""
Database Setup Script
Prepares the music database and generates signatures.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from music_identifier import MusicIdentifier


def main():
    parser = argparse.ArgumentParser(description='Setup music identification database')
    parser.add_argument('--database-dir', default='./database',
                       help='Directory containing music files')
    parser.add_argument('--signatures-dir', default='./signatures',
                       help='Directory to store signatures')
    parser.add_argument('--getmaxfreqs-path', default='./GetMaxFreqs/bin/GetMaxFreqs',
                       help='Path to GetMaxFreqs executable')
    parser.add_argument('--win-size', type=int, default=1024,
                       help='Window size for frequency analysis')
    parser.add_argument('--shift', type=int, default=256,
                       help='Shift between windows')
    parser.add_argument('--down-sampling', type=int, default=4,
                       help='Down sampling factor')
    parser.add_argument('--n-freqs', type=int, default=4,
                       help='Number of frequency components')
    parser.add_argument('--rebuild', action='store_true',
                       help='Rebuild database even if it exists')
    
    args = parser.parse_args()
    
    # Check if database directory exists
    if not Path(args.database_dir).exists():
        print(f"Error: Database directory '{args.database_dir}' not found")
        print("Please place your music files in the database directory")
        return 1
    
    # Initialize identifier
    try:
        identifier = MusicIdentifier(
            database_dir=args.database_dir,
            signatures_dir=args.signatures_dir,
            getmaxfreqs_path=args.getmaxfreqs_path
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Check if database already exists
    if not args.rebuild and identifier.load_database():
        print("Database already exists. Use --rebuild to recreate it.")
        return 0
    
    # Build database
    signature_params = {
        'win_size': args.win_size,
        'shift': args.shift,
        'down_sampling': args.down_sampling,
        'n_freqs': args.n_freqs
    }
    
    print("Building signature database...")
    success = identifier.build_database(signature_params)
    
    if success:
        print("Database setup completed successfully!")
        print(f"Generated {len(identifier.database_signatures)} signatures")
        return 0
    else:
        print("Database setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())