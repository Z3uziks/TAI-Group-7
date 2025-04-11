import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def get_group(name):
    """
    Extract a simple group name from the Organism string.
    Convert the name to string if needed, then remove the accession number 
    (first token) and return the first two words from the remaining string.
    """
    name = str(name)
    parts = name.split(" ", 1)
    if len(parts) > 1:
        rest = parts[1]
        group_words = rest.split()[:2]
        return " ".join(group_words)
    return name

def shorten_name(name, max_length=20):
    """
    Shorten the name to max_length characters (adding ellipsis if needed).
    """
    name = str(name)
    return name if len(name) <= max_length else name[:max_length] + "..."

with open('results.csv') as f:
    lines = f.readlines()

data = []
for line in lines[1:]: 
    parts = line.strip().split(',', 2)
    if len(parts) == 3:
        rank, nrc, organism = parts
        data.append({'Rank': int(rank), 'NRC': float(nrc), 'Organism': organism})
        
results = pd.DataFrame(data)
print(results['NRC'])

results['group'] = results['Organism'].apply(get_group)

group_counts = results['group'].value_counts()
similar_groups = group_counts[group_counts > 1].index.tolist()

output_dir = 'plots/similarity_heatmaps'
os.makedirs(output_dir, exist_ok=True)

for grp in similar_groups:
    grp_data = results[results['group'] == grp].reset_index(drop=True)
    n = len(grp_data)
    
    # Create matrix of absolute differences in NRC values
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i, j] = abs(grp_data.loc[i, 'NRC'] - grp_data.loc[j, 'NRC'])
    
    short_names = grp_data['Organism'].apply(lambda n: shorten_name(n, max_length=20))
    df_matrix = pd.DataFrame(matrix, index=short_names, columns=short_names)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(df_matrix, annot=True, cmap='YlGnBu', fmt=".3f", linewidths=0.5,
                cbar_kws={'label': 'NRC Difference'})
    plt.title(f'Similarity Heatmap for Group: {grp}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    filename = os.path.join(output_dir, f"{grp.replace(' ', '_')}_similarity_heatmap.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Saved heatmap for group '{grp}' to {filename}")