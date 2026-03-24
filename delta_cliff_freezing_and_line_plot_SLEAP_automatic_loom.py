# -*- coding: utf-8 -*-
"""
Complete Behavioral Analysis Script
Combines Cliff's delta analysis with timecourse plotting
WITH AUTOMATIC LOOM DETECTION from VisualStim column

Based on your current script with added timecourse functionality
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
    
    Parameters:
    -----------
    df_try : pd.DataFrame
        Dataframe with 'Behavior' column
        
    Returns:
    --------
    pd.DataFrame : Modified dataframe with simplified behaviors
    """
    # Define mapping from complex to simplified behaviors
    behavior_mapping = {
        # Freeze variants -> Freeze
        'Transient_Freeze': 'Freeze',
        'Sustained_Freeze': 'Freeze',
        'Resistant_Freeze': 'Resistant_Freeze',      
        # Stationary variants -> Stationary
        'Transient_Stationary': 'Stationary',
        'Sustained_Stationary': 'Stationary',
        'Resistant_Stationary': 'Stationary',        
        # Walk variants -> Walk
        'Transient_Walk': 'Walk',
        'Sustained_Walk': 'Walk',
        'Resistant_Walk': 'Walk',        
        # Jump variants -> Jump
        'Transient_Jump': 'Jump',
    }
    
    # Apply mapping
    df_try['Behavior'] = df_try['Behavior'].replace(behavior_mapping)    
    return df_try

#%% ==================== LOOM DETECTION ====================

