# -*- coding: utf-8 -*-  at the moment try to do things separately for 'Floor_Turn' and 'Turn' (Turn = wall turn)
"""
Created on Wed Nov 11 19:16:08 2020

@author: Violetta
"""

import tkinter, tkinter.filedialog
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import os
import seaborn as sns
import math
import tkinter, tkinter.filedialog
import math
from scipy.stats import ttest_ind
from matplotlib.collections import PolyCollection, PathCollection
from matplotlib.lines import Line2D
import pickle
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
#%%
def identify_behavior_bouts(df, behavior_label='Turn', behavior_column='Charlie_Behavior'):
    """
    Identify bouts of a specific behavior in a dataframe.
    A bout is a continuous sequence of frames with the same behavior label.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataframe with behavior data
    behavior_label : str
        The behavior to identify (e.g., 'Turn', 'Freeze', 'Jump')
    behavior_column : str
        Name of the column containing behavior labels
    
    Returns:
    --------
    list of dict
        Each dict contains: {'start': frame_index, 'end': frame_index, 'duration': num_frames}
    """
    # Find all frames with the specified behavior
    behavior_mask = df[behavior_column] == behavior_label
    behavior_frames = df[behavior_mask].index.tolist()
    
    if len(behavior_frames) == 0:
        return []
    
    # Identify bouts (consecutive sequences)
    bouts = []
    current_bout_start = behavior_frames[0]
    current_bout_end = behavior_frames[0]
    
    for j in range(1, len(behavior_frames)):
        # If consecutive frame, extend current bout
        if behavior_frames[j] == behavior_frames[j-1] + 1:
            current_bout_end = behavior_frames[j]
        else:
            # Save current bout and start a new one
            bouts.append({
                'start': current_bout_start,
                'end': current_bout_end,
                'duration': current_bout_end - current_bout_start + 1
            })
            current_bout_start = behavior_frames[j]
            current_bout_end = behavior_frames[j]
    
    # Don't forget the last bout
    bouts.append({
        'start': current_bout_start,
        'end': current_bout_end,
        'duration': current_bout_end - current_bout_start + 1
    })
    
    return bouts


#%%
def analyze_bout_distribution(all_flies_data_with_looms, baseline_frames, behavior_label='Turn'):
    """
    Analyze bout duration distribution during entire baseline and stimulation periods.
    
    Parameters:
    -----------
    all_flies_data_with_looms : list of tuples
        Each tuple contains (df_try, loom_onset) - loom_onset is not used here
    baseline_frames : int
        Number of frames in baseline period
    behavior_label : str
        The behavior to analyze
    
    Returns:
    --------
    dict with 'baseline' and 'stimulation' keys, each containing bout statistics
    """
    baseline_durations = []
    stimulation_durations = []
    baseline_counts = []
    stimulation_counts = []
    
    for df_try, _ in all_flies_data_with_looms:  # Use _ to indicate we're ignoring loom_onset
        # Baseline period (frames 0 to baseline_frames)
        df_baseline = df_try.loc[:baseline_frames].copy()
        baseline_bouts = identify_behavior_bouts(df_baseline, behavior_label=behavior_label)
        baseline_durations.extend([bout['duration'] for bout in baseline_bouts])
        baseline_counts.append(len(baseline_bouts))
        
        # Stimulation period (frames baseline_frames to end)
        df_stimulation = df_try.loc[baseline_frames:].copy()
        stimulation_bouts = identify_behavior_bouts(df_stimulation, behavior_label=behavior_label)
        stimulation_durations.extend([bout['duration'] for bout in stimulation_bouts])
        stimulation_counts.append(len(stimulation_bouts))
    
    return {
        'baseline': {
            'durations': baseline_durations,
            'counts': baseline_counts,
            'total_bouts': len(baseline_durations),
            'mean_duration': np.mean(baseline_durations) if baseline_durations else 0,
            'median_duration': np.median(baseline_durations) if baseline_durations else 0,
            'std_duration': np.std(baseline_durations) if baseline_durations else 0
        },
        'stimulation': {
            'durations': stimulation_durations,
            'counts': stimulation_counts,
            'total_bouts': len(stimulation_durations),
            'mean_duration': np.mean(stimulation_durations) if stimulation_durations else 0,
            'median_duration': np.median(stimulation_durations) if stimulation_durations else 0,
            'std_duration': np.std(stimulation_durations) if stimulation_durations else 0
        }
    }


def save_bout_statistics(bout_data, group_name, save_path):
    """
    Save bout statistics to a CSV file.
    """
    stats_dict = {
        'Group': [group_name, group_name],
        'Period': ['Baseline', 'Stimulation'],
        'Total_Bouts': [bout_data['baseline']['total_bouts'], bout_data['stimulation']['total_bouts']],
        'Mean_Duration_frames': [bout_data['baseline']['mean_duration'], bout_data['stimulation']['mean_duration']],
        'Median_Duration_frames': [bout_data['baseline']['median_duration'], bout_data['stimulation']['median_duration']],
        'Std_Duration_frames': [bout_data['baseline']['std_duration'], bout_data['stimulation']['std_duration']],
        'Mean_Count_per_Fly': [np.mean(bout_data['baseline']['counts']), np.mean(bout_data['stimulation']['counts'])],
        'Std_Count_per_Fly': [np.std(bout_data['baseline']['counts']), np.std(bout_data['stimulation']['counts'])]
    }
    
    df_stats = pd.DataFrame(stats_dict)
    df_stats.to_csv(save_path + group_name + '_bout_statistics_Turn.csv', index=False)
    print(f"Statistics saved to: {save_path + group_name}_bout_statistics.csv")
    
    return df_stats    

