# -*- coding: utf-8 -*-
"""
Baseline Comparison Analysis - 5min vs 30sec
Simplified for 2 groups only: comparing baseline durations

For your thesis committee meeting - Good luck! 🎓
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dabest
import tkinter, tkinter.filedialog
from datetime import datetime

#%% ==================== BEHAVIOR SIMPLIFICATION ====================

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

#%% ==================== LOOM DETECTION ====================

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
            'baseline_frames': baseline_frames
        }
    else:
        print("\n⚠️  WARNING: No looms detected!")
        return {
            'loom_frames': np.array([0, 600, 1200, 1800, 2400, 3000]),
            'loom_times': np.array([0, 10, 20, 30, 40, 50]),
            'baseline_frames': {group: 300*frame_rate if '5minbase' in group else 30*frame_rate 
                               for group in group_names}
        }

#%% ==================== TIMECOURSE FUNCTIONS ====================

def calculate_behavior_timecourse(rootdir, group_names, behavior_type, 
                                   baseline_frames_dict, frame_rate=60, 
                                   bin_size_sec=0.5):
    """
    Calculate the percentage of flies showing a specific behavior over time.
    """
    bin_size_frames = int(bin_size_sec * frame_rate)
    group_data = {}
    max_total_length = 0
    max_baseline_frames = max(baseline_frames_dict.values())
    
    for group in group_names:
        group_flies = []
        baseline_frames = baseline_frames_dict[group]
        start_padding = max_baseline_frames - baseline_frames
        
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
                
            fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
            fly_df = simplify_behaviors(fly_df)
            
            if behavior_type == 'Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Freeze').astype(float)
            elif behavior_type == 'Resistant_Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Resistant_Freeze').astype(float)
            elif behavior_type == 'All_Freeze':
                fly_df['target_behavior'] = ((fly_df['Behavior'] == 'Freeze') | 
                                            (fly_df['Behavior'] == 'Resistant_Freeze')).astype(float)
            else:
                raise ValueError(f"Unknown behavior_type: {behavior_type}")
            
            all_data = fly_df['target_behavior'].values
            
            if start_padding > 0:
                all_data = np.concatenate([np.full(start_padding, np.nan), all_data])
            
            group_flies.append(all_data)
            max_total_length = max(max_total_length, len(all_data))
        
        padded_flies = []
        for fly_data in group_flies:
            if len(fly_data) < max_total_length:
                padded = np.concatenate([fly_data, np.full(max_total_length - len(fly_data), np.nan)])
            else:
                padded = fly_data
            padded_flies.append(padded)
        
        group_data[group] = np.array(padded_flies)
    
    n_bins = int(np.ceil(max_total_length / bin_size_frames))
    timecourse_df = pd.DataFrame()
    
    for group in group_names:
        group_array = group_data[group]
        percentages = []
        
        for i in range(n_bins):
            start_frame = i * bin_size_frames
            end_frame = min((i + 1) * bin_size_frames, group_array.shape[1])
            bin_data = group_array[:, start_frame:end_frame]
            percentage = np.nanmean(bin_data) * 100
            percentages.append(percentage)
        
        timecourse_df[group] = percentages
    
    time_vector = np.arange(n_bins) * bin_size_sec - max_baseline_frames / frame_rate
    timecourse_df.insert(0, 'Time_sec', time_vector)
    
    return {
        'timecourse_data': timecourse_df,
        'aligned_time': time_vector,
        'baseline_frames': baseline_frames_dict,
        'bin_size_sec': bin_size_sec,
        'max_baseline_frames': max_baseline_frames
    }


def plot_behavior_timecourse(timecourse_results, group_names, behavior_type,
                            loom_times, colors=None, figsize=(12, 6),
                            title=None, ylabel=None, show_legend=True,
                            save_path=None):
    """
    Plot behavior timecourse with loom stimulation markers.
    """
    df = timecourse_results['timecourse_data']
    time = df['Time_sec'].values / 60  # Convert to minutes
    loom_times_minutes = np.array(loom_times) / 60
    
    if colors is None:
        colors = sns.color_palette("husl", len(group_names))
    
    fig, ax = plt.subplots(figsize=figsize)
    
    for i, group in enumerate(group_names):
        ax.plot(time, df[group].values, 
               label=group, 
               color=colors[i], 
               linewidth=2,
               alpha=0.8)
    
    for loom_time in loom_times_minutes:
        if loom_time >= time[0] and loom_time <= time[-1]:
            ax.axvline(x=loom_time, color='grey', linestyle='--', 
                      linewidth=1.5, alpha=0.6, zorder=0)
    
    ax.set_xlabel('Time (minutes)', fontsize=12)
    
    if ylabel is None:
        ylabel = f'Percentage of flies showing {behavior_type} (%)'
    ax.set_ylabel(ylabel, fontsize=12)
    
    if title is None:
        title = f'{behavior_type} behavior over time'
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.grid(True, alpha=0.3, linestyle=':')
    if show_legend:
        ax.legend(loc='best', framealpha=0.9)
    
    ax.set_ylim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(f"{save_path}.png", dpi=300, bbox_inches='tight')
        plt.savefig(f"{save_path}.pdf", bbox_inches='tight')
        print(f"Timecourse plot saved: {os.path.basename(save_path)}")
    
    return fig, ax

#%% ==================== SETUP ====================

# Define ONLY 2 groups - your control groups with different baselines
group_5min = '5minbase'  # ⚠️ CHANGE THIS to match your filenames
group_30sec = '30secbase'  # ⚠️ CHANGE THIS to match your filenames

group_names = [group_5min, group_30sec]

frame_rate = 60

def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(
        parent=root, 
        title='Choose parent folder to load files'
    )
    root.destroy()
    return filename

rootdir = load_path()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(rootdir, f"baseline_comparison_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("BASELINE COMPARISON ANALYSIS (5min vs 30sec)")
print("=" * 60)
print(f"\nOutput directory: {output_dir}")
print(f"Groups: {group_names}")

#%% ==================== DETECT LOOM TIMES ====================

loom_info = detect_loom_times(rootdir, group_names, frame_rate)
loom_times = loom_info['loom_times']
baseline_frames_dict = loom_info['baseline_frames']

print(f"\nUsing detected loom times: {loom_times}")

#%% ==================== CLIFF'S DELTA ANALYSIS ====================

print("\n" + "=" * 60)
print("CLIFF'S DELTA ANALYSIS - 30sec vs 5min baseline")
print("=" * 60)

# Collect data for all three behavior types
df_freeze = pd.DataFrame()
df_resistant_freeze = pd.DataFrame()
df_all_freeze = pd.DataFrame()

for group in group_names:
    fly_n = 0
    group_baseline_frames = baseline_frames_dict[group]
    
    for filename in sorted(os.listdir(rootdir)):
        if group not in filename or '.csv' not in filename:
            continue
            
        fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
        fly_df = simplify_behaviors(fly_df)
        
        # Calculate proportions for each behavior type
        freeze = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Freeze').mean()
        resistant_freeze = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Resistant_Freeze').mean()
        all_freeze = ((fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Freeze') | 
                      (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Resistant_Freeze')).mean()
        
        df_freeze.loc[fly_n, group] = freeze
        df_resistant_freeze.loc[fly_n, group] = resistant_freeze
        df_all_freeze.loc[fly_n, group] = all_freeze
        fly_n += 1

print("\nNumber of flies per group:")
print(f"5min baseline: {df_freeze[group_5min].count()}")
print(f"30sec baseline: {df_freeze[group_30sec].count()}")

# Reshape data into a single DataFrame for dabest
# Each behavior becomes its own pair of columns so dabest can do all 3 in one plot
df_combined = pd.DataFrame({
    'Freeze_5min':              df_freeze[group_5min].values,
    'Freeze_30sec':             df_freeze[group_30sec].values,
    'Resistant_Freeze_5min':    df_resistant_freeze[group_5min].values,
    'Resistant_Freeze_30sec':   df_resistant_freeze[group_30sec].values,
    'All_Freeze_5min':          df_all_freeze[group_5min].values,
    'All_Freeze_30sec':         df_all_freeze[group_30sec].values,
})

print("\n--- Cliff's delta: all behaviors in one plot ---")

# Load into dabest - one tuple per behavior, each comparing 5min vs 30sec
multi_behaviors = dabest.load(df_combined, idx=(
    ('Freeze_5min', 'Freeze_30sec'),
    ('Resistant_Freeze_5min', 'Resistant_Freeze_30sec'),
    ('All_Freeze_5min', 'All_Freeze_30sec')
))

fig_cliff = multi_behaviors.cliffs_delta.plot(
    title="Cliff's Delta: 5min vs 30sec baseline",
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6}
)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "cliffs_delta_all_behaviors.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "cliffs_delta_all_behaviors.pdf"), bbox_inches='tight')
print("✓ Combined Cliff's delta plot saved")

# Save statistics
stats_all = multi_behaviors.cliffs_delta
stats_all_results = stats_all.results.copy()
stats_all_results.to_csv(os.path.join(output_dir, "cliffs_delta_all_behaviors_stats.csv"))
print(stats_all)

# Descriptive statistics
df_combined.describe().to_csv(os.path.join(output_dir, "descriptive_stats_all_behaviors.csv"))

#%% ==================== TIMECOURSE PLOTS ====================

print("\n" + "=" * 60)
print("TIMECOURSE ANALYSIS - 5min vs 30sec baseline")
print("=" * 60)

behaviors_to_plot = ['Freeze', 'Resistant_Freeze', 'All_Freeze']

for behavior in behaviors_to_plot:
    print(f"\n--- Processing {behavior} ---")
    
    timecourse = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=group_names,
        behavior_type=behavior,
        baseline_frames_dict=baseline_frames_dict,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig, ax = plot_behavior_timecourse(
        timecourse_results=timecourse,
        group_names=group_names,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - Baseline Comparison',
        colors=['C0', '#A9CCE3'],  # Blue for 5min, light blue for 30sec
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_baseline_comparison")
    )

# Save loom info
loom_info_df = pd.DataFrame({
    'Loom_Number': range(len(loom_times)),
    'Time_seconds': loom_times,
    'Frame': loom_info['loom_frames']
})
loom_info_df.to_csv(os.path.join(output_dir, "detected_loom_times.csv"), index=False)

#%% ==================== SUMMARY ====================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
print(f"\nAll results saved to:")
print(f"{output_dir}")
print("\nGenerated files:")
print("  - Cliff's delta plot (1 plot with all 3 behaviors x 2 formats = 2 files)")
print("  - Cliff's delta statistics (1 CSV file)")
print("  - Descriptive statistics (1 CSV file)")
print("  - Timecourse plots (3 behaviors x 2 formats = 6 files)")
print("  - Detected loom times (1 CSV file)")
print("\nComparisons:")
print("  • Freeze: 5min vs 30sec baseline")
print("  • Resistant_Freeze: 5min vs 30sec baseline")
print("  • All_Freeze: 5min vs 30sec baseline")
print("\n" + "=" * 60)
print("Good luck with your thesis committee meeting tomorrow! 🎓")
print("=" * 60)

plt.show()
