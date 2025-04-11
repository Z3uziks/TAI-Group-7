import subprocess
import os
import pandas as pd
import numpy as np
import re

# Define parameter ranges
k_values = [4, 6, 8, 10, 12]
a_values = [0.001, 0.01, 0.05, 0.1, 0.2]

# Output file for heatmap matrix
results_matrix = []

# Output directory for each run
if not os.path.exists("runs"):
    os.makedirs("runs")

def run_metaclass(k, a):
    output_file = f"runs/output_k{k}_a{a}.txt"
    command = f"./MetaClass -d db.txt -s meta.txt -k {k} -a {a} -t 20"
    
    print(f"Running: {command}")
    result = subprocess.run(command.split(), capture_output=True, text=True)

    with open(output_file, 'w') as f:
        f.write(result.stdout)

    return output_file

def parse_output_for_average(file_path):
    nrc_values = []
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search(r'([0-9]+\.[0-9]+)', line)
            if match:
                try:
                    value = float(match.group(1))
                    nrc_values.append(value)
                except:
                    pass
    if nrc_values:
        return round(sum(nrc_values) / len(nrc_values), 4)
    else:
        return None

# Run combinations
for k in k_values:
    row = []
    for a in a_values:
        output = run_metaclass(k, a)
        avg_nrc = parse_output_for_average(output)
        row.append(avg_nrc if avg_nrc is not None else np.nan)
    results_matrix.append(row)

# Save matrix for plotting
df = pd.DataFrame(results_matrix, index=[f'k={k}' for k in k_values], columns=[f'a={a}' for a in a_values])
df.to_csv("nrc_heatmap_matrix.csv")
print("\n✅ Grid results saved to nrc_heatmap_matrix.csv")
