#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:47:11 2020

@author: mirjamheinemans - VERSION EDITED BY RIC IN WHICH WE CAN COMPARE 2 GROUPS!
"""
# FOR DATASET IN WICH THE COORDINATE SYSTEM GO FROM 0 TO 30!!! (at the moment data coming from bonfly)
#it contain for 2 groups potentially: polar plots, magnitude of turn (made by me, with violin overlaid), bar plots (made by me)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 19:19:50 2020

@author: mirjamheinemans

This is a copy from FlyHigher_ BehaviorScoring. 
I assume the following folder structure:
    
    - SS02299 (name of experiment)
        -tracked (all tracked.csv files are stored here)
        -scored (all scored_frames.csv files will be stored here)
        
       - Maybe the folder with big dataframes/hdf5 file subfolder here?
       
       
fly_tracked files are loaded one by one, `nd the following behaviors are scored 
and saved in a flynamescored.csv file (ordered by column number):
    
    0.looming_binary -> 1=loom, 0=no_loom
    1.redled -> 1 = led_on, 0 = led_off
    2.greenled -> 1 = led_on, 0 = led_off
    3.fly_x_norm_mm -> relative x-position of fly in mm
    4.fly_y_norm_mm -> relative y-position of fly in mm
    5.fly_pixelchange -> amount of pixels changed 
    6.fly_velocity -> velocity of fly calculated by delta_x and delta_y
    7.fly_walk -> 1 = walking, 0=no_walking
    8.fly_freeze_bout -> 1=freezing, 0=no_freezing
    9.fly_jumps -> 1=jumping, 0=no_jumping
    10.fly_groom -> 1=grooming, 0=no_grooming
    
Important variables to fill in by experimenter:
    
    --We should define all variables that should be entered by experimenter.
    Do you think we should make the GUI way, or just modifying it in the script?
    I liked what Anna had, to make a file from where this script would retrieve that,
    what do you both think? I also liked that she had a file with all different functions she needed,
    that would also make it cleaner. 
   
    We could also make this whole file into a function, and then just loop though the files outside this?
    So, we would iterate over the tracked files, compare to files in scored folder and then run this script 
    if the file does not exist yet. 
    
    
"""
import tkinter, tkinter.filedialog
import numpy as np
import os
import pandas as pd
import math
from math import atan2
import seaborn as sns
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, PathCollection
from matplotlib.lines import Line2D
from scipy.stats import chi2_contingency, fisher_exact
from scipy.stats import norm



def prepare_comparison_data(raw1, raw2, group1_label, group2_label):
    """
    Prepare data for comparison between two groups
    
    Parameters:
    -----------
    raw1, raw2 : pd.DataFrame
        Raw dataframes from escape_counter function (df_all output)
    group1_label, group2_label : str
        Labels for the groups
    
    Returns:
    --------
    combined_df : pd.DataFrame
        Combined data with group labels
    """
    # Add group labels
    raw1_copy = raw1.copy()
    raw2_copy = raw2.copy()
    raw1_copy['group'] = group1_label
    raw2_copy['group'] = group2_label
    
    # Combine
    combined_df = pd.concat([raw1_copy, raw2_copy], ignore_index=True)
    
    return combined_df


def chi_square_test(raw1, raw2): #Statistical tests
    """
    Perform chi-square test on behavior distributions between two groups
    
    Returns:
    --------
    chi2_stat : float
    p_value : float
    contingency_table : pd.DataFrame
    """
    # Count behaviors for each group
    behaviors = ['escape', 'esc_freeze', 'esc_none']
    
    counts1 = raw1[behaviors].sum().values
    counts2 = raw2[behaviors].sum().values
    
    # Create contingency table
    contingency_table = np.array([counts1, counts2])
    contingency_df = pd.DataFrame(
        contingency_table,
        columns=behaviors,
        index=['Group1', 'Group2']
    )
    
    # Perform chi-square test
    chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return chi2_stat, p_value, contingency_df

def two_proportion_ztest(count1, n1, count2, n2):
    """
    Two-proportion z-test for comparing proportions between groups
    
    Parameters:
    -----------
    count1, count2 : int
        Number of successes in each group
    n1, n2 : int
        Total observations in each group
    
    Returns:
    --------
    z_stat : float
    p_value : float
    """
    p1 = count1 / n1
    p2 = count2 / n2
    p_pool = (count1 + count2) / (n1 + n2)
    
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    z_stat = (p1 - p2) / se
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))  # two-tailed
    
    return z_stat, p_value

def bonferroni_correction(p_values, alpha=0.05):
    """Apply Bonferroni correction for multiple comparisons"""
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests
    significant = [p < corrected_alpha for p in p_values]
    return corrected_alpha, significant

def cohens_h(p1, p2):
    """
    Calculate Cohen's h effect size for difference between two proportions
    
    Parameters:
    -----------
    p1, p2 : float
        Proportions to compare (between 0 and 1)
    
    Returns:
    --------
    h : float
        Cohen's h effect size
    """
    h = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))
    return h

def cramers_v(chi2, n, rows, cols):
    """
    Calculate Cramér's V effect size for chi-square test
    
    Parameters:
    -----------
    chi2 : float
        Chi-square statistic
    n : int
        Total sample size
    rows, cols : int
        Number of rows and columns in contingency table
    
    Returns:
    --------
    v : float
        Cramér's V effect size
    """
    k = min(rows, cols)
    v = np.sqrt(chi2 / (n * (k - 1)))
    return v

def interpret_cohens_h(h):
    """Interpret Cohen's h effect size"""
    abs_h = abs(h)
    if abs_h < 0.2:
        return "negligible"
    elif abs_h < 0.5:
        return "small"
    elif abs_h < 0.8:
        return "medium"
    else:
        return "large"

def interpret_cramers_v(v, df):
    """
    Interpret Cramér's V effect size based on degrees of freedom
    df = min(rows-1, cols-1)
    """
    if df == 1:
        if v < 0.10:
            return "small"
        elif v < 0.30:
            return "medium"
        else:
            return "large"
    elif df == 2:
        if v < 0.07:
            return "small"
        elif v < 0.21:
            return "medium"
        else:
            return "large"
    else:  # df >= 3
        if v < 0.06:
            return "small"
        elif v < 0.17:
            return "medium"
        else:
            return "large"


