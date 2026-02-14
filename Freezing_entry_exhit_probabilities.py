# -*- coding: utf-8 -*- #can be used for 2 groups of different baseline lenght 
"""
5min vs 30sec
Simplified for 2 groups only: comparing probability of freezing exhit and entry 
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter, tkinter.filedialog
from datetime import datetime
from scipy.stats import mannwhitneyu


def simplify_behaviors(df_try):
    """
    Simplify behavior categories by combining similar behaviors.
    """
    behavior_mapping = {
        'Transient_Freeze': 'Freeze',
        'Sustained_Freeze': 'Freeze',
        'Resistant_Freeze': 'Resistant_Freeze',      
        'Transient_Stationary': 'Stationary',
        'Sustained_Stationary': 'Stationary',
        'Resistant_Stationary': 'Stationary',        
        'Transient_Walk': 'Walk',
        'Sustained_Walk': 'Walk',
        'Resistant_Walk': 'Walk',        
        'Transient_Jump': 'Jump',
    }
    df_try['Behavior'] = df_try['Behavior'].replace(behavior_mapping)    
    return df_try


def get_dominant_behavior(df_window, behavior_column='Behavior'):
    """Get the most frequent behavior in a window."""
    if len(df_window) == 0:
        return None
    behavior_counts = df_window[behavior_column].value_counts()
    if len(behavior_counts) == 0:
        return None
    return behavior_counts.index[0]


def is_freezing(behavior_val):
    """Check if a behavior value represents freezing (Freeze or Resistant_Freeze)"""
    return behavior_val in ['Freeze', 'Resistant_Freeze']

def check_freezing_by_type(behavior_val, freeze_type='all'):
    """
    Check if a behavior matches the specified freeze type.
    
    Parameters:
    -----------
    behavior_val : str
        The behavior value to check
    freeze_type : str
        'all' - both Freeze and Resistant_Freeze
        'labile' - only Freeze
        'resistant' - only Resistant_Freeze
    
    Returns:
    --------
    bool : True if behavior matches the freeze type
    """
    if freeze_type == 'all':
        return behavior_val in ['Freeze', 'Resistant_Freeze']
    elif freeze_type == 'labile':
        return behavior_val == 'Freeze'
    elif freeze_type == 'resistant':
        return behavior_val == 'Resistant_Freeze'
    else:
        raise ValueError(f"Unknown freeze_type: {freeze_type}. Use 'all', 'labile', or 'resistant'")



def analyze_freezing_entry(fly_df, loom_onset, loom_offset, frame_rate=60, freeze_type='all'):
    """
    Probability of freezing ENTRY: 
    Fly NOT freezing before loom → starts freezing after loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window is NOT freezing
    - Before loom: 3 frames immediately before loom onset are NOT freezing
    - After loom: DOMINANT behavior in 1sec window after loom offset IS freezing
    
    Parameters:
    -----------
    freeze_type : str
        'all' - both Freeze and Resistant_Freeze
        'labile' - only Freeze
        'resistant' - only Resistant_Freeze
    
    Returns: 1 if entry occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)  # 1 second window
    
    # Check if we have enough data
    if loom_onset < window_1sec or loom_offset + window_1sec >= len(fly_df):
        return np.nan
    
    # PRE-LOOM CHECK: 1 sec window before loom onset - get DOMINANT behavior
    pre_window = fly_df.iloc[loom_onset - window_1sec:loom_onset]
    dominant_pre = get_dominant_behavior(pre_window)
    
    # PRE-LOOM CHECK: 3 frames immediately before loom onset
    frames_before_loom = fly_df.iloc[loom_onset - 3:loom_onset]['Behavior'].values
    
    # POST-LOOM CHECK: 1 sec window after loom offset - get DOMINANT behavior
    post_window = fly_df.iloc[loom_offset:loom_offset + window_1sec]
    dominant_post = get_dominant_behavior(post_window)
    
    # Check criteria using freeze_type:
    # Pre: dominant is NOT freezing AND 3 frames before are NOT freezing
    pre_not_freezing = (not check_freezing_by_type(dominant_pre, freeze_type)) and \
                       all(not check_freezing_by_type(b, freeze_type) for b in frames_before_loom)
    # Post: dominant IS freezing
    post_freezing = check_freezing_by_type(dominant_post, freeze_type)
    
    if pre_not_freezing:
        return 1.0 if post_freezing else 0.0
    else:
        return np.nan  # Doesn't meet pre-loom criteria


