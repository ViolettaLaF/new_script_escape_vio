# -*- coding: utf-8 -*- 
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
#%%
def data_polar_all_flies(path, group_name, all_flies_data_with_looms):
    """
    Extract orientation before and after turns from all flies pooled together.
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
            
            # Find turns in this window
            turn_frames = df_try.loc[window_start:window_end][
                df_try['Charlie_Behavior'] == 'Turn'
            ].index.tolist()
            
            for turn_frame in turn_frames:
                # Get orientation before the turn (e.g., 3 frames before)
                if turn_frame >= 3:
                    heading_before = df_try.loc[turn_frame - 3, 'orientation_smooth']
                    all_heading_before.append(heading_before)
                    
                    # Get orientation after the turn (e.g., 3 frames after)
                    if turn_frame + 3 < len(df_try):
                        heading_after = df_try.loc[turn_frame + 3, 'orientation_smooth']
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
    plt.savefig(save_path + group_name + '_polar_before.jpeg', bbox_inches='tight', dpi=1800)
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
    plt.savefig(save_path + group_name + '_polar_after.jpeg', bbox_inches='tight', dpi=1800)
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
    
    ax.set_title(group_name + ': magnitude of turn')
    ax.set_ylabel('degrees')
    ax.set_xlabel("")
    ax.set_xticklabels([])
    sns.despine()
    
    plt.savefig(save_path + group_name + '_scatter_violin_hollow_outline.jpeg',
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
    plt.savefig(save_path + group_name + '_polar_before_fake.jpeg', bbox_inches='tight', dpi=1800)
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
    plt.savefig(save_path + group_name + '_polar_after_fake.jpeg', bbox_inches='tight', dpi=1800)
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
    
    ax.set_title(group_name + ': magnitude of turn')
    ax.set_ylabel('degrees')
    ax.set_xlabel("")
    ax.set_xticklabels([])
    sns.despine()
    
    plt.savefig(save_path + group_name + '_scatter_violin_hollow_outline_fake.jpeg',
                bbox_inches='tight', dpi=1800)
    plt.show()  
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

experiment_name = 'VLF-39347_GFP_RNAi_KK-5min'

group1_label = '39347_GFP_RNAi_KK-5min'

#TIME SCALES
frame_rate = 60

#EXPERIMENT DURATION (in sec)
baseline  = 300
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


for filename in sorted(os.listdir(path+'/GFP_RNAi/')): #to change here with the names of the folder where the classified_pose.csv are!!
    if not filename.endswith('classified_pose.csv'):
        continue
    capital_x = filename.replace('X','x')
    if not capital_x.startswith(experiment_name):
        continue
    df_try = pd.read_csv(path+'/GFP_RNAi/'+filename, usecols=['FrameIndex', 'VisualStim', 'Position_X', 'Position_Y', 'Speed', 'Orientation'])

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
    
    all_flies_data_with_looms.append((df_try, loom_onset))  # Store as tuple of (dataframe, loom_onsets) 
    all_flies_data_with_fake_looms.append((df_try, loom_onset_fake))  # Store as tuple of (dataframe, loom_onsets) 
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
    
    #df_try.loc[(df_try['walk'] == 1), 'walk_speed'] = df_try['velocity']    
    df_try.loc[(df_try['Charlie_Behavior'] == 'Walk'), 'walk_speed'] = df_try['Speed'] #walking velocity
    df_try.loc[(df_try['Speed'] < jump_velocity), 'speed2d'] = df_try['Speed'] #velocity excluding jump speed     
        #%% CLEAN VELOCITY DATA: REMOVE JUMPS AND SMOOTH - it will be inportant for esc_run! Do the same for orientation important for heading for escape turn!
    # Step 1: Create a cleaned velocity column (remove jumps)
    df_try['walk_velocity_clean'] = df_try['walk_speed'].copy()
    df_try['orientation_clean'] = df_try['Orientation'].copy()    
    # Mark frames with jumps as NaN
    df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'walk_velocity_clean'] = np.nan
    df_try.loc[(df_try['Charlie_Behavior'] == 'Jump'), 'orientation_clean'] = np.nan    
    # Also remove frames right before and after jump (they're often artifacts) #now removing 6 frames before and after
    for idx in df_try[df_try['Charlie_Behavior'] == 'Jump'].index:
        if idx >= 6:
            df_try.loc[idx-6:idx-1, 'walk_velocity_clean'] = np.nan
            df_try.loc[idx-6:idx-1, 'orientation_clean'] = np.nan
        if idx <= len(df_try) - 7:
            df_try.loc[idx+1:idx+6, 'walk_velocity_clean'] = np.nan
            df_try.loc[idx+1:idx+6, 'orientation_clean'] = np.nan    
    # Step 2: Apply running average (7 frames) - NaNs will be skipped
    df_try['velocity_smooth'] = df_try['walk_velocity_clean'].rolling(window=7, center=True, min_periods=1).mean()
    df_try['orientation_smooth'] = df_try['orientation_clean'].rolling(window=7, center=True, min_periods=1).mean()       
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
 #%%            
plot_polar(exp_path, group1_label, all_flies_data_with_looms)
plot_polar_fake_loom(exp_path, group1_label, all_flies_data_with_fake_looms)
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