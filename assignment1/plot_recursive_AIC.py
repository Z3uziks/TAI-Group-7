import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create directory if it doesn't exist
os.makedirs("graphics/plots_recursive", exist_ok=True)

def plot_AIC_recursive():
    # Load the CSV file
    df = pd.read_csv("aic_results_recursive.csv")
    
    # Convert Iteration column to numeric for sorting
    df['Iteration'] = df['Iteration'].astype(int)
    
    # Sort data for correct plotting
    df = df.sort_values(by=['File', 'Iteration'])
    
    # Set the style for seaborn
    sns.set_style("whitegrid")
    
    # Get unique files for separate plots
    unique_files = df['File'].unique()
    
    # Plot AIC and Entropy for each file
    for file in unique_files:
        df_file = df[df['File'] == file]
        
        # Get the prior and sequence length for this file
        prior = df_file['Prior'].iloc[0]  # Get prior from the first row
        seq_length = df_file['Sequence_Length'].iloc[0]  # Get sequence length from the first row
        
        plt.figure(figsize=(12, 6))
        
        # Plot AIC
        sns.lineplot(data=df_file, x='Iteration', y='AIC', marker="o", label="AIC", color="blue")
        
        # Plot Entropy on the same graph
        sns.lineplot(data=df_file, x='Iteration', y='Entropy', marker="s", label="Entropy", color="red")
        
        # Customize plot
        plt.xlabel("Iteration")
        plt.ylabel("Value (bps)")
        plt.title(f"AIC and Entropy Evolution for {file}\nPrior: '{prior}', Sequence Length: {seq_length}")
        plt.legend()
        plt.grid(True)
        
        # Save each plot as an image
        plt.savefig(f"graphics/plots_recursive/aic_entropy_evolution_{file}.png")
        plt.show()

if __name__ == "__main__":
    plot_AIC_recursive()