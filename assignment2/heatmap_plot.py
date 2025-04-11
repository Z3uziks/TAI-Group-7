import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load matrix
df = pd.read_csv('nrc_heatmap_matrix.csv', index_col=0)

plt.figure(figsize=(10, 6))
sns.heatmap(df, annot=True, cmap='YlGnBu', fmt=".3f", linewidths=0.5, cbar_kws={'label': 'Average NRC'})
plt.title('Average NRC Heatmap for Top 20 Matches')
plt.xlabel('Alpha (-a)')
plt.ylabel('Context Length (-k)')
plt.tight_layout()
plt.savefig('plots/nrc_param_heatmap.png', dpi=300)
plt.show()