def plot_stacked_comparison(raw1, raw2, group1_label, group2_label, 
                           save_path, experiment_name): # PART 3: Visualization - Stacked bar plot with statistics
    """
    Create side-by-side stacked bar plot comparing behavior distributions
    with statistical annotations
    """
    behaviors = ['escape', 'esc_freeze', 'esc_none']
    behavior_labels = ['Escape', 'Freeze', 'No response']
    colors = ['tomato', 'darkcyan', 'lightgrey']
    
    # Calculate counts and fractions
    counts1 = raw1[behaviors].sum()
    counts2 = raw2[behaviors].sum()
    total1 = counts1.sum()
    total2 = counts2.sum()
    fractions1 = counts1 / total1
    fractions2 = counts2 / total2
    
    # Perform statistical tests
    chi2_stat, p_value_chi2, contingency_table = chi_square_test(raw1, raw2)
    
    # Calculate Cramér's V effect size for overall chi-square
    total_n = total1 + total2
    cramers_v_value = cramers_v(chi2_stat, total_n, rows=2, cols=3)
    cramers_interpretation = interpret_cramers_v(cramers_v_value, df=1)  # min(2-1, 3-1) = 1
    
    # Post-hoc pairwise comparisons
    p_values_pairwise = []
    for behavior in behaviors:
        z, p = two_proportion_ztest(
            counts1[behavior], total1,
            counts2[behavior], total2
        )
        p_values_pairwise.append(p)
    
    # Apply Bonferroni correction
    corrected_alpha, significant = bonferroni_correction(p_values_pairwise)
    
    # Calculate Cohen's h effect sizes for each behavior
    cohens_h_values = []
    cohens_h_interpretations = []
    risk_ratios = []
    
    for i, behavior in enumerate(behaviors):
        # Cohen's h
        h = cohens_h(fractions1.values[i], fractions2.values[i])
        cohens_h_values.append(h)
        cohens_h_interpretations.append(interpret_cohens_h(h))
        
        # Risk ratio (Group2 / Group1)
        if fractions1.values[i] > 0:
            rr = fractions2.values[i] / fractions1.values[i]
        else:
            rr = np.inf if fractions2.values[i] > 0 else 1.0
        risk_ratios.append(rr)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 7))
    
    width = 0.4
    x_pos = [0, 1]
    group_labels = [group1_label, group2_label]
    
    # Stack bars for group 1
    bottom1 = 0
    for i, (behavior, color, label) in enumerate(zip(behaviors, colors, behavior_labels)):
        ax.bar(x_pos[0], fractions1[behavior], width, bottom=bottom1, 
               color=color, label=label, edgecolor='black', linewidth=1.5, alpha=0.85)
        
        # Add percentage text in the middle of each segment
        if fractions1[behavior] > 0.05:  # Only show text if segment is big enough
            ax.text(x_pos[0], bottom1 + fractions1[behavior]/2, 
                   f'{fractions1[behavior]*100:.1f}%',
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        bottom1 += fractions1[behavior]
    
    # Stack bars for group 2
    bottom2 = 0
    for i, (behavior, color) in enumerate(zip(behaviors, colors)):
        ax.bar(x_pos[1], fractions2[behavior], width, bottom=bottom2, 
               color=color, edgecolor='black', linewidth=1.5, alpha=0.85)
        
        # Add percentage text
        if fractions2[behavior] > 0.05:
            ax.text(x_pos[1], bottom2 + fractions2[behavior]/2, 
                   f'{fractions2[behavior]*100:.1f}%',
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        bottom2 += fractions2[behavior]
    
    # Add significance brackets between groups for each behavior
    # Calculate cumulative positions for bracket placement
    cumsum1 = np.cumsum([0] + fractions1.tolist())
    cumsum2 = np.cumsum([0] + fractions2.tolist())
    
    for i, (is_sig, p_val) in enumerate(zip(significant, p_values_pairwise)):
        if is_sig:
            # Determine significance level
            if p_val < 0.001:
                sig_text = '***'
            elif p_val < 0.01:
                sig_text = '**'
            elif p_val < corrected_alpha:
                sig_text = '*'
            else:
                continue
            
            # Position bracket at the middle of each behavior segment
            y_pos1 = cumsum1[i] + fractions1.values[i]/2
            y_pos2 = cumsum2[i] + fractions2.values[i]/2
            y_bracket = max(y_pos1, y_pos2)
            
            # Draw horizontal lines from each bar
            ax.plot([x_pos[0] + width/2 + 0.02, x_pos[0] + width/2 + 0.08], 
                   [y_pos1, y_bracket], 'k-', lw=1.5)
            ax.plot([x_pos[1] - width/2 - 0.02, x_pos[1] - width/2 - 0.08], 
                   [y_pos2, y_bracket], 'k-', lw=1.5)
            # Draw connecting line
            ax.plot([x_pos[0] + width/2 + 0.08, x_pos[1] - width/2 - 0.08], 
                   [y_bracket, y_bracket], 'k-', lw=1.5)
            # Add significance text
            ax.text((x_pos[0] + x_pos[1])/2, y_bracket + 0.02, sig_text, 
                   ha='center', fontsize=12, fontweight='bold')
    
    # Formatting
    ax.set_ylabel('Fraction of behaviors', fontsize=13, fontweight='bold')
    ax.set_title(f'{experiment_name}\nBehavior Distribution Comparison\n' + 
                 f'Chi-square: χ² = {chi2_stat:.2f}, p < 0.001, Cramér\'s V = {cramers_v_value:.3f} ({cramers_interpretation})',
                 fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(group_labels, fontsize=11, fontweight='bold')
    ax.set_ylim([0, 1.2])  # Extra space for significance markers
    ax.set_xlim([-0.5, 1.5])
    
    # Legend
    ax.legend(fontsize=11, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
             ncol=3, frameon=False)
    
    # Clean up plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    
    plt.tight_layout()
    plt.savefig(f'{save_path}/{experiment_name}_stacked_comparison.png', 
                dpi=600, bbox_inches='tight')
    plt.show()
    
    # Print statistical summary
    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("="*70)
    print(f"\nContingency Table:")
    print(contingency_table)
    print(f"\nTotal observations: Group1={total1}, Group2={total2}")
    print(f"\nChi-square test of independence:")
    print(f"  χ² = {chi2_stat:.4f}")
    print(f"  p-value = {p_value_chi2:.4f}")
    print(f"  Cramér's V = {cramers_v_value:.3f} ({cramers_interpretation} effect)")
    if p_value_chi2 < 0.05:
        print("  Result: SIGNIFICANT difference in behavior distributions")
    else:
        print("  Result: NO significant difference in behavior distributions")
    
    print(f"\n{'─'*70}")
    print("Post-hoc pairwise comparisons (with Bonferroni correction):")
    print(f"Corrected alpha level: {corrected_alpha:.4f}")
    print(f"{'─'*70}")
    for i, behavior in enumerate(behavior_labels):
        print(f"\n{behavior}:")
        print(f"  Group1: {fractions1.values[i]:.3f} ({counts1.values[i]}/{total1})")
        print(f"  Group2: {fractions2.values[i]:.3f} ({counts2.values[i]}/{total2})")
        print(f"  Difference: {(fractions2.values[i] - fractions1.values[i]):.3f} ({(fractions2.values[i] - fractions1.values[i])*100:.1f}%)")
        print(f"  Risk Ratio (Group2/Group1): {risk_ratios[i]:.2f}x")
        print(f"  Cohen's h: {cohens_h_values[i]:.3f} ({cohens_h_interpretations[i]} effect)")
        print(f"  p-value: {p_values_pairwise[i]:.4f}")
        if significant[i]:
            print(f"  Result: SIGNIFICANT difference (*)")
        else:
            print(f"  Result: Not significant")
    print("="*70)
    
    return chi2_stat, p_value_chi2, p_values_pairwise, cramers_v_value, cohens_h_values


def save_statistics_to_csv(raw1, raw2, group1_label, group2_label, # PART 4: Save statistics to CSV
                           save_path, experiment_name):
    """
    Save all statistical results to a CSV file
    
    Parameters:
    -----------
    raw1, raw2 : pd.DataFrame
        Raw dataframes from escape_counter function
    group1_label, group2_label : str
        Labels for the groups
    save_path : str
        Path to save the CSV file
    experiment_name : str
        Name of the experiment for filename
    """
    behaviors = ['escape', 'esc_freeze', 'esc_none']
    behavior_labels = ['Escape', 'Freeze', 'No response']
    
    # Calculate counts and fractions
    counts1 = raw1[behaviors].sum()
    counts2 = raw2[behaviors].sum()
    total1 = counts1.sum()
    total2 = counts2.sum()
    fractions1 = counts1 / total1
    fractions2 = counts2 / total2
    
    # Perform statistical tests
    chi2_stat, p_value_chi2, contingency_table = chi_square_test(raw1, raw2)
    
    # Calculate Cramér's V effect size
    total_n = total1 + total2
    cramers_v_value = cramers_v(chi2_stat, total_n, rows=2, cols=3)
    cramers_interpretation = interpret_cramers_v(cramers_v_value, df=1)
    
    # Post-hoc pairwise comparisons
    p_values_pairwise = []
    z_stats = []
    for behavior in behaviors:
        z, p = two_proportion_ztest(
            counts1[behavior], total1,
            counts2[behavior], total2
        )
        z_stats.append(z)
        p_values_pairwise.append(p)
    
    # Apply Bonferroni correction
    corrected_alpha, significant = bonferroni_correction(p_values_pairwise)
    
    # Calculate Cohen's h and risk ratios
    cohens_h_values = []
    cohens_h_interpretations = []
    risk_ratios = []
    
    for i, behavior in enumerate(behaviors):
        # Cohen's h
        h = cohens_h(fractions1.values[i], fractions2.values[i])
        cohens_h_values.append(h)
        cohens_h_interpretations.append(interpret_cohens_h(h))
        
        # Risk ratio
        if fractions1.values[i] > 0:
            rr = fractions2.values[i] / fractions1.values[i]
        else:
            rr = np.inf if fractions2.values[i] > 0 else 1.0
        risk_ratios.append(rr)
    
    # Create comprehensive statistics dataframe
    stats_data = {
        'Behavior': behavior_labels,
        f'{group1_label}_count': counts1.values,
        f'{group1_label}_total': [total1] * len(behaviors),
        f'{group1_label}_fraction': fractions1.values,
        f'{group1_label}_percentage': fractions1.values * 100,
        f'{group2_label}_count': counts2.values,
        f'{group2_label}_total': [total2] * len(behaviors),
        f'{group2_label}_fraction': fractions2.values,
        f'{group2_label}_percentage': fractions2.values * 100,
        'difference_fraction': fractions1.values - fractions2.values,
        'difference_percentage': (fractions1.values - fractions2.values) * 100,
        'risk_ratio_G2_vs_G1': risk_ratios,
        'cohens_h': cohens_h_values,
        'cohens_h_interpretation': cohens_h_interpretations,
        'z_statistic': z_stats,
        'p_value': p_values_pairwise,
        'bonferroni_corrected_alpha': [corrected_alpha] * len(behaviors),
        'significant_after_correction': significant
    }
    
    df_stats = pd.DataFrame(stats_data)
    
    # Add chi-square test results as a summary row
    summary_data = {
        'Behavior': 'OVERALL_CHI_SQUARE',
        f'{group1_label}_count': '',
        f'{group1_label}_total': total1,
        f'{group1_label}_fraction': '',
        f'{group1_label}_percentage': '',
        f'{group2_label}_count': '',
        f'{group2_label}_total': total2,
        f'{group2_label}_fraction': '',
        f'{group2_label}_percentage': '',
        'difference_fraction': '',
        'difference_percentage': '',
        'risk_ratio_G2_vs_G1': '',
        'cohens_h': '',
        'cohens_h_interpretation': f"Cramér's V = {cramers_v_value:.3f} ({cramers_interpretation})",
        'z_statistic': chi2_stat,
        'p_value': p_value_chi2,
        'bonferroni_corrected_alpha': 0.05,
        'significant_after_correction': p_value_chi2 < 0.05
    }
    
    df_stats = pd.concat([df_stats, pd.DataFrame([summary_data])], ignore_index=True)
    
    # Format p-values for better display (use scientific notation for very small values)
    df_stats['p_value_formatted'] = df_stats['p_value'].apply(
        lambda x: f'{x:.2e}' if x < 0.0001 else f'{x:.6f}' if isinstance(x, (int, float)) else x
    )
    
    # Save to CSV
    csv_filename = f'{save_path}/{experiment_name}_statistics.csv'
    df_stats.to_csv(csv_filename, index=False)
    
    print(f"\nStatistics saved to: {csv_filename}")
    print("\nNote: Check 'p_value_formatted' column for readable p-values")
    print("Values shown in scientific notation (e.g., 1.23e-08) when p < 0.0001")
    
    return df_stats



def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files')
    root.destroy()
    return filename
exp_path = load_path()

plot_path = exp_path + '/plots'
plot_path_pdf = exp_path + '/plots_pdf'

plot_path_escape_plots = exp_path + '/plots/escape_plots'
plot_path_pdf_escape_plots = exp_path + '/plots_pdf/escape_plots'

#CHANGE EXPT NAME AND GROUP LABELS BELOW

experiment_name = 'VLF-39347_tsh_gal80_DH44_vs_GFP_RNAi_KK-30secbase' #"Tsh_GAL80_DH44_GAL4_DH44_or_DH44_RNAi_TRIP" #

group1_label = 'VLF-39347_tsh_gal80_GFP_RNAi_KK-30secbase' #"Tsh_GAL80_DH44_GAL4_luc_RNAi_TRIP" #"Tsh_GAL80_DH44_GAL4_luc_RNAi_TRIP"
group2_label = 'VLF-39347_tsh_gal80_DH44_RNAi_KK-30secbase' #"Tsh_GAL80_DH44_GAL4_DH44_RNAi_TRIP" #"Tsh_GAL80_DH44_GAL4_DH44_RNAi_TRIP"

#%%
'''try-out for angular speed calculation.
General idea: calculate delta(x) and delta(y) per frame. Calculate the the heading angle (direction of movement) at each time point
'''
def heading(dx, dy): #wait in all this script this function is never being used??!!! So I'm never really talking about angle but about desplacement
    degs_lst =[]
    for i in range(len(dx)):
        if isinstance(dx[i], str): #If the displacement was stored as a string (maybe due to bad parsing), it just marks that frame as "nan" instead of computing.
            degs_lst.append('nan')
        else:
            rads = atan2(dy[i], dx[i]) 
            rads %= 2*np.pi
            degs = math.degrees(rads)
            degs_lst.append(degs)
    return degs_lst
#%%
def data_polar(path, group_name): #give heading direction of walking flies before loom  
    all_heading_before = np.empty(0) #of the desplacement vector that go from 30 frames before the loom to loom onset
    all_heading_after = np.empty(0) #of the desplacement vector that go from loom offset to 30 frames after loom offset of not freezing flies
    all_heading_diff = np.empty(0)
    
    for filename in sorted(os.listdir(path+'/scored/')): 
    
        if not filename.endswith('frames.csv'):
            continue
        capital_x = filename.replace('x','X')
        if not capital_x.startswith(group_name):
            continue
        df_try = pd.read_csv(path+'/scored/'+filename )
        
        loom_onset = df_try.loc[df_try['looming_bout'].diff() == 1].index.values.astype(int)
        loom_offset = df_try.loc[df_try['looming_bout'].diff() == -1].index.values.astype(int)
         
        '''checking turns'''
        heading_x_before = []
        heading_y_before = []
        heading_x_after = []
        heading_y_after = []

        "CHANGING COORDINATE SYSTEM TO BE WITH THE CENTER OF THE ARENA IN (0,0) INSTEAD OF (15,15) and screen on top" #important to check turn
        df_try['fly_x_norm_mm'] = df_try['fly_x_norm_mm'] - 15
        df_try['fly_y_norm_mm'] = (df_try['fly_y_norm_mm'] - 15) * -1         
        
        for loom in range(len(df_try)):    
            if loom in loom_onset:
                if df_try.loc[loom-30:loom,'velocity'].mean() < 4: #just consider situations in which the flies is walking before the loom
                    x_before = np.nan 
                    y_before = np.nan
                    
                else:
                    x_before = df_try.loc[loom,'fly_x_norm_mm'] - df_try.loc[loom-30,'fly_x_norm_mm'] #the displacement vector heading_before go from 30 frames before the loom to loom onset 
                    y_before = df_try.loc[loom,'fly_y_norm_mm'] - df_try.loc[loom-30,'fly_y_norm_mm'] 
                heading_x_before.append(x_before) 
                heading_y_before.append(y_before)
        
            elif loom in loom_offset:
                if df_try.loc[loom:loom+30,'freeze_bout'].sum() >1: #just consider situations in which the flies is not freezing after the loom
                    x_after = np.nan
                    y_after = np.nan
                else:
                    x_after = df_try.loc[loom+30,'fly_x_norm_mm'] - df_try.loc[loom,'fly_x_norm_mm'] #the displacement vector heading_after go from loom offset to 30 frames after loom offset 
                    y_after = df_try.loc[loom+30,'fly_y_norm_mm'] - df_try.loc[loom,'fly_y_norm_mm']
                heading_x_after.append(x_after)
                heading_y_after.append(y_after)
        
        heading_before = np.array(heading(heading_x_before,heading_y_before)) #here go from displacement to heading angles
        heading_after = np.array(heading(heading_x_after,heading_y_after))
        heading_diff = abs(heading_after - heading_before) #delta heading => amount of turn
        
        for loom in range(len(heading_diff)):
            if heading_y_before[loom] < heading_y_after[loom]:
               heading_diff[loom] =heading_diff[loom]*-1  #why +-1??? to don't have negative value (this is just a delta)
               
        all_heading_before = np.append(all_heading_before,heading_before)
        all_heading_after = np.append(all_heading_after,heading_after)
        all_heading_diff = np.append(all_heading_diff,heading_diff)
        
    all_heading_before = all_heading_before.T   
    all_heading_after = all_heading_after.T
    all_heading_diff = all_heading_diff.T

    df_output = pd.DataFrame([all_heading_before, all_heading_after, all_heading_diff], index = ['all_heading_before', 'all_heading_after', 'all_heading_diff'])
    df_out = df_output.T
    return df_out   
#%%
def plot_polar(path, group_name):
    df_group_polar = data_polar(path, group_name)
    save_path = path + '/plots/'
    degrees_before = (df_group_polar['all_heading_before'])
    bin_size = 20 #?so the polar plot will have 18 bins (360/20) 
    a_bef , b=np.histogram(degrees_before, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1])
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_bef, width=np.deg2rad(bin_size), bottom=0.0, color='yellow', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name +': heading before');
    plt.savefig(save_path + group_name + '_polar_before.jpeg',bbox_inches='tight', dpi=1800)
    plt.show()    

    degrees_after = (df_group_polar['all_heading_after'])
    bin_size = 20
    a_aft , b=np.histogram(degrees_after, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1]) 
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_aft, width=np.deg2rad(bin_size), bottom=0.0, color='blue', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name +': heading after');
    plt.savefig(save_path + group_name + '_polar_after.jpeg',bbox_inches='tight', dpi=1800)
    plt.show()    

    
    df_group_polar['degrees_diff'] =  df_group_polar['all_heading_diff'] #Normalize angles so they’re within ±180° (so we are imposing that the turn can not be bigger than 180 degrees)
    for i in range(len(df_group_polar)):                                   #So the idea is to always express turns in the shortest rotation direction (≤180°)
        if df_group_polar.loc[i, 'all_heading_diff'] >180:            
            angle =  df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff'] = 360-angle
        elif df_group_polar.loc[i, 'all_heading_diff'] <-180:
            angle = df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff']= (angle +360)*-1
    
   
    df_group_polar['away from screen'] = 'away from screen'
    df_group_polar.loc[df_group_polar['degrees_diff']<0, 'away from screen'] = 'towards screen'
    df_group_polar['flies'] = 'fly' #You’re not comparing individual flies here, just pooling them. Setting all rows to "fly" allows you to plot everything in a single category on the x-axis (and split them only by hue = turn direction)


        # --- Colors ---
    edge_colors = {
        "away from screen": (0.121, 0.466, 0.705, 1.0),   # blue, fully opaque
        "towards screen":  (1.000, 0.498, 0.054, 1.0)     # orange, fully opaque
    }
    
    hue_order = ["away from screen", "towards screen"]
    fig, ax = plt.subplots(figsize=(8,6))
    # --- 1) Violin plot ---
    sns.violinplot(
        y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, data=df_group_polar,
        split=True, inner=None, cut=0, linewidth=1.2, palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    # --- 2) Make violin edges opaque and fill extremely faint ---
    for col in ax.collections:
        if isinstance(col, PolyCollection):
            fc = col.get_facecolor()[0]            # RGB
            col.set_facecolor((fc[0], fc[1], fc[2], 0.1))  # 10% opacity fill
            col.set_edgecolor((fc[0], fc[1], fc[2], 0.4))   # 40% opaque edge
            col.set_linewidth(1)
    # --- 3) Stripplot ---
    sns.stripplot( y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, data=df_group_polar, dodge=True, jitter=True,
        size=5, marker='o', linewidth=0.8, palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    # --- 4) Make stripplot points hollow ---
    for col in ax.collections:
        if isinstance(col, PathCollection):
            fc = col.get_facecolors()
            if fc.size != 0:
                col.set_edgecolors(fc)   # preserve outline color
                col.set_facecolors('none')  # transparent inside
                col.set_linewidth(0.8)
    # --- 5) Custom legend ---
    legend_handles = [ Line2D([0], [0], marker='o', color='none', markeredgecolor="blue", markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='away from screen'),
        Line2D([0], [0], marker='o', color='none', markeredgecolor="orange", markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='towards screen')]
    ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(0.6, 0.8))
    # --- Formatting ---
    ax.set_title(group_name + ': magnitude of turn')
    ax.set_ylabel('degrees')
    ax.set_xlabel("")        # remove x axis label
    ax.set_xticklabels([])   # remove x tick labels... well this is not working at the moment
    sns.despine()
    # --- Save & show ---
    plt.savefig(save_path + group_name + '_scatter_violin_hollow_outline.jpeg',
                bbox_inches='tight', dpi=1800)
    plt.show()
    
#group1_1_polar = plot_polar(exp_path, group1_label)
#group1_2_polar = plot_polar(exp_path, group2_label)    
#%%
'''upload scored file'''
def escape_counter(condition): # condition is the first part of the string of fly-name, only flies in that condition will be used
    df_all = pd.DataFrame() #this will contain all excapes per loom in the end

    path = exp_path
    
    for filename in sorted(os.listdir(path+'/scored/')):  #folder with scored files you want to check

        if not filename.endswith('frames.csv'):
            continue
        capital_x = filename.replace('X','x')
        if not capital_x.startswith(condition):
            continue
        df_try = pd.read_csv(path+'/scored/'+filename )
                
        loom_onset = df_try.loc[df_try['looming_bout'].diff() == 1].index.values.astype(int)
        loom_offset = df_try.loc[df_try['looming_bout'].diff() == -1].index.values.astype(int)
       
        df_try['esc_turn'] = 0
        df_try['esc_run'] = 0
        df_try['esc_jump'] = 0
        df_try['esc_freeze'] = 0
        df_try['escape'] = 0
        df_try['turn_run'] = 0
    
        '''checking turns'''
        heading_x_before = []
        heading_y_before = []
        heading_x_after = []
        heading_y_after = []
        
        "CHANGING COORDINATE SYSTEM TO BE WITH THE CENTER OF THE ARENA IN (0,0) INSTEAD OF (15,15) " # to check turn
        df_try['fly_x_norm_mm'] = df_try['fly_x_norm_mm'] - 15
        df_try['fly_y_norm_mm'] = (df_try['fly_y_norm_mm'] - 15) * -1 
        #print(df_try['fly_y_norm_mm'])
        
        for loom in range(len(df_try)):    
            if loom in loom_onset:
                if df_try.loc[loom,'freeze_bout'] == 1: #ignore condition in whic they are freezing
                    x_before = 'nan'
                    y_before = 'nan'
                    
                else:
                    x_before = df_try.loc[loom,'fly_x_norm_mm'] - df_try.loc[loom-30,'fly_x_norm_mm'] #the displacement vector heading_before go from 30 frames before the loom to loom onset
                    y_before = df_try.loc[loom,'fly_y_norm_mm'] - df_try.loc[loom-30,'fly_y_norm_mm']
                heading_x_before.append(x_before)
                heading_y_before.append(y_before)
        
            elif loom in loom_offset:
                if df_try.loc[loom:loom+30,'freeze_bout'].sum() >1: #ignore condition in whic they are freezing
                    x_after = 'nan'
                    y_after = 'nan'
                else:
                    x_after = df_try.loc[loom+30,'fly_x_norm_mm'] - df_try.loc[loom,'fly_x_norm_mm'] #the displacement vector heading_after go from loom offset to 30 frames after loom offset 
                    y_after = df_try.loc[loom+30,'fly_y_norm_mm'] - df_try.loc[loom,'fly_y_norm_mm']
                heading_x_after.append(x_after)
                heading_y_after.append(y_after)
                
        
        for i in range(len(heading_y_before)):
            if isinstance(heading_y_before[i], str) | isinstance(heading_y_after[i], str):#here we are taliking about desplacemnt, not heading (angle)!!
                continue
            elif (heading_y_before[i] > 0) & (heading_y_after[i] < 0): #because screen is at y+ (I changed from original script)
                df_try.loc[loom_offset[i], 'esc_turn'] = 1       
#            elif heading_y_before[i]<heading_y_after[i]: 
#                df_try.loc[loom_offset[i], 'esc_turn'] = 1

    
        '''checking jumps and freeze'''
        for i in range(len(loom_onset)):
            if df_try.loc[loom_onset[i]:(loom_onset[i]+120), 'jumps'].sum() > 0: #if there was a jump from loom onset till 2 seconds from loom onset
                df_try.loc[loom_offset[i], 'esc_jump'] = 1
 
            elif df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'freeze_bout'].sum() > 0: #if there was a freeze bout from loom onset till 2 seconds from  loom_offset
                df_try.loc[loom_offset[i], 'esc_freeze'] = 1
        
    
        '''checking increase in speed''' #This block is checking if flies significantly increase their running speed after the looming stimulus. It does this with a bootstrapping approach (sampling random subsets of velocities before and after) and then applying a t-test. If the increase is real and not just noise, it marks that loom as an “escape run.”
        for loom in range(len(loom_onset)):
            permutated_pre = df_try.loc[loom_onset[i]-120:(loom_onset[i]), 'velocity'] #velocities in the time window that goes from 2 second before loom onset to loom onset! 
            permutated_post = df_try.loc[loom_offset[i]:(loom_offset[i]+120), 'velocity'] #velocities in the time window that goes from loom offset to 2 second after!
            
            train_pre = []
            train_post = []
            ''' run 100 permutations of velocity per frame per loom(2 seconds before and after loom)'''
            for perm in range (100):
                df_sample_pre  = permutated_pre.sample(n=30) #df_sample_pre grabs 30 random frames from the 120 available
                row_pre = df_sample_pre.mean(axis=0) #mean of 30 frames
                train_pre.append(row_pre)
            
                df_sample_post  = permutated_post.sample(n=30)
                row_post = df_sample_post.mean(axis=0) #mean of 30 samples --> take unpaired t-test instead, if >0.05
                train_post.append(row_post)
        
            '''take t-test of 100 samples between groups'''            
            t, p = ttest_ind(train_pre, train_post, alternative='less') #changed here from original script as in this case the one sided is better!!
            if (df_try.loc[loom_onset[loom],'freeze_bout']==0):
                if (p<0.05):
                    df_try.loc[loom_offset[loom], 'esc_run'] = 1 #if t-test is significant, if yes --> 1
        
                
        '''slicing dataframe from esc_turn until end'''
        df_loom = df_try.loc[loom_offset, 'esc_turn':].copy().reset_index(drop=True) #Selects only the rows where loom_offset and columns from 'esc_turn' onwards (all the escape behavior columns: esc_turn, esc_run, esc_jump, esc_freeze, etc.)
        df_all = pd.concat([df_all,df_loom])

    df_all = df_all.reset_index() #It's collecting all the escape behavior data (one row per loom per file) into a single dataframe that you can analyze across your entire dataset.

    for i in range(len(df_all)):
        if df_all.loc[i,'esc_jump']==1: #=> jumping is ovveriding everything!
            df_all.loc[i,'esc_run']=0
            df_all.loc[i,'esc_mean_vel']=0
            df_all.loc[i,'esc_turn']=0
            df_all.loc[i,'esc_freeze']=0 # can flies jump and then freeze? Which escape is counted? at the moment jump!
      
        elif df_all.loc[i,'esc_run']==1: #=> running is ovveriding freezing!
            df_all.loc[i,'esc_freeze']=0
    

    #df_all.loc[(df_all['esc_run']==1) & (df_all['esc_turn']==1), ['turn_run', 'esc_run', 'esc_turn']]=[1,0,0] #if flies is in an escape turn and in a escape_run she will be categorized as turn run!
    df_all.loc[(df_all['esc_run']==1) & (df_all['esc_turn']==1), ['turn_run', 'esc_run', 'esc_turn']]=[1,1,0] #if flies is in an escape turn and in a escape_run she will be categorized as escape_run! running overriding turning!
    
    col_lst = ['esc_turn', 'esc_jump', 'esc_run', 'esc_freeze','esc_mean_vel']
    df_all['esc_none'] = df_all[col_lst].sum(axis=1)
    for i in range(len(df_all)):
        if df_all.loc[i,'esc_none']==0:
            df_all.loc[i,'esc_none']=1 #if fly is not engaging in any of this behaviour (turn, jump, run, freeze): she is classified as non responder!
        else:
            df_all.loc[i,'esc_none']=0
    
    escape = ['esc_turn', 'esc_jump', 'esc_run']
    df_all['escape'] = df_all[escape].sum(axis=1)
    for i in range(len(df_all)):
        if df_all.loc[i,'escape']>0:
            df_all.loc[i,'escape']=1
        else:
            df_all.loc[i,'escape']=0
    
    df_grouped = df_all.groupby('index').mean() #all rows in df_all that have the same value in the 'index' column (which represent looms) are put into the same group and the mean is calculated
    df_grouped['loom'] = range(len(df_grouped)) #groupby('index') → groups rows by loom. .mean() → computes the fraction of flies engaging in this behaviours per loom.
    #return df_grouped, df_all


    # === plotting Stacked bar plot of behaviors (fractions) ===
    #counts = df_all[['esc_turn', 'esc_jump', 'esc_run', 'esc_freeze', 'esc_none']].sum()
    counts = df_all[['escape', 'esc_freeze', 'esc_none']].sum()
    total = counts.sum()
    fractions = counts / total  # fraction of each behavior

    fig, ax = plt.subplots()     # Plot stacked bar 
    #ax.bar("Behaviors", fractions["esc_turn"], width=0.1, label="Turn", color="y")
    #ax.bar("Behaviors", fractions["esc_jump"], bottom=fractions["esc_turn"], width=0.1, label="Jump", color="darkslateblue")
    #ax.bar("Behaviors", fractions["esc_run"], bottom=fractions["esc_turn"]+fractions["esc_jump"], width=0.1, label="Run", color="tomato")
    #ax.bar("Behaviors", fractions["esc_freeze"], bottom=fractions["esc_turn"]+fractions["esc_jump"]+fractions["esc_run"],width=0.1, label="Freeze", color="darkcyan")
    #ax.bar("Behaviors", fractions["esc_none"], bottom=fractions["esc_turn"]+fractions["esc_jump"]+fractions["esc_run"]+fractions["esc_freeze"],width=0.1, label="No response", color="lightgrey")
    ax.bar("Behaviors", fractions['escape'], width=0.1, label="Escape", color='tomato')
    ax.bar("Behaviors", fractions['esc_freeze'], bottom=fractions['escape'], width=0.1, label="Freeze", color="darkcyan")
    ax.bar("Behaviors", fractions['esc_none'], bottom=fractions['esc_freeze']+fractions['escape'], width=0.1, label="No response", color="lightgrey")

    ax.set_ylim([0, 1])  # fraction scale
    ax.set_ylabel("Fraction of behaviour (0–1)")
    ax.set_title(condition + ": behavior distribution (stacked)")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.8))
    #plt.savefig(plot_path + condition + "_behav_distribution_stacked.jpeg", bbox_inches="tight", dpi=600)
    plt.savefig(plot_path+"/"+str(condition + "_behav_distribution_stacked.png"), bbox_inches="tight", dpi=600)
    plt.show()
    plt.clf()

    # === Stacked bar per 5 looms (4 bins total) ===
    df_all_withloom = df_all.copy()
    
    # Use the 'index' column (loom number) to create bins of 5 looms
    df_all_withloom["loom_bin"] = (df_all_withloom["index"] // 5) + 1  # bins: 1,2,3,4
    
    # Sum behaviors per bin
    behaviors = ["esc_turn", "esc_jump", "esc_run", "esc_freeze", "esc_none"]
    counts_per_bin = df_all_withloom.groupby("loom_bin")[behaviors].sum()
    
    # Convert counts to fractions
    fractions_per_bin = counts_per_bin.div(counts_per_bin.sum(axis=1), axis=0)
    
    # Plot stacked bars
    fig, ax = plt.subplots(figsize=(6, 4))
    bottom = np.zeros(len(fractions_per_bin))
    
    colors = ["y", "darkslateblue", "tomato", "darkcyan", "lightgrey"]
    for behavior, color in zip(fractions_per_bin.columns, colors):
        ax.bar(fractions_per_bin.index, fractions_per_bin[behavior], bottom=bottom, color=color, label=behavior, width=0.6)
        bottom += fractions_per_bin[behavior].values
    
    ax.set_ylim([0, 1])
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Looms 1–5", "Looms 6–10", "Looms 11–15", "Looms 16–20"])
    ax.set_ylabel("Fraction of behaviour")
    ax.set_title(condition + ": behavior distribution across loom bins")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.8))
    plt.savefig(plot_path+"/"+str(condition + "_behav_distribution_by_bins.png"), bbox_inches="tight", dpi=600)
    plt.show()
    
    return df_grouped, df_all