#%%
def plot_bout_analysis(bout_data, group_name, save_path):
    """
    Plot bout duration distributions (log scale) and counts for baseline vs stimulation.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot 1: Bout duration distribution (log scale)
    ax1 = axes[0]
    baseline_dur = bout_data['baseline']['durations']
    stim_dur = bout_data['stimulation']['durations']
    
    bins= 1000
    
    
    ax1.set_xlim(0, 100)
    ax1.hist(baseline_dur, bins=bins, alpha=0.5, label='Baseline', color='blue', )
    ax1.hist(stim_dur, bins=bins, alpha=0.5, label='Stimulation', color='orange')
    #ax1.set_xscale('log') #otherwise bins have different size!
    #ax1.set_yscale('log')
    ax1.set_xlabel('Bout Duration (frames, log scale)')
    ax1.set_ylabel('Count')
    ax1.set_title(f'{group_name}: Turn Bout Duration Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Total bout counts (baseline vs stimulation)
    ax2 = axes[1]
    total_counts = [bout_data['baseline']['total_bouts'], bout_data['stimulation']['total_bouts']]
    colors = ['blue', 'orange']
    bars = ax2.bar(['Baseline', 'Stimulation'], total_counts, color=colors, alpha=0.7, edgecolor='black')
    
    # Add count labels on bars
    for bar, count in zip(bars, total_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax2.set_ylabel('Total Number of Turn Bouts')
    ax2.set_title(f'{group_name}: Total Turn Bout Count')
    
    # Plot 3: Bout counts per fly (boxplot)
    ax3 = axes[2]
    baseline_counts = bout_data['baseline']['counts']
    stim_counts = bout_data['stimulation']['counts']
    
    positions = [1, 2]
    bp = ax3.boxplot([baseline_counts, stim_counts], positions=positions, widths=0.6,
                      patch_artist=True, labels=['Baseline', 'Stimulation'])
    bp['boxes'][0].set_facecolor('blue')
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor('orange')
    bp['boxes'][1].set_alpha(0.7)
    
    # Add individual points
    for i, counts in enumerate([baseline_counts, stim_counts], 1):
        x = np.random.normal(i, 0.04, size=len(counts))
        ax3.scatter(x, counts, alpha=0.5, s=30, color='black')
    
    ax3.set_ylabel('Number of Turn Bouts per Fly')
    ax3.set_title(f'{group_name}: Turn Bout Count per Fly')
    
    plt.tight_layout()
    plt.savefig(plot_path+"/"+str(experiment_name) + '_bout_analysis_Turn.jpeg', bbox_inches='tight', dpi=300)
    plt.show() 

# Usage example: commenting just because I don't need right now but is correct!
#bout_analysis = analyze_bout_distribution(all_flies_data_with_looms, baseline_frames, behavior_label='Turn')

# Save statistics
#stats_df = save_bout_statistics(bout_analysis, group1_label, plot_path)
#print(stats_df)

# Create plots
#plot_bout_analysis(bout_analysis, group1_label, plot_path)

# Print summary
#print(f"\nBaseline: {bout_analysis['baseline']['total_bouts']} total bouts, mean duration: {bout_analysis['baseline']['mean_duration']:.2f} frames")
#print(f"Stimulation: {bout_analysis['stimulation']['total_bouts']} total bouts, mean duration: {bout_analysis['stimulation']['mean_duration']:.2f} frames")  
#%%
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
    # Create a copy to avoid modifying original
    #df_try = df_try.copy()
    
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
 #%% ETOGRAMME COLLAPSING LOOM TOGETHER (YOU CAN SELECT THE n OF LOOM THAT YOU WANT AND THE SIZE OF THE WINDOW)
def create_ethogram_data_aligned(all_flies_data_with_looms, variable, loom_indices, 
                                 frames_before=60, frames_after=60, 
                                 filter_func=None):
    """
    Create ethogram data matrix with all looms aligned to common onset/offset.
    
    Parameters:
    -----------
    all_flies_data_with_looms : list of tuples
        Each tuple contains (df_try, loom_onset)
    variable : str
        Column name to plot ('Charlie_Behavior', 'Speed', 'Orientation', etc.)
    loom_indices : list
        Which looms to include (e.g., [0, 1, 2] for first 3 looms)
    frames_before : int
        Number of frames before loom onset
    frames_after : int
        Number of frames after loom onset
    filter_func : callable, optional
        Function that takes (df_try, loom_onset, loom_idx, frames_before, frames_after)
        and returns True if this loom trial should be included
        
    Returns:
    --------
    pd.DataFrame : Matrix with loom trials as rows and time as columns
    list : Metadata for each trial (fly_idx, loom_idx)
    """
    all_loom_trials = []
    trial_metadata = []
    
    for fly_idx, (df_try, loom_onset) in enumerate(all_flies_data_with_looms):
        for loom_idx in loom_indices:
            if loom_idx < len(loom_onset):
                loom_start = loom_onset[loom_idx]
                window_start = loom_start - frames_before
                window_end = loom_start + frames_after
                
                # Apply filter if provided
                if filter_func is not None:
                    if not filter_func(df_try, loom_start, window_start, window_end):
                        continue
                
                # Extract data for this window
                if window_start >= 0 and window_end < len(df_try):
                    trace = df_try.loc[window_start:window_end, variable].values
                    all_loom_trials.append(trace)
                    trial_metadata.append({'fly_idx': fly_idx, 'loom_idx': loom_idx})
                else:
                    # Pad with NaN if window extends beyond data
                    trace = [np.nan] * (frames_before + frames_after + 1)
                    all_loom_trials.append(trace)
                    trial_metadata.append({'fly_idx': fly_idx, 'loom_idx': loom_idx})
    
    # Create DataFrame
    n_frames = frames_before + frames_after + 1
    df_ethogram = pd.DataFrame(all_loom_trials, 
                               columns=[f'frame_{i}' for i in range(n_frames)])
    df_ethogram.index.name = 'trial'
    
    return df_ethogram, trial_metadata


def plot_ethogram_raster_aligned(ethogram_data, trial_metadata, variable, group_name,
                                 frames_before=60, frames_after=60, frame_rate=60, 
                                 loom_duration_frames=30,
                                 cbar=True, figsize=None, save_path=None): #figsize=(10, 15)
    """
    Plot ethogram raster with all looms aligned to common onset/offset.
    
    Parameters:
    -----------
    ethogram_data : pd.DataFrame
        Matrix with trials as rows and time as columns
    trial_metadata : list
        Metadata for each trial
    variable : str
        Variable name being plotted
    group_name : str
        Name for the plot title
    frames_before : int
        Number of frames before loom onset
    frames_after : int
        Number of frames after loom onset
    frame_rate : int
        Frame rate for time axis labels
    loom_duration_frames : int
        Duration of loom stimulus in frames
    cbar : bool
        Whether to show colorbar
    figsize : tuple
        Figure size (if None, auto-calculated based on data)
    save_path : str
        Path to save the figure (optional)
    """
    
    raster_width = 8 # Width of the actual raster plot
    raster_height = 10 # Height of the actual raster plot
# Add space for margins, labels, legend
    fig_width = raster_width + 4  # Extra space for legend and margins
    fig_height = raster_height + 2  # Extra space for title and labels    
    
    
    fig = plt.figure(figsize=(fig_width, fig_height))
    
    # Create GridSpec: main plot takes fixed space, rest is for legend/labels
    gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[raster_width, 4], 
                          wspace=0.3, left=0.1, right=0.95, top=0.93, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])  # Main raster plot in first column
    
    # Define color schemes for different variables
    behaviour_colours = {
        'Resistant_Freeze': '#2297C3',
        'Freeze': '#7AD9F1',
        'Stationary': '#F2D657',
        'Walk': 'grey',
        'Turn': '#22C350',
        'Backwards_Walk': '#FB6609',
        'Jump': '#8756B2',
        'Floor_Turn': '#206233',
    }
    
    view_colours = {
        'Left': '#F7E97E', 
        'Top': '#324450',
        'Right': '#A67354',
        'Vertical': '#CC4646'
    }
    
    # Set up colormap and parameters based on variable type
    vmax = None
    cmap = plt.get_cmap("viridis")
    legend_handles = None
    mask = None
    
    if variable == 'Charlie_Behavior' or variable == 'Behavior':
        # Get all unique behaviors in the data
        unique_behaviors = ethogram_data.stack().unique()
        unique_behaviors = [b for b in unique_behaviors if pd.notna(b)]
        
        # Check for behaviors not in our color dictionary
        missing_behaviors = set(unique_behaviors) - set(behaviour_colours.keys())
        if missing_behaviors:
            print(f"Warning: Found behaviors not in color dictionary: {missing_behaviors}")
            print("Adding them with default colors...")
            # Add missing behaviors with random colors
            default_colors = plt.cm.tab20(np.linspace(0, 1, len(missing_behaviors)))
            for i, beh in enumerate(missing_behaviors):
                behaviour_colours[beh] = mcolors.rgb2hex(default_colors[i])
        
        # Convert behavior strings to numeric for plotting
        behavior_to_num = {beh: i for i, beh in enumerate(behaviour_colours.keys())}
        
        # Create numeric matrix
        numeric_data = ethogram_data.replace(behavior_to_num)
        
        cmap = mcolors.ListedColormap(list(behaviour_colours.values()))
        vmax = len(behaviour_colours) - 1
        legend_handles = [mpatches.Patch(color=color, label=beh) 
                         for beh, color in behaviour_colours.items()]
        
        # Mask NaN values
        mask = numeric_data.isna()
        plot_data = numeric_data
        
    elif variable == 'View':
        # Convert view strings to numeric
        view_to_num = {view: i for i, view in enumerate(view_colours.keys())}
        numeric_data = ethogram_data.replace(view_to_num)
        
        cmap = mcolors.ListedColormap(list(view_colours.values()))
        vmax = len(view_colours) - 1
        legend_handles = [mpatches.Patch(color=color, label=view) 
                         for view, color in view_colours.items()]
        
        mask = numeric_data.isna()
        plot_data = numeric_data
        
    elif variable == 'Speed':
        vmax = 20  # mm/s
        plot_data = ethogram_data
        mask = ethogram_data.isna()
        
    elif variable == 'Orientation':
        vmax = 360
        plot_data = ethogram_data
        mask = ethogram_data.isna()
        
    else:
        # Generic continuous variable
        plot_data = ethogram_data
        mask = ethogram_data.isna()
    
    # Set bad color (for NaN/masked values)
    cmap.set_bad('white')
    
    # Create heatmap
    sns.heatmap(plot_data, mask=mask, cmap=cmap, vmin=0, vmax=vmax, 
                cbar=cbar, ax=ax, linewidths=0, alpha=1, rasterized=True)
    
# Add legend for categorical variables
    if legend_handles:
        # Place legend in the second column (separate from raster)
        legend_ax = fig.add_subplot(gs[0, 1])
        legend_ax.axis('off')
        legend_ax.legend(handles=legend_handles, loc='center left', 
                        title=variable, fontsize=10, frameon=False)
    elif cbar and variable not in ['Charlie_Behavior', 'Behavior', 'View']:
        # For continuous variables, add colorbar in second column
        cbar_ax = fig.add_subplot(gs[0, 1])
        cbar_ax.axis('off')
    
    # Add vertical lines at loom onset and offset (ONLY TWO LINES)
    loom_onset_frame = frames_before
    loom_offset_frame = frames_before + loom_duration_frames
    
    ax.axvline(x=loom_onset_frame, color='black', linewidth=3, linestyle='-', alpha=0.9, zorder=10)
    ax.axvline(x=loom_offset_frame, color='black', linewidth=3, linestyle='-', alpha=0.9, zorder=10)
    
    
    # Set up x-axis (time)
    time_points = [-frames_before/frame_rate, 0, loom_duration_frames/frame_rate, frames_after/frame_rate]
    frame_points = [0, loom_onset_frame, loom_offset_frame, frames_before + frames_after]
    
    ax.set_xticks(frame_points)
    ax.set_xticklabels([f'{t:.1f}s' for t in time_points], fontsize=10)
    ax.set_xlabel('Time relative to loom onset', fontsize=12)
    ax.set_ylabel('Trial (Fly × Loom)', fontsize=12)
    
    # Show y-axis with trial numbers
    ax.yaxis.set_visible(True)
    n_trials = len(ethogram_data)
    trial_ticks = np.arange(0, n_trials, max(1, n_trials//20))  # Show max 20 ticks
    ax.set_yticks(trial_ticks + 0.5)
    ax.set_yticklabels(trial_ticks, fontsize=8)
    
    # Title with trial count
    n_flies = len(set(m['fly_idx'] for m in trial_metadata))
    title = f'{group_name} - {variable}\n({n_trials} trials from {n_flies} flies)'
    fig.suptitle(title, fontsize=14, y=0.98)
    
    if save_path:
        try:
            # Ensure directory exists
            import os
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            
            # Save as PNG instead of JPEG (more reliable)
            if save_path.endswith('.jpeg') or save_path.endswith('.jpg'):
                save_path = save_path.replace('.jpeg', '.png').replace('.jpg', '.png')
            
            plt.savefig(save_path, bbox_inches='tight', dpi=300, format='png')
            print(f"Saved ethogram to: {save_path}")
        except Exception as e:
            print(f"Error saving figure: {e}")
    
    plt.show()


# Example filter functions TO FILTER DATA THAT WILL BE DISPLAYED IN THE ETOGRAMME 
def filter_turns_in_window(df_try, loom_start, window_start, window_end):
    """
    Filter function: Include only trials where fly turned during the window.
    """
    window_data = df_try.loc[window_start:window_end]
    has_turn = (window_data['Charlie_Behavior'] == 'Turn').any() #change to Floor_Turn if you want Floor turn 
    return has_turn


def filter_jumps_in_window(df_try, loom_start, window_start, window_end):
    """
    Filter function: Include only trials where fly jumped during the window.
    """
    window_data = df_try.loc[window_start:window_end]
    has_jump = (window_data['Charlie_Behavior'] == 'Jump').any()
    return has_jump


def filter_speed_threshold(df_try, loom_start, window_start, window_end, min_speed=10):
    """
    Filter function: Include only trials where fly exceeded speed threshold.
    """
    window_data = df_try.loc[window_start:window_end]
    exceeded_threshold = (window_data['Speed'] > min_speed).any()
    return exceeded_threshold
"""