def analyze_freezing_resumption(fly_df, loom_onset, loom_offset, frame_rate=60, freeze_type='all'):
    """
    Probability of freezing RESUMPTION:
    Fly freezing before loom → breaks during loom → resumes freezing after loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window IS freezing
    - Before loom: 3 frames immediately before loom onset ARE freezing
    - During loom: freeze interrupted for at least 3 frames in 1.5s window from onset (actually is from loom onset to 1 sec after loom offset)
    - After loom: DOMINANT behavior in 1sec window after 1 sec from loom offset IS freezing
    
    Parameters:
    -----------
    freeze_type : str
        'all' - both Freeze and Resistant_Freeze
        'labile' - only Freeze
        'resistant' - only Resistant_Freeze
    
    Returns: 1 if resumption occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)
    
    # Check if we have enough data
    if loom_onset < window_1sec or loom_offset + window_1sec >= len(fly_df):
        return np.nan
    
    # PRE-LOOM CHECK: 1 sec window before loom onset - get DOMINANT behavior
    pre_window = fly_df.iloc[loom_onset - window_1sec:loom_onset]
    dominant_pre = get_dominant_behavior(pre_window)
    
    # PRE-LOOM CHECK: 3 frames immediately before loom onset
    frames_before_loom = fly_df.iloc[loom_onset - 3:loom_onset]['Behavior'].values
    
    # Check if DOMINANT behavior is freezing AND 3 frames before are freezing
    pre_freezing = check_freezing_by_type(dominant_pre, freeze_type) and \
                   all(check_freezing_by_type(b, freeze_type) for b in frames_before_loom)
    
    if not pre_freezing:
        return np.nan  # Doesn't meet pre-loom criteria
    
    # DURING LOOM CHECK: Look for break in 1.5s window from loom onset
    during_window = fly_df.iloc[loom_onset:min(loom_offset + window_1sec, len(fly_df))]['Behavior'].values
    
    # Check if freeze was interrupted for at least 3 consecutive frames
    broke_freeze = False
    consecutive_non_freeze = 0
    for behavior in during_window:
        if not check_freezing_by_type(behavior, freeze_type):
            consecutive_non_freeze += 1
            if consecutive_non_freeze >= 3:
                broke_freeze = True
                break
        else:
            consecutive_non_freeze = 0
    
    if not broke_freeze:
        return np.nan  # Didn't break from freezing during loom
    
    # POST-LOOM CHECK: from 1 sec window after loom offset - get DOMINANT behavior
    post_window = fly_df.iloc[loom_offset + window_1sec: loom_offset + window_1sec + window_1sec]
    dominant_post = get_dominant_behavior(post_window)
    
    # If broke during loom, did they resume freezing (DOMINANT)?
    return 1.0 if check_freezing_by_type(dominant_post, freeze_type) else 0.0


def analyze_freeze_break_by_loom(fly_df, loom_onset, loom_offset, frame_rate=60, freeze_type='all'):
    """
    Probability of freeze BREAK by loom:
    Fly freezing before loom → breaks during loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window IS freezing
    - Before loom: 3 frames immediately before loom onset ARE freezing
    - During loom: freeze interrupted for at least 3 frames in 1.5s window from onset (actually is from loom onset to 1 sec after loom offset)
    
    Parameters:
    -----------
    freeze_type : str
        'all' - both Freeze and Resistant_Freeze
        'labile' - only Freeze
        'resistant' - only Resistant_Freeze
    
    Returns: 1 if break occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)
    
    # Check if we have enough data
    if loom_onset < window_1sec:
        return np.nan
    
    # PRE-LOOM CHECK: 1 sec window before loom onset - get DOMINANT behavior
    pre_window = fly_df.iloc[loom_onset - window_1sec:loom_onset]
    dominant_pre = get_dominant_behavior(pre_window)
    
    # PRE-LOOM CHECK: 3 frames immediately before loom onset
    frames_before_loom = fly_df.iloc[loom_onset - 3:loom_onset]['Behavior'].values
    
    # Check if DOMINANT behavior is freezing AND 3 frames before are freezing
    pre_freezing = check_freezing_by_type(dominant_pre, freeze_type) and \
                   all(check_freezing_by_type(b, freeze_type) for b in frames_before_loom)
    
    if not pre_freezing:
        return np.nan  # Doesn't meet pre-loom criteria
    
    # DURING LOOM CHECK: Look for break in 750ms window from loom onset
    during_window = fly_df.iloc[loom_onset:min(loom_offset + window_1sec, len(fly_df))]['Behavior'].values
    
    # Check if freeze was interrupted for at least 3 consecutive frames
    consecutive_non_freeze = 0
    for behavior in during_window:
        if not check_freezing_by_type(behavior, freeze_type):
            consecutive_non_freeze += 1
            if consecutive_non_freeze >= 3:
                return 1.0  # Broke freeze
        else:
            consecutive_non_freeze = 0
    
    return 0.0  # Did not break freeze


