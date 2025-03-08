import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_AIC():
    # Load data
    df = pd.read_csv("aic_results.csv")
    
    # Define a custom color palette
    custom_palette = sns.color_palette("husl", df['Alpha'].nunique())
    
    # Get unique files
    unique_files = df['File'].unique()
    
    for file in unique_files:
        # Filter data for the current file
        df_file = df[df['File'] == file]
        
        # Create plots
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_file, x='k', y='AIC', hue='Alpha', style='Alpha', markers=True, dashes=False, palette=custom_palette, markersize=8)
        
        # Customize plot
        plt.xlabel("Markov Order (k)")
        plt.ylabel("Average Information Content")
        plt.title(f"Average Information Content - {file}")
        plt.legend(title="Alpha")
        plt.grid(True)
        
        # Save and show plot
        plt.savefig(f"aic_plot_{file}.png")
        plt.show()

if __name__ == "__main__":
    plot_AIC()
