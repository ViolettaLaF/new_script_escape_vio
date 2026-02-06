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


def detect_loom_times(rootdir, group_names, frame_rate=60):
    """
    Automatically detect loom onset times from VisualStim column.
    """
    all_loom_onsets = []
    baseline_frames = {}
    
    print("\n" + "=" * 60)
    print("DETECTING LOOM TIMES FROM DATA")
    print("=" * 60)
    
    for group in group_names:
        group_loom_onsets = []
        
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
            
            try:
                fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['VisualStim'])
                loom_onset = fly_df.loc[fly_df['VisualStim'].diff() == -1].index.values.astype(int)
                loom_offset = fly_df.loc[fly_df['VisualStim'].diff() == 1].index.values.astype(int)
                if len(loom_onset) > 0:
                    group_loom_onsets.append(loom_onset)
                    all_loom_onsets.append(loom_onset)
                    
                    if group not in baseline_frames:
                        baseline_frames[group] = loom_onset[0]
                        
            except Exception as e:
                print(f"Warning: Could not read VisualStim from {filename}: {e}")
                continue        
        
        if len(group_loom_onsets) > 0:
            avg_looms = np.array(group_loom_onsets[0])
            print(f"\n{group}:")
            print(f"  Baseline frames: {baseline_frames[group]}")
            print(f"  Baseline duration: {baseline_frames[group]/frame_rate:.1f} seconds")
            print(f"  Number of looms detected: {len(avg_looms)}")
    
    if len(all_loom_onsets) > 0:
        reference_looms = all_loom_onsets[0]
        first_loom_frame = reference_looms[0]
        relative_loom_frames = reference_looms - first_loom_frame
        relative_loom_times = relative_loom_frames / frame_rate
        
        print("\n" + "-" * 60)
        print("DETECTED LOOM PATTERN:")
        print(f"Loom times (seconds from first loom): {relative_loom_times}")
        print(f"Inter-loom intervals: {np.diff(relative_loom_times)}")
        print("-" * 60)
        
        return {
            'loom_frames': relative_loom_frames,
            'loom_times': relative_loom_times,
            'baseline_frames': baseline_frames,
            'loom_onsets': reference_looms,
            'all_loom_onsets': all_loom_onsets
        }
    else:
        print("\n⚠️  WARNING: No looms detected!")
        return None


def analyze_freezing_entry(fly_df, loom_onset, loom_offset, frame_rate=60):
    """
    Probability of freezing ENTRY: 
    Fly NOT freezing before loom → starts freezing after loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window is NOT freezing
    - Before loom: 3 frames immediately before loom onset are NOT freezing
    - After loom: DOMINANT behavior in 1sec window after loom offset IS freezing
    
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
    
    # Check criteria:
    # Pre: dominant is NOT freezing AND 3 frames before are NOT freezing
    pre_not_freezing = (not is_freezing(dominant_pre)) and all(not is_freezing(b) for b in frames_before_loom)
    # Post: dominant IS freezing
    post_freezing = is_freezing(dominant_post)
    
    if pre_not_freezing:
        return 1.0 if post_freezing else 0.0
    else:
        return np.nan  # Doesn't meet pre-loom criteria


def analyze_freezing_resumption(fly_df, loom_onset, loom_offset, frame_rate=60):
    """
    Probability of freezing RESUMPTION:
    Fly freezing before loom → breaks during loom → resumes freezing after loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window IS freezing
    - Before loom: 3 frames immediately before loom onset ARE freezing
    - During loom: freeze interrupted for at least 3 frames in 750ms window from onset
    - After loom: DOMINANT behavior in 1sec window after loom offset IS freezing
    
    Returns: 1 if resumption occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)
    window_750ms = int(frame_rate * 0.75)
    
    # Check if we have enough data
    if loom_onset < window_1sec or loom_offset + window_1sec >= len(fly_df):
        return np.nan
    
    # PRE-LOOM CHECK: 1 sec window before loom onset - get DOMINANT behavior
    pre_window = fly_df.iloc[loom_onset - window_1sec:loom_onset]
    dominant_pre = get_dominant_behavior(pre_window)
    
    # PRE-LOOM CHECK: 3 frames immediately before loom onset
    frames_before_loom = fly_df.iloc[loom_onset - 3:loom_onset]['Behavior'].values
    
    # Check if DOMINANT behavior is freezing AND 3 frames before are freezing
    pre_freezing = is_freezing(dominant_pre) and all(is_freezing(b) for b in frames_before_loom)
    
    if not pre_freezing:
        return np.nan  # Doesn't meet pre-loom criteria
    
    # DURING LOOM CHECK: Look for break in 750ms window from loom onset
    during_window = fly_df.iloc[loom_onset:min(loom_onset + window_750ms, len(fly_df))]['Behavior'].values
    
    # Check if freeze was interrupted for at least 3 consecutive frames
    broke_freeze = False
    consecutive_non_freeze = 0
    for behavior in during_window:
        if not is_freezing(behavior):
            consecutive_non_freeze += 1
            if consecutive_non_freeze >= 3:
                broke_freeze = True
                break
        else:
            consecutive_non_freeze = 0
    
    if not broke_freeze:
        return np.nan  # Didn't break from freezing during loom
    
    # POST-LOOM CHECK: 1 sec window after loom offset - get DOMINANT behavior
    post_window = fly_df.iloc[loom_offset:loom_offset + window_1sec]
    dominant_post = get_dominant_behavior(post_window)
    
    # If broke during loom, did they resume freezing (DOMINANT)?
    return 1.0 if is_freezing(dominant_post) else 0.0


