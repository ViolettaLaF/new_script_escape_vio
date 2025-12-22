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


def data_polar_all_flies(path, group_name, all_flies_data_with_looms):
    """
    Extract orientation before and after Turn bouts from all flies pooled together.
    """
    all_heading_before = []
    all_heading_after = []
    all_heading_diff = []
    
    # Loop through each fly's data
    for df_try, loom_onset in all_flies_data_with_looms:
        for i in range(len(loom_onset)):
            # Get the window from loom onset to 120 frames after
            window_start = loom_onset[i]
            window_end = loom_onset[i] + 120
            
            # Create a subset dataframe for this window
            df_window = df_try.loc[window_start:window_end].copy()
            
            # Identify turn bouts in this window
            turn_bouts = identify_behavior_bouts(df_window, behavior_label='Floor_Turn')
            
            # For each turn bout, get orientation before and after
            for bout in turn_bouts:
                bout_start = bout['start']
                bout_end = bout['end']
                
                # Get orientation before the bout starts (e.g., 1 frames before)
                if bout_start >= 1:
                    heading_before = df_try.loc[bout_start - 3, 'Orientation'] #'orientation_smooth' - DECIDED THAT IS BETTER NO SMOOTH (a lot of nan and nature of 0-360 problem)
                    
                    # Get orientation after the bout ends (e.g., 1 frames after)
                    if bout_end + 1 < len(df_try):
                        heading_after = df_try.loc[bout_end + 3, 'Orientation']
                        
                        all_heading_before.append(heading_before)
                        all_heading_after.append(heading_after)
                        
                        # Calculate the difference
                        heading_diff = heading_after - heading_before
                        all_heading_diff.append(heading_diff)
    
    # Create dataframe
    df_group_polar = pd.DataFrame({
        'all_heading_before': all_heading_before,
        'all_heading_after': all_heading_after,
        'all_heading_diff': all_heading_diff
    })
    
    return df_group_polar

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
def plot_polar(path, group_name, all_flies_data_with_looms):
    df_group_polar = data_polar_all_flies(path, group_name, all_flies_data_with_looms)
    #save_path = path + '/plots/'
    save_path = path 
    
    # Plot heading before
    degrees_before = df_group_polar['all_heading_before']
    bin_size = 20
    a_bef, b = np.histogram(degrees_before, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1])
    
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_bef, width=np.deg2rad(bin_size), bottom=0.0, color='yellow', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name + ': heading before')
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_polar_before_Floor_Turn.jpeg', bbox_inches='tight', dpi=1800)
    plt.show()    

    # Plot heading after
    degrees_after = df_group_polar['all_heading_after']
    a_aft, b = np.histogram(degrees_after, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1]) 
    
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_aft, width=np.deg2rad(bin_size), bottom=0.0, color='blue', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name + ': heading after')
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_polar_after_Floor_Turn.jpeg', bbox_inches='tight', dpi=1800)
    plt.show()    

    # Normalize angles to ±180°
    df_group_polar['degrees_diff'] = df_group_polar['all_heading_diff']
    for i in range(len(df_group_polar)):
        if df_group_polar.loc[i, 'all_heading_diff'] > 180:            
            angle = df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff'] = 360 - angle
        elif df_group_polar.loc[i, 'all_heading_diff'] < -180:
            angle = df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff'] = (angle + 360) * -1
    
    # Classify turns based on screen at 0°
    # If screen is at 0°, turning away means the fly's heading after the turn should be further from 0°
    # We need to check if the turn brings the fly closer to 0° (towards) or further from 0° (away)
    
    df_group_polar['away from screen'] = 'away from screen'
    
    for i in range(len(df_group_polar)):
        heading_before = df_group_polar.loc[i, 'all_heading_before']
        heading_after = df_group_polar.loc[i, 'all_heading_after']
        
        # Calculate angular distance from screen (0°) before and after
        # Angular distance considering wrap-around (so possible minimum angle, es: a 270 turn is considered a 90 turn)
        dist_before = min(abs(heading_before - 0), 360 - abs(heading_before - 0))
        dist_after = min(abs(heading_after - 0), 360 - abs(heading_after - 0))
        
        # If distance increased, fly turned away; if decreased, fly turned towards
        if dist_after < dist_before:
            df_group_polar.loc[i, 'away from screen'] = 'towards screen'
    
    df_group_polar['flies'] = 'fly'

    # Violin/strip plot
    hue_order = ["away from screen", "towards screen"]
    fig, ax = plt.subplots(figsize=(8,6))
    
    sns.violinplot(
        y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, 
        data=df_group_polar, split=True, inner=None, cut=0, linewidth=1.2, 
        palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    
    # Make violin edges opaque and fill faint
    for col in ax.collections:
        if isinstance(col, PolyCollection):
            fc = col.get_facecolor()[0]
            col.set_facecolor((fc[0], fc[1], fc[2], 0.1))
            col.set_edgecolor((fc[0], fc[1], fc[2], 0.4))
            col.set_linewidth(1)
    
    sns.stripplot(
        y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, 
        data=df_group_polar, dodge=True, jitter=True, size=5, marker='o', 
        linewidth=0.8, palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    
    # Make stripplot points hollow
    for col in ax.collections:
        if isinstance(col, PathCollection):
            fc = col.get_facecolors()
            if fc.size != 0:
                col.set_edgecolors(fc)
                col.set_facecolors('none')
                col.set_linewidth(0.8)
    
    # Custom legend
    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markeredgecolor="blue", 
               markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='away from screen'),
        Line2D([0], [0], marker='o', color='none', markeredgecolor="orange", 
               markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='towards screen')
    ]
    ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(0.6, 0.8))
    
    ax.set_title(group_name + ': magnitude of Turn')
    ax.set_ylabel('degrees')
    ax.set_xlabel("")
    ax.set_xticklabels([])
    sns.despine()
    
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_scatter_violin_hollow_outline_Floor_Turn.jpeg',
                bbox_inches='tight', dpi=1800)
    plt.show()
    