# Example usage:

# Define parameters
loom_indices = list(range(20))  # First 5 looms
frames_before = 120  # 2 seconds before
frames_after = 120   # 2 seconds after
loom_duration_frames = 30  # 0.5 seconds

# ALL TRIALS - no filter
#ethogram_all, metadata_all = create_ethogram_data_aligned(all_flies_data_with_looms, variable='Charlie_Behavior', loom_indices=loom_indices, frames_before=frames_before, frames_after=frames_after, filter_func=None  ) # No filter
#plot_ethogram_raster_aligned(ethogram_all, metadata_all, 'Charlie_Behavior', group1_label, frames_before, frames_after, frame_rate, loom_duration_frames, save_path=plot_path + '/ethogram_all_trials.png')

# ONLY TRIALS WITH TURNS
ethogram_turns, metadata_turns = create_ethogram_data_aligned(all_flies_data_with_looms, variable='Charlie_Behavior', loom_indices=loom_indices, frames_before=frames_before, frames_after=frames_after, filter_func=filter_turns_in_window) # Only include trials with turns
plot_ethogram_raster_aligned(ethogram_turns, metadata_turns, 'Charlie_Behavior', group1_label, frames_before, frames_after, frame_rate, loom_duration_frames, save_path=plot_path + '/ethogram_turns_only.png')
#View
ethogram_turns, metadata_turns = create_ethogram_data_aligned(all_flies_data_with_looms, variable='View', loom_indices=loom_indices, frames_before=frames_before, frames_after=frames_after, filter_func=filter_turns_in_window) # Only include trials with turns
plot_ethogram_raster_aligned(ethogram_turns, metadata_turns, 'View', group1_label, frames_before, frames_after, frame_rate, loom_duration_frames, save_path=plot_path + '/ethogram_View_turns_only.png')

