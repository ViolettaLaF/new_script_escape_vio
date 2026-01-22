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
baseline  = 30 #300
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
    all_flies_data_with_fake_looms.append((df_try, loom_onset_fake))  # Store as tuple of (dataframe, loom_onsets) 
#%%   
    df_try['esc_turn_wall'] = 0
    df_try['esc_turn_floor'] = 0
    df_try['esc_run'] = 0
    df_try['esc_jump'] = 0
    df_try['backwards'] = 0
    df_try['walk_away'] = 0
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
 #%%
    '''checking jumps, freeze, backwards, turning, walk_away''' # behaviour mutually exclusive at the moment!
    for i in range(len(loom_onset)):
        if (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Jump').sum() > 0:
            df_try.loc[loom_offset[i], 'esc_jump'] = 1
     
        elif ((df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Freeze') | 
              (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Resistant_Freeze')).sum() > 0:
            df_try.loc[loom_offset[i], 'freeze'] = 1
            
        elif (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Backwards_Walk').sum() > 0:
            df_try.loc[loom_offset[i], 'backwards'] = 1
            
        elif (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Turn').sum() > 0:
            df_try.loc[loom_offset[i], 'esc_turn_wall'] = 1
            
        elif (df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'Charlie_Behavior'] == 'Floor_Turn').sum() > 0:
            df_try.loc[loom_offset[i], 'esc_turn_floor'] = 1        
        
        # Walk away check
        else:
            # Check pre-loom behavior (2 second before loom)
            pre_loom_start = max(0, loom_onset[i] - 120)
            pre_loom_data = df_try.loc[pre_loom_start:loom_onset[i]-1]
            
            # Check if fly was stationary or freezing before loom (all frames)
            pre_loom_behaviors = pre_loom_data['Charlie_Behavior'].values
            #is_stationary_before = all(b in ['Stationary', 'Freeze', 'Resistant_Freeze'] 
            #                          for b in pre_loom_behaviors if pd.notna(b))
            
            
            

            # At least 95% of frames must be stationary/freeze
            stationary_frames = sum(b in ['Stationary', 'Freeze', 'Resistant_Freeze'] 
                                    for b in pre_loom_behaviors if pd.notna(b))
            total_frames = sum(pd.notna(b) for b in pre_loom_behaviors)
            is_stationary_before = (stationary_frames / total_frames) >= 0.95 if total_frames > 0 else False


            
            if is_stationary_before:
                # Check if starts walking within 2.5s (150 frames) after loom onset
                post_loom_end = min(len(df_try)-1, loom_onset[i] + 150)
                post_loom_data = df_try.loc[loom_onset[i]:post_loom_end]
                walk_frames = post_loom_data[post_loom_data['Charlie_Behavior'] == 'Walk'].index.tolist()
                
                if len(walk_frames) >= 3:
                    df_try.loc[loom_offset[i], 'walk_away'] = 1  
                
                
#%% Walk Away Analysis Functions

def identify_walk_away_trials(all_flies_data_with_looms, pre_loom_window=120, 
                               post_loom_window=150):
    """
    Extract walk away trials from already flagged data.
    """
    walk_away_trials = []
    
    for fly_idx, (df_try, loom_onset) in enumerate(all_flies_data_with_looms):
        # Get loom offsets
        loom_offset = df_try.loc[df_try['VisualStim'].diff() == 1].index.values.astype(int)
        
        for loom_idx, (onset, offset) in enumerate(zip(loom_onset, loom_offset)):
            # Skip baseline looms
            if onset < baseline_frames:
                continue
            
            # Check if this loom was flagged as walk_away
            if df_try.loc[offset, 'walk_away'] == 1:
                # Find when walking started
                post_loom_end = min(len(df_try)-1, onset + post_loom_window)
                post_loom_data = df_try.loc[onset:post_loom_end]
                walk_frames = post_loom_data[post_loom_data['Charlie_Behavior'] == 'Walk'].index.tolist()
                
                if len(walk_frames) > 0:
                    walk_start = walk_frames[0]
                    
                    # Calculate total distance traveled during walking bout
                    walk_bout_data = df_try.loc[walk_start:post_loom_end]
                    walk_bout_data = walk_bout_data[walk_bout_data['Charlie_Behavior'] == 'Walk']
                    
                    # Distance = speed * time (speed is mm/s, divide by 60 for per frame)
                    total_distance = (walk_bout_data['Speed'].sum()) / 60  # mm
                    
                    walk_away_trials.append({
                        'fly_idx': fly_idx,
                        'loom_idx': loom_idx,
                        'loom_frame': onset,
                        'walk_start_frame': walk_start,
                        'walk_latency': walk_start - onset,  # frames
                        'total_distance': total_distance,  # mm
                        'df_try': df_try
                    })
    
    return walk_away_trials


def plot_walk_away_speed_profiles(walk_away_trials, group_name, save_path, 
                                  frames_before=120, frames_after=150, frame_rate=60):
    """
    Plot average speed and walk_speed profiles for walk away trials.
    """
    if len(walk_away_trials) == 0:
        print("No walk away trials found!")
        return
    
    # Collect speed traces
    all_speed_traces = []
    all_walk_speed_traces = []
    
    for trial in walk_away_trials:
        loom_frame = trial['loom_frame']
        df_try = trial['df_try']
        
        window_start = loom_frame - frames_before
        window_end = loom_frame + frames_after
        
        if window_start >= 0 and window_end < len(df_try):
            speed_trace = df_try.loc[window_start:window_end, 'Speed'].values
            walk_speed_trace = df_try.loc[window_start:window_end, 'walk_speed'].values
            
            all_speed_traces.append(speed_trace)
            all_walk_speed_traces.append(walk_speed_trace)
    
    # Convert to arrays
    all_speed_traces = np.array(all_speed_traces)
    all_walk_speed_traces = np.array(all_walk_speed_traces)
    
    # Calculate mean and SEM
    mean_speed = np.nanmean(all_speed_traces, axis=0)
    sem_speed = np.nanstd(all_speed_traces, axis=0) / np.sqrt(len(all_speed_traces))
    
    mean_walk_speed = np.nanmean(all_walk_speed_traces, axis=0)
    sem_walk_speed = np.nanstd(all_walk_speed_traces, axis=0) / np.sqrt(len(all_walk_speed_traces))
    
    # Time axis
    time_axis = np.arange(-frames_before, frames_after+1) / frame_rate
    
    # Create plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Speed
    ax1 = axes[0]
    ax1.plot(time_axis, mean_speed, color='blue', linewidth=2, label='Mean Speed')
    ax1.fill_between(time_axis, mean_speed - sem_speed, mean_speed + sem_speed, 
                     color='blue', alpha=0.3, label='SEM')
    ax1.axvline(x=0, color='black', linestyle='--', linewidth=2, label='Loom Onset')
    ax1.axvline(x=0.5, color='gray', linestyle='--', linewidth=1, label='Loom Offset')
    ax1.set_ylabel('Speed (mm/s)', fontsize=12)
    ax1.set_title(f'{group_name} - Walk Away Behavior: Speed Profile\n(n={len(walk_away_trials)} trials)', 
                 fontsize=14)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Walk Speed
    ax2 = axes[1]
    ax2.plot(time_axis, mean_walk_speed, color='green', linewidth=2, label='Mean Walk Speed')
    ax2.fill_between(time_axis, mean_walk_speed - sem_walk_speed, mean_walk_speed + sem_walk_speed, 
                     color='green', alpha=0.3, label='SEM')
    ax2.axvline(x=0, color='black', linestyle='--', linewidth=2, label='Loom Onset')
    ax2.axvline(x=0.5, color='gray', linestyle='--', linewidth=1, label='Loom Offset')
    ax2.set_xlabel('Time relative to loom onset (s)', fontsize=12)
    ax2.set_ylabel('Walk Speed (mm/s)', fontsize=12)
    ax2.set_title('Walk Speed Profile', fontsize=14)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path + '/' + experiment_name + '_walk_away_speed_profiles.png', 
                bbox_inches='tight', dpi=300)
    plt.show()


def plot_individual_walk_away_examples(walk_away_trials, group_name, save_path, 
                                       n_examples=10, frames_before=120, 
                                       frames_after=150, frame_rate=60):
    """
    Plot individual examples of walk away trials.
    """
    if len(walk_away_trials) == 0:
        print("No walk away trials found!")
        return
    
    # Select random examples or first n
    n_to_plot = min(n_examples, len(walk_away_trials))
    if n_to_plot > len(walk_away_trials):
        examples = walk_away_trials
    else:
        import random
        examples = random.sample(walk_away_trials, n_to_plot)
    
    # Create subplots
    n_cols = 2
    n_rows = int(np.ceil(n_to_plot / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4*n_rows), sharex=True)
    if n_to_plot == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, trial in enumerate(examples):
        ax = axes[idx]
        loom_frame = trial['loom_frame']
        df_try = trial['df_try']
        
        window_start = loom_frame - frames_before
        window_end = loom_frame + frames_after
        
        speed_trace = df_try.loc[window_start:window_end, 'Speed'].values
        walk_speed_trace = df_try.loc[window_start:window_end, 'walk_speed'].values
        
        time_axis = np.arange(-frames_before, frames_after+1) / frame_rate
        
        ax.plot(time_axis, speed_trace, color='blue', linewidth=1.5, label='Speed', alpha=0.7)
        ax.plot(time_axis, walk_speed_trace, color='green', linewidth=1.5, label='Walk Speed', alpha=0.7)
        ax.axvline(x=0, color='black', linestyle='--', linewidth=2, alpha=0.7)
        ax.axvline(x=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        
        # Mark walk start
        walk_latency_sec = trial['walk_latency'] / frame_rate
        ax.axvline(x=walk_latency_sec, color='red', linestyle=':', linewidth=1.5, 
                  label=f'Walk Start ({walk_latency_sec:.2f}s)')
        
        ax.set_ylabel('Speed (mm/s)', fontsize=10)
        ax.set_title(f'Fly {trial["fly_idx"]}, Loom {trial["loom_idx"]+1}\n' + 
                    f'Distance: {trial["total_distance"]:.1f} mm', fontsize=11)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Remove empty subplots
    for idx in range(n_to_plot, len(axes)):
        fig.delaxes(axes[idx])
    
    # Add common x-label
    fig.text(0.5, 0.02, 'Time relative to loom onset (s)', ha='center', fontsize=12)
    
    plt.suptitle(f'{group_name} - Walk Away Examples', fontsize=14, y=0.995)
    plt.tight_layout(rect=[0, 0.03, 1, 0.99])
    plt.savefig(save_path + '/' + experiment_name + '_walk_away_examples.png', 
                bbox_inches='tight', dpi=300)
    plt.show()


def plot_walk_away_distance_distribution(walk_away_trials, group_name, save_path):
    """
    Plot distribution of total distance traveled during walk away bouts.
    """
    if len(walk_away_trials) == 0:
        print("No walk away trials found!")
        return
    
    distances = [trial['total_distance'] for trial in walk_away_trials]
    latencies = [trial['walk_latency'] / 60 for trial in walk_away_trials]  # Convert to seconds
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Distance distribution
    ax1 = axes[0]
    ax1.hist(distances, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax1.axvline(x=np.median(distances), color='red', linestyle='--', linewidth=2, 
               label=f'median: {np.median(distances):.1f} mm')
    ax1.set_xlabel('Total Distance Traveled (mm)', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title(f'{group_name} - Walk Away Distance Distribution\n(n={len(walk_away_trials)} trials)', 
                 fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Latency to walk start
    ax2 = axes[1]
    ax2.hist(latencies, bins=20, color='green', alpha=0.7, edgecolor='black')
    ax2.axvline(x=np.median(latencies), color='red', linestyle='--', linewidth=2, 
               label=f'median: {np.median(latencies):.2f} s')
    ax2.set_xlabel('Latency to Walk Start (s)', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Walk Start Latency Distribution', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path + '/' + experiment_name + '_walk_away_distributions.png', 
                bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print summary statistics
    print(f"\n=== Walk Away Behavior Summary for {group_name} ===")
    print(f"Total trials: {len(walk_away_trials)}")
    print(f"Mean distance: {np.mean(distances):.2f} ± {np.std(distances):.2f} mm")
    print(f"Median distance: {np.median(distances):.2f} mm")
    print(f"Mean latency: {np.mean(latencies):.2f} ± {np.std(latencies):.2f} s")
    print(f"Median latency: {np.median(latencies):.2f} s")


#%% RUN WALK AWAY ANALYSIS

# Identify walk away trials
walk_away_trials = identify_walk_away_trials(
    all_flies_data_with_looms, 
    pre_loom_window=60,  # 1 second before loom
    post_loom_window=150  # 2.5 seconds after loom
)

print(f"Found {len(walk_away_trials)} walk away trials")

# Plot average speed profiles
plot_walk_away_speed_profiles(
    walk_away_trials, 
    group1_label, 
    plot_path,
    frames_before=120,  # 2 seconds before
    frames_after=150,   # 2.5 seconds after
    frame_rate=60
)

# Plot individual examples
plot_individual_walk_away_examples(
    walk_away_trials, 
    group1_label, 
    plot_path,
    n_examples=10,
    frames_before=120,
    frames_after=150,
    frame_rate=60
)

# Plot distance and latency distributions
plot_walk_away_distance_distribution(walk_away_trials, group1_label, plot_path)
 #%%  commenting just because I don't need right now but is correct!          
#plot_polar(exp_path, group1_label, all_flies_data_with_looms)
#plot_polar_fake_loom(exp_path, group1_label, all_flies_data_with_fake_looms)
 #%%   
            
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