#%%
def plot_polar_fake_loom(path, group_name, all_flies_data_with_fake_looms):
    df_group_polar = data_polar_all_flies(path, group_name, all_flies_data_with_fake_looms)
    #save_path = path + '/plots/'
    save_path = path 
    
    # Plot heading before
    degrees_before = df_group_polar['all_heading_before']
    bin_size = 20
    a_bef, b = np.histogram(degrees_before, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1])
    
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_bef, width=np.deg2rad(bin_size), bottom=0.0, color='yellow', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name + ': heading before')
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_polar_before_fake_Floor_Turn.jpeg', bbox_inches='tight', dpi=1800)
    plt.show()    

    # Plot heading after
    degrees_after = df_group_polar['all_heading_after']
    a_aft, b = np.histogram(degrees_after, bins=np.arange(0, 360+bin_size, bin_size))
    centers = np.deg2rad(np.ediff1d(b)//2 + b[:-1]) 
    
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='polar')
    ax.bar(centers, a_aft, width=np.deg2rad(bin_size), bottom=0.0, color='blue', edgecolor='k', alpha=0.6)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    ax.set_title(group_name + ': heading after')
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_polar_after_fake_Turn.jpeg', bbox_inches='tight', dpi=1800)
    plt.show()    

    # Normalize angles to ±180°
    df_group_polar['degrees_diff'] = df_group_polar['all_heading_diff']
    for i in range(len(df_group_polar)):
        if df_group_polar.loc[i, 'all_heading_diff'] > 180:            
            angle = df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff'] = 360 - angle
        elif df_group_polar.loc[i, 'all_heading_diff'] < -180:
            angle = df_group_polar.loc[i, 'all_heading_diff']
            df_group_polar.loc[i, 'degrees_diff'] = (angle + 360) * -1
    
    # Classify turns based on screen at 0°
    # If screen is at 0°, turning away means the fly's heading after the turn should be further from 0°
    # We need to check if the turn brings the fly closer to 0° (towards) or further from 0° (away)
    
    df_group_polar['away from screen'] = 'away from screen'
    
    for i in range(len(df_group_polar)):
        heading_before = df_group_polar.loc[i, 'all_heading_before']
        heading_after = df_group_polar.loc[i, 'all_heading_after']
        
        # Calculate angular distance from screen (0°) before and after
        # Angular distance considering wrap-around (so possible minimum angle, es: a 270 turn is considered a 90 turn)
        dist_before = min(abs(heading_before - 0), 360 - abs(heading_before - 0))
        dist_after = min(abs(heading_after - 0), 360 - abs(heading_after - 0))
        
        # If distance increased, fly turned away; if decreased, fly turned towards
        if dist_after < dist_before:
            df_group_polar.loc[i, 'away from screen'] = 'towards screen'
    
    df_group_polar['flies'] = 'fly'

    # Violin/strip plot
    hue_order = ["away from screen", "towards screen"]
    fig, ax = plt.subplots(figsize=(8,6))
    
    sns.violinplot(
        y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, 
        data=df_group_polar, split=True, inner=None, cut=0, linewidth=1.2, 
        palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    
    # Make violin edges opaque and fill faint
    for col in ax.collections:
        if isinstance(col, PolyCollection):
            fc = col.get_facecolor()[0]
            col.set_facecolor((fc[0], fc[1], fc[2], 0.1))
            col.set_edgecolor((fc[0], fc[1], fc[2], 0.4))
            col.set_linewidth(1)
    
    sns.stripplot(
        y='degrees_diff', x='flies', hue='away from screen', hue_order=hue_order, 
        data=df_group_polar, dodge=True, jitter=True, size=5, marker='o', 
        linewidth=0.8, palette={"away from screen": "blue", "towards screen": "orange"}, ax=ax)
    
    # Make stripplot points hollow
    for col in ax.collections:
        if isinstance(col, PathCollection):
            fc = col.get_facecolors()
            if fc.size != 0:
                col.set_edgecolors(fc)
                col.set_facecolors('none')
                col.set_linewidth(0.8)
    
    # Custom legend
    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markeredgecolor="blue", 
               markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='away from screen'),
        Line2D([0], [0], marker='o', color='none', markeredgecolor="orange", 
               markerfacecolor='none', markersize=8, markeredgewidth=1.2, label='towards screen')
    ]
    ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(0.6, 0.8))
    
    ax.set_title(group_name + ': magnitude of Turn')
    ax.set_ylabel('degrees')
    ax.set_xlabel("")
    ax.set_xticklabels([])
    sns.despine()
    
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_scatter_violin_hollow_outline_fake_Turn.jpeg',
                bbox_inches='tight', dpi=1800)
    plt.show()  
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
def plot_turn_spatial_distribution(all_flies_data_with_looms, baseline_frames, arena_raggio, arena_center_x, arena_center_y, group_name, save_path, behavior_label='Turn'):
    """
    Plot the spatial distribution of turn bouts on the arena for baseline and stimulation periods.
    
    Parameters:
    -----------
    all_flies_data_with_looms : list of tuples
        Each tuple contains (df_try, loom_onset)
    baseline_frames : int
        Number of frames in baseline period
    arena_raggio : float
        Arena radius in mm
    arena_center_x : float
        Arena center X coordinate in mm
    arena_center_y : float
        Arena center Y coordinate in mm
    group_name : str
        Name of the group for plot title
    save_path : str
        Path to save the plots
    behavior_label : str
        The behavior to analyze (default 'Turn')
    """
    
    # Collect turn bout positions
    baseline_x = []
    baseline_y = []
    stimulation_x = []
    stimulation_y = []
    
    for df_try, _ in all_flies_data_with_looms:
        # Baseline period
        df_baseline = df_try.loc[df_try.index < baseline_frames].copy()
        baseline_bouts = identify_behavior_bouts(df_baseline, behavior_label=behavior_label)
        
        for bout in baseline_bouts:
            # Get position at the start of the bout
            bout_start = bout['start']
            if bout_start in df_try.index:
                baseline_x.append(df_try.loc[bout_start, 'Position_X'])
                baseline_y.append(df_try.loc[bout_start, 'Position_Y'])
        
        # Stimulation period
        df_stimulation = df_try.loc[df_try.index >= baseline_frames].copy()
        stimulation_bouts = identify_behavior_bouts(df_stimulation, behavior_label=behavior_label)
        
        for bout in stimulation_bouts:
            bout_start = bout['start']
            if bout_start in df_try.index:
                stimulation_x.append(df_try.loc[bout_start, 'Position_X'])
                stimulation_y.append(df_try.loc[bout_start, 'Position_Y'])
    
    # Create figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Draw arena circle for both plots
    for ax, title, x_data, y_data, color in zip(
        axes, 
        ['Baseline', 'Stimulation'],
        [baseline_x, stimulation_x],
        [baseline_y, stimulation_y],
        ['blue', 'orange']
    ):
        # Draw arena boundary
        circle = plt.Circle((arena_center_x, arena_center_y), arena_raggio, 
                           color='black', fill=False, linewidth=2)
        ax.add_patch(circle)
        
        # Plot turn positions
        ax.scatter(x_data, y_data, c=color, alpha=0.5, s=20, edgecolors='black', linewidth=0.5)
        
        # Set equal aspect ratio and limits
        ax.set_aspect('equal')
        ax.set_xlim(arena_center_x - arena_raggio - 2, arena_center_x + arena_raggio + 2)
        ax.set_ylim(arena_center_y - arena_raggio - 2, arena_center_y + arena_raggio + 2)
        
        # Labels and title
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.set_title(f'{group_name} - {title}\nTurn Bouts (n={len(x_data)})')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_turn_spatial_distribution_Turn.jpeg', bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print summary
    print(f"Baseline turn bouts: {len(baseline_x)}")
    print(f"Stimulation turn bouts: {len(stimulation_x)}")