#original behaviour 'Behavior'
ethogram_turns, metadata_turns = create_ethogram_data_aligned(all_flies_data_with_looms, variable='Behavior', loom_indices=loom_indices, frames_before=frames_before, frames_after=frames_after, filter_func=filter_turns_in_window) # Only include trials with turns
plot_ethogram_raster_aligned(ethogram_turns, metadata_turns, 'Behavior', group1_label, frames_before, frames_after, frame_rate, loom_duration_frames, save_path=plot_path + '/ethogram_original_behav_turns_only.png')


# ONLY TRIALS WITH JUMPS
ethogram_jumps, metadata_jumps = create_ethogram_data_aligned(
    all_flies_data_with_looms, 
    variable='Charlie_Behavior',
    loom_indices=loom_indices,
    frames_before=frames_before,
    frames_after=frames_after,
    filter_func=filter_jumps_in_window
)

plot_ethogram_raster_aligned(
    ethogram_jumps, metadata_jumps, 'Charlie_Behavior', group1_label,
    frames_before, frames_after, frame_rate, loom_duration_frames,
    save_path=plot_path + '/ethogram_jumps_only.png'
)

# CUSTOM FILTER - High speed trials
def filter_high_speed(df_try, loom_start, window_start, window_end):
    return filter_speed_threshold(df_try, loom_start, window_start, window_end, min_speed=15)

