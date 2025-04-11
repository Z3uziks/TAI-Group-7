import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import os
import re

def extract_sequence_from_db(db_file, organism_name):
    """Extract the DNA sequence for a specific organism from the database file."""
    with open(db_file, 'r') as f:
        content = f.read()
    
    # Find the section for the organism
    pattern = f"@{re.escape(organism_name)}\\n([ACGT\\n]+?)(?=@|$)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Get the sequence and remove any whitespace
        sequence = match.group(1)
        sequence = re.sub(r'\s+', '', sequence)
        return sequence
    else:
        print(f"Warning: Could not find organism '{organism_name}' in the database.")
        return None

def find_stabilization_organisms():
    """Find the organisms before stabilization point from the results.csv file."""
    cmd = ["./MetaClass", "-d", "db.txt", "-s", "meta.txt", "-k", "10", "-a", "0.01", "-t", "20"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running MetaClass: {e}")
        return []

    with open('results.csv') as f:
        lines = f.readlines()

    data = []
    for line in lines[1:]:
        parts = line.strip().split(',', 2)
        if len(parts) == 3:
            rank, nrc, organism = parts
            data.append({'Rank': int(rank), 'NRC': float(nrc), 'Organism': organism})

    df = pd.DataFrame(data)
    
    # Calculate 1-NRC for each organism (higher means more similar)
    df['Similarity'] = 1 - df['NRC']
    
    # Find stabilization point
    def find_stabilization_point(values, window=3, threshold=0.03):
        if len(values) <= window:
            return len(values)
        
        diffs = np.abs(np.diff(values))
        
        for i in range(len(diffs) - window + 1):
            if all(diff < threshold for diff in diffs[i:i+window]):
                return i + 1
        
        return len(values)
    
    cutoff_idx = find_stabilization_point(df['Similarity'].values)
    print(f"Stabilization detected at index {cutoff_idx} (Organism: {df['Organism'][cutoff_idx-1]})")
    
    return df.iloc[:cutoff_idx]['Organism'].tolist()

def create_similarity_matrix(db_file, organisms, output_dir="./"):
    """Create a similarity matrix for the given organisms."""
    # Create directory for temporary files
    os.makedirs("temp_meta", exist_ok=True)
    
    n_organisms = len(organisms)
    similarity_matrix = np.zeros((n_organisms, n_organisms))
    
    for i, query_organism in enumerate(organisms):
        print(f"Processing {i+1}/{n_organisms}: {query_organism}")
        
        sequence = extract_sequence_from_db(db_file, query_organism)
        if sequence is None:
            continue
            
        with open("temp_meta/query.txt", "w") as f:
            f.write(sequence)
        
        # Run MetaClass with this sequence as the query
        cmd = ["./MetaClass", "-d", db_file, "-s", "temp_meta/query.txt", "-k", "10", "-a", "0.01", "-t", "20"]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running MetaClass: {e}")
            continue
            
        with open('results.csv') as f:
            lines = f.readlines()[1:]  
        
        results = {}
        for line in lines:
            parts = line.strip().split(',', 2)
            if len(parts) == 3:
                rank, nrc, org = parts
                results[org] = float(nrc)
        
        for j, ref_organism in enumerate(organisms):
            if ref_organism in results:
                similarity_matrix[i, j] = max(0, 1 - results[ref_organism])  # Ensure no negative values
            else:
                # If not found, use a default low similarity value
                similarity_matrix[i, j] = 0.0
                print(f"Warning: {ref_organism} not found in results for {query_organism}")
    
    # Make sure diagonal is 1.0 (perfect similarity with self)
    for i in range(n_organisms):
        similarity_matrix[i, i] = 1.0
    
    short_names = []
    for name in organisms:
        # Simplify names for better display
        short_name = re.sub(r'^([^|]*\|){0,4}', '', name)
        short_name = re.sub(r'^(NC_|gi\||ref\|)', '', short_name)
        if ',' in short_name:
            short_name = short_name.split(',')[0]
        if len(short_name) > 15:
            short_name = short_name[:15] + '...'
        short_names.append(short_name)
    
    plt.figure(figsize=(12, 10))
    
    ax = sns.heatmap(similarity_matrix, 
                 cmap="YlGnBu",
                 vmin=0, 
                 vmax=1.0,
                 annot=True,
                 fmt=".2f",
                 square=True,
                 linewidths=.5,
                 cbar_kws={"shrink": .8, "label": "Similarity (1-NRC)"},
                 xticklabels=short_names,
                 yticklabels=short_names)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.title("Genomic Similarity Matrix", fontsize=16, pad=20)
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/similarity_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    df_matrix = pd.DataFrame(similarity_matrix, index=organisms, columns=organisms)
    df_matrix.to_csv(f"{output_dir}/similarity_matrix.csv")
    
    print(f"Full similarity matrix created and saved to {output_dir}/similarity_matrix.png")
    print(f"Matrix data saved to {output_dir}/similarity_matrix.csv")
    
    return similarity_matrix


def cleanup():
    """Clean up temporary files."""
    if os.path.exists("temp_meta"):
        import shutil
        shutil.rmtree("temp_meta")

def main():
    # Get the database file path
    db_file = input("Enter the path to your database file (e.g., db.txt): ")
    
    if not os.path.exists(db_file):
        print(f"Error: Database file {db_file} not found.")
        return
    
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    # Find organisms before stabilization
    print("Finding organisms before stabilization...")
    organisms = find_stabilization_organisms()
    
    if not organisms:
        print("No organisms found before stabilization. Check results.csv file.")
        return
    
    print(f"Found {len(organisms)} organisms before stabilization:")
    for i, org in enumerate(organisms):
        print(f"{i+1}. {org}")
    
    # Create similarity matrix
    print("\nCreating similarity matrix...")
    create_similarity_matrix(db_file, organisms, "plots")
    
    cleanup()
    
    print("\nDone! Similarity matrix has been created in the 'plots' directory.")

if __name__ == "__main__":
    main()