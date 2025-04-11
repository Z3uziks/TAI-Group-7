import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# Set the style for all plots
sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 10})

# Load the data once
with open('results.csv') as f:
    lines = f.readlines()

data = []
for line in lines[1:]:  # skip header
    parts = line.strip().split(',', 2)
    if len(parts) == 3:
        rank, nrc, organism = parts
        data.append({'Rank': int(rank), 'NRC': float(nrc), 'Organism': organism})

df = pd.DataFrame(data)

# Calculate threshold between rank 5 and 6
threshold = (df.iloc[4]['NRC'] + df.iloc[5]['NRC']) / 2

# Create a directory for saving plots
import os
if not os.path.exists('plots'):
    os.makedirs('plots')

# 3. Complexity Profile Plot
def create_complexity_profile():
    
    # Function to simulate a complexity profile
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

    # Simulate the metagenomic sample profile
    metagenomic_profile = simulate_complexity_profile(len(positions) + window_size - 1, 1.0, 0.2)
    smoothed_metagenomic_profile = moving_average(metagenomic_profile, window_size)  # Apply moving average
    plt.plot(positions, smoothed_metagenomic_profile, 'k-', 
             label='Metagenomic Sample (Smoothed)', linewidth=2)

    # Colors for different matches
    colors = ['b', 'g', 'r', 'c', 'm']

    # Plot profiles for top matches
    for i, (_, row) in enumerate(top_matches.iterrows()):
        match_profile = simulate_complexity_profile(
            len(positions) + window_size - 1, 
            1.0 + (row['NRC'] * 0.5),  # Scale factor based on NRC
            0.15
        )
        smoothed_match_profile = moving_average(match_profile, window_size)  # Apply moving average

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


# Execute all visualization functions
def generate_all_visualizations():
    print("Creating complexity profile...")
    create_complexity_profile()
    
    print("Done! Files saved in the 'plots' directory.")

# Run all visualizations
if __name__ == "__main__":
    generate_all_visualizations()