ethogram_speed, metadata_speed = create_ethogram_data_aligned(
    all_flies_data_with_looms, 
    variable='Speed',
    loom_indices=loom_indices,
    frames_before=frames_before,
    frames_after=frames_after,
    filter_func=filter_high_speed
)

plot_ethogram_raster_aligned(
    ethogram_speed, metadata_speed, 'Speed', group1_label,
    frames_before, frames_after, frame_rate, loom_duration_frames,
    save_path=plot_path + '/ethogram_high_speed_trials.png'
)

"""
 #%% TO SORT ETOGRAMME DATA BASED ON BEHAVIOUR, SPEED ETC 
def sort_ethogram_simple(ethogram_data, sort_by='turn_count', frames_before=60, 
                         loom_duration_frames=30):
    """
    Sort ethogram data directly based on the data itself.
    Works on filtered data!
    
    Returns sorted data AND the sorting indices.
    """
    loom_onset_frame = frames_before
    loom_offset_frame = frames_before + loom_duration_frames
    
    sort_values = []
    
    for idx, (row_idx, row) in enumerate(ethogram_data.iterrows()):
        if sort_by == 'turn_count':
            turn_count = (row.iloc[loom_onset_frame:] == 'Turn').sum() #change to Turn if you want to sort by wall turn 
            sort_values.append(turn_count)
            
        elif sort_by == 'turn_count_during':
            turn_count = (row.iloc[loom_onset_frame:loom_offset_frame] == 'Turn').sum()
            sort_values.append(turn_count)
            
        elif sort_by == 'turn_count_after':
            turn_count = (row.iloc[loom_offset_frame:] == 'Turn').sum()
            sort_values.append(turn_count)
            
        elif sort_by == 'first_turn_latency':
            post_loom = row.iloc[loom_onset_frame:]
            turn_frames = np.where(post_loom == 'Turn')[0]
            latency = turn_frames[0] if len(turn_frames) > 0 else 9999
            sort_values.append(latency)
            
        elif sort_by == 'mean_speed':
            mean_speed = row.iloc[loom_onset_frame:].mean()
            sort_values.append(mean_speed if not pd.isna(mean_speed) else 0)
            
        elif sort_by == 'max_speed':
            max_speed = row.iloc[loom_onset_frame:].max()
            sort_values.append(max_speed if not pd.isna(max_speed) else 0)
    
    # Get sorting indices
    if sort_by == 'first_turn_latency':
        sorted_indices = np.argsort(sort_values)  # Ascending
    else:
        sorted_indices = np.argsort(sort_values)[::-1]  # Descending
    
    # Apply sorting
    sorted_ethogram = ethogram_data.iloc[sorted_indices].reset_index(drop=True)
    
    return sorted_ethogram, sorted_indices
"""
# Example usage:
# Step 1: Create filtered ethograms for all variables you want
ethogram_charlie_behavior, metadata = create_ethogram_data_aligned(
    all_flies_data_with_looms, 
    variable='Charlie_Behavior',
    loom_indices=list(range(20)),
    frames_before=120,
    frames_after=120,
    filter_func=filter_turns_in_window  # Filtered!
)

ethogram_behavior, _ = create_ethogram_data_aligned(
    all_flies_data_with_looms, 
    variable='Behavior',
    loom_indices=list(range(20)),
    frames_before=120,
    frames_after=120,
    filter_func=filter_turns_in_window  # Same filter!
)

ethogram_view, _ = create_ethogram_data_aligned(
    all_flies_data_with_looms, 
    variable='View',
    loom_indices=list(range(20)),
    frames_before=120,
    frames_after=120,
    filter_func=filter_turns_in_window  # Same filter!
)

# Step 2: Sort the BEHAVIOR ethogram and get the sorting indices
ethogram_sorted_charlie_behavior, sort_indices = sort_ethogram_simple(
    ethogram_charlie_behavior, 
    sort_by='turn_count',
    frames_before=120,
    loom_duration_frames=30
)

# Step 3: Apply THE SAME sorting indices to ALL other variables
ethogram_sorted_behavior = ethogram_behavior.iloc[sort_indices].reset_index(drop=True)
ethogram_sorted_view = ethogram_view.iloc[sort_indices].reset_index(drop=True)

# Step 4: Plot everything with the same sorting
plot_ethogram_raster_aligned(
    ethogram_sorted_charlie_behavior, metadata, 'Charlie_Behavior', group1_label,
    120, 120, 60, 30,
    save_path=plot_path + '/behavior_sorted_by_Turn.png'
)

plot_ethogram_raster_aligned(
    ethogram_sorted_behavior, metadata, 'Behavior', group1_label,
    120, 120, 60, 30,
    save_path=plot_path + '/original_Behavior_sorted_by_Turn.png'
)

plot_ethogram_raster_aligned(
    ethogram_sorted_view, metadata, 'View', group1_label,
    120, 120, 60, 30,
    save_path=plot_path + '/view_sorted_by_Turn.png'
)