def analyze_freeze_break_by_loom(fly_df, loom_onset, loom_offset, frame_rate=60):
    """
    Probability of freeze BREAK by loom:
    Fly freezing before loom → breaks during loom
    
    Criteria:
    - Before loom: DOMINANT behavior (most frequent) in 1sec window IS freezing
    - Before loom: 3 frames immediately before loom onset ARE freezing
    - During loom: freeze interrupted for at least 3 frames in 750ms window from onset
    
    Returns: 1 if break occurred, 0 if not, NaN if criteria not met
    """
    window_1sec = int(frame_rate * 1.0)
    window_750ms = int(frame_rate * 0.75)
    
    # Check if we have enough data
    if loom_onset < window_1sec:
        return np.nan
    
    # PRE-LOOM CHECK: 1 sec window before loom onset - get DOMINANT behavior
    pre_window = fly_df.iloc[loom_onset - window_1sec:loom_onset]
    dominant_pre = get_dominant_behavior(pre_window)
    
    # PRE-LOOM CHECK: 3 frames immediately before loom onset
    frames_before_loom = fly_df.iloc[loom_onset - 3:loom_onset]['Behavior'].values
    
    # Check if DOMINANT behavior is freezing AND 3 frames before are freezing
    pre_freezing = is_freezing(dominant_pre) and all(is_freezing(b) for b in frames_before_loom)
    
    if not pre_freezing:
        return np.nan  # Doesn't meet pre-loom criteria
    
    # DURING LOOM CHECK: Look for break in 750ms window from loom onset
    during_window = fly_df.iloc[loom_onset:min(loom_onset + window_750ms, len(fly_df))]['Behavior'].values
    
    # Check if freeze was interrupted for at least 3 consecutive frames
    consecutive_non_freeze = 0
    for behavior in during_window:
        if not is_freezing(behavior):
            consecutive_non_freeze += 1
            if consecutive_non_freeze >= 3:
                return 1.0  # Broke freeze
        else:
            consecutive_non_freeze = 0
    
    return 0.0  # Did not break freeze