def detect_loom_times(rootdir, group_names, frame_rate=60):
    """
    Automatically detect loom onset times from VisualStim column.
    
    Parameters:
    -----------
    rootdir : str
        Directory containing CSV files
    group_names : list
        List of group names
    frame_rate : int
        Frame rate (fps)
        
    Returns:
    --------
    dict : Dictionary with keys:
        - 'loom_frames': list of loom onset frames (relative to first loom)
        - 'loom_times': list of loom onset times in seconds (relative to first loom)
        - 'baseline_frames': dict mapping group to baseline duration in frames
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
            
            # Read file with VisualStim column
            try:
                fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['VisualStim'])
                
                # Detect loom onsets (when VisualStim changes from 1 to 0, or adjust based on your setup)
                # Using diff() == -1 as in your code (for flipped looms from Bonsai)
                loom_onset = fly_df.loc[fly_df['VisualStim'].diff() == -1].index.values.astype(int)
                
                if len(loom_onset) > 0:
                    group_loom_onsets.append(loom_onset)
                    all_loom_onsets.append(loom_onset)
                    
                    # Store first loom onset as baseline duration for this group
                    if group not in baseline_frames:
                        baseline_frames[group] = loom_onset[0]
                        
            except Exception as e:
                print(f"Warning: Could not read VisualStim from {filename}: {e}")
                continue
        
        if len(group_loom_onsets) > 0:
            # Use the most common loom pattern (mode)
            avg_looms = np.array(group_loom_onsets[0])  # Start with first fly's looms
            print(f"\n{group}:")
            print(f"  Baseline frames: {baseline_frames[group]}")
            print(f"  Baseline duration: {baseline_frames[group]/frame_rate:.1f} seconds")
            print(f"  Number of looms detected: {len(avg_looms)}")
    
    # Calculate average loom pattern across all files
    if len(all_loom_onsets) > 0:
        # Use the first file as reference for loom pattern
        reference_looms = all_loom_onsets[0]
        
        # Convert to relative times (from first loom)
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
        print("\n⚠️  WARNING: No looms detected! Check your VisualStim column.")
        print("Using default loom times: [0, 10, 20, 30, 40, 50]")
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
    Includes baseline period and aligns all groups to first loom onset.
    
    Parameters:
    -----------
    rootdir : str
        Directory containing the CSV files
    group_names : list
        List of group names to analyze
    behavior_type : str
        Type of behavior to analyze: 'Freeze', 'Resistant_Freeze', or 'All_Freeze'
    baseline_frames_dict : dict
        Dictionary mapping group names to baseline duration in frames
    frame_rate : int
        Frame rate of the video (default: 60 fps)
    bin_size_sec : float
        Bin size in seconds for calculating percentage (default: 1 second)
        
    Returns:
    --------
    dict : Dictionary containing timecourse data and metadata
    """
    
    bin_size_frames = int(bin_size_sec * frame_rate)
    
    # Store data for each group
    group_data = {}
    max_total_length = 0
    
    # Find the maximum baseline to use as reference
    max_baseline_frames = max(baseline_frames_dict.values())
    
    for group in group_names:
        group_flies = []
        baseline_frames = baseline_frames_dict[group]
        
        # Calculate how much padding we need at the start for this group
        # to align all first looms together
        start_padding = max_baseline_frames - baseline_frames
        
        # Load all files for this group
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
                
            # Read and process file
            fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
            fly_df = simplify_behaviors(fly_df)
            
            # Create binary behavior column based on behavior_type
            if behavior_type == 'Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Freeze').astype(float)
            elif behavior_type == 'Resistant_Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Resistant_Freeze').astype(float)
            elif behavior_type == 'All_Freeze':
                fly_df['target_behavior'] = ((fly_df['Behavior'] == 'Freeze') | 
                                            (fly_df['Behavior'] == 'Resistant_Freeze')).astype(float)
            else:
                raise ValueError(f"Unknown behavior_type: {behavior_type}")
            
            # Get all data from start
            all_data = fly_df['target_behavior'].values
            
            # Pad at the beginning if needed to align first looms
            if start_padding > 0:
                all_data = np.concatenate([np.full(start_padding, np.nan), all_data])
            
            group_flies.append(all_data)
            
            # Track maximum length
            max_total_length = max(max_total_length, len(all_data))
        
        # Pad all flies to same length at the end with NaN
        padded_flies = []
        for fly_data in group_flies:
            if len(fly_data) < max_total_length:
                padded = np.concatenate([fly_data, np.full(max_total_length - len(fly_data), np.nan)])
            else:
                padded = fly_data
            padded_flies.append(padded)
        
        # Stack all flies for this group
        group_data[group] = np.array(padded_flies)
    
    # Calculate time bins
    n_bins = int(np.ceil(max_total_length / bin_size_frames))
    
    # Create results dataframe
    timecourse_df = pd.DataFrame()
    
    for group in group_names:
        group_array = group_data[group]
        percentages = []
        
        for i in range(n_bins):
            start_frame = i * bin_size_frames
            end_frame = min((i + 1) * bin_size_frames, group_array.shape[1])
            
            # Get data for this bin across all flies
            bin_data = group_array[:, start_frame:end_frame]
            
            # Calculate percentage (ignoring NaN values)
            percentage = np.nanmean(bin_data) * 100
            percentages.append(percentage)
        
        timecourse_df[group] = percentages
    
    # Create time vector starting from beginning of longest baseline
    # Time 0 will be at the first loom of the longest baseline group
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
    
    Parameters:
    -----------
    timecourse_results : dict
        Output from calculate_behavior_timecourse()
    group_names : list
        List of group names to plot
    behavior_type : str
        Behavior type being plotted (for labeling)
    loom_times : array-like
        Array of loom onset times in seconds (relative to first loom at 0)
    colors : list, optional
        List of colors for each group
    figsize : tuple
        Figure size (width, height)
    title : str, optional
        Plot title
    ylabel : str, optional
        Y-axis label
    show_legend : bool
        Whether to show legend
    save_path : str, optional
        If provided, saves figure to this path (without extension)
        
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    
    df = timecourse_results['timecourse_data']
    time = df['Time_sec'].values / 60  # Convert to minutes
    
    # Convert loom times to minutes (they're already in seconds relative to first loom at 0)
    loom_times_minutes = np.array(loom_times) / 60
    
    # Set up colors
    if colors is None:
        colors = sns.color_palette("husl", len(group_names))
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each group
    for i, group in enumerate(group_names):
        ax.plot(time, df[group].values, 
               label=group, 
               color=colors[i], 
               linewidth=2,
               alpha=0.8)
    
    # Add loom stimulus markers (grey dashed lines)
    for loom_time in loom_times_minutes:
        if loom_time >= time[0] and loom_time <= time[-1]:  # Only plot looms within the time range
            ax.axvline(x=loom_time, color='grey', linestyle='--', 
                      linewidth=1.5, alpha=0.6, zorder=0)
    
    # Labels and formatting
    ax.set_xlabel('Time (minutes)', fontsize=12)
    
    if ylabel is None:
        ylabel = f'Percentage of flies showing {behavior_type} (%)'
    ax.set_ylabel(ylabel, fontsize=12)
    
    if title is None:
        title = f'{behavior_type} behavior over time'
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle=':')
    if show_legend:
        ax.legend(loc='best', framealpha=0.9)
    
    # Set y-axis limits
    ax.set_ylim(0, 100)
    
    # Remove top and right spines (keep only x and y axes)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save figure if path provided
    if save_path:
        plt.savefig(f"{save_path}.png", dpi=300, bbox_inches='tight')
        plt.savefig(f"{save_path}.pdf", bbox_inches='tight')
        print(f"Timecourse plot saved: {os.path.basename(save_path)}")
    
    return fig, ax

