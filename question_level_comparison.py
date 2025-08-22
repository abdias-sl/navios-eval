import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np

def load_and_prepare_data():
    """
    Load the two CSV files and prepare them for plotting
    """
    # File paths
    c_file = "./out_csvs/c.csv"
    c37_file = "./out_csvs/c37.csv"
    
    # Check if files exist
    if not os.path.exists(c_file):
        print(f"❌ File not found: {c_file}")
        return None, None
    
    if not os.path.exists(c37_file):
        print(f"❌ File not found: {c37_file}")
        return None, None
    
    try:
        # Load the CSV files
        df_c = pd.read_csv(c_file)
        df_c37 = pd.read_csv(c37_file)
        
        print(f"✅ Loaded {len(df_c)} rows from c.csv")
        print(f"✅ Loaded {len(df_c37)} rows from c37.csv")
        
        # Add model identifier column
        df_c['model'] = 'Claude-3.7'
        df_c37['model'] = 'NaviOS'
        
        # Check if required columns exist
        required_columns = ['answer_relevancy', 'factual_correctness(mode=f1)', 'nv_accuracy']
        
        for col in required_columns:
            if col not in df_c.columns:
                print(f"❌ Column '{col}' not found in c.csv")
                print(f"Available columns: {list(df_c.columns)}")
                return None, None
            if col not in df_c37.columns:
                print(f"❌ Column '{col}' not found in c37.csv")
                print(f"Available columns: {list(df_c37.columns)}")
                return None, None
        
        return df_c, df_c37
        
    except Exception as e:
        print(f"❌ Error loading files: {str(e)}")
        return None, None

def create_individual_plots(df_c, df_c37):
    """
    Create individual plots for each model
    """
    # Create output directory if it doesn't exist
    os.makedirs("./out_imgs", exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Metrics to plot
    metrics = ['answer_relevancy', 'factual_correctness(mode=f1)', 'nv_accuracy']
    metric_names = ['Answer Relevancy', 'Factual Correctness', 'NV Accuracy']
    
    # Get unique categories for coloring
    all_categories = list(set(df_c['category'].unique()) | set(df_c37['category'].unique()))
    # Create a color map for categories
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_categories)))
    category_colors = dict(zip(all_categories, colors))
    
    # Plot 1: Claude-3.7 (c.csv)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Claude-3.7 Performance Metrics', fontsize=16, fontweight='bold')
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        # Create scatter plot with colors based on category
        for category in df_c['category'].unique():
            mask = df_c['category'] == category
            if mask.any():
                axes[i].scatter(df_c[mask].index, df_c[mask][metric], 
                              c=[category_colors[category]], label=category, 
                              alpha=0.7, s=50)
        
        axes[i].set_title(f'{metric_name}')
        axes[i].set_xlabel('Question Index')
        axes[i].set_ylabel('Score')
        axes[i].grid(True, alpha=0.3)
        axes[i].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f'./out_imgs/{timestamp}_claude37_individual.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: NaviOS (c37.csv)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('NaviOS Performance Metrics', fontsize=16, fontweight='bold')
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        # Create scatter plot with colors based on category
        for category in df_c37['category'].unique():
            mask = df_c37['category'] == category
            if mask.any():
                axes[i].scatter(df_c37[mask].index, df_c37[mask][metric], 
                              c=[category_colors[category]], label=category, 
                              alpha=0.7, s=50)
        
        axes[i].set_title(f'{metric_name}')
        axes[i].set_xlabel('Question Index')
        axes[i].set_ylabel('Score')
        axes[i].grid(True, alpha=0.3)
        axes[i].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f'./out_imgs/{timestamp}_navios_individual.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created individual plots with timestamp: {timestamp}")
    return timestamp