def analyze_spontaneous_break(fly_df, loom_offset, next_loom_onset, frame_rate=60):
    """
    Probability of SPONTANEOUS break:
    Fly freezing after loom → breaks before next loom
    
    Criteria:
    - After loom: DOMINANT behavior (most frequent) in 1sec window after loom offset IS freezing
    - Before next loom: sliding 1sec window shows non-freezing as DOMINANT behavior
    
    We slide the window frame-by-frame starting from the end of the post-loom window
    until we find a window where freezing is no longer dominant, or we reach the next loom.
    
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
    post_freezing = is_freezing(dominant_post)
    
    if not post_freezing:
        return np.nan  # Doesn't meet post-loom criteria
    
    # SLIDING WINDOW CHECK: From end of post-loom window to next loom
    # Slide frame by frame looking for when freezing is no longer DOMINANT
    start_slide = loom_offset + window_1sec
    
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
        
        if not is_freezing(dominant):
            return 1.0  # Found spontaneous break (freezing no longer dominant)
    
    return 0.0  # No spontaneous break detected


def analyze_all_flies(rootdir, group_names, loom_info, frame_rate=60):
    """
    Analyze all four freezing probabilities for all flies in all groups.
    
    Returns a dictionary with DataFrames for each probability type.
    """
    results = {
        'entry': [],
        'resumption': [],
        'break': [],
        'spontaneous': []
    }
    
    baseline_frames_dict = loom_info['baseline_frames']
    
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
            
            # Analyze each loom
            fly_entry = []
            fly_resumption = []
            fly_break = []
            fly_spontaneous = []
            
            for i in range(len(loom_onset)):
                onset = loom_onset[i]
                offset = loom_offset[i] if i < len(loom_offset) else onset + int(frame_rate * 0.5)
                next_onset = loom_onset[i + 1] if i + 1 < len(loom_onset) else None
                
                # Calculate all probabilities
                entry_prob = analyze_freezing_entry(fly_df, onset, offset, frame_rate)
                resumption_prob = analyze_freezing_resumption(fly_df, onset, offset, frame_rate)
                break_prob = analyze_freeze_break_by_loom(fly_df, onset, offset, frame_rate)
                spontaneous_prob = analyze_spontaneous_break(fly_df, offset, next_onset, frame_rate)
                
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
            results['entry'].append({
                'group': group,
                'fly_id': fly_n,
                'probability': np.mean(fly_entry) if len(fly_entry) > 0 else np.nan,
                'n_events': len(fly_entry)
            })
            
            results['resumption'].append({
                'group': group,
                'fly_id': fly_n,
                'probability': np.mean(fly_resumption) if len(fly_resumption) > 0 else np.nan,
                'n_events': len(fly_resumption)
            })
            
            results['break'].append({
                'group': group,
                'fly_id': fly_n,
                'probability': np.mean(fly_break) if len(fly_break) > 0 else np.nan,
                'n_events': len(fly_break)
            })
            
            results['spontaneous'].append({
                'group': group,
                'fly_id': fly_n,
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
    Create violin plots for all four probability types.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    
    probability_types = ['entry', 'resumption', 'break', 'spontaneous']
    titles = [
        'Freezing Entry Probability\n(Not freezing → Freezing)',
        'Freezing Resumption Probability\n(Freezing → Break → Freezing)',
        'Freeze Break by Loom Probability\n(Freezing → Break during loom)',
        'Spontaneous Break Probability\n(Freezing → Break before next loom)'
    ]
    
    colors = sns.color_palette("husl", len(group_names))
    
    for idx, (prob_type, title) in enumerate(zip(probability_types, titles)):
        ax = axes[idx]
        df = results[prob_type]
        
        if len(df) == 0:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            continue
        
        # Create violin plot
        parts = ax.violinplot(
            [df[df['group'] == group]['probability'].values for group in group_names],
            positions=range(len(group_names)),
            showmeans=True,
            showmedians=True,
            widths=0.7
        )
        
        # Color the violins
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        # Add individual points
        for i, group in enumerate(group_names):
            group_data = df[df['group'] == group]['probability'].values
            x = np.random.normal(i, 0.04, size=len(group_data))
            ax.scatter(x, group_data, alpha=0.6, s=30, color=colors[i], edgecolors='black', linewidths=0.5)
        
        # Formatting
        ax.set_xticks(range(len(group_names)))
        ax.set_xticklabels(group_names, fontsize=11)
        ax.set_ylabel('Probability', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add sample sizes
        for i, group in enumerate(group_names):
            n = len(df[df['group'] == group])
            ax.text(i, -0.1, f'n={n}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'freezing_probabilities_violins.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'freezing_probabilities_violins.pdf'), bbox_inches='tight')
    print(f"\n✓ Violin plots saved to: {output_dir}")
    
    return fig


def save_summary_statistics(results, output_dir, group_names):
    """
    Save summary statistics to CSV files.
    """
    summary_file = os.path.join(output_dir, 'freezing_probabilities_summary.csv')
    
    with open(summary_file, 'w') as f:
        f.write("FREEZING PROBABILITY ANALYSIS - SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")
        
        for prob_type in ['entry', 'resumption', 'break', 'spontaneous']:
            df = results[prob_type]
            
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
    
    # Save individual DataFrames
    for prob_type in ['entry', 'resumption', 'break', 'spontaneous']:
        df = results[prob_type]
        df.to_csv(os.path.join(output_dir, f'{prob_type}_probabilities.csv'), index=False)
    
    print(f"✓ Summary statistics saved to: {summary_file}")


#%% ==================== MAIN ANALYSIS ====================

if __name__ == "__main__":
    # Define groups
    group_5min = '5minbase'  # ⚠️ CHANGE THIS to match your filenames
    group_30sec = '30secbase'  # ⚠️ CHANGE THIS to match your filenames
    group_names = [group_5min, group_30sec]
    
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
    
    # Detect loom times
    loom_info = detect_loom_times(rootdir, group_names, frame_rate)
    
    if loom_info is None:
        print("\n❌ ERROR: Could not detect looms. Exiting...")
        exit()
    
    # Analyze all flies
    results = analyze_all_flies(rootdir, group_names, loom_info, frame_rate)
    
    # Print quick summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for prob_type in ['entry', 'resumption', 'break', 'spontaneous']:
        print(f"\n{prob_type.upper()}:")
        for group in group_names:
            df = results[prob_type]
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