#%%
group1, raw1 = escape_counter(group1_label )
group2, raw2 = escape_counter(group2_label)

# Create stacked comparison plot with statistics
chi2, p_chi2, p_pairwise = plot_stacked_comparison(raw1, raw2, group1_label, group2_label, plot_path, experiment_name)

# Save statistics to CSV
df_statistics = save_statistics_to_csv(raw1, raw2, group1_label, group2_label, plot_path, experiment_name)
#%% Commenting all of this just because right now I don't need this plot - but if they are needed decomment this section!
"""
def plot_escape(group,raw_group, group_name):
    '''plot df_empty_TNT:escape vs freeze vs none'''
    n = len(raw_group)/20
    plt.figure(figsize=(10,6)) #largura x altura
    ax = sns.lineplot(x='loom', y='esc_freeze', data=group, label='freezers', color='darkcyan', linestyle='--')
    ax = sns.lineplot(x='loom', y='escape', data=group, label='escapers', color='tomato')
    ax = sns.lineplot(x='loom', y='esc_none', data=group, label='non-responders', color='lightgrey')
    ax = sns.scatterplot(x='loom', y='esc_freeze', data=group, color='darkcyan', s=50) #label='freezers'
    ax = sns.scatterplot(x='loom', y='escape', data=group, color='tomato', s=50) #label='escapers',
    ax = sns.scatterplot(x='loom', y='esc_none', data=group, color='lightgrey', s=50) #label='non-responders'    
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.8))
    ax.set_title(group_name +': grouped behaviour (n=%i)' %n, fontsize = 20, pad = 15)
    ax.set_ylabel('Fraction of flies', fontsize = 18)
    ax.set_xlabel('Loom #', fontsize = 18)
#    ax.set_ylabel('fraction of flies')
    ax.set_xticks(np.array(range(20)))
    ax.set_xticklabels(np.arange(1, 21, 1))
    ax.set_ylim([0,1]);
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.tick_params(axis='x', colors = 'k', labelsize=16)
    ax.tick_params(axis='y', colors = 'k', labelsize=16)
    ax.xaxis.label.set_color('k')
    ax.yaxis.label.set_color('k')
    
    plt.savefig(plot_path+"/"+str(group_name+"_grouped_behaviour.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf+"/"+str(group_name+"_grouped_behaviour.pdf"), bbox_inches='tight', format='pdf')
    
    plt.savefig(plot_path_escape_plots+"/"+str(group_name+"_grouped_behaviour.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf_escape_plots+"/"+str(group_name+"_grouped_behaviour.pdf"), bbox_inches='tight', format='pdf')
    
    plt.show()
    
   
    plt.figure(figsize=(10,6)) 
    ax = sns.lineplot(x='loom', y='esc_freeze', data=group, label='freeze', color='darkcyan')
    ax = sns.scatterplot(x='loom', y='esc_freeze', data=group, color='darkcyan', s=50) #label='freeze', 
    ax = sns.lineplot(x='loom', y='esc_run', data=group, label='run', color='tomato')
    ax = sns.scatterplot(x='loom', y='esc_run', data=group, color='tomato', s=50) #label='run', 
    ax = sns.lineplot(x='loom', y='esc_jump', data=group, label='jump', color='darkslateblue')
    ax = sns.scatterplot(x='loom', y='esc_jump', data=group, color='darkslateblue', s=50) #label='jump', 
    ax = sns.lineplot(x='loom', y='esc_turn', data=group, label='turn', color='y', zorder=5)
    ax = sns.scatterplot(x='loom', y='esc_turn', data=group, color='y', zorder=5, s=50) #label='turn', 
    ax = sns.lineplot(x='loom', y='esc_none', data=group, label='no response', color='lightgrey')
    ax = sns.scatterplot(x='loom', y='esc_none', data=group, color='lightgrey', s=50) #label='no response', 
    #ax = sns.lineplot(x='loom', y='turn_run', data=group, label='turn&run', color='purple')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.8))
    ax.set_xticks(np.array(range(20)))
    ax.set_xticklabels(np.arange(1, 21, 1))
    ax.set_ylim([0,1]);
    
    ax.set_title(group_name +': all_behaviours (n=%i)' %n, fontsize = 20)
    ax.set_ylabel('Fraction of flies', fontsize = 18)
    ax.set_xlabel('Loom #', fontsize = 18)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.tick_params(axis='x', colors = 'k', labelsize=16)
    ax.tick_params(axis='y', colors = 'k', labelsize=16)
    ax.xaxis.label.set_color('k')
    ax.yaxis.label.set_color('k')
    
    plt.savefig(plot_path+"/"+str(group_name+"_all_behaviours.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf+"/"+str(group_name+"_all_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
    plt.savefig(plot_path_escape_plots+"/"+str(group_name+"_all_behaviours.png"), bbox_inches='tight',format='png')
    plt.savefig(plot_path_pdf_escape_plots+"/"+str(group_name+"_all_behaviours.pdf"), bbox_inches='tight', format='pdf')
        
    plt.show()
    plt.clf();
           
    '''of the escapes, what is the distribution between turn, run and jump? (only escapes included, not freezing)'''
    raw_nofreeze = raw_group.mask(raw_group.esc_freeze == 1).dropna(how='all')
    raw_clean = raw_nofreeze.mask(raw_nofreeze.esc_none == 1).dropna(how='all')
    raw_clean.drop('escape', axis=1,inplace=True)
    
    group_clean = raw_clean.groupby('index').mean()
    group_clean['loom'] = range(len(group_clean))
    escape = ['esc_turn', 'esc_jump', 'esc_run', 'turn_run']
    group_clean['sum'] = group_clean[escape].sum(axis=1)
    

    plt.figure(figsize=(10,6)) ; 
    ax = sns.lineplot(x='loom', y='esc_jump', data=group_clean, label='jump', color='darkslateblue')
    ax = sns.lineplot(x='loom', y='esc_run', data=group_clean, label='run', color='tomato')   
    ax = sns.lineplot(x='loom', y='esc_turn', data=group_clean, label='turn', color='y', zorder=5)
    ax = sns.scatterplot(x='loom', y='esc_jump', data=group_clean, color='darkslateblue', s=50)
    ax = sns.scatterplot(x='loom', y='esc_run', data=group_clean, color='tomato', s=50)      
    ax = sns.scatterplot(x='loom', y='esc_turn', data=group_clean, color='y', zorder=5, s=50)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.8))
    ax.set_xticks(np.array(range(20)))
    ax.set_xticklabels(np.arange(1, 21, 1))
    ax.set_ylim([0,1.2]);
    
    ax.set_title(group_name +': different escape behaviours (n=%i)' %n, fontsize = 20, pad = 20)
    ax.set_ylabel('Fraction of flies', fontsize = 18)
    ax.set_xlabel('Loom #', fontsize = 18)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.tick_params(axis='x', colors = 'k', labelsize=16)
    ax.tick_params(axis='y', colors = 'k', labelsize=16)
    ax.xaxis.label.set_color('k')
    ax.yaxis.label.set_color('k')
    
    plt.savefig(plot_path+"/"+str(group_name+"_different_escape_behaviours.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf+"/"+str(group_name+"_different_escape_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
    plt.savefig(plot_path_escape_plots+"/"+str(group_name+"_different_escape_behaviours.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf_escape_plots+"/"+str(group_name+"_different_escape_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
    plt.show()
    plt.clf();
     
    group_clean['cumulative_bout_1'] = group_clean['esc_run'] + group_clean['esc_turn'] + group_clean['turn_run'] + group_clean['esc_jump']
    group_clean['cumulative_bout_2'] = group_clean['esc_run'] + group_clean['esc_turn'] + group_clean['turn_run']
    group_clean['cumulative_bout_3'] = group_clean['esc_run'] + group_clean['esc_turn'] 
    group_clean['cumulative_bout_4'] = group_clean['esc_run'] 
    print(group_clean['turn_run'].max())
    
    x_coordinate = [i for i in range(len(group_clean))]
    
    fig, ax = plt.subplots(figsize=(10,6))
    
    ax.set_title(group_name +': different escape behaviours (n=%i)' %n, fontsize = 20)
    ax.set_ylabel('Fraction of flies', fontsize = 18)
    ax.set_xlabel('Loom #', fontsize = 18)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('outward', 5))
    ax.spines['bottom'].set_position(('outward', 5))
    ax.spines['left'].set_color('dimgrey')
    ax.spines['bottom'].set_color('dimgrey')
    ax.tick_params(axis='x', colors = 'k', labelsize=16)
    ax.tick_params(axis='y', colors = 'k', labelsize=16)
    ax.xaxis.label.set_color('k')
    ax.yaxis.label.set_color('k')
    
    
    plt.title(group_name +': different escape behaviours (n=%i)' %n, fontsize = 20, pad = 20)
    plt.xlabel('Loom #', fontsize = 18)
    plt.ylabel('Fraction of flies', fontsize = 18)
    
    ax.plot(x_coordinate, group_clean['cumulative_bout_4'], 'tomato', label = ('Run'))
    ax.fill_between(x_coordinate, 0, group_clean['cumulative_bout_4'], color='tomato', alpha=0.7)
    ax.plot(x_coordinate, group_clean['cumulative_bout_3'], 'y-', label = ('Turn'))
    ax.fill_between(x_coordinate, group_clean['cumulative_bout_4'], group_clean['cumulative_bout_3'], color='y', alpha=0.7)
    ax.plot(x_coordinate, group_clean['cumulative_bout_1'], 'darkslateblue', label = ('Jumping'))
    ax.fill_between(x_coordinate, group_clean['cumulative_bout_2'], group_clean['cumulative_bout_1'], color='darkslateblue', alpha=0.6)
    plt.xticks(np.array(range(20)))
    ax.set_xticklabels(np.arange(1, 21, 1))
    plt.ylim([0,1.0]);    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.8))
    
    
    plt.savefig(plot_path+"/"+str(group_name+"_cumulative_escape_behaviours.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf+"/"+str(group_name+"_cumulative_escape_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
    plt.savefig(plot_path_escape_plots+"/"+str(group_name+"_cumulative_escape_behaviours.png"), bbox_inches='tight', format='png')
    plt.savefig(plot_path_pdf_escape_plots+"/"+str(group_name+"_cumulative_escape_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
    plt.show();
    return group_clean


clean1 = plot_escape(group1, raw1, group1_label )
clean2 = plot_escape(group2, raw2, group2_label)

'''line plot 2 groups together'''
plt.figure(figsize=(10,6))
ax = sns.lineplot(x='loom', y='esc_freeze', data=group1, label=(str(group1_label) + ' freezers'), color='darkcyan')
ax = sns.lineplot(x='loom', y='escape', data=group1, label=(str(group1_label) + ' escapers'), color='tomato')
ax = sns.lineplot(x='loom', y='esc_none', data=group1, label=(str(group1_label) + ' non-responders'), color='lightgrey')
ax = sns.lineplot(x='loom', y='esc_freeze', data=group2, label=(str(group2_label) + ' freezers'), color='darkcyan', alpha = 1)
ax = sns.lineplot(x='loom', y='escape', data=group2, label=(str(group2_label) + ' escapers'), color='tomato', alpha = 1)
ax = sns.lineplot(x='loom', y='esc_none', data=group2, label=(str(group2_label) + ' non-responders'), color='lightgrey', alpha = 1)
ax = sns.scatterplot(x='loom', y='esc_freeze', data=group1, color='darkcyan', s=50) #label=(str(group1_label) + ' freezers')
ax = sns.scatterplot(x='loom', y='escape', data=group1, color='tomato', s=50) #label=(str(group1_label) + ' escapers'), 
ax = sns.scatterplot(x='loom', y='esc_none', data=group1, color='lightgrey', s=50) #label=(str(group1_label) + ' non-responders')
ax = sns.scatterplot(x='loom', y='esc_freeze', data=group2, color='darkcyan', alpha = 1, s=50) #label=(str(group2_label) + ' freezers'), 
ax = sns.scatterplot(x='loom', y='escape', data=group2, color='tomato', alpha = 1) #label=(str(group2_label) + ' escapers'),
ax = sns.scatterplot(x='loom', y='esc_none', data=group2, color='lightgrey', alpha = 1, s=50) #label=(str(group2_label) + ' non-responders'), 
ax.lines[3].set_linestyle('dashed')
ax.lines[4].set_linestyle('dashed')
ax.lines[5].set_linestyle('dashed')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.8)) #1, 0.8
ax.set_xticks(np.array(range(20)))
ax.set_xticklabels(np.arange(1, 21, 1))
ax.set_ylim([0,1]);

ax.set_title(str(experiment_name), fontsize = 20)
ax.set_ylabel('Fraction of flies', fontsize = 18)
ax.set_xlabel('Loom #', fontsize = 18)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_position(('outward', 5))
ax.spines['bottom'].set_position(('outward', 5))
ax.spines['left'].set_color('dimgrey')
ax.spines['bottom'].set_color('dimgrey')
ax.tick_params(axis='x', colors = 'k', labelsize=16)
ax.tick_params(axis='y', colors = 'k', labelsize=16)
ax.xaxis.label.set_color('k')
ax.yaxis.label.set_color('k')

plt.savefig(plot_path+"/"+str(experiment_name+"_grouped_behaviours.png"), bbox_inches='tight', format='png')
plt.savefig(plot_path_pdf+"/"+str(experiment_name+"_grouped_behaviours.pdf"), bbox_inches='tight', format='pdf')
    
plt.savefig(plot_path_escape_plots+"/"+str(experiment_name+"_grouped_behaviours.png"), bbox_inches='tight', format='png')
plt.savefig(plot_path_pdf_escape_plots+"/"+str(experiment_name+"_grouped_behaviours.pdf"), bbox_inches='tight', format='pdf')

plt.show()
plt.clf();

plt.figure(figsize=(10,6)) 
ax = sns.lineplot(x='loom', y='esc_jump', data=clean1, label=(str(group1_label) + ' jumpers'), color='darkslateblue')
ax = sns.lineplot(x='loom', y='esc_run', data=clean1, label=(str(group1_label) + ' runners'), color='tomato')
ax = sns.lineplot(x='loom', y='esc_turn', data=clean1, label=(str(group1_label) + ' turners'), color='y', zorder=5)
ax = sns.lineplot(x='loom', y='esc_jump', data=clean2, label=(str(group2_label) + ' jumpers'), color='darkslateblue')
ax = sns.lineplot(x='loom', y='esc_run', data=clean2, label=(str(group2_label) + ' runners'), color='tomato')
ax = sns.lineplot(x='loom', y='esc_turn', data=clean2, label=(str(group2_label) + ' turners'), color='y', zorder=5)
ax = sns.scatterplot(x='loom', y='esc_jump', data=clean1, color='darkslateblue', s=50) #label=(str(group1_label) + ' jumpers'), 
ax = sns.scatterplot(x='loom', y='esc_run', data=clean1, color='tomato', s=50) #label=(str(group1_label) + ' runners'),
ax = sns.scatterplot(x='loom', y='esc_turn', data=clean1, color='y', zorder=5, s=50) #label=(str(group1_label) + ' turners'), 
ax = sns.scatterplot(x='loom', y='esc_jump', data=clean2, color='darkslateblue', s=50) #label=(str(group2_label) + ' jumpers'), 
ax = sns.scatterplot(x='loom', y='esc_run', data=clean2, color='tomato', s=50) #label=(str(group2_label) + ' runners'), 
ax = sns.scatterplot(x='loom', y='esc_turn', data=clean2, color='y', zorder=5, s=50) #label=(str(group2_label) + ' turners'), 
ax.lines[3].set_linestyle('dashed')
ax.lines[4].set_linestyle('dashed')
ax.lines[5].set_linestyle('dashed')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.8))
ax.set_xticks(np.array(range(20)))
ax.set_xticklabels(np.arange(1, 21, 1))
ax.set_ylim([0,1]);

ax.set_title(str(experiment_name), fontsize = 20)
ax.set_ylabel('Fraction of flies', fontsize = 18)
ax.set_xlabel('Loom #', fontsize = 18)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_position(('outward', 5))
ax.spines['bottom'].set_position(('outward', 5))
ax.spines['left'].set_color('dimgrey')
ax.spines['bottom'].set_color('dimgrey')
ax.tick_params(axis='x', colors = 'k', labelsize=16)
ax.tick_params(axis='y', colors = 'k', labelsize=16)
ax.xaxis.label.set_color('k')
ax.yaxis.label.set_color('k')

plt.savefig(plot_path+"/"+str(experiment_name+"_different_escape_behaviours.png.png"), bbox_inches='tight', format='png')
plt.savefig(plot_path_pdf+"/"+str(experiment_name+"_different_escape_behaviours.png.pdf"), bbox_inches='tight', format='pdf')
    
plt.savefig(plot_path_escape_plots+"/"+str(experiment_name+"_different_escape_behaviours.png.png"), bbox_inches='tight', format='png')
plt.savefig(plot_path_pdf_escape_plots+"/"+str(experiment_name+"_different_escape_behaviours.png.pdf"), bbox_inches='tight', format='pdf')

plt.show()
plt.clf();
#%%
"""