def create_comparison_plot(df_c, df_c37, timestamp):
    """
    Create comparison plot with both models
    """
    # Combine dataframes for comparison
    df_combined = pd.concat([df_c, df_c37], ignore_index=True)
    
    # Metrics to plot
    metrics = ['answer_relevancy', 'factual_correctness(mode=f1)', 'nv_accuracy']
    metric_names = ['Answer Relevancy', 'Factual Correctness', 'NV Accuracy']
    
    # Create comparison plot
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Claude-3.7 vs NaviOS Performance Comparison', fontsize=16, fontweight='bold')
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        # Create box plot comparison
        df_combined.boxplot(column=metric, by='model', ax=axes[i])
        axes[i].set_title(f'{metric_name} Comparison')
        axes[i].set_xlabel('Model')
        axes[i].set_ylabel('Score')
        axes[i].grid(True, alpha=0.3)
        
        # Add mean values as text
        for j, model in enumerate(['Claude-3.7', 'NaviOS']):
            mean_val = df_combined[df_combined['model'] == model][metric].mean()
            axes[i].text(j+1, mean_val, f'Mean: {mean_val:.3f}', 
                        ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'./out_imgs/{timestamp}_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created comparison plot with timestamp: {timestamp}")

def create_additional_comparison_plots(df_c, df_c37, timestamp):
    """
    Create additional comparison visualizations
    """
    # Combine dataframes
    df_combined = pd.concat([df_c, df_c37], ignore_index=True)
    
    # Create a comprehensive comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comprehensive Model Comparison', fontsize=16, fontweight='bold')
    
    # Plot 1: Violin plot for all metrics
    metrics = ['answer_relevancy', 'factual_correctness(mode=f1)', 'nv_accuracy']
    metric_names = ['Answer Relevancy', 'Factual Correctness', 'NV Accuracy']
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        row = i // 2
        col = i % 2
        
        # Create violin plot
        sns.violinplot(data=df_combined, x='model', y=metric, ax=axes[row, col])
        axes[row, col].set_title(f'{metric_name} Distribution')
        axes[row, col].set_xlabel('Model')
        axes[row, col].set_ylabel('Score')
        axes[row, col].grid(True, alpha=0.3)
    
    # Plot 4: Scatter plot comparing two models with category-based coloring
    # Get unique categories for coloring
    all_categories = list(set(df_c['category'].unique()) | set(df_c37['category'].unique()))
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_categories)))
    category_colors = dict(zip(all_categories, colors))
    
    # Use answer_relevancy for the comparison scatter plot
    for category in all_categories:
        # Get data for this category from both models
        c_mask = df_c['category'] == category
        c37_mask = df_c37['category'] == category
        
        if c_mask.any() and c37_mask.any():
            # Ensure we have the same number of points from both models
            min_len = min(c_mask.sum(), c37_mask.sum())
            c_data = df_c[c_mask]['answer_relevancy'].iloc[:min_len]
            c37_data = df_c37[c37_mask]['answer_relevancy'].iloc[:min_len]
            
            axes[1, 1].scatter(c_data, c37_data, 
                              c=[category_colors[category]], label=category, 
                              alpha=0.7, s=50)
    
    # Add diagonal line
    min_val = min(df_c['answer_relevancy'].min(), df_c37['answer_relevancy'].min())
    max_val = max(df_c['answer_relevancy'].max(), df_c37['answer_relevancy'].max())
    axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='Perfect Agreement')
    
    axes[1, 1].set_xlabel('Claude-3.7 Score')
    axes[1, 1].set_ylabel('NaviOS Score')
    axes[1, 1].set_title('Model Score Comparison (Answer Relevancy)')
    axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'./out_imgs/{timestamp}_comprehensive_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Created comprehensive comparison plot with timestamp: {timestamp}")

def main():
    """
    Main function to run the comparison analysis
    """
    print("=== Question Level Comparison ===")
    
    # Load data
    df_c, df_c37 = load_and_prepare_data()
    
    if df_c is None or df_c37 is None:
        print("❌ Failed to load data")
        return
    
    # Create individual plots
    timestamp = create_individual_plots(df_c, df_c37)
    
    # Create comparison plot
    create_comparison_plot(df_c, df_c37, timestamp)
    
    # Create additional comparison plots
    create_additional_comparison_plots(df_c, df_c37, timestamp)
    
    # Print summary statistics
    print(f"\n📊 Summary Statistics:")
    print(f"Claude-3.7 (c.csv): {len(df_c)} questions")
    print(f"NaviOS (c37.csv): {len(df_c37)} questions")
    
    metrics = ['answer_relevancy', 'factual_correctness(mode=f1)', 'nv_accuracy']
    metric_names = ['Answer Relevancy', 'Factual Correctness', 'NV Accuracy']
    
    print(f"\n📈 Average Scores:")
    for metric, metric_name in zip(metrics, metric_names):
        c_mean = df_c[metric].mean()
        c37_mean = df_c37[metric].mean()
        print(f"{metric_name}:")
        print(f"  Claude-3.7: {c_mean:.3f}")
        print(f"  NaviOS: {c37_mean:.3f}")
        print(f"  Difference: {c37_mean - c_mean:.3f}")
    
    print(f"\n✅ All plots saved to ./out_imgs/ with timestamp: {timestamp}")

if __name__ == "__main__":
    main()