#%% ==================== SETUP AND CONFIGURATION ====================

# Define all groups
group_a = 'Tsh_Empty_Gtacr1-20Looms'
group_b = 'Tsh_Empty_Gtacr1-green_LED'
group_c = 'Tsh_39347_Gtacr1-20Looms'
group_d = 'Tsh_39347_Gtacr1-green_LED'

group_names = [group_a, group_b, group_c, group_d]
number_of_groups = len(group_names)

# TIME SCALES
frame_rate = 60

# Load path
def load_path():
    """Load folder path using file dialog"""
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(
        parent=root, 
        title='Choose parent folder to load files'
    )
    root.destroy()
    return filename

rootdir = load_path()

# Create output directory for results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(rootdir, f"analysis_results_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("BEHAVIORAL ANALYSIS PIPELINE")
print("=" * 60)
print(f"\nOutput directory: {output_dir}")
print(f"Groups: {group_names}")

#%% ==================== DETECT LOOM TIMES ====================

# Automatically detect loom times from data
loom_info = detect_loom_times(rootdir, group_names, frame_rate)
loom_times = loom_info['loom_times']
baseline_frames_dict = loom_info['baseline_frames']

# Create baseline_durations dict for convenience (in seconds)
baseline_durations = {k: v/frame_rate for k, v in baseline_frames_dict.items()}

print(f"\nUsing detected loom times: {loom_times}")

#%% ==================== CLIFF'S DELTA ANALYSIS ====================

print("\n" + "=" * 60)
print("PART 1: CLIFF'S DELTA ANALYSIS")
print("=" * 60)

df_resist_freeze_all = pd.DataFrame()
df_freeze_all = pd.DataFrame()

for i in range(number_of_groups):
    fly_n = 0
    group = group_names[i]
    group_baseline_frames = baseline_frames_dict[group]
    
    for filename in sorted(os.listdir(rootdir)):
        if group not in filename:
            continue
        if not '.csv' in filename:
            continue
            
        # Read CSV with explicit keyword arguments
        fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
        fly_df = simplify_behaviors(fly_df)
        
        # Use the detected baseline frames for this group
        resist_freeze_loom = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Resistant_Freeze').mean()
        freeze_loom = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Freeze').mean()
            
        df_resist_freeze_all.loc[fly_n, group] = resist_freeze_loom
        df_freeze_all.loc[fly_n, group] = freeze_loom
        fly_n += 1

print("\nNumber of flies per group:")
print("Freeze:")
print(df_freeze_all.count())
print("\nResistant Freeze:")
print(df_resist_freeze_all.count())

#%% Analysis 1: comparison within same RNAi - FREEZE

print("\n--- FREEZE: Baseline comparison (within RNAi) ---")
multi_2group = dabest.load(df_freeze_all, idx=(
    (group_a, group_b),
    (group_c, group_d)))

fig1 = multi_2group.cliffs_delta.plot(
    title='Delta Labile Freeze per baseline', 
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette={group_a: 'C0',           # Blue for 5min
                    group_b: '#A9CCE3',      # Light blue for 30sec
                    group_c: 'C1',           # Orange for DH44-5min
                    group_d: '#FFB366'})      # Light orange for DH44-30sec
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_LabileF.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_LabileF.pdf"), bbox_inches='tight')
print("✓ Baseline comparison plot saved")

stats1 = multi_2group.cliffs_delta
stats1_results = stats1.results.copy()
stats1_results.to_csv(os.path.join(output_dir, "diff_baseline_comparison_stats_LabileF.csv"))
print(stats1)

