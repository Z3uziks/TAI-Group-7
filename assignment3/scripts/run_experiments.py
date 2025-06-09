#!/usr/bin/env python3
"""
Experiment Runner Script
Runs comprehensive music identification experiments.
"""

import os
import sys
import argparse
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from music_identifier import MusicIdentifier


def plot_results(df: pd.DataFrame, output_dir: str):
    """Generate plots for experimental results."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. Accuracy by compressor
    if 'correct' in df.columns and df['correct'].notna().any():
        plt.figure(figsize=(10, 6))
        accuracy_by_comp = df.groupby('compressor')['correct'].mean()
        bars = plt.bar(accuracy_by_comp.index, accuracy_by_comp.values)
        plt.title('Identification Accuracy by Compressor')
        plt.xlabel('Compressor')
        plt.ylabel('Accuracy')
        plt.ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, accuracy_by_comp.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path / 'accuracy_by_compressor.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. NCD value distribution by compressor
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='compressor', y='ncd_value')
    plt.title('NCD Value Distribution by Compressor')
    plt.xlabel('Compressor')
    plt.ylabel('NCD Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path / 'ncd_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Processing time by compressor
    plt.figure(figsize=(10, 6))
    time_by_comp = df.groupby('compressor')['processing_time'].mean()
    bars = plt.bar(time_by_comp.index, time_by_comp.values)
    plt.title('Average Processing Time by Compressor')
    plt.xlabel('Compressor')
    plt.ylabel('Processing Time (seconds)')
    
    # Add value labels
    for bar, value in zip(bars, time_by_comp.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{value:.3f}s', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path / 'processing_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Correlation matrix
    numeric_cols = ['ncd_value', 'processing_time']
    if 'correct' in df.columns:
        numeric_cols.append('correct')
    
    if len(numeric_cols) > 1:
        plt.figure(figsize=(8, 6))
        corr_matrix = df[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_path / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Plots saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Run music identification experiments')
    parser.add_argument('--database-dir', default='./database',
                       help='Directory containing music files')
    parser.add_argument('--queries-dir', default='./queries',
                       help='Directory containing query segments')
    parser.add_argument('--signatures-dir', default='./signatures',
                       help='Directory for signatures')
    parser.add_argument('--results-dir', default='./results',
                       help='Directory for results')
    parser.add_argument('--getmaxfreqs-path', default='./GetMaxFreqs/bin/GetMaxFreqs',
                       help='Path to GetMaxFreqs executable')
    parser.add_argument('--compressors', nargs='+', 
                       default=['gzip', 'bzip2', 'lzma', 'zstd'],
                       help='Compressors to test')
    parser.add_argument('--noise-levels', nargs='+', type=float,
                       default=[0.0, 0.02, 0.05, 0.1],
                       help='Noise levels to test')
    parser.add_argument('--max-queries', type=int, default=None,
                       help='Maximum number of queries to test')
    parser.add_argument('--generate-plots', action='store_true',
                       help='Generate result plots')
    
    args = parser.parse_args()
    
    # Create results directory
    results_path = Path(args.results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
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
    
    # Load database
    if not identifier.load_database():
        print("Database not found. Please run setup_database.py first.")
        return 1
    
    print(f"Loaded database with {len(identifier.database_signatures)} signatures")
    
    # Find query files
    queries_path = Path(args.queries_dir)
    if not queries_path.exists():
        print(f"Queries directory '{args.queries_dir}' not found")
        print("Please run generate_queries.py first or place query files manually")
        return 1
    
    query_files = []
    for ext in ['.wav', '.flac']:
        query_files.extend(list(queries_path.glob(f"*{ext}")))
    
    if not query_files:
        print("No query files found")
        return 1
    
    # Limit queries if specified
    if args.max_queries and len(query_files) > args.max_queries:
        query_files = query_files[:args.max_queries]
    
    print(f"Found {len(query_files)} query files")
    
    # Run experiments
    print("Starting experiments...")
    results = identifier.batch_identify(
        [str(f) for f in query_files],
        compressors=args.compressors,
        add_noise_levels=args.noise_levels
    )
    
    if not results:
        print("No results generated")
        return 1
    
    # Save raw results
    results_file = results_path / "identification_results.json"
    identifier.save_results(results, str(results_file))
    
    # Evaluate results
    df = identifier.evaluate_results(results)
    
    # Save evaluation DataFrame
    csv_file = results_path / "evaluation_results.csv"
    df.to_csv(csv_file, index=False)
    print(f"Results saved to {csv_file}")
    
    # Print summary statistics
    print("\n" + "="*50)
    print("EXPERIMENT SUMMARY")
    print("="*50)
    
    print(f"Total tests run: {len(results)}")
    print(f"Unique queries: {df['query'].nunique()}")
    print(f"Compressors tested: {', '.join(args.compressors)}")
    print(f"Noise levels tested: {args.noise_levels}")
    
    if 'correct' in df.columns and df['correct'].notna().any():
        overall_accuracy = df['correct'].mean()
        print(f"\nOverall accuracy: {overall_accuracy:.3f}")
        
        print("\nAccuracy by compressor:")
        accuracy_by_comp = df.groupby('compressor')['correct'].mean()
        for comp, acc in accuracy_by_comp.items():
            print(f"  {comp:8s}: {acc:.3f}")
    
    print(f"\nAverage NCD values by compressor:")
    ncd_by_comp = df.groupby('compressor')['ncd_value'].mean()
    for comp, ncd in ncd_by_comp.items():
        print(f"  {comp:8s}: {ncd:.4f}")
    
    print(f"\nAverage processing time by compressor:")
    time_by_comp = df.groupby('compressor')['processing_time'].mean()
    for comp, time_val in time_by_comp.items():
        print(f"  {comp:8s}: {time_val:.3f}s")
    
    # Generate plots if requested
    if args.generate_plots:
        try:
            plot_results(df, str(results_path / "plots"))
        except Exception as e:
            print(f"Warning: Could not generate plots: {e}")
    
    print(f"\nAll results saved in: {results_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())