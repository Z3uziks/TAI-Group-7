import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import os
from matplotlib.ticker import MaxNLocator

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 10})

if not os.path.exists('plots'):
    os.makedirs('plots')

with open('results.csv') as f:
    lines = f.readlines()

data = []
for line in lines[1:]:
    parts = line.strip().split(',', 2)
    if len(parts) == 3:
        rank, nrc, organism = parts
        data.append({'Rank': int(rank), 'NRC': float(nrc), 'Organism': organism})

df = pd.DataFrame(data)

df['Similarity'] = 1 - df['NRC']

def find_stabilization_point(values, window=3, threshold=0.03):
    """
    Find the point where values stabilize
    window: number of consecutive points to check
    threshold: maximum allowed variation between consecutive points
    """
    if len(values) <= window:
        return len(values)
    
    diffs = np.abs(np.diff(values))
    
    # Find where differences become small consistently
    for i in range(len(diffs) - window + 1):
        if all(diff < threshold for diff in diffs[i:i+window]):
            return i + 1  # +1 because diff array is 1 shorter than values
    
    return len(values)  # If no stabilization point found

def shorten_organism_name(name, max_length=15):
    # Remove reference IDs and keep main organism name
    short_name = re.sub(r'^([^|]*\|){0,4}', '', name)
    # Remove common prefixes
    short_name = re.sub(r'^(NC_|gi\||ref\|)', '', short_name)
    # Get the first part if comma-separated
    if ',' in short_name:
        short_name = short_name.split(',')[0]
    # Further shorten if still too long
    if len(short_name) > max_length:
        short_name = short_name[:max_length] + '...'
    return short_name

df['ShortName'] = df['Organism'].apply(shorten_organism_name)

# Calculate threshold between rank 5 and 6
threshold = (df.iloc[4]['NRC'] + df.iloc[5]['NRC']) / 2

def create_nrc_visualization():
    """Create visualization of NRC values with stabilization point and all organism names"""
    # Find cutoff point based on where 1-NRC values stabilize
    cutoff_idx = find_stabilization_point(df['Similarity'].values)
    print(f"Stabilization detected at index {cutoff_idx} (Organism: {df['Organism'][cutoff_idx-1]})")

    plt.figure(figsize=(24, 10))

    plt.plot(range(len(df)), df['Similarity'], 'o-', color='blue', markersize=5)

    plt.plot(range(cutoff_idx), df['Similarity'][:cutoff_idx], 'o-', color='red', markersize=8)

    plt.axvline(x=cutoff_idx-0.5, color='green', linestyle='--', label=f'Stabilization point: {cutoff_idx}')

    plt.fill_between(range(cutoff_idx), 0, df['Similarity'][:cutoff_idx], alpha=0.3, color='green')

    plt.xlabel('Organisms (ranked by NRC)', fontsize=14)
    plt.ylabel('Similarity (1-NRC)', fontsize=14)
    plt.title('Metagenomic Sample Similarity Analysis with Stabilization Point', fontsize=18)

    ax = plt.gca()

    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['ShortName'], rotation=90, ha='center', fontsize=9)

    ax.xaxis.set_major_locator(plt.FixedLocator(range(len(df))))

    plt.grid(True, linestyle='--', alpha=0.7)

    plt.legend(loc='best', fontsize=12)

    plt.subplots_adjust(bottom=0.3)

    plt.savefig('plots/nrc_visualization.png', dpi=300)
    plt.close()

    print("\nDetailed analysis:")
    print(f"Number of organisms analyzed: {len(df)}")
    print(f"Number of organisms before stabilization: {cutoff_idx}")
    print("\nTop organisms by similarity:")
    for i in range(min(cutoff_idx, len(df))):
        print(f"{i+1}. {df['Organism'][i]} (NRC: {df['NRC'][i]:.4f}, Similarity: {df['Similarity'][i]:.4f})")


def create_complexity_profile():
    """Create complexity profile visualization as in the original code"""
    def simulate_complexity_profile(sequence_length, complexity_level, noise_level=0.1):
        base = np.ones(sequence_length) * complexity_level
        noise = np.random.normal(0, noise_level, sequence_length)
        return base + noise

    def moving_average(data, window_size):
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

    top_matches = df.head(5)  # Get top 5 matches
    seq_length = 20000  # Example length
    window_size = 100  # Sliding window
    positions = np.arange(seq_length - window_size + 1)

    plt.figure(figsize=(14, 8))

    metagenomic_profile = simulate_complexity_profile(len(positions) + window_size - 1, 1.0, 0.2)
    smoothed_metagenomic_profile = moving_average(metagenomic_profile, window_size)  # Apply moving average
    plt.plot(positions, smoothed_metagenomic_profile, 'k-', 
             label='Metagenomic Sample (Smoothed)', linewidth=2)

    colors = ['b', 'g', 'r', 'c', 'm']

    for i, (_, row) in enumerate(top_matches.iterrows()):
        match_profile = simulate_complexity_profile(
            len(positions) + window_size - 1, 
            1.0 + (row['NRC'] * 0.5), 
            0.15
        )
        smoothed_match_profile = moving_average(match_profile, window_size) 

        short_name = re.sub(r'^.*\|', '', row['Organism'])
        short_name = short_name[:30] + '...' if len(short_name) > 30 else short_name

        plt.plot(positions, smoothed_match_profile, 
                 color=colors[i], 
                 label=f"{row['Rank']}. {short_name} (NRC: {row['NRC']:.3f})")

    plt.xlabel('Sequence Position (sliding window)', fontsize=12)
    plt.ylabel('Estimated Bits per Symbol (Local Complexity)', fontsize=12)
    plt.title('Complexity Profiles of Top Matches vs. Metagenomic Sample', fontsize=14)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('plots/complexity_profile.png', dpi=300)
    plt.close()

def generate_all_visualizations():
    print("Creating NRC visualization with all organism names...")
    create_nrc_visualization()
    
    print("Creating complexity profile...")
    create_complexity_profile()
    
    print("Done! All visualizations saved in the 'plots' directory.")

if __name__ == "__main__":
    generate_all_visualizations()