#%% Analysis 2: RNAi comparison within same baseline - FREEZE
print("\n--- FREEZE: RNAi comparison (within baseline) ---")
multi_2group_rnai = dabest.load(df_freeze_all, idx=(
    (group_a, group_c),
    (group_b, group_d)))

fig2 = multi_2group_rnai.cliffs_delta.plot(
    title='Delta Labile Freeze per RNAi', 
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette={group_a: 'C0',           # Blue for 5min
                    group_b: '#A9CCE3',      # Light blue for 30sec
                    group_c: 'C1',           # Orange for DH44-5min
                    group_d: '#FFB366'})      # Light orange for DH44-30sec
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rnai_comparison_LabileF.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "rnai_comparison_LabileF.pdf"), bbox_inches='tight')
print("✓ RNAi comparison plot saved")

stats2 = multi_2group_rnai.cliffs_delta
stats2_results = stats2.results.copy()
stats2_results.to_csv(os.path.join(output_dir, "rnai_comparison_stats_LabileF.csv"))
print(stats2)

desc_stats = df_freeze_all.describe()
desc_stats.to_csv(os.path.join(output_dir, "descriptive_statistics_LabileF.csv"))

#%% Analysis 1: comparison within same RNAi - RESISTANT FREEZE
print("\n--- RESISTANT FREEZE: Baseline comparison (within RNAi) ---")
multi_2group_resist = dabest.load(df_resist_freeze_all, idx=(
    (group_a, group_b),
    (group_c, group_d)))

fig3 = multi_2group_resist.cliffs_delta.plot(
    title='Delta Resistant Freeze per baseline', 
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette={group_a: 'C0',           # Blue for 5min
                    group_b: '#A9CCE3',      # Light blue for 30sec
                    group_c: 'C1',           # Orange for DH44-5min
                    group_d: '#FFB366'})      # Light orange for DH44-30sec
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Resistant_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Resistant_Freeze.pdf"), bbox_inches='tight')
print("✓ Baseline comparison plot saved")

stats3 = multi_2group_resist.cliffs_delta
stats3_results = stats3.results.copy()
stats3_results.to_csv(os.path.join(output_dir, "diff_baseline_comparison_stats_Resistant_Freeze.csv"))
print(stats3)

#%% Analysis 2: RNAi comparison within same baseline - RESISTANT FREEZE
print("\n--- RESISTANT FREEZE: RNAi comparison (within baseline) ---")
multi_2group_rnai_resist = dabest.load(df_resist_freeze_all, idx=(
    (group_a, group_c),
    (group_b, group_d)))

fig4 = multi_2group_rnai_resist.cliffs_delta.plot(
    title='Delta Resistant Freeze per RNAi', 
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette={group_a: 'C0',           # Blue for 5min
                    group_b: '#A9CCE3',      # Light blue for 30sec
                    group_c: 'C1',           # Orange for DH44-5min
                    group_d: '#FFB366'})      # Light orange for DH44-30sec
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rnai_comparison_Resistant_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "rnai_comparison_Resistant_Freeze.pdf"), bbox_inches='tight')
print("✓ RNAi comparison plot saved")

stats4 = multi_2group_rnai_resist.cliffs_delta
stats4_results = stats4.results.copy()
stats4_results.to_csv(os.path.join(output_dir, "rnai_comparison_stats_Resistant_Freeze.csv"))
print(stats4)

desc_stats_resist = df_resist_freeze_all.describe()
desc_stats_resist.to_csv(os.path.join(output_dir, "descriptive_statistics_Resistant_Freeze.csv"))

#%% ==================== TIMECOURSE PLOTS ====================

print("\n" + "=" * 60)
print("PART 2: TIMECOURSE ANALYSIS")
print("=" * 60)