def analyze_spontaneous_break(fly_df, loom_offset, next_loom_onset, frame_rate=60, freeze_type='all'):
    """
    Probability of SPONTANEOUS break:
    Fly freezing after loom → breaks before next loom
    
    Criteria:
    - After loom: DOMINANT behavior (most frequent) in 1sec window after loom offset IS freezing
    - Before next loom: sliding 1sec window shows non-freezing as DOMINANT behavior
    
    We slide the window frame-by-frame starting from 1sec after the end of the post-loom window
    until we find a window where freezing is no longer dominant, or we reach the next loom.
    
    Parameters:
    -----------
    freeze_type : str
        'all' - both Freeze and Resistant_Freeze
        'labile' - only Freeze
        'resistant' - only Resistant_Freeze
    
    Returns: 1 if spontaneous break occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)
    
    # Check if we have enough data
    if loom_offset + window_1sec >= len(fly_df):
        return np.nan
    
    # POST-LOOM CHECK: 1 sec window after loom offset - get DOMINANT behavior
    post_window = fly_df.iloc[loom_offset:loom_offset + window_1sec]
    dominant_post = get_dominant_behavior(post_window)
    
    # Check if DOMINANT behavior is freezing after loom
    post_freezing = check_freezing_by_type(dominant_post, freeze_type)
    
    if not post_freezing:
        return np.nan  # Doesn't meet post-loom criteria
    
    # SLIDING WINDOW CHECK: From 1sec after the post-loom window to next loom
    # Slide frame by frame looking for when freezing is no longer DOMINANT
    start_slide = loom_offset + window_1sec + window_1sec
    
    # If there's no next loom, use end of data
    if next_loom_onset is None:
        end_slide = len(fly_df) - window_1sec
    else:
        end_slide = next_loom_onset - window_1sec
    
    if end_slide <= start_slide:
        return 0.0  # Not enough time to check for break
    
    for frame_idx in range(start_slide, end_slide + 1):
        window = fly_df.iloc[frame_idx:frame_idx + window_1sec]
        dominant = get_dominant_behavior(window)
        
        if not check_freezing_by_type(dominant, freeze_type):
            return 1.0  # Found spontaneous break (freezing no longer dominant)
    
    return 0.0  # No spontaneous break detected


def analyze_all_flies(rootdir, group_names, frame_rate=60):
    """
    Analyze all four freezing probabilities for all flies in all groups.
    Runs analysis for three freeze types: 'all', 'labile', and 'resistant'.
    
    Returns a dictionary with DataFrames for each probability type and freeze type.
    """
    freeze_types = ['all', 'labile', 'resistant']
    results = {
        f'{prob_type}_{freeze_type}': []
        for prob_type in ['entry', 'resumption', 'break', 'spontaneous']
        for freeze_type in freeze_types
    }
        
    print("\n" + "=" * 60)
    print("ANALYZING FREEZING PROBABILITIES")
    print("=" * 60)
    
    for group in group_names:
        print(f"\nProcessing group: {group}")
        
        fly_n = 0
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
            
            print(f"  Analyzing {filename}...")
            
            # Load data
            fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior', 'VisualStim'])
            fly_df = simplify_behaviors(fly_df)
            
            # Detect looms for this specific fly
            loom_onset = fly_df.loc[fly_df['VisualStim'].diff() == -1].index.values.astype(int)
            loom_offset = fly_df.loc[fly_df['VisualStim'].diff() == 1].index.values.astype(int)
            
            if len(loom_onset) == 0:
                print(f"    WARNING: No looms detected, skipping...")
                continue
            
            # Analyze each freeze type
            for freeze_type in freeze_types:
                fly_entry = []
                fly_resumption = []
                fly_break = []
                fly_spontaneous = []
                
                # Analyze each loom
                for i in range(len(loom_onset)):
                    onset = loom_onset[i]
                    offset = loom_offset[i] if i < len(loom_offset) else onset + int(frame_rate * 0.5)
                    next_onset = loom_onset[i + 1] if i + 1 < len(loom_onset) else None
                    
                    # Calculate all probabilities for this freeze type
                    entry_prob = analyze_freezing_entry(fly_df, onset, offset, frame_rate, freeze_type)
                    resumption_prob = analyze_freezing_resumption(fly_df, onset, offset, frame_rate, freeze_type)
                    break_prob = analyze_freeze_break_by_loom(fly_df, onset, offset, frame_rate, freeze_type)
                    spontaneous_prob = analyze_spontaneous_break(fly_df, offset, next_onset, frame_rate, freeze_type)
                    
                    # Store results (only if not NaN)
                    if not np.isnan(entry_prob):
                        fly_entry.append(entry_prob)
                    if not np.isnan(resumption_prob):
                        fly_resumption.append(resumption_prob)
                    if not np.isnan(break_prob):
                        fly_break.append(break_prob)
                    if not np.isnan(spontaneous_prob):
                        fly_spontaneous.append(spontaneous_prob)
                
                # Calculate mean probability for this fly (across all valid looms)
                results[f'entry_{freeze_type}'].append({
                    'group': group,
                    'fly_id': filename, 
                    'probability': np.mean(fly_entry) if len(fly_entry) > 0 else np.nan,
                    'n_events': len(fly_entry)
                })
                
                results[f'resumption_{freeze_type}'].append({
                    'group': group,
                    'fly_id': filename, 
                    'probability': np.mean(fly_resumption) if len(fly_resumption) > 0 else np.nan,
                    'n_events': len(fly_resumption)
                })
                
                results[f'break_{freeze_type}'].append({
                    'group': group,
                    'fly_id': filename, 
                    'probability': np.mean(fly_break) if len(fly_break) > 0 else np.nan,
                    'n_events': len(fly_break)
                })
                
                results[f'spontaneous_{freeze_type}'].append({
                    'group': group,
                    'fly_id': filename, 
                    'probability': np.mean(fly_spontaneous) if len(fly_spontaneous) > 0 else np.nan,
                    'n_events': len(fly_spontaneous)
                })
            
            fly_n += 1
    
    # Convert to DataFrames
    for key in results:
        results[key] = pd.DataFrame(results[key])
        # Remove NaN probabilities
        results[key] = results[key].dropna(subset=['probability'])
    
    return results


def plot_probability_violins(results, output_dir, group_names):
    """
    Create violin plots for all four probability types across all freeze types.
    Creates separate figures for 'all', 'labile', and 'resistant' freeze types.
    """
    freeze_types = ['all', 'labile', 'resistant']
    freeze_type_labels = {
        'all': 'All Freezing',
        'labile': 'Labile Freezing',
        'resistant': 'Resistant Freezing'
    }
    
    probability_types = ['entry', 'break', 'resumption', 'spontaneous']
    titles = [
        'Freezing Entry',
        'Freeze Break by Loom',
        'Freezing Resumption',        
        'Spontaneous Break'
    ]
    
    colors= ['C0', '#A9CCE3']  #blu and pale blu  ['#1f77b4', '#ff7f0e'] Classic blue and orange color
    
    # Create a separate figure for each freeze type
    for freeze_type in freeze_types:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()
        
        fig.suptitle(freeze_type_labels[freeze_type], fontsize=16, fontweight='bold', y=0.995)
        
        for idx, (prob_type, title) in enumerate(zip(probability_types, titles)):
            ax = axes[idx]
            key = f'{prob_type}_{freeze_type}'
            df = results[key]
            
            if len(df) == 0:
                ax.text(0.5, 0.5, 'No data available', 
                       ha='center', va='center', fontsize=12)
                ax.set_title(title, fontsize=14, fontweight='bold')
                continue
            
            # Create violin plot (without showing default mean/median lines)
            parts = ax.violinplot(
                [df[df['group'] == group]['probability'].values for group in group_names],
                positions=range(len(group_names)),
                showmeans=False,
                showmedians=False,
                showextrema=False,  # Don't show the default quartile bars
                widths=0.7
            )
            
            # Color the violins
            for pc, color in zip(parts['bodies'], colors):
                pc.set_facecolor(color)
                pc.set_alpha(0.7)
            
            # Add custom median line that is clearly visible
            for i, group in enumerate(group_names):
                group_data = df[df['group'] == group]['probability'].values
                if len(group_data) > 0:
                    median_val = np.median(group_data)
                    
                    # Draw median as thick black solid line
                    ax.plot([i-0.25, i+0.25], [median_val, median_val], 
                           color='black', linewidth=1.25, linestyle='-', zorder=3)
            
            # Add individual points
            for i, group in enumerate(group_names):
                group_data = df[df['group'] == group]['probability'].values
                x = np.random.normal(i, 0.04, size=len(group_data))
                ax.scatter(x, group_data, alpha=0.6, s=30, color=colors[i], edgecolors='black', linewidths=0.5)
                
            # Perform Mann-Whitney U test
            group1_data = df[df['group'] == group_names[0]]['probability'].values
            group2_data = df[df['group'] == group_names[1]]['probability'].values
            
            if len(group1_data) > 0 and len(group2_data) > 0:
                try:
                    statistic, p_value = mannwhitneyu(group1_data, group2_data, alternative='two-sided')
                    
                    # Add significance stars
                    if p_value < 0.001:
                        sig_text = '***'
                    elif p_value < 0.01:
                        sig_text = '**'
                    elif p_value < 0.05:
                        sig_text = '*'
                    else:
                        sig_text = 'ns'
                    
                    # Add p-value text to plot
                    y_max = ax.get_ylim()[1]
                    ax.text(0.5, y_max * 0.95, sig_text, 
                           ha='center', fontsize=14, fontweight='bold')
                except Exception as e:
                    print(f"Warning: Could not compute statistics for {key}: {e}")

            
            # Formatting
            ax.set_xticks(range(len(group_names)))
            labels_with_n = [f'{group} (n={len(df[df["group"] == group])})' for group in group_names]
            ax.set_xticklabels(labels_with_n, fontsize=12)
            ax.set_ylabel('Probability', fontsize=15)
            ax.set_title(title, fontsize=16)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save figure for this freeze type
        plt.savefig(os.path.join(output_dir, f'freezing_probabilities_{freeze_type}.png'), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(output_dir, f'freezing_probabilities_{freeze_type}.pdf'), bbox_inches='tight')
        print(f"\n✓ {freeze_type.capitalize()} freeze violin plots saved")
    
    print(f"\n✓ All violin plots saved to: {output_dir}")
    
    return fig


def save_summary_statistics(results, output_dir, group_names):
    """
    Save summary statistics to CSV files for all freeze types.
    Includes Mann-Whitney U test with both raw and Bonferroni-corrected p-values.
    """
    
    freeze_types = ['all', 'labile', 'resistant']
    probability_types = ['entry', 'resumption', 'break', 'spontaneous']
    
    # Bonferroni correction factor (12 total comparisons)
    bonferroni_alpha = 0.05 / 12  # = 0.00417
    
    summary_file = os.path.join(output_dir, 'freezing_probabilities_summary.csv')
    stats_file = os.path.join(output_dir, 'statistical_tests.csv')
    
    # Save descriptive statistics
    with open(summary_file, 'w') as f:
        f.write("FREEZING PROBABILITY ANALYSIS - SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")
        
        for freeze_type in freeze_types:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{freeze_type.upper()} FREEZING\n")
            f.write(f"{'=' * 80}\n")
            
            for prob_type in probability_types:
                key = f'{prob_type}_{freeze_type}'
                df = results[key]
                
                f.write(f"\n{prob_type.upper()} PROBABILITY\n")
                f.write("-" * 80 + "\n")
                
                for group in group_names:
                    group_data = df[df['group'] == group]['probability'].values
                    
                    if len(group_data) > 0:
                        f.write(f"\n{group}:\n")
                        f.write(f"  N flies: {len(group_data)}\n")
                        f.write(f"  Mean: {np.mean(group_data):.3f}\n")
                        f.write(f"  SEM: {np.std(group_data) / np.sqrt(len(group_data)):.3f}\n")
                        f.write(f"  Median: {np.median(group_data):.3f}\n")
                        f.write(f"  Min: {np.min(group_data):.3f}\n")
                        f.write(f"  Max: {np.max(group_data):.3f}\n")
                    else:
                        f.write(f"\n{group}: No data\n")
                
                f.write("\n")
    
    # Save statistical tests
    stats_data = []
    
    for freeze_type in freeze_types:
        for prob_type in probability_types:
            key = f'{prob_type}_{freeze_type}'
            df = results[key]
            
            # Get data for both groups
            group1_data = df[df['group'] == group_names[0]]['probability'].values
            group2_data = df[df['group'] == group_names[1]]['probability'].values
            
            if len(group1_data) > 0 and len(group2_data) > 0:
                try:
                    # Mann-Whitney U test
                    statistic, p_value = mannwhitneyu(group1_data, group2_data, alternative='two-sided')
                    
                    # Standard significance
                    if p_value < 0.001:
                        sig_standard = '***'
                    elif p_value < 0.01:
                        sig_standard = '**'
                    elif p_value < 0.05:
                        sig_standard = '*'
                    else:
                        sig_standard = 'ns'
                    
                    # Bonferroni-corrected significance
                    if p_value < bonferroni_alpha:
                        sig_bonferroni = 'significant'
                    else:
                        sig_bonferroni = 'ns'
                    
                    stats_data.append({
                        'freeze_type': freeze_type,
                        'probability_type': prob_type,
                        'group_1': group_names[0],
                        'group_2': group_names[1],
                        'n_group_1': len(group1_data),
                        'n_group_2': len(group2_data),
                        'mean_group_1': np.mean(group1_data),
                        'mean_group_2': np.mean(group2_data),
                        'median_group_1': np.median(group1_data),
                        'median_group_2': np.median(group2_data),
                        'U_statistic': statistic,
                        'p_value': p_value,
                        'significance_standard': sig_standard,
                        'bonferroni_alpha': bonferroni_alpha,
                        'significance_bonferroni': sig_bonferroni
                    })
                except Exception as e:
                    print(f"Warning: Could not compute statistics for {key}: {e}")
    
    # Save to CSV
    if stats_data:
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_csv(stats_file, index=False)
        print(f"✓ Statistical tests saved to: {stats_file}")
    
    # Save individual DataFrames for each freeze type and probability type
    for freeze_type in freeze_types:
        for prob_type in probability_types:
            key = f'{prob_type}_{freeze_type}'
            df = results[key]
            df.to_csv(os.path.join(output_dir, f'{prob_type}_{freeze_type}_probabilities.csv'), index=False)
    
    print(f"✓ Summary statistics saved to: {summary_file}")


#%% ==================== MAIN ANALYSIS ====================

if __name__ == "__main__":
    # Define groups    
    group_1 = '5minbase' #'luc_RNAi_TRIP-5'
    group_2 = '30secbase' #'DH44_RNAi_TRIP-5'
    group_names = [group_1, group_2]
    #group_names = [group_1]
    
    frame_rate = 60
    
    # Load directory
    def load_path():
        root = tkinter.Tk()
        filename = tkinter.filedialog.askdirectory(
            parent=root, 
            title='Choose parent folder to load files'
        )
        root.destroy()
        return filename
    
    rootdir = load_path()
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(rootdir, f"freezing_probability_analysis_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📁 Output directory: {output_dir}")
    
    
    # Analyze all flies
    results = analyze_all_flies(rootdir, group_names, frame_rate)
    
    # Print quick summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    freeze_types = ['all', 'labile', 'resistant']
    probability_types = ['entry', 'resumption', 'break', 'spontaneous']
    
    for freeze_type in freeze_types:
        print(f"\n{freeze_type.upper()} FREEZING:")
        print("-" * 60)
        for prob_type in probability_types:
            key = f'{prob_type}_{freeze_type}'
            print(f"\n{prob_type.upper()}:")
            for group in group_names:
                df = results[key]
                group_data = df[df['group'] == group]['probability'].values
                if len(group_data) > 0:
                    print(f"  {group}: {np.mean(group_data):.3f} ± {np.std(group_data)/np.sqrt(len(group_data)):.3f} (n={len(group_data)})")
                else:
                    print(f"  {group}: No data")
    
    # Create plots
    plot_probability_violins(results, output_dir, group_names)
    
    # Save statistics
    save_summary_statistics(results, output_dir, group_names)
    
    print("\n" + "=" * 60)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\nAll results saved to: {output_dir}")


