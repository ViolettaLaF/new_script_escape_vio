# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 17:03:21 2026

@author: User
"""

import tkinter, tkinter.filedialog
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files') #the one where you can see the folder called plots that will contain the csv 
    root.destroy()
    return filename

exp_path = load_path()
plot_path = exp_path + '/plots'
plot_path_pdf = exp_path + '/plots_pdf'
plot_path_escape_plots = exp_path + '/plots/escape_plots'
plot_path_pdf_escape_plots = exp_path + '/plots_pdf/escape_plots'

# Create directories
os.makedirs(plot_path, exist_ok=True)
os.makedirs(plot_path_pdf, exist_ok=True)
os.makedirs(plot_path_escape_plots, exist_ok=True)
os.makedirs(plot_path_pdf_escape_plots, exist_ok=True)


#CHANGE EXPT NAME AND GROUP LABELS BELOW
experiment_name = '5_min_vs_30_sec_base_ctrl' #'VLF-39347_tsh_gal80_DH44_RNAi_TRIP-5min'
group1_file = 'VLF-39347_5min_stacked_bar_summary.csv'
group2_file = 'VLF-39347_30sec_stacked_bar_summary.csv'
group1_label = 'Ctrl 5min base'
group2_label = 'Ctrl 30sec base'

# Load CSVs
df_group1 = pd.read_csv(os.path.join(plot_path, group1_file))
df_group2 = pd.read_csv(os.path.join(plot_path, group2_file))

print("Group 1 data:")
print(df_group1)
print("\nGroup 2 data:")
print(df_group2)
#%%
# STATISTICAL ANALYSIS
def perform_statistical_tests(df_group1, df_group2):
    """
    Perform chi-square test and post-hoc z-tests with Bonferroni correction.
    """
    
    # Extract counts for contingency table
    # Rows = groups, Columns = categories (Freeze_only, Mix, Escape_only, None)
    counts_group1 = df_group1['Count'].values
    counts_group2 = df_group2['Count'].values
    
    contingency_table = [counts_group1, counts_group2]
    
    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    
    # ========================================================================
    # 1. CHI-SQUARE TEST OF INDEPENDENCE
    # ========================================================================
    
    chi2, p_chi, dof, expected = chi2_contingency(contingency_table)
    
    print(f"\n1. Chi-Square Test of Independence:")
    print(f"   χ² = {chi2:.3f}, df = {dof}, p = {p_chi:.4f}")
    
    if p_chi < 0.05:
        print(f"   *** SIGNIFICANT: Groups differ in response distributions (p < 0.05)")
        run_posthoc = True
    else:
        print(f"   NOT SIGNIFICANT: Groups do not differ overall (p ≥ 0.05)")
        run_posthoc = False
    
    # ========================================================================
    # 2. POST-HOC PAIRWISE COMPARISONS (if chi-square is significant)
    # ========================================================================
    
    z_test_results = {}
    bonferroni_alpha = 0.05 / 4  # 4 categories
    
    if run_posthoc:
        print(f"\n2. Post-hoc Two-Proportion Z-Tests:")
        print(f"   Bonferroni-corrected alpha = {bonferroni_alpha:.4f} (0.05/4)")
        print(f"   {'Category':<20} {'z-stat':<10} {'p-value':<10} {'Significant?':<15}")
        print(f"   {'-'*55}")
        
        categories = df_group1['Category'].values
        totals = [df_group1['Total_trials'].iloc[0], df_group2['Total_trials'].iloc[0]]
        
        for i, category in enumerate(categories):
            count = [counts_group1[i], counts_group2[i]]
            
            # Two-proportion z-test
            z_stat, p_value = proportions_ztest(count, totals)
            
            is_significant = p_value < bonferroni_alpha
            sig_marker = "***" if is_significant else ""
            
            z_test_results[category] = {
                'z_stat': z_stat,
                'p_value': p_value,
                'significant': is_significant
            }
            
            print(f"   {category:<20} {z_stat:>9.3f} {p_value:>9.4f}    {sig_marker:<15}")
    else:
        print("\n2. Post-hoc tests not performed (chi-square not significant)")
        categories = df_group1['Category'].values
        for category in categories:
            z_test_results[category] = {
                'z_stat': np.nan,
                'p_value': 1.0,
                'significant': False
            }
    
    print("="*70 + "\n")
    
    return {
        'chi2': chi2,
        'p_chi': p_chi,
        'dof': dof,
        'z_tests': z_test_results,
        'bonferroni_alpha': bonferroni_alpha
    }


# Run statistical tests
stats_results = perform_statistical_tests(df_group1, df_group2)

# PLOT SIDE-BY-SIDE STACKED BARS WITH STATS
def plot_two_groups_comparison(df_group1, df_group2, group1_label, group2_label, 
                               stats_results, save_path, experiment_name):
    """
    Plot two stacked bars side by side with statistical annotations.
    """
    
    # Colors (same as before)
    colors = ['darkcyan', 'purple', 'tomato', 'lightgrey']
    category_labels = ['Freeze', 'Mix responses', 'Escape', 'Others']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Bar positions
    x_positions = [0, 1]
    bar_width = 0.48
    
    # Plot Group 1
    bottom = 0
    for i, (frac, color) in enumerate(zip(df_group1['Fraction'].values, colors)):
        ax.bar(x_positions[0], frac, bottom=bottom, color=color, width=bar_width)        
        if frac > 0.02:
            ax.text(x_positions[0], bottom + frac/2, f'{frac*100:.1f}%', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   color='white')
        
        bottom += frac
    
    # Plot Group 2
    bottom = 0
    for i, (frac, color, label) in enumerate(zip(df_group2['Fraction'].values, colors, category_labels)):
        ax.bar(x_positions[1], frac, bottom=bottom, color=color, label=label, width=bar_width)
        
        if frac > 0.02:
            ax.text(x_positions[1], bottom + frac/2, f'{frac*100:.1f}%', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   color='white')
        
        bottom += frac
    
    # Add significance stars between bars for each category
    if stats_results['p_chi'] < 0.05:
        y_cumulative_1 = 0
        y_cumulative_2 = 0
        
        for i, category in enumerate(df_group1['Category'].values):
            frac1 = df_group1['Fraction'].iloc[i]
            frac2 = df_group2['Fraction'].iloc[i]
            
            # Y position for significance line (middle of category segment)
            y_pos_1 = y_cumulative_1 + frac1/2
            y_pos_2 = y_cumulative_2 + frac2/2
            y_pos = (y_pos_1 + y_pos_2) / 2
            
            # Check if this category is significant
            if stats_results['z_tests'][category]['significant']:
                # Draw significance line
                #ax.plot([x_positions[0] + bar_width/2, x_positions[1] - bar_width/2], [y_pos, y_pos], 'k-', linewidth=1.5)
                
                # Add stars
                p_val = stats_results['z_tests'][category]['p_value']
                if p_val < 0.001:
                    stars = '***'
                elif p_val < 0.01:
                    stars = '**'
                else:
                    stars = '*'
                
                ax.text((x_positions[0] + x_positions[1])/2, y_pos, stars,
                       ha='center', va='bottom', fontsize=14)
            
            y_cumulative_1 += frac1
            y_cumulative_2 += frac2
    
    # Formatting
    ax.set_ylim([0, 1.05])
    ax.set_xlim([-0.5, 1.5])
    ax.set_xticks(x_positions)
    ax.set_xticklabels([group1_label, group2_label], fontsize=18)
    ax.tick_params(axis='x', labelsize=18)  # Force the size this way
    ax.set_ylabel('Fraction of loom responses', fontsize=18)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    
    # Title with chi-square result
    chi_text = f"χ² = {stats_results['chi2']:.2f}, p = {stats_results['p_chi']:.4f}"
    if stats_results['p_chi'] < 0.05:
        chi_text += " ***"
    
    ax.set_title(f'{experiment_name} - Group Comparison\n{chi_text}', 
                fontsize=16, pad=20)
    
    # Legend
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=14, frameon=False)
    
    # Spines
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add footnote with statistical details
    footnote = f"* p < 0.05, ** p < 0.01, *** p < 0.001 (Bonferroni-corrected α = {stats_results['bonferroni_alpha']:.4f})"
    fig.text(0.5, 0.02, footnote, ha='center', fontsize=9, style='italic')
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    
    # Save
    plt.savefig(f"{save_path}/{experiment_name}_comparison_stacked_bars.png", 
                bbox_inches='tight', dpi=300)
    
    pdf_path = save_path.replace('plots', 'plots_pdf')
    os.makedirs(pdf_path, exist_ok=True)
    plt.savefig(f"{pdf_path}/{experiment_name}_comparison_stacked_bars.pdf", 
                bbox_inches='tight')
    
    escape_path = save_path + '/escape_plots'
    os.makedirs(escape_path, exist_ok=True)
    plt.savefig(f"{escape_path}/{experiment_name}_comparison_stacked_bars.png", 
                bbox_inches='tight', dpi=300)
    
    escape_pdf_path = pdf_path + '/escape_plots'
    os.makedirs(escape_pdf_path, exist_ok=True)
    plt.savefig(f"{escape_pdf_path}/{experiment_name}_comparison_stacked_bars.pdf", 
                bbox_inches='tight')
    
    plt.show()
    
    print(f"✓ Saved comparison plot to: {save_path}/{experiment_name}_comparison_stacked_bars.png")


# Create the plot
plot_two_groups_comparison(df_group1, df_group2, group1_label, group2_label, stats_results, plot_path, experiment_name)

# ============================================================================
# SAVE STATISTICAL RESULTS TO CSV
# ============================================================================

def save_stats_to_csv(stats_results, df_group1, df_group2, save_path, experiment_name):
    """
    Save statistical results to CSV.
    """
    
    # Overall chi-square result
    chi_summary = pd.DataFrame({
        'Test': ['Chi-Square'],
        'Statistic': [stats_results['chi2']],
        'df': [stats_results['dof']],
        'p_value': [stats_results['p_chi']],
        'Significant': [stats_results['p_chi'] < 0.05]
    })
    
    chi_summary.to_csv(f"{save_path}/{experiment_name}_chi_square_result.csv", index=False)
    
    # Post-hoc z-test results
    z_test_data = []
    for category, results in stats_results['z_tests'].items():
        z_test_data.append({
            'Category': category,
            'z_statistic': results['z_stat'],
            'p_value': results['p_value'],
            'Bonferroni_alpha': stats_results['bonferroni_alpha'],
            'Significant': results['significant']
        })
    
    z_test_df = pd.DataFrame(z_test_data)
    z_test_df.to_csv(f"{save_path}/{experiment_name}_z_tests_results.csv", index=False)
    
    print(f"\n✓ Saved chi-square results to: {save_path}/{experiment_name}_chi_square_result.csv")
    print(f"✓ Saved z-test results to: {save_path}/{experiment_name}_z_tests_results.csv")


# Save stats
save_stats_to_csv(stats_results, df_group1, df_group2, exp_path, experiment_name)

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)