"""
#%%
def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files') #select folder called "ClassifiedPose"
    root.destroy()
    return filename
exp_path = load_path()

plot_path = exp_path + '/plots'
plot_path_pdf = exp_path + '/plots_pdf'

plot_path_escape_plots = exp_path + '/plots/escape_plots'
plot_path_pdf_escape_plots = exp_path + '/plots_pdf/escape_plots'

#CHANGE EXPT NAME AND GROUP LABELS BELOW
experiment_name = 'VLF-39347' #'VLF-39347_tsh_gal80_DH44_RNAi_TRIP-5min'
group1_label = 'VLF-39347'

#arena in mm
arena_raggio = 15 #in mm
arena_center_x = 15 
arena_center_y = 15

#TIME SCALES
frame_rate = 60

#EXPERIMENT DURATION (in sec)
baseline  = 300 #300
stimulation = 300
#(in min)
total_duration_min = (baseline + stimulation) / 60
#(in frame)
baseline_frames = baseline * frame_rate
stimulation_frames = stimulation * frame_rate
tot_frame = baseline_frames + stimulation_frames

#Zoom plots window
number_of_looms= 20
loom_duration_sec = 0.5
loom_duration  = loom_duration_sec * frame_rate


all_flies_data_with_looms = [] #is a list of tupla: with the df_try and an array with loom onset for every fly!
#all_flies_data_with_fake_looms = [] #is a list of tupla: with the df_try and an array with fake loom onset (same inter loom interval but during baseline) for every fly!
#%%
'''upload scored file'''

df_all = pd.DataFrame()

path = exp_path
jump_velocity = 75

behavior_files = [f for f in os.listdir(path) if group1_label in f and f.endswith('_Behavior.csv')] #loading Charlie's analysis on behaviours to have backwards and turns included as escape!!
if behavior_files:                                                                                  #NB. _Behavior.csv need to contain group1_label otherwise will not find it!
    df_behave_charlie = pd.read_csv(os.path.join(path, behavior_files[0]))
    print(f"Loaded behavior file: {behavior_files[0]}")
else:
    print(f"Warning: No _Behavior.csv file found containing '{group1_label}'!")
    df_behave_charlie = None


for filename in sorted(os.listdir(path+'/control_RNAi/')): #NB. to change here with the names of the folder where the classified_pose.csv are!!  es:path+'/DH44_RNAi/'
    if not filename.endswith('classified_pose.csv'):
        continue
    capital_x = filename.replace('X','x')
    if not capital_x.startswith(experiment_name):
        continue
    df_try = pd.read_csv(path+'/control_RNAi/'+filename, usecols=['FrameIndex', 'VisualStim', 'Position_X', 'Position_Y', 'Speed', 'Orientation', 'View', 'Behavior'])

    # Add Charlie behavior data to df_try if available
    if df_behave_charlie is not None:
        # Find the column that ends with the current filename (ignoring path prefix)
        matching_column = None
        for col in df_behave_charlie.columns:
            if col.endswith(filename):
                matching_column = col
                break
    
        if matching_column:    # Create a temporary dataframe with frame and behavior for this fly
            df_behavior_temp = df_behave_charlie[['frame', matching_column]].copy()
            df_behavior_temp.columns = ['frame', 'Charlie_Behavior']  # Rename for clarity    
            df_try = df_try.merge(df_behavior_temp, left_on='FrameIndex', right_on='frame', how='left') # Merge with df_try based on frame alignment   
            df_try = df_try.drop('frame', axis=1)             # Drop the redundant 'frame' column after merge   
            print(f"Added behavior data for {filename}")
        else:
            print(f"Warning: No column ending with '{filename}' found in behavior file")
            df_try['Charlie_Behavior'] = None
    else:
        df_try['Charlie_Behavior'] = None
            
    loom_onset = df_try.loc[df_try['VisualStim'].diff() == -1].index.values.astype(int) #changed here as my loom are flipped_coming from bonsai tracker!!!
    loom_offset = df_try.loc[df_try['VisualStim'].diff() == 1].index.values.astype(int) #changed here as my loom are flipped_coming from bonsai tracker!!!
    #loom_onset_fake = loom_onset - baseline_frames    
    df_try = simplify_behaviors(df_try) #simplify Matheus original behaviour (they are too many, impossible to understand anything)   
    all_flies_data_with_looms.append((df_try, loom_onset))  # Store as tuple of (dataframe, loom_onsets) 
    #all_flies_data_with_fake_looms.append((df_try, loom_onset_fake))  # Store as tuple of (dataframe, loom_onsets) 
#%%   
    df_try['esc_turn_wall'] = 0
    df_try['esc_turn_floor'] = 0
    df_try['esc_run'] = 0
    df_try['esc_jump'] = 0
    df_try['backwards'] = 0
    df_try['walk_away'] = 0 #only one being excluded from other escapes - at the end of the gerarchy 
    df_try['escape'] = 0 #containing all form of escape: esc_turn, esc_run, esc_jump, backwards, 'walk_away'
    df_try['freeze'] = 0 # this before was called 'esc_freeze' contain freeze and resistent freeze
    df_try['walk_speed'] = np.nan
    df_try['speed2d'] = np.nan
      
    df_try.loc[(df_try['Charlie_Behavior'] == 'Walk'), 'walk_speed'] = df_try['Speed'] #walking velocity
    df_try.loc[(df_try['Speed'] < jump_velocity), 'speed2d'] = df_try['Speed'] #velocity excluding jump speed     
        #%% CLEAN VELOCITY DATA: REMOVE JUMPS AND SMOOTH - it will be inportant for esc_run! 
    # Step 1: Create a cleaned velocity column (remove jumps)
    df_try['walk_velocity_clean'] = df_try['walk_speed'].copy()
    df_try['speed2d_clean'] = df_try['speed2d'].copy() 
    # Mark frames with jumps as NaN
    df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'walk_velocity_clean'] = np.nan 
    df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'speed2d_clean'] = np.nan 
    # Also remove frames right before and after jump (they're often artifacts) #now removing 6 frames before and after
    for idx in df_try[df_try['Charlie_Behavior'] == 'Jump'].index:
        if idx >= 6:
            df_try.loc[idx-6:idx-1, 'walk_velocity_clean'] = np.nan
            df_try.loc[idx-6:idx-1, 'speed2d_clean'] = np.nan
        if idx <= len(df_try) - 7:
            df_try.loc[idx+1:idx+6, 'walk_velocity_clean'] = np.nan
            df_try.loc[idx+1:idx+6, 'speed2d_clean'] = np.nan
    # Step 2: Apply running average (7 frames) - NaNs will be skipped
    df_try['velocity_smooth'] = df_try['walk_velocity_clean'].rolling(window=7, center=True, min_periods=1).mean()
    df_try['speed2d_smooth'] = df_try['speed2d_clean'].rolling(window=7, center=True, min_periods=1).mean() 
#%% CALCULATE BASELINE STATISTICS (PER FLY)
    baseline_walk_speed = df_try.loc[:baseline_frames, 'velocity_smooth'].dropna()
    baseline_mean = baseline_walk_speed.mean()
    baseline_std = baseline_walk_speed.std()
    speed_threshold = baseline_mean + baseline_std       
 #%% 
    '''checking all escapes - not mutually exclusive except walk away at the end of the gerarchy'''  
    for i in range(len(loom_onset)):
        
        '''run''' #This block is checking if flies significantly increase their walking speed after the looming stimulus. It does this with a bootstrapping approach (sampling random subsets of velocities before and after) and then applying a t-test. If the increase is real and not just noise, it marks that loom as an “escape run.”
        permutated_pre = df_try.loc[loom_onset[i]-120:(loom_onset[i]), 'velocity_smooth'] #velocities in the time window that goes from 2 second before loom onset to loom onset! 
        permutated_post = df_try.loc[loom_offset[i]:(loom_offset[i]+120), 'velocity_smooth'] #velocities in the time window that goes from loom offset to 2 second after!        
        train_pre = []
        train_post = []
        post_loom_walk_velocity_mean = permutated_post.mean()   # Calculate mean of post-loom window
        #run 100 permutations of velocity per frame per loom(2 seconds before and after loom)
        for perm in range (10): #to change here for 1000 
            df_sample_pre  = permutated_pre.sample(n=30) #df_sample_pre grabs 30 random frames from the 120 available
            row_pre = df_sample_pre.mean(axis=0) #mean of 30 frames
            train_pre.append(row_pre)
        
            df_sample_post  = permutated_post.sample(n=30)
            row_post = df_sample_post.mean(axis=0) #mean of 30 samples --> take unpaired t-test instead, if >0.05
            train_post.append(row_post)            
        #post_loom_mean_speed = permutated_post.mean()    
        #take t-test of 100 samples between groups           
        t, p = ttest_ind(train_pre, train_post, alternative='less') #changed here from original script as in this case the one sided is better!!
        if (p < 0.05) & (post_loom_walk_velocity_mean > speed_threshold):
            df_try.loc[loom_offset[i], 'esc_run'] = 1 #if t-test is significant, if yes --> 1        
                        
        '''checking jumps, freeze, backwards, turns'''        
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Jump').sum() > 0:
            df_try.loc[loom_offset[i], 'esc_jump'] = 1
     
        if ((df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Freeze') | 
              (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Resistant_Freeze')).sum() > 2:
            df_try.loc[loom_offset[i], 'freeze'] = 1
            
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Backwards_Walk').sum() > 2:
            df_try.loc[loom_offset[i], 'backwards'] = 1
            
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Turn').sum() > 2:
            df_try.loc[loom_offset[i], 'esc_turn_wall'] = 1
            
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Floor_Turn').sum() > 2:
            df_try.loc[loom_offset[i], 'esc_turn_floor'] = 1        
        
        "Walk away - ONLY if no other escape happened" 
        # Check if ANY other escape was detected for this loom
        has_other_escape = (df_try.loc[loom_offset[i], 'esc_run'] == 1 or
                           df_try.loc[loom_offset[i], 'esc_jump'] == 1 or
                           df_try.loc[loom_offset[i], 'freeze'] == 1 or
                           df_try.loc[loom_offset[i], 'backwards'] == 1 or
                           df_try.loc[loom_offset[i], 'esc_turn_wall'] == 1 or
                           df_try.loc[loom_offset[i], 'esc_turn_floor'] == 1)
        
        if not has_other_escape:
            # Check pre-loom behavior (2 second before loom)
            pre_loom_start = max(0, loom_onset[i] - 120)
            pre_loom_data = df_try.loc[pre_loom_start:loom_onset[i]-1]
        
            # Check if fly was stationary or freezing before loom
            pre_loom_behaviors = pre_loom_data['Charlie_Behavior'].values
        
            # Count Jump frames (not allowed at all)
            jump_frames_count = sum(b == 'Jump' for b in pre_loom_behaviors if pd.notna(b))
        
            # Count frames that are NOT stationary/freeze (but excluding Jump from this count)
            non_stationary_count = sum(b not in ['Stationary', 'Freeze', 'Resistant_Freeze', 'Jump'] 
                                       for b in pre_loom_behaviors if pd.notna(b))
        
            # Allow if: (1) NO jumps AND (2) less than 3 frames of other behaviors
            is_stationary_before = (jump_frames_count == 0) and (non_stationary_count < 3)
        
            if is_stationary_before:
                # Check if starts walking within 2.5s (150 frames) after loom onset
                post_loom_end = min(len(df_try)-1, loom_onset[i] + 150)
                post_loom_data = df_try.loc[loom_onset[i]:post_loom_end]
                walk_frames = post_loom_data[post_loom_data['Charlie_Behavior'] == 'Walk'].index.tolist()
        
                if len(walk_frames) >= 3:
                    df_try.loc[loom_offset[i], 'walk_away'] = 1  

#%%             
#    '''slicing dataframe from esc_turn until end''' #I'm commenting everything here as I don't need right now!!
#    df_loom = df_try.loc[loom_offset, 'esc_turn':].copy().reset_index(drop=True)
#    df_all = pd.concat([df_all,df_loom])

#df_all = df_all.reset_index()
#%% Plot Speed Profiles by Escape Type

def plot_escape_speed_profiles(all_flies_data_with_looms, group_name, save_path, 
                               frames_before=120, frames_after=120, frame_rate=60):
    """
    Plot speed profiles for different escape types.
    """
    escape_types = {
        'esc_jump': 'Jump',
        'esc_run': 'Run',
        'freeze': 'Freeze',
        'backwards': 'Backwards',
        'esc_turn_wall': 'Turn (Wall)',
        'esc_turn_floor': 'Turn (Floor)',
        'walk_away': 'Walk Away'
    }
    
    # Collect speed traces for each escape type
    escape_traces = {etype: [] for etype in escape_types.keys()}
    escape_counts = {etype: 0 for etype in escape_types.keys()}
    
    for df_try, loom_onset in all_flies_data_with_looms:
        loom_offset = df_try.loc[df_try['VisualStim'].diff() == 1].index.values.astype(int)
        
        for i, (onset, offset) in enumerate(zip(loom_onset, loom_offset)):
            # Skip baseline looms
            if onset < baseline_frames:
                continue
            
            window_start = onset - frames_before
            window_end = onset + frames_after
            
            if window_start >= 0 and window_end < len(df_try):
                speed_trace = df_try.loc[window_start:window_end, 'Speed'].values
                
                # Check which escape type this loom has
                for etype in escape_types.keys():
                    if df_try.loc[offset, etype] == 1:
                        escape_traces[etype].append(speed_trace)
                        escape_counts[etype] += 1
    
    # Create subplots
    fig, axes = plt.subplots(3, 3, figsize=(18, 14), sharex=True, sharey=True)
    axes = axes.flatten()
    
    time_axis = np.arange(-frames_before, frames_after+1) / frame_rate
    
    for idx, (etype, label) in enumerate(escape_types.items()):
        ax = axes[idx]
        
        if len(escape_traces[etype]) > 0:
            traces = np.array(escape_traces[etype])
            mean_speed = np.nanmean(traces, axis=0)
            sem_speed = np.nanstd(traces, axis=0) / np.sqrt(len(traces))
            
            ax.plot(time_axis, mean_speed, linewidth=2, label=f'Mean (n={escape_counts[etype]})')
            ax.fill_between(time_axis, mean_speed - sem_speed, mean_speed + sem_speed, alpha=0.3)
        else:
            ax.text(0.5, 0.5, f'No {label} escapes', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        
        ax.axvline(x=0, color='black', linestyle='--', linewidth=2, alpha=0.7, label='Loom Onset')
        ax.axvline(x=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Loom Offset')
        ax.set_title(f'{label} (n={escape_counts[etype]})', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        if idx >= 6:
            ax.set_xlabel('Time (s)', fontsize=10)
        if idx % 3 == 0:
            ax.set_ylabel('Speed (mm/s)', fontsize=10)
    
    # Remove empty subplot
    fig.delaxes(axes[7])
    fig.delaxes(axes[8])
    
    plt.suptitle(f'{group_name} - Speed Profiles by Escape Type', fontsize=16, y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(save_path + '/' + experiment_name + '_escape_speed_profiles.png', 
                bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print summary
    print("\n=== Escape Type Summary ===")
    for etype, label in escape_types.items():
        print(f"{label}: {escape_counts[etype]} occurrences")


# Call the function
plot_escape_speed_profiles(all_flies_data_with_looms, group1_label, plot_path, 
                          frames_before=120, frames_after=120, frame_rate=60)
#%%
'''#removing this here because at the moment I don't want behaviours to be mutally excluding!
# for i in range(len(df_all)): 
#     if df_all.loc[i,'esc_jump']==1: #=> jumping is ovveriding everything!
#         df_all.loc[i,'esc_run']=0
#         df_all.loc[i,'esc_mean_vel']=0
#         df_all.loc[i,'esc_turn']=0
#         df_all.loc[i,'esc_freeze']=0 # can flies jump and then freeze? Which escape is counted?
  
#     elif df_all.loc[i,'esc_run']==1: #=> running is ovveriding freezing!
#         df_all.loc[i,'esc_freeze']=0


# df_all.loc[(df_all['esc_run']==1) & (df_all['esc_turn']==1), ['turn_run', 'esc_run', 'esc_turn']]=[1,0,0] #if flies is in an escape turn and in a escape_run she will be categorized as turn run!


# col_lst = ['esc_turn', 'esc_jump', 'esc_run', 'esc_freeze','esc_mean_vel']
# df_all['esc_none'] = df_all[col_lst].sum(axis=1)
# for i in range(len(df_all)):
#     if df_all.loc[i,'esc_none']==0:
#         df_all.loc[i,'esc_none']=1 #if fly is not engaging in any of this behaviour (turn, jump, run, freeze): she is classified as non responder!
#     else:
#         df_all.loc[i,'esc_none']=0

# escape = ['esc_turn', 'esc_jump', 'esc_run']
# df_all['escape'] = df_all[escape].sum(axis=1)
# for i in range(len(df_all)):
#     if df_all.loc[i,'escape']>0:
#         df_all.loc[i,'escape']=1
#     else:
#         df_all.loc[i,'escape']=0
'''
#%%
#df_grouped = df_all.groupby('index').mean() #all rows in df_all that have the same value in the 'index' column (which represent looms) are put into the same group and the mean is calculated
#df_grouped['loom'] = range(len(df_grouped)) #groupby('index') → groups rows by loom. .mean() → computes the fraction of flies engaging in this behaviours per loom.
#%%
'''
def plot_escape(group,raw_group, group_name):
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
           
    #of the escapes, what is the distribution between turn, run and jump? (only escapes included, not freezing)
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

'''