behaviors_to_plot = ['Freeze', 'Resistant_Freeze', 'All_Freeze']
#behaviors_to_plot = ['Resistant_Freeze', 'All_Freeze']
for behavior in behaviors_to_plot:
    print(f"\n--- Processing {behavior} ---")
    
    # Plot 1: All groups together
    timecourse_all = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=group_names,
        behavior_type=behavior,
        baseline_frames_dict=baseline_frames_dict,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig_all, ax_all = plot_behavior_timecourse(
        timecourse_results=timecourse_all,
        group_names=group_names,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - All Groups',
        colors=['C0', '#A9CCE3', 'C1', '#FFB366'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_all_groups")
    )
    
    # Data available in timecourse_all['timecourse_data'] if needed
    
    # Plot 2: 5-minute baseline groups only
    groups_5min = [group_a, group_c]
    baseline_5min = {k: v for k, v in baseline_frames_dict.items() if k in groups_5min}
    
    timecourse_5min = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=groups_5min,
        behavior_type=behavior,
        baseline_frames_dict=baseline_5min,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig_5min, ax_5min = plot_behavior_timecourse(
        timecourse_results=timecourse_5min,
        group_names=groups_5min,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - 5 min baseline',
        colors=['C0', 'C1'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_5min_baseline")
    )
    
    # Plot 3: 30-second baseline groups only
    groups_30sec = [group_b, group_d]
    baseline_30sec = {k: v for k, v in baseline_frames_dict.items() if k in groups_30sec}
    
    timecourse_30sec = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=groups_30sec,
        behavior_type=behavior,
        baseline_frames_dict=baseline_30sec,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig_30sec, ax_30sec = plot_behavior_timecourse(
        timecourse_results=timecourse_30sec,
        group_names=groups_30sec,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - 30 sec baseline',
        colors=['#A9CCE3', '#FFB366'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_30sec_baseline")
    )
    
    # Plot 4: GFP groups only (5min vs 30sec baseline)
    groups_gfp = [group_a, group_b]
    baseline_gfp = {k: v for k, v in baseline_frames_dict.items() if k in groups_gfp}
    
    timecourse_gfp = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=groups_gfp,
        behavior_type=behavior,
        baseline_frames_dict=baseline_gfp,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig_gfp, ax_gfp = plot_behavior_timecourse(
        timecourse_results=timecourse_gfp,
        group_names=groups_gfp,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - GFP RNAi (5min vs 30sec baseline)',
        colors=['C0', '#A9CCE3'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_GFP_baselines")
    )
    
    # Plot 5: DH44 groups only (5min vs 30sec baseline)
    groups_dh44 = [group_c, group_d]
    baseline_dh44 = {k: v for k, v in baseline_frames_dict.items() if k in groups_dh44}
    
    timecourse_dh44 = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=groups_dh44,
        behavior_type=behavior,
        baseline_frames_dict=baseline_dh44,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig_dh44, ax_dh44 = plot_behavior_timecourse(
        timecourse_results=timecourse_dh44,
        group_names=groups_dh44,
        behavior_type=behavior,
        loom_times=loom_times,
        title=f'{behavior} - DH44 RNAi (5min vs 30sec baseline)',
        colors=['C1', '#FFB366'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}_DH44_baselines")
    )

# Save detected loom information to a file for reference
loom_info_df = pd.DataFrame({
    'Loom_Number': range(len(loom_times)),
    'Time_seconds': loom_times,
    'Frame': loom_info['loom_frames']
})
loom_info_df.to_csv(os.path.join(output_dir, "detected_loom_times.csv"), index=False)
print(f"\n✓ Loom detection info saved: detected_loom_times.csv")

#%% ==================== SUMMARY ====================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
print(f"\nAll results saved to:")
print(f"{output_dir}")
print("\nGenerated files:")
print("  - Cliff's delta plots (4 plots x 2 formats = 8 files)")
print("  - Cliff's delta statistics (4 CSV files)")
print("  - Timecourse plots (3 behaviors x 5 comparisons x 2 formats = 30 files)")
print("  - Descriptive statistics (2 CSV files)")
print("  - Detected loom times (1 CSV file)")
print("\nTimecourse plot comparisons:")
print("  1. All 4 groups together")
print("  2. 5-min baseline groups (GFP vs DH44)")
print("  3. 30-sec baseline groups (GFP vs DH44)")
print("  4. GFP RNAi groups (5min vs 30sec)")
print("  5. DH44 RNAi groups (5min vs 30sec)")
print("\n" + "=" * 60)
print("✓ Loom times were automatically detected from VisualStim column")
print(f"  Detected pattern: {loom_times}")
print("=" * 60)

plt.show()