# Usage:
#plot_turn_spatial_distribution(all_flies_data_with_looms, baseline_frames, arena_raggio, arena_center_x, arena_center_y,  group1_label, plot_path, behavior_label='Turn')

   #%% 
def plot_turn_spatial_loom_with_orientation(all_flies_data_with_looms, group_name, save_path, behavior_label='Turn'): #real loom 
    """
    Plot the spatial distribution of turn bouts during loom windows with orientation arrows.
    Shows orientation before (red) and after (green) each turn bout.
    
    Parameters:
    -----------
    all_flies_data_with_looms : list of tuples
        Each tuple contains (df_try, loom_onset)
    group_name : str
        Name of the group for plot title
    save_path : str
        Path to save the plots
    behavior_label : str
        The behavior to analyze (default 'Turn')
    """
    
    # Collect turn bout data during loom windows
    positions_x = []
    positions_y = []
    orientations_before = []
    orientations_after = []
    
    for df_try, loom_onset in all_flies_data_with_looms:
        for i in range(len(loom_onset)):
            # Get the window from loom onset to 120 frames after
            window_start = loom_onset[i]
            window_end = loom_onset[i] + 120
            
            # Create a subset dataframe for this window
            df_window = df_try.loc[window_start:window_end].copy()
            
            # Identify turn bouts in this window
            turn_bouts = identify_behavior_bouts(df_window, behavior_label=behavior_label)
            
            # For each turn bout, get position and orientation
            for bout in turn_bouts:
                bout_start = bout['start']
                bout_end = bout['end']
                
                # Get position at the start of the bout
                if bout_start in df_try.index:
                    positions_x.append(df_try.loc[bout_start, 'Position_X'])
                    positions_y.append(df_try.loc[bout_start, 'Position_Y'])
                    
                    # Get orientation before the bout (1 frame before)
                    if bout_start - 1 >= 0 and bout_start - 1 in df_try.index:
                        orientations_before.append(df_try.loc[bout_start - 1, 'Orientation'])
                    else:
                        # If we can't get 1 frame before, use the start frame
                        orientations_before.append(df_try.loc[bout_start, 'Orientation'])
                    
                    # Get orientation after the bout (1 frame after)
                    if bout_end + 1 < len(df_try) and bout_end + 1 in df_try.index:
                        orientations_after.append(df_try.loc[bout_end + 1, 'Orientation'])
                    else:
                        # If we can't get 1 frame after, use the end frame
                        orientations_after.append(df_try.loc[bout_end, 'Orientation'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Draw arena boundary
    circle = plt.Circle((arena_center_x, arena_center_y), arena_raggio, 
                       color='black', fill=False, linewidth=2)
    ax.add_patch(circle)
    
    # Arrow length (adjust as needed)
    arrow_length = 1.5  # in mm
    
    # Plot each turn bout with orientation arrows
    for x, y, ori_before, ori_after in zip(positions_x, positions_y, orientations_before, orientations_after):
        # Convert orientation from degrees to radians
        angle_before_rad = np.deg2rad(ori_before - 90) # Subtract 90 to convert back to math convention where 0° = East
        angle_after_rad = np.deg2rad(ori_after - 90) # Subtract 90 to convert back to math convention where 0° = East
        
                # Calculate arrow endpoints
        #arrow before
        dx_before = arrow_length * np.cos(angle_before_rad)
        dy_before = -arrow_length * np.sin(angle_before_rad)  # Negative because of how you calculated dy
        
        ax.arrow(x, y, dx_before, dy_before,  
                head_width=0.5, head_length=0.3, fc='red', ec='red', 
                alpha=0.7, linewidth=1.5, zorder=3)
        #arrow after
        dx_after = arrow_length * np.cos(angle_after_rad)
        dy_after = -arrow_length * np.sin(angle_after_rad)  # Negative because of how you calculated dy
        
        ax.arrow(x, y, dx_after, dy_after, 
                head_width=0.5, head_length=0.3, fc='green', ec='green', 
                alpha=0.7, linewidth=1.5, zorder=4)
        
        # Mark the position with a small dot
        ax.scatter(x, y, c='black', s=10, zorder=5)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    ax.set_xlim(arena_center_x - arena_raggio - 2, arena_center_x + arena_raggio + 2)
    ax.set_ylim(arena_center_y - arena_raggio - 2, arena_center_y + arena_raggio + 2)
    
    # Labels and title
    ax.set_xlabel('X Position (mm)', fontsize=12)
    ax.set_ylabel('Y Position (mm)', fontsize=12)
    ax.set_title(f'{group_name} - Turn Bouts During Loom Windows\n(n={len(positions_x)} turns)', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=8, label='Turn position'),
        Line2D([0], [0], color='red', linewidth=2, label='Orientation before turn'),
        Line2D([0], [0], color='green', linewidth=2, label='Orientation after turn')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(plot_path+"/"+str(experiment_name)+ 'Floor_Turn_loom_orientation.jpeg', bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print summary
    print(f"Total turn bouts during loom windows: {len(positions_x)}")


def plot_turn_spatial_fake_loom_with_orientation(all_flies_data_with_fake_looms, group_name, save_path, behavior_label='Turn'): #fake loom 
    """
    Plot the spatial distribution of turn bouts during loom windows with orientation arrows.
    Shows orientation before (red) and after (green) each turn bout.
    
    Parameters:
    -----------
    all_flies_data_with_looms : list of tuples
        Each tuple contains (df_try, loom_onset)
    group_name : str
        Name of the group for plot title
    save_path : str
        Path to save the plots
    behavior_label : str
        The behavior to analyze (default 'Turn')
    """
    
    # Collect turn bout data during loom windows
    positions_x = []
    positions_y = []
    orientations_before = []
    orientations_after = []
    
    for df_try, loom_onset in all_flies_data_with_fake_looms:
        for i in range(len(loom_onset)):
            # Get the window from loom onset to 120 frames after
            window_start = loom_onset[i] 
            window_end = loom_onset[i] + 120
            
            # Create a subset dataframe for this window
            df_window = df_try.loc[window_start:window_end].copy()
            
            # Identify turn bouts in this window
            turn_bouts = identify_behavior_bouts(df_window, behavior_label=behavior_label)
            
            # For each turn bout, get position and orientation
            for bout in turn_bouts:
                bout_start = bout['start']
                bout_end = bout['end']
                
                # Get position at the start of the bout
                if bout_start in df_try.index:
                    positions_x.append(df_try.loc[bout_start, 'Position_X'])
                    positions_y.append(df_try.loc[bout_start, 'Position_Y'])
                    
                    # Get orientation before the bout (1 frame before)
                    if bout_start - 1 >= 0 and bout_start - 1 in df_try.index:
                        orientations_before.append(df_try.loc[bout_start - 1, 'Orientation'])
                    else:
                        # If we can't get 1 frame before, use the start frame
                        orientations_before.append(df_try.loc[bout_start, 'Orientation'])
                    
                    # Get orientation after the bout (1 frame after)
                    if bout_end + 1 < len(df_try) and bout_end + 1 in df_try.index:
                        orientations_after.append(df_try.loc[bout_end + 1, 'Orientation'])
                    else:
                        # If we can't get 1 frame after, use the end frame
                        orientations_after.append(df_try.loc[bout_end, 'Orientation'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Draw arena boundary
    circle = plt.Circle((arena_center_x, arena_center_y), arena_raggio, 
                       color='black', fill=False, linewidth=2)
    ax.add_patch(circle)
    
    # Arrow length (adjust as needed)
    arrow_length = 1.5  # in mm
    
    # Plot each turn bout with orientation arrows
    for x, y, ori_before, ori_after in zip(positions_x, positions_y, orientations_before, orientations_after):
        # Convert orientation from degrees to radians
        angle_before_rad = np.deg2rad(ori_before - 90) # Subtract 90 to convert back to math convention where 0° = East
        angle_after_rad = np.deg2rad(ori_after - 90) # Subtract 90 to convert back to math convention where 0° = East
        
                # Calculate arrow endpoints
        #arrow before
        dx_before = arrow_length * np.cos(angle_before_rad)
        dy_before = -arrow_length * np.sin(angle_before_rad)  # Negative because of how you calculated dy
        
        ax.arrow(x, y, dx_before, dy_before,  
                head_width=0.5, head_length=0.3, fc='red', ec='red', 
                alpha=0.7, linewidth=1.5, zorder=3)
        #arrow after
        dx_after = arrow_length * np.cos(angle_after_rad)
        dy_after = -arrow_length * np.sin(angle_after_rad)  # Negative because of how you calculated dy
        
        ax.arrow(x, y, dx_after, dy_after, 
                head_width=0.5, head_length=0.3, fc='green', ec='green', 
                alpha=0.7, linewidth=1.5, zorder=4)
        
        # Mark the position with a small dot
        ax.scatter(x, y, c='black', s=10, zorder=5)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    ax.set_xlim(arena_center_x - arena_raggio - 2, arena_center_x + arena_raggio + 2)
    ax.set_ylim(arena_center_y - arena_raggio - 2, arena_center_y + arena_raggio + 2)
    
    # Labels and title
    ax.set_xlabel('X Position (mm)', fontsize=12)
    ax.set_ylabel('Y Position (mm)', fontsize=12)
    ax.set_title(f'{group_name} - Turn Bouts During fake Loom Windows\n(n={len(positions_x)} turns)', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=8, label='Turn position'),
        Line2D([0], [0], color='red', linewidth=2, label='Orientation before turn'),
        Line2D([0], [0], color='green', linewidth=2, label='Orientation after turn')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(plot_path+"/"+str(experiment_name)+ '_Turn_fake_loom_orientation.jpeg', bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print summary
    print(f"Total turn bouts during fake loom windows: {len(positions_x)}")

# Usage:
#plot_turn_spatial_loom_with_orientation(all_flies_data_with_looms, group1_label, plot_path, behavior_label='Floor_Turn')  #real loom #'Floor_Turn'
#plot_turn_spatial_fake_loom_with_orientation(all_flies_data_with_fake_looms, group1_label, plot_path, behavior_label='Turn')  #fake loom but remember to change title and name of fig in the function   
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
#%%
def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files') #select folder called "classified_pose"
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
all_flies_data_with_fake_looms = [] #is a list of tupla: with the df_try and an array with fake loom onset (same inter loom interval but during baseline) for every fly!
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
    loom_onset_fake = loom_onset - baseline_frames    
    df_try = simplify_behaviors(df_try) #simplify Matheus original behaviour (they are too many, impossible to understand anything)   
    all_flies_data_with_looms.append((df_try, loom_onset))  # Store as tuple of (dataframe, loom_onsets) 
    #all_flies_data_with_fake_looms.append((df_try, loom_onset_fake))  # Store as tuple of (dataframe, loom_onsets) 
#%%   
    df_try['esc_turn'] = 0
    df_try['esc_run'] = 0
    df_try['esc_jump'] = 0
    df_try['backwards'] = 0
    df_try['walk_away'] = 0
    df_try['escape'] = 0 #containing all form of escape: esc_turn, esc_run, esc_jump, backwards, 'walk_away'
    df_try['freeze'] = 0 # this before was called 'esc_freeze' contain freeze and resistent freeze
    df_try['walk_speed'] = np.nan
    df_try['speed2d'] = np.nan

    '''checking turns'''
    heading_x_before = []
    heading_y_before = []
    heading_x_after = []
    heading_y_after = []
      
    df_try.loc[(df_try['Charlie_Behavior'] == 'Walk'), 'walk_speed'] = df_try['Speed'] #walking velocity
    df_try.loc[(df_try['Speed'] < jump_velocity), 'speed2d'] = df_try['Speed'] #velocity excluding jump speed     
        #%% CLEAN VELOCITY DATA: REMOVE JUMPS AND SMOOTH - it will be inportant for esc_run! 
    # Step 1: Create a cleaned velocity column (remove jumps)
    df_try['walk_velocity_clean'] = df_try['walk_speed'].copy()
    #df_try['orientation_clean'] = df_try['Orientation'].copy()    
    # Mark frames with jumps as NaN
    df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'walk_velocity_clean'] = np.nan
    #df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'orientation_clean'] = np.nan    
    # Also remove frames right before and after jump (they're often artifacts) #now removing 6 frames before and after
    for idx in df_try[df_try['Charlie_Behavior'] == 'Jump'].index:
        if idx >= 6:
            df_try.loc[idx-6:idx-1, 'walk_velocity_clean'] = np.nan
            #df_try.loc[idx-6:idx-1, 'orientation_clean'] = np.nan
        if idx <= len(df_try) - 7:
            df_try.loc[idx+1:idx+6, 'walk_velocity_clean'] = np.nan
            #df_try.loc[idx+1:idx+6, 'orientation_clean'] = np.nan    
    # Step 2: Apply running average (7 frames) - NaNs will be skipped
    df_try['velocity_smooth'] = df_try['walk_velocity_clean'].rolling(window=7, center=True, min_periods=1).mean()
    #df_try['orientation_smooth'] = df_try['orientation_clean'].rolling(window=7, center=True, min_periods=1).mean()       
 #%%
    '''checking jumps, freeze, backwards'''
    for i in range(len(loom_onset)):
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Jump').sum() > 0:
            df_try.loc[loom_offset[i], 'esc_jump'] = 1
     
        elif ((df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Freeze') | 
              (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Resistant_Freeze')).sum() > 0:
            df_try.loc[loom_offset[i], 'freeze'] = 1
            
        elif (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Backwards_Walk').sum() > 0:
            df_try.loc[loom_offset[i], 'backwards'] = 1
 #%%  commenting just because I don't need right now but is correct!          
#plot_polar(exp_path, group1_label, all_flies_data_with_looms)
#plot_polar_fake_loom(exp_path, group1_label, all_flies_data_with_fake_looms)

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


# Example filter functions
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
 #%%
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


# COMPLETE EXAMPLE - ADD THIS TO YOUR CODE:

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


 #%% ETOGRAMME WITH LOOM SIDE BY SIDE (YOU CAN SELECT THE n OF LOOM THAT YOU WANT AND THE SIZE OF THE WINDOW) - work well

def create_ethogram_data(all_flies_data_with_looms, variable, loom_indices, 
                         frames_before=60, frames_after=60, combine_looms=True):
    """
    Create ethogram data matrix for plotting.
    
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
    combine_looms : bool
        If True, combines all looms into one continuous trace per fly
        
    Returns:
    --------
    pd.DataFrame : Matrix with flies as rows and time as columns
    """
    all_fly_data = []
    
    for fly_idx, (df_try, loom_onset) in enumerate(all_flies_data_with_looms):
        fly_traces = []
        
        for loom_idx in loom_indices:
            if loom_idx < len(loom_onset):
                loom_start = loom_onset[loom_idx]
                window_start = loom_start - frames_before
                window_end = loom_start + frames_after
                
                # Extract data for this window
                if window_start >= 0 and window_end < len(df_try):
                    trace = df_try.loc[window_start:window_end, variable].values
                    fly_traces.extend(trace)
                else:
                    # Pad with NaN if window extends beyond data
                    trace = [np.nan] * (frames_before + frames_after + 1)
                    fly_traces.extend(trace)
        
        all_fly_data.append(fly_traces)
    
    # Create DataFrame
    n_frames_per_loom = frames_before + frames_after + 1
    total_frames = n_frames_per_loom * len(loom_indices)
    
    df_ethogram = pd.DataFrame(all_fly_data, 
                               columns=[f'frame_{i}' for i in range(total_frames)])
    df_ethogram.index.name = 'fly'
    
    return df_ethogram


def plot_ethogram_raster(ethogram_data, variable, group_name, loom_indices,
                         frames_before=60, frames_after=60, frame_rate=60, 
                         loom_duration_frames=30,
                         cbar=True, figsize=None, save_path=None):
    """
    Plot ethogram raster with flexible variable types.
    
    Parameters:
    -----------
    ethogram_data : pd.DataFrame
        Matrix with flies as rows and time as columns
    variable : str
        Variable name being plotted
    group_name : str
        Name for the plot title
    loom_indices : list
        Which looms are included
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
    # Auto-calculate figure size if not provided
    if figsize is None:
        n_flies = len(ethogram_data)
        n_frames = len(ethogram_data.columns)
        # Width based on time, height based on number of flies
        width = max(12, n_frames / 50)  # Adjust divisor to control width
        height = max(8, n_flies / 10)   # Adjust divisor to control height
        figsize = (width, height)
    
    fig, ax = plt.subplots(figsize=figsize)
    
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
        plt.legend(handles=legend_handles, bbox_to_anchor=(1.15, 1), 
                  loc='upper left', title=variable, fontsize=10)
    
    # Add vertical lines at loom onsets and offsets
    n_frames_per_loom = frames_before + frames_after + 1
    for i, loom_idx in enumerate(loom_indices):
        # Loom onset position
        loom_onset_frame = i * n_frames_per_loom + frames_before
        ax.axvline(x=loom_onset_frame, color='black', linewidth=2, linestyle='-', alpha=0.8)
        
        # Loom offset position
        loom_offset_frame = loom_onset_frame + loom_duration_frames
        ax.axvline(x=loom_offset_frame, color='black', linewidth=2, linestyle='-', alpha=0.8)
        
        # Add text label at top
        ax.text(loom_onset_frame, -0.5, f'Loom {loom_idx+1}', 
               ha='center', va='top', fontsize=10, fontweight='bold')
    
    # Set up x-axis (time)
    n_frames_per_loom = frames_before + frames_after + 1
    x_ticks = []
    x_labels = []
    
    for i, loom_idx in enumerate(loom_indices):
        # Loom onset position
        loom_onset_frame = i * n_frames_per_loom + frames_before
        
        # Add ticks: start of window, loom onset, loom offset, end of window
        # Start of window
        x_ticks.append(i * n_frames_per_loom)
        x_labels.append(f'-{frames_before/frame_rate:.1f}s')
        
        # Loom onset
        x_ticks.append(loom_onset_frame)
        x_labels.append('ON')
        
        # Loom offset
        loom_offset_frame = loom_onset_frame + loom_duration_frames
        x_ticks.append(loom_offset_frame)
        x_labels.append('OFF')
        
        # End of window
        x_ticks.append((i + 1) * n_frames_per_loom - 1)
        x_labels.append(f'+{frames_after/frame_rate:.1f}s')
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=9)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Fly ID', fontsize=12)
    
    # Show y-axis with fly numbers
    ax.yaxis.set_visible(True)
    fly_ticks = np.arange(0, len(ethogram_data), max(1, len(ethogram_data)//20))  # Show max 20 ticks
    ax.set_yticks(fly_ticks + 0.5)
    ax.set_yticklabels(fly_ticks, fontsize=8)
    
    # Title
    title = f'{group_name} - {variable}\n(Looms {loom_indices[0]+1} to {loom_indices[-1]+1})'
    ax.set_title(title, fontsize=14, pad=20)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show() 
 
# Create ethograms for the same looms with different variables
loom_indices = list(range(5))  # First 5 looms
frames_before = 120  # 2 seconds before
frames_after = 120   # 2 seconds after
loom_duration_frames = 30  # 0.5 seconds loom duration

# Behavior ethogram
ethogram_behavior = create_ethogram_data(
    all_flies_data_with_looms, 'Charlie_Behavior',
    loom_indices, frames_before, frames_after
)

plot_ethogram_raster(ethogram_behavior, 'Charlie_Behavior', group1_label,
                     loom_indices, frames_before, frames_after, frame_rate,
                     loom_duration_frames=loom_duration_frames,
                     save_path=plot_path + '/ethogram_behavior_loom.jpeg')

# Speed ethogram - same flies, same positions!
ethogram_speed = create_ethogram_data(
    all_flies_data_with_looms, 'Speed',
    loom_indices, frames_before, frames_after
)

plot_ethogram_raster(ethogram_speed, 'Speed', group1_label,
                     loom_indices, frames_before, frames_after, frame_rate,
                     loom_duration_frames=loom_duration_frames,
                     save_path=plot_path + '/ethogram_speed_loom.jpeg') 
#%% 
"""        
    for loom in range(len(df_try)):    
        if loom in loom_onset:
            if df_try.loc[loom,'freeze_bout'] == 1: #excluding freezing to calculate heading!! I don't need all of this now!!
                x_before = 'nan'
                y_before = 'nan'
            else:
                x_before = df_try.loc[loom,'fly_x_norm_mm'] - df_try.loc[loom-30,'fly_x_norm_mm']
                y_before = df_try.loc[loom,'fly_y_norm_mm'] - df_try.loc[loom-30,'fly_y_norm_mm']
            heading_x_before.append(x_before)
            heading_y_before.append(y_before)
    
        elif loom in loom_offset:
            if df_try.loc[loom:loom+30,'freeze_bout'].sum() >1:
                x_after = 'nan'
                y_after = 'nan'
            else:
                x_after = df_try.loc[loom+30,'fly_x_norm_mm'] - df_try.loc[loom,'fly_x_norm_mm']
                y_after = df_try.loc[loom+30,'fly_y_norm_mm'] - df_try.loc[loom,'fly_y_norm_mm']
            heading_x_after.append(x_after)
            heading_y_after.append(y_after)
    
    for i in range(len(heading_y_before)):
        if isinstance(heading_y_before[i], str) | isinstance(heading_y_after[i], str):
            continue
        elif (heading_y_before[i] > 0) & (heading_y_after[i] < 0):
            df_try.loc[loom_offset[i], 'esc_turn'] = 1       
"""
#%% Plot to visualize smoothing effect
""" 
        # Pick a random loom to visualize
    if len(loom_offset) > 0:
        test_loom = loom_offset[0]
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # Plot 1: Original velocity
        ax = axes[0]
        window_data = df_try.loc[test_loom-120:test_loom+600]
        time_points = np.arange(len(window_data)) / frame_rate - 2
        ax.plot(time_points, window_data['velocity'].values, 'k-', linewidth=1, alpha=0.5, label='Original')
        ax.scatter(time_points[window_data['jumps'].values == 1], 
                  window_data.loc[window_data['jumps'] == 1, 'velocity'].values,
                  color='red', s=50, zorder=5, label='Jumps')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_ylabel('Velocity (mm/sec)', fontsize=11)
        ax.set_title('Original Velocity with Jumps', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-2, 10)
        
        # Plot 2: Cleaned velocity (jumps removed)
        ax = axes[1]
        ax.plot(time_points, window_data['velocity_clean'].values, 'b-', linewidth=1, label='Cleaned (jumps removed)')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_ylabel('Velocity (mm/sec)', fontsize=11)
        ax.set_title('Cleaned Velocity (Jumps Removed)', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-2, 10)
        
        # Plot 3: Smoothed velocity
        ax = axes[2]
        ax.plot(time_points, window_data['velocity_smooth'].values, 'g-', linewidth=2, label='Smoothed (7-frame avg)')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_xlabel('Time relative to loom onset (sec)', fontsize=11)
        ax.set_ylabel('Velocity (mm/sec)', fontsize=11)
        ax.set_title('Final Smoothed Velocity', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-2, 10)
        
        plt.tight_layout()
        filename_base = filename.replace('_frames.csv', '')
        plt.savefig(plot_path + f'/velocity_smoothing_demo_{filename_base}.png', dpi=300, bbox_inches='tight')
        plt.savefig(plot_path_pdf + f'/velocity_smoothing_demo_{filename_base}.pdf', bbox_inches='tight')
        print(f"Saved: velocity_smoothing_demo_{filename_base}.png/pdf")
    
    #%% SLIDING WINDOW ANALYSIS FOR ESCAPE RUNNING
    '''checking running escape'''
    window_size_sec = 2
    window_size_frames = window_size_sec * frame_rate

    start_window_sec = 0.5
    end_window_sec = 1.5 #8 
    step_sec = 0.5
    step_frames = int(step_sec * frame_rate)

    window_starts_sec = np.arange(start_window_sec, end_window_sec + step_sec, step_sec)
    window_starts_frames = (window_starts_sec * frame_rate).astype(int)

    print(f"\n--- SLIDING WINDOW ANALYSIS FOR {filename} ---")
    print(f"Window size: {window_size_sec} sec ({window_size_frames} frames)")
    print(f"Testing windows from {start_window_sec}s to {end_window_sec}s after loom onset")
    print(f"Step size: {step_sec} sec ({step_frames} frames)")
    print(f"Total windows to test: {len(window_starts_sec)}\n")

    window_results = {}
    window_p_values = {}
    window_escape_runs = {}
    
    # Calculate baseline speed statistics 
    baseline_speed = df_try.loc[0:baseline_frames, 'velocity_smooth']
    baseline_mean = baseline_speed.mean()
    baseline_std = baseline_speed.std()
    speed_threshold = baseline_mean + baseline_std

    print(f"Baseline mean speed: {baseline_mean:.2f} mm/sec")
    print(f"Baseline std: {baseline_std:.2f} mm/sec")
    print(f"Speed threshold (mean + 1 SD): {speed_threshold:.2f} mm/sec")

    for window_idx, window_start_frames in enumerate(window_starts_frames):
        window_end_frames = window_start_frames + window_size_frames
        window_time_sec = window_starts_sec[window_idx]
        
        print(f"Testing window: {window_time_sec:.1f}s - {window_time_sec + window_size_sec:.1f}s after loom onset")
        
        df_try_window = df_try.copy()
        df_try_window['esc_run_window'] = 0
        p_values_per_loom = []
        escape_runs_per_loom = []
        
        for loom in range(len(loom_onset)):
            window_post_start = loom_offset[loom] + window_start_frames
            window_post_end = loom_offset[loom] + window_end_frames
            
            permutated_pre = df_try_window.loc[loom_onset[loom]-120:(loom_onset[loom]), 'velocity_smooth']
            permutated_post = df_try_window.loc[window_post_start:window_post_end, 'velocity_smooth']
            
            if len(permutated_pre) < 30 or len(permutated_post) < 30:
                p_values_per_loom.append(np.nan)
                escape_runs_per_loom.append(0)
                continue
            
            train_pre = []
            train_post = []
            
            for perm in range(1000): #1000
                df_sample_pre = permutated_pre.sample(n=30, replace=True)
                row_pre = df_sample_pre.mean(axis=0)
                train_pre.append(row_pre)
                
                df_sample_post = permutated_post.sample(n=30, replace=True)
                row_post = df_sample_post.mean(axis=0)
                train_post.append(row_post)
            
            post_loom_mean_speed = permutated_post.mean()
            
            t, p = ttest_ind(train_pre, train_post, alternative='less')
            p_values_per_loom.append(p)
            
            if (p < 0.05) & (post_loom_mean_speed > speed_threshold):
                # NEW: Check if there was a jump in the window
                has_jump = df_try_window.loc[loom_onset[loom]:(loom_offset[loom]+window_end_frames), 'jumps'].sum() > 0
                            
                if not has_jump:  # Only classify as escape if no jump
                    df_try_window.loc[loom_offset[loom], 'esc_run_window'] = 1
                    escape_runs_per_loom.append(1)
                else:
                    escape_runs_per_loom.append(0)
            else:
                escape_runs_per_loom.append(0)
        
        window_key = f"{window_time_sec:.1f}s"
        window_results[window_key] = df_try_window.copy()
        window_p_values[window_key] = p_values_per_loom
        window_escape_runs[window_key] = escape_runs_per_loom
        
        n_escapes = sum(escape_runs_per_loom)
        print(f"  → Escape runs detected: {n_escapes} / {len(loom_onset)}")
        p_sig = [p for p in p_values_per_loom if p < 0.05 and not np.isnan(p)]
        if p_sig:
            print(f"  → Mean p-value (significant only): {np.mean(p_sig):.4f}\n")
        else:
            print(f"  → No significant p-values\n")

    #%% MODIFICATION 1: PLOT SPEED PROFILES TO 10 SECONDS
    windows_to_plot = ['0.5s', '2.0s', '4.0s', '8.0s']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for plot_idx, window_key in enumerate(windows_to_plot):
        if window_key not in window_results:
            continue
        
        ax = axes[plot_idx]
        df_w = window_results[window_key]
        
        escape_speeds = []
        non_escape_speeds = []
        
        for i, loom in enumerate(loom_offset):
            speed_window = df_try.loc[loom-120:loom+600, 'velocity_smooth'].values  # CHANGED: 10 sec after (600 frames)
            if len(speed_window) == 721:  # CHANGED: full window check
                if window_escape_runs[window_key][i] == 1:
                    escape_speeds.append(speed_window)
                else:
                    non_escape_speeds.append(speed_window)
        
        if escape_speeds:
            escape_array = np.array(escape_speeds)
            escape_mean = escape_array.mean(axis=0)
            escape_sem = escape_array.std(axis=0) / np.sqrt(len(escape_speeds))
            time_points = np.arange(len(escape_mean)) / frame_rate - 2
            ax.plot(time_points, escape_mean, 'r-', linewidth=2, label='Escape runs (n=' + str(len(escape_speeds)) + ')')
            ax.fill_between(time_points, escape_mean - escape_sem, escape_mean + escape_sem, alpha=0.3, color='red')
        
        if non_escape_speeds:
            non_escape_array = np.array(non_escape_speeds)
            non_escape_mean = non_escape_array.mean(axis=0)
            non_escape_sem = non_escape_array.std(axis=0) / np.sqrt(len(non_escape_speeds))
            time_points = np.arange(len(non_escape_mean)) / frame_rate - 2
            ax.plot(time_points, non_escape_mean, 'b-', linewidth=2, label='Non-escapes (n=' + str(len(non_escape_speeds)) + ')')
            ax.fill_between(time_points, non_escape_mean - non_escape_sem, non_escape_mean + non_escape_sem, alpha=0.3, color='blue')
        
        ax.axhline(y=speed_threshold, color='green', linestyle='--', alpha=0.5, label='Speed threshold (mean+1SD)')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, label='Loom onset')
        ax.set_xlabel('Time relative to loom onset (sec)', fontsize=11)
        ax.set_ylabel('Velocity (mm/sec)', fontsize=11)
        ax.set_title(f'Speed Profile - Window: {window_key}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-2, 10)  # CHANGED: Show up to 10 seconds

    plt.tight_layout()
    plt.savefig(plot_path + f'/speed_profiles_{filename_base}.png', dpi=300, bbox_inches='tight')
    plt.savefig(plot_path_pdf + f'/speed_profiles_{filename_base}.pdf', bbox_inches='tight')
    print(f"Saved: speed_profiles_{filename_base}.png/pdf")
    plt.show()

    #%% PLOT: INDIVIDUAL EXAMPLES AS SINGLE TRACES
    example_window = '2.0s'  # Change this to your chosen window
    n_examples_to_plot = 2  # Number of examples per category
    
    if example_window in window_results:
        escape_indices = [i for i in range(len(window_escape_runs[example_window])) 
                         if window_escape_runs[example_window][i] == 1]
        non_escape_indices = [i for i in range(len(window_escape_runs[example_window])) 
                             if window_escape_runs[example_window][i] == 0]
        
        n_escape_examples = min(n_examples_to_plot, len(escape_indices))
        n_non_escape_examples = min(n_examples_to_plot, len(non_escape_indices))
        
        # Plot escape examples (one per subplot)
        if n_escape_examples > 0:
            fig, axes = plt.subplots(n_escape_examples, 1, figsize=(12, 4*n_escape_examples))
            if n_escape_examples == 1:
                axes = [axes]  # Make it iterable
            
            for i in range(n_escape_examples):
                idx = escape_indices[i]
                loom = loom_offset[idx]
                speed_trace = df_try.loc[loom-120:loom+600, 'velocity_smooth'].values
                
                if len(speed_trace) == 721:
                    ax = axes[i]
                    time_points = np.arange(len(speed_trace)) / frame_rate - 2
                    ax.plot(time_points, speed_trace, linewidth=2, color='red')
                    
                    ax.axhline(y=speed_threshold, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Speed threshold')
                    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Loom onset')
                    ax.set_ylabel('Velocity (mm/sec)', fontsize=12, fontweight='bold')
                    ax.set_title(f'Escape Run Example {i+1} (Loom #{idx+1})', fontsize=13, fontweight='bold')
                    ax.legend(fontsize=10)
                    ax.grid(True, alpha=0.3)
                    ax.set_xlim(-2, 10)
                    
                    if i == n_escape_examples - 1:  # Only bottom plot
                        ax.set_xlabel('Time relative to loom onset (sec)', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(plot_path + f'/individual_esc_{filename_base}.png', dpi=300, bbox_inches='tight')
            plt.savefig(plot_path_pdf + f'/individual_esc_{filename_base}.pdf', bbox_inches='tight')
            print(f"Saved: individual_esc_{filename_base}.png/pdf")
            plt.show()
        
        # Plot non-escape examples (one per subplot)
        if n_non_escape_examples > 0:
            fig, axes = plt.subplots(n_non_escape_examples, 1, figsize=(12, 4*n_non_escape_examples))
            if n_non_escape_examples == 1:
                axes = [axes]  # Make it iterable
            
            for i in range(n_non_escape_examples):
                idx = non_escape_indices[i]
                loom = loom_offset[idx]
                speed_trace = df_try.loc[loom-120:loom+600, 'velocity_smooth'].values
                
                if len(speed_trace) == 721:
                    ax = axes[i]
                    time_points = np.arange(len(speed_trace)) / frame_rate - 2
                    ax.plot(time_points, speed_trace, linewidth=2, color='blue')
                    
                    ax.axhline(y=speed_threshold, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Speed threshold')
                    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Loom onset')
                    ax.set_ylabel('Velocity (mm/sec)', fontsize=12, fontweight='bold')
                    ax.set_title(f'Non-Escape Example {i+1} (Loom #{idx+1})', fontsize=13, fontweight='bold')
                    ax.legend(fontsize=10)
                    ax.grid(True, alpha=0.3)
                    ax.set_xlim(-2, 10)
                    
                    if i == n_non_escape_examples - 1:  # Only bottom plot
                        ax.set_xlabel('Time relative to loom onset (sec)', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(plot_path + f'/individual_non_esc_{filename_base}.png', dpi=300, bbox_inches='tight')
            #plt.savefig(plot_path_pdf + f'/individual_non_escape_examples_{filename_base}.pdf', bbox_inches='tight')
            print(f"Saved: individual_non_esc_{filename_base}.png/pdf")
            plt.show()
#%% MODIFICATION 3: AGGREGATE SPEED PLOT ACROSS ALL DATASET
all_escape_speeds = []
all_non_escape_speeds = []
final_window = '0.5s' #'2.0s'  CHANGE THIS to your chosen window

print(f"\nCollecting speed data from all files for window: {final_window}...")

# Load saved data and collect speed traces
for temp_file in sorted(os.listdir(plot_path + '/temp_data')):
    if temp_file.endswith('.pkl'):
        with open(plot_path + f'/temp_data/{temp_file}', 'rb') as f:
            data = pickle.load(f)
        
        filename = data['filename']
        window_escape_runs = data['window_escape_runs']
        loom_offset = data['loom_offset']
        
                # Load the scored file
        df_file = pd.read_csv(path+'/scored/'+filename)
        
        # Need to create velocity_smooth for this reloaded file
        df_file['velocity_clean'] = df_file['velocity'].copy()
        df_file.loc[df_file['jumps'] == 1, 'velocity_clean'] = np.nan
        #for idx in df_file[df_file['jumps'] == 1].index:
        #    if idx >= 2:
        #        df_file.loc[idx-2:idx-1, 'velocity_clean'] = np.nan
        #    if idx <= len(df_file) - 3:
        #        df_file.loc[idx+1:idx+2, 'velocity_clean'] = np.nan
        df_file['velocity_smooth'] = df_file['velocity_clean'].rolling(window=7, center=True, min_periods=1).mean()
        
        # Extract speed traces
        for i, loom in enumerate(loom_offset):
            speed_window = df_file.loc[loom-120:loom+600, 'velocity_smooth'].values
            if len(speed_window) == 721:
                if window_escape_runs[final_window][i] == 1:
                    all_escape_speeds.append(speed_window)
                else:
                    all_non_escape_speeds.append(speed_window)

print(f"Total escape runs collected: {len(all_escape_speeds)}")
print(f"Total non-escapes collected: {len(all_non_escape_speeds)}")

# Create aggregate plot
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

if all_escape_speeds:
    escape_array = np.array(all_escape_speeds)
    escape_mean = escape_array.mean(axis=0)
    escape_sem = escape_array.std(axis=0) / np.sqrt(len(all_escape_speeds))
    time_points = np.arange(len(escape_mean)) / frame_rate - 2
    ax.plot(time_points, escape_mean, 'r-', linewidth=3, label=f'Escape runs (n={len(all_escape_speeds)})')
    ax.fill_between(time_points, escape_mean - escape_sem, escape_mean + escape_sem, alpha=0.3, color='red')

if all_non_escape_speeds:
    non_escape_array = np.array(all_non_escape_speeds)
    non_escape_mean = non_escape_array.mean(axis=0)
    non_escape_sem = non_escape_array.std(axis=0) / np.sqrt(len(all_non_escape_speeds))
    time_points = np.arange(len(non_escape_mean)) / frame_rate - 2
    ax.plot(time_points, non_escape_mean, 'b-', linewidth=3, label=f'Non-escapes (n={len(all_non_escape_speeds)})')
    ax.fill_between(time_points, non_escape_mean - non_escape_sem, non_escape_mean + non_escape_sem, alpha=0.3, color='blue')

ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Loom onset')
ax.set_xlabel('Time relative to loom onset (sec)', fontsize=14, fontweight='bold')
ax.set_ylabel('Velocity (mm/sec)', fontsize=14, fontweight='bold')
ax.set_title(f'Speed Profile - ALL DATASET (Window: {final_window})', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(-2, 10)

plt.tight_layout()
plt.savefig(plot_path + '/aggregate_speed_profile_all_data.png', dpi=300, bbox_inches='tight')
plt.savefig(plot_path_pdf + '/aggregate_speed_profile_all_data.pdf', bbox_inches='tight')
print("\nSaved: aggregate_speed_profile_all_data.png/pdf")
plt.show()

# Clean up temp files
import shutil
shutil.rmtree(plot_path + '/temp_data')
print("Cleaned up temporary files")

print("\n" + "="*70)
print("ALL ANALYSIS COMPLETE!")
print("="*70)
"""    
            
#    '''slicing dataframe from esc_turn until end''' #I'm commenting everything here as I don't need right now!!
#    df_loom = df_try.loc[loom_offset, 'esc_turn':].copy().reset_index(drop=True)
#    df_all = pd.concat([df_all,df_loom])

#df_all = df_all.reset_index()
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