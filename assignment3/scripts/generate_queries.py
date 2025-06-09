#!/usr/bin/env python3
"""
Query Generation Script
Generates query segments from database music files for testing.
"""

import os
import sys
import argparse
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio_processor import AudioProcessor


def main():
    parser = argparse.ArgumentParser(description='Generate query segments for testing')
    parser.add_argument('--database-dir', default='./database',
                       help='Directory containing music files')
    parser.add_argument('--queries-dir', default='./queries',
                       help='Directory to store query segments')
    parser.add_argument('--getmaxfreqs-path', default='./GetMaxFreqs/bin/GetMaxFreqs',
                       help='Path to GetMaxFreqs executable')
    parser.add_argument('--segment-duration', type=float, default=10.0,
                       help='Duration of query segments in seconds')
    parser.add_argument('--segments-per-song', type=int, default=3,
                       help='Number of segments per song')
    parser.add_argument('--max-songs', type=int, default=None,
                       help='Maximum number of songs to process')
    parser.add_argument('--add-noise', action='store_true',
                       help='Generate noisy versions of segments')
    parser.add_argument('--noise-levels', nargs='+', type=float, 
                       default=[0.02, 0.05, 0.1],
                       help='Noise levels to apply')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Check database directory
    database_path = Path(args.database_dir)
    if not database_path.exists():
        print(f"Error: Database directory '{args.database_dir}' not found")
        return 1
    
    # Create queries directory
    queries_path = Path(args.queries_dir)
    queries_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize audio processor
    try:
        processor = AudioProcessor(args.getmaxfreqs_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Find audio files
    audio_extensions = ['.wav', '.flac', '.mp3']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(list(database_path.glob(f"*{ext}")))
        #audio_files.extend(list(database_path.glob(f"**/*{ext}")))
    
    if not audio_files:
        print("No audio files found in database directory")
        return 1
    
    # Limit number of songs if specified
    if args.max_songs and len(audio_files) > args.max_songs:
        audio_files = random.sample(audio_files, args.max_songs)
    
    print(f"Processing {len(audio_files)} audio files")
    print(f"Generating {args.segments_per_song} segments per song")
    
    total_segments = 0
    successful_songs = 0
    
    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file.name}")
        
        # Generate segments for this song
        segments = processor.generate_random_segments(
            str(audio_file),
            str(queries_path),
            segment_duration=args.segment_duration,
            num_segments=args.segments_per_song
        )
        
        if segments:
            successful_songs += 1
            total_segments += len(segments)
            print(f"  Generated {len(segments)} segments")
            
            # Generate noisy versions if requested
            if args.add_noise:
                for segment in segments:
                    segment_path = Path(segment)
                    for noise_level in args.noise_levels:
                        noisy_name = f"{segment_path.stem}_noise_{noise_level:.3f}.wav"
                        noisy_file = queries_path / noisy_name
                        
                        if processor.add_noise(segment, str(noisy_file), noise_level):
                            total_segments += 1
                            print(f"    Added noise version (level {noise_level})")
        else:
            print(f"  Failed to generate segments for {audio_file.name}")
    
    print(f"\nQuery generation completed!")
    print(f"Processed {successful_songs}/{len(audio_files)} songs")
    print(f"Generated {total_segments} total query segments")
    print(f"Segments saved in: {queries_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())