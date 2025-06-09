#!/usr/bin/env python3
"""
Evaluation Module
Tools for evaluating music identification performance.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from pathlib import Path


class MusicIdentificationEvaluator:
    """Evaluate music identification results."""
    
    def __init__(self):
        self.results_df = None
    
    def load_results(self, csv_file: str):
        """Load results from CSV file."""
        self.results_df = pd.read_csv(csv_file)
        return self.results_df
    
    def calculate_metrics(self, df: pd.DataFrame = None) -> Dict:
        """Calculate evaluation metrics."""
        if df is None:
            df = self.results_df
        
        if df is None:
            raise ValueError("No results loaded")
        
        metrics = {}
        
        # Basic statistics
        metrics['total_queries'] = len(df)
        metrics['unique_queries'] = df['query'].nunique()
        metrics['compressors_tested'] = df['compressor'].unique().tolist()
        
        # Accuracy metrics (if ground truth available)
        if 'correct' in df.columns and df['correct'].notna().any():
            metrics['overall_accuracy'] = df['correct'].mean()
            metrics['accuracy_by_compressor'] = df.groupby('compressor')['correct'].mean().to_dict()
            
            # Top-k accuracy (assuming we have top_5_matches)
            if 'top_5_matches' in df.columns:
                top_k_accuracies = {}
                for k in [1, 3, 5]:
                    correct_in_top_k = []
                    for _, row in df.iterrows():
                        if pd.isna(row['true_song']):
                            continue
                        top_matches = eval(row['top_5_matches']) if isinstance(row['top_5_matches'], str) else row['top_5_matches']
                        correct_in_top_k.append(any(row['true_song'] in match for match in top_matches[:k]))
                    top_k_accuracies[f'top_{k}_accuracy'] = np.mean(correct_in_top_k) if correct_in_top_k else 0
                metrics.update(top_k_accuracies)
        
        # NCD statistics
        metrics['mean_ncd'] = df['ncd_value'].mean()
        metrics['std_ncd'] = df['ncd_value'].std()
        metrics['min_ncd'] = df['ncd_value'].min()
        metrics['max_ncd'] = df['ncd_value'].max()
        metrics['ncd_by_compressor'] = df.groupby('compressor')['ncd_value'].agg(['mean', 'std']).to_dict()
        
        # Performance metrics
        metrics['mean_processing_time'] = df['processing_time'].mean()
        metrics['processing_time_by_compressor'] = df.groupby('compressor')['processing_time'].mean().to_dict()
        
        return metrics
    
    def analyze_compressor_performance(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyze performance by compressor."""
        if df is None:
            df = self.results_df
        
        summary = df.groupby('compressor').agg({
            'ncd_value': ['mean', 'std', 'min', 'max'],
            'processing_time': ['mean', 'std'],
            'correct': 'mean' if 'correct' in df.columns else lambda x: None
        }).round(4)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns]
        
        return summary
    
    def confusion_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyze common confusion patterns."""
        if df is None:
            df = self.results_df
        
        if 'true_song' not in df.columns or 'predicted' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without ground truth
        valid_df = df.dropna(subset=['true_song'])
        
        confusion_data = []
        for _, row in valid_df.iterrows():
            confusion_data.append({
                'true_song': row['true_song'],
                'predicted_song': row['predicted'],
                'correct': row['correct'] if 'correct' in row else None,
                'ncd_value': row['ncd_value'],
                'compressor': row['compressor']
            })
        
        return pd.DataFrame(confusion_data)
    
    def noise_robustness_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyze robustness to noise."""
        if df is None:
            df = self.results_df
        
        # Extract noise level from query names
        def extract_noise_level(query_name):
            if '_noise_' in query_name:
                try:
                    return float(query_name.split('_noise_')[1].split('_')[0])
                except:
                    return None
            return 0.0
        
        df_copy = df.copy()
        df_copy['noise_level'] = df_copy['query'].apply(extract_noise_level)
        
        # Group by noise level and compressor
        noise_analysis = df_copy.groupby(['noise_level', 'compressor']).agg({
            'ncd_value': ['mean', 'std'],
            'correct': 'mean' if 'correct' in df.columns else lambda x: None,
            'processing_time': 'mean'
        }).round(4)
        
        return noise_analysis
    
    def generate_report(self, output_file: str = None):
        """Generate comprehensive evaluation report."""
        if self.results_df is None:
            raise ValueError("No results loaded")
        
        metrics = self.calculate_metrics()
        compressor_perf = self.analyze_compressor_performance()
        
        report = []
        report.append("MUSIC IDENTIFICATION EVALUATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Basic statistics
        report.append("BASIC STATISTICS:")
        report.append(f"Total queries tested: {metrics['total_queries']}")
        report.append(f"Unique queries: {metrics['unique_queries']}")
        report.append(f"Compressors tested: {', '.join(metrics['compressors_tested'])}")
        report.append("")
        
        # Accuracy results
        if 'overall_accuracy' in metrics:
            report.append("ACCURACY RESULTS:")
            report.append(f"Overall accuracy: {metrics['overall_accuracy']:.3f}")
            report.append("Accuracy by compressor:")
            for comp, acc in metrics['accuracy_by_compressor'].items():
                report.append(f"  {comp:10s}: {acc:.3f}")
            
            # Top-k accuracy
            for k in [1, 3, 5]:
                key = f'top_{k}_accuracy'
                if key in metrics:
                    report.append(f"Top-{k} accuracy: {metrics[key]:.3f}")
            report.append("")
        
        # NCD statistics
        report.append("NCD STATISTICS:")
        report.append(f"Mean NCD: {metrics['mean_ncd']:.4f} ± {metrics['std_ncd']:.4f}")
        report.append(f"NCD range: [{metrics['min_ncd']:.4f}, {metrics['max_ncd']:.4f}]")
        report.append("Mean NCD by compressor:")
        for comp in metrics['compressors_tested']:
            mean_ncd = metrics['ncd_by_compressor']['mean'][comp]
            std_ncd = metrics['ncd_by_compressor']['std'][comp]
            report.append(f"  {comp:10s}: {mean_ncd:.4f} ± {std_ncd:.4f}")
        report.append("")
        
        # Performance statistics
        report.append("PERFORMANCE STATISTICS:")
        report.append(f"Mean processing time: {metrics['mean_processing_time']:.3f}s")
        report.append("Processing time by compressor:")
        for comp, time_val in metrics['processing_time_by_compressor'].items():
            report.append(f"  {comp:10s}: {time_val:.3f}s")
        report.append("")
        
        # Detailed compressor analysis
        report.append("DETAILED COMPRESSOR ANALYSIS:")
        report.append(compressor_perf.to_string())
        report.append("")
        
        # Noise robustness (if applicable)
        noise_analysis = self.noise_robustness_analysis()
        if not noise_analysis.empty:
            report.append("NOISE ROBUSTNESS ANALYSIS:")
            report.append(noise_analysis.to_string())
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to {output_file}")
        
        return report_text
    
    def plot_performance_comparison(self, output_dir: str = "./plots"):
        """Generate performance comparison plots."""
        if self.results_df is None:
            raise ValueError("No results loaded")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        df = self.results_df
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. NCD distribution by compressor
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        sns.violinplot(data=df, x='compressor', y='ncd_value')
        plt.title('NCD Value Distribution by Compressor')
        plt.xticks(rotation=45)
        
        # 2. Processing time comparison
        plt.subplot(2, 2, 2)
        time_stats = df.groupby('compressor')['processing_time'].mean()
        bars = plt.bar(time_stats.index, time_stats.values)
        plt.title('Average Processing Time')
        plt.ylabel('Time (seconds)')
        plt.xticks(rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, time_stats.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 3. Accuracy comparison (if available)
        if 'correct' in df.columns and df['correct'].notna().any():
            plt.subplot(2, 2, 3)
            acc_stats = df.groupby('compressor')['correct'].mean()
            bars = plt.bar(acc_stats.index, acc_stats.values)
            plt.title('Identification Accuracy')
            plt.ylabel('Accuracy')
            plt.ylim(0, 1)
            plt.xticks(rotation=45)
            
            for bar, value in zip(bars, acc_stats.values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 4. NCD vs Processing Time scatter
        plt.subplot(2, 2, 4)
        for comp in df['compressor'].unique():
            comp_data = df[df['compressor'] == comp]
            plt.scatter(comp_data['processing_time'], comp_data['ncd_value'], 
                       label=comp, alpha=0.6)
        plt.xlabel('Processing Time (s)')
        plt.ylabel('NCD Value')
        plt.title('NCD vs Processing Time')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path / 'performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance plots saved to {output_path}")


def main():
    """Example usage of MusicIdentificationEvaluator."""
    evaluator = MusicIdentificationEvaluator()
    
    results_csv = "results/evaluation_results.csv"
    report_txt = "results/evaluation_report.txt"
    plots_dir = "results/plots"
    
    # Load results
    df = evaluator.load_results(results_csv)
    
    # Generate and save report
    report = evaluator.generate_report(report_txt)
    print(report)
    
    # Generate and save performance plots
    evaluator.plot_performance_comparison(plots_dir)