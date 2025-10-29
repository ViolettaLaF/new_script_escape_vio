# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 19:16:08 2020

@author: Matheus Farias

#use this code when one of the groups is exposed to control stimuli instead of loom 
#(so no problem for zero division given that flies are not freezing) 


violin plots data is mean time per fly
and traces are also mean
should we change it for median? we don't check normality
"""

import tkinter, tkinter.filedialog
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import os
import seaborn as sns


#%%%

'''
EXPERIMENT PARAMETERS - Modified for different baseline lengths
'''

number_of_groups = 2
experiment_name = 'VLF-39347_DH44_RNAi_TRIP-different-baselines'

# GROUP NAMES
group1 = 'VLF-39347_DH44_RNAi_TRIP-5minbase'
group2 = 'VLF-39347_DH44_RNAi_TRIP-30secbase'

# Plot labels
group1_label = '39347_DH44_RNAi_TRIP-5minbase'
group2_label = '39347_DH44_RNAi_TRIP-30secbase'

# Colors
group1_color = 'C0' #'firebrick'     
group2_color = 'C1' #'rosybrown'
walk_color = 'tomato'
low_vel_color = 'y'
freeze_color = 'darkcyan'
jump_color = 'darkslateblue'

# TIME SCALES
frame_rate = 60

# EXPERIMENT DURATION (in sec) - DEFINE PER GROUP
baseline_group1 = 300  # 5 minutes
baseline_group2 = 30   # 30 seconds
stimulation = 300      # 5 minutes for both groups

# Calculate frames for each group
baseline_frames_group1 = baseline_group1 * frame_rate
baseline_frames_group2 = baseline_group2 * frame_rate
stimulation_frames = stimulation * frame_rate

# Use the longer baseline as reference for plotting
max_baseline_frames = max(baseline_frames_group1, baseline_frames_group2)
tot_frames = max_baseline_frames + stimulation_frames

# For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate
limit = int(tot_frames/bin_size)
limit_min = int(limit/120)

# Create time labels - will show negative time for baseline
# Time 0 = start of stimulation
baseline_duration_min = int(max_baseline_frames / (frame_rate * 60))
my_label = np.arange(-baseline_duration_min, (stimulation/60) + 1).tolist()

# Upper threshold for speed 2D
jump_velocity = 75

'''
Choosing where to load files
'''
def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files')
    root.destroy()
    return filename

exp_path = load_path()
path = exp_path + '/scored'
plot_path = exp_path + '/plots'

groups = [group1, group2]
groups_labels = [group1_label, group2_label]
baseline_frames_per_group = [baseline_frames_group1, baseline_frames_group2]

'''
GROUP DATAFRAMES FOR PLOTS
'''
line_plots_df = pd.DataFrame()
violin_plots_df = pd.DataFrame()

group_n = 0
number_flies = []

'''
DEFINING FUNCTIONS FOR ANALYSIS
'''

def is_outlier(points, thresh=3.5):
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)
    modified_z_score = 0.6745 * diff / med_abs_deviation
    return modified_z_score > thresh

def violin_plots_variables(behavior, df_behavior, baseline_frames_current):
    baseline_behavior_bout = behavior[:baseline_frames_current].mean(axis=0).reset_index(drop=True)
    stimulation_behavior_bout = behavior[baseline_frames_current:].mean(axis=0).reset_index(drop=True)
    violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'] = baseline_behavior_bout
    violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'] = stimulation_behavior_bout
    violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'])]
    violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'])]

def line_plots_variables_aligned(behavior, df_behavior, baseline_frames_current):
    """
    Align data so stimulation starts at the same time point for all groups
    Pad shorter baselines with NaN
    """
    # Calculate padding needed
    padding_frames = max_baseline_frames - baseline_frames_current
    
    # Create padded dataframe
    if padding_frames > 0:
        # Add NaN padding at the beginning
        pad_df = pd.DataFrame(np.nan, index=range(padding_frames), columns=behavior.columns)
        behavior_padded = pd.concat([pad_df, behavior.reset_index(drop=True)], ignore_index=True)
    else:
        behavior_padded = behavior.copy()
    
    # Calculate mean and sem
    behavior_padded['mean'] = behavior_padded.mean(axis=1)
    behavior_padded['sem'] = behavior_padded.sem(axis=1)
    
    # Bin the data
    line_plots_df['group'+(str(group_n))+'_'+df_behavior+'_mean'] = (behavior_padded['mean'].groupby(behavior_padded.index // bin_size).mean())
    line_plots_df['group'+(str(group_n))+'_'+df_behavior+'_sem'] = behavior_padded['sem'].groupby(behavior_padded.index // bin_size).mean()

'''
LOADING FILES
'''

for idx, group in enumerate(groups):
    group_n = group_n + 1
    baseline_frames_current = baseline_frames_per_group[idx]
    
    '''VARIABLES'''
    list_of_flies = []
    looming = pd.DataFrame()
    looming_onset = pd.DataFrame()
    looming_offset = pd.DataFrame()
    walk_bout = pd.DataFrame()
    freeze_bout = pd.DataFrame()
    jumps = pd.DataFrame()
    jumps_bout = pd.DataFrame()
    low_vel_bout = pd.DataFrame()
    walk_speed_bout = pd.DataFrame()
    
    for filename in glob.glob(os.path.join(path, str(group + '*'))):
        fly_df = pd.read_csv(filename, ',', index_col=0)
        location, flyid = filename.split('\\', 1)
        list_of_flies.append(flyid)
        
        looming[str(flyid)] = fly_df['looming_bout']
        walk_bout[str(flyid)] = fly_df['walk_bout']
        freeze_bout[str(flyid)] = fly_df['freeze_bout']
        jumps[str(flyid)] = fly_df['jumps']
        jumps_bout[str(flyid)] = fly_df['jumps_bout']
        low_vel_bout[str(flyid)] = fly_df['low_vel_bout']
        
        fly_df['walk_speed_bout'] = np.nan
        fly_df.loc[(fly_df['walk_bout'] == 1), 'walk_speed_bout'] = fly_df['velocity']
        walk_speed_bout[str(flyid)] = fly_df['walk_speed_bout']
        
        # Extract loom onsets and offsets
        fly_df['looming_flip'] = fly_df['looming_bout'].diff()
        looming_onset[str(flyid)] = fly_df.loc[fly_df['looming_flip'] == 1].index.values.astype(int)
        looming_offset[str(flyid)] = fly_df.loc[fly_df['looming_flip'] == -1].index.values.astype(int)
    
    number_flies.append(len(looming.columns))
    
    '''PLOTS VARIABLES'''
    
    # For looming alignment
    padding_frames = max_baseline_frames - baseline_frames_current
    if padding_frames > 0:
        pad_df = pd.DataFrame(np.nan, index=range(padding_frames), columns=looming.columns)
        looming_padded = pd.concat([pad_df, looming.reset_index(drop=True)], ignore_index=True)
    else:
        looming_padded = looming.copy()
    
    looming_padded['mean'] = looming_padded.mean(axis=1)
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = looming_padded['mean'].groupby(looming_padded.index // bin_size).mean()
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = line_plots_df['group'+(str(group_n))+'_looming_mean'].round(0)
    
    # Violin plots (use actual baseline for each group)
    violin_plots_variables(walk_speed_bout, 'walk_speed_bout', baseline_frames_current)
    violin_plots_variables(walk_bout, 'walk_bout', baseline_frames_current)
    violin_plots_variables(freeze_bout, 'freeze_bout', baseline_frames_current)
    violin_plots_variables(low_vel_bout, 'low_vel_bout', baseline_frames_current)
    
    # Jumps violins
    baseline_jumps = jumps[:baseline_frames_current].sum(axis=0).reset_index(drop=True)
    stimulation_jumps = jumps[baseline_frames_current:].sum(axis=0).reset_index(drop=True)
    violin_plots_df['group'+(str(group_n))+'_baseline_jumps_mean'] = baseline_jumps
    violin_plots_df['group'+(str(group_n))+'_stimulation_jumps_mean'] = stimulation_jumps
    
    # Line plots with alignment
    line_plots_variables_aligned(walk_speed_bout, 'walk_speed_bout', baseline_frames_current)
    line_plots_variables_aligned(walk_bout, 'walk_bout', baseline_frames_current)
    line_plots_variables_aligned(freeze_bout, 'freeze_bout', baseline_frames_current)
    line_plots_variables_aligned(low_vel_bout, 'low_vel_bout', baseline_frames_current)
    line_plots_variables_aligned(jumps_bout, 'jumps_bout', baseline_frames_current)
    
    # Cumulative bouts
    line_plots_df['group'+(str(group_n))+'_cumulative_bout_1'] = (line_plots_df['group'+(str(group_n))+'_walk_bout_mean'] + 
                                                                    line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'] + 
                                                                    line_plots_df['group'+(str(group_n))+'_freeze_bout_mean'] + 
                                                                    line_plots_df['group'+(str(group_n))+'_jumps_bout_mean'])
    
    # Calculate loom coordinates for this group (aligned to padded timeline)
    median_loom_onset = looming_onset.median(axis=1)
    median_loom_offset = looming_offset.median(axis=1)
    median_loom = (median_loom_onset + median_loom_offset) / 2
    
    # Adjust loom coordinates for padding
    loom_coordinate_adjusted = [(i + padding_frames) / bin_size for i in median_loom]
    
    # Store for plotting
    if group_n == 1:
        loom_coordinates_group1 = loom_coordinate_adjusted
    else:
        loom_coordinates_group2 = loom_coordinate_adjusted

x_coordinate = [i for i in range(len(line_plots_df))]

'''
PLOTTING FUNCTION - Modified for aligned data
'''

def multiple_groups_plots(title, behavior):
    fig, axs = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey=False)
    fig.subplots_adjust(wspace=0.15)
    
    # Violin plot setup
    axs[1].set_facecolor('white')
    axs[1].axes.xaxis.set_visible(False)
    axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
    axs[1].set_axisbelow(True)
    sns.despine(left=True, bottom=True, right=True)
    axs[1].set_title('Baseline      Stimulation', y=-0.09, fontsize=16)
    axs[1].tick_params(axis='y', colors='k', labelsize=16)
    
    dashed = [1.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw=0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group1_color, 3: group2_color}
    
    axs[1] = sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, 
                               violin_plots_df['group2_baseline_'+behavior+'_mean']*100,
                               violin_plots_df['group1_stimulation_'+behavior+'_mean']*100,
                               violin_plots_df['group2_stimulation_'+behavior+'_mean']*100),
                         palette=my_pal, boxprops={'facecolor':'None', 'edgecolor':'k', 'linewidth':3, "zorder":10, 'alpha':0.6},
                         whiskerprops={'color':'k', 'linewidth':3, "zorder":10, 'linestyle':'--', 'alpha':0.6},
                         medianprops={'color':'k', 'linewidth':3, "zorder":10},
                         capprops={'color':'k', 'linewidth':3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100,
                                  violin_plots_df['group2_baseline_'+behavior+'_mean']*100,
                                  violin_plots_df['group1_stimulation_'+behavior+'_mean']*100,
                                  violin_plots_df['group2_stimulation_'+behavior+'_mean']*100),
                           bw=0.06, linewidth=1.3, width=0.9, scale='width', inner=None, palette=my_pal, cut=0)
    
    # Line plot setup
    axs[0].set_ylabel(title+' %', fontsize=18)
    axs[0].set_xlabel('Time (min)', fontsize=18)
    axs[0].set_xlim(0, limit)
    axs[0].set_ylim(0, 100)
    axs[0].set_yticks([0, 20, 40, 60, 80, 100])
    axs[0].set_xticks(np.arange(0, limit+1, 120))
    axs[0].set_xticklabels(my_label)
    axs[0].spines['left'].set_visible(True)
    axs[0].spines['bottom'].set_visible(True)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['left'].set_position(('outward', 5))
    axs[0].spines['bottom'].set_position(('outward', 5))
    axs[0].spines['left'].set_color('dimgrey')
    axs[0].spines['bottom'].set_color('dimgrey')
    axs[0].tick_params(axis='x', colors='k', labelsize=16)
    axs[0].tick_params(axis='y', colors='k', labelsize=16)
    axs[0].xaxis.label.set_color('k')
    axs[0].yaxis.label.set_color('k')
    
    # Vertical lines for loom onsets - use group1 looms as reference
    # (both groups should have same loom timing during stimulation)
    axs[0].vlines(loom_coordinates_group1, 0, 100, linestyles='--', lw=1, color='grey')
    
    axs[0].plot(x_coordinate, line_plots_df['group1_'+behavior+'_mean']*100, 'k-',
                label=(str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color, linewidth=2)
    axs[0].plot(x_coordinate, line_plots_df['group2_'+behavior+'_mean']*100, 'k-',
                label=(str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color, linewidth=2)
    
    axs[0].legend(loc="upper left", frameon=True, framealpha=0.3, fontsize=15)
    
    fig.savefig((plot_path+"/"+str(experiment_name)+'_'+title+'%.png'), format='png', dpi=300)
    plt.show()

# Generate plots
multiple_groups_plots('Walking', 'walk_bout')
multiple_groups_plots('Freezing', 'freeze_bout')
multiple_groups_plots('Low velocity', 'low_vel_bout')
    
#%% - still to adapt 
'''WALKING SPEED'''
"""
fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
fig.subplots_adjust(wspace = 0.15)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=True, bottom=True, right=True)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].set_title('Baseline      Stimulation', y=-0.09, fontsize = 16)
axs[1].set_ylim(0, 20)
if number_of_groups == 1:
    dashed = [0.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group1_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group1_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group1_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 2:
    dashed = [1.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group1_color, 3: group2_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 3:
    dashed = [2.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group1_color, 4: group2_color, 5: group3_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 4:
    dashed = [3.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group1_color, 5: group2_color, 6: group3_color, 7: group4_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)



axs[0].set_ylabel('Walking speed (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (min)', fontsize = 18)
axs[0].set_xlim(0, limit)
axs[0].set_ylim(2, 50)
#axs[0].set_yticks([5, 10, 15, 20])
axs[0].set_xticks(np.arange(0, limit+1, 120))
axs[0].set_xticklabels(my_label)
axs[0].spines['left'].set_visible(True)
axs[0].spines['bottom'].set_visible(True)
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)
axs[0].spines['left'].set_position(('outward', 5))
axs[0].spines['bottom'].set_position(('outward', 5))
axs[0].spines['left'].set_color('dimgrey')
axs[0].spines['bottom'].set_color('dimgrey')
axs[0].tick_params(axis='x', colors = 'k', labelsize=16)
axs[0].tick_params(axis='y', colors = 'k', labelsize=16)
axs[0].xaxis.label.set_color('k')
axs[0].yaxis.label.set_color('k')
axs[0].vlines(loom_coordinate, 0, 100, linestyles='--', lw= 1, color='grey')
axs[0].plot(x_coordinate, line_plots_df['group1_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color)
axs[0].fill_between(x_coordinate, (line_plots_df['group1_walk_speed_bout_mean']-line_plots_df['group1_walk_speed_bout_sem']),(line_plots_df['group1_walk_speed_bout_mean']+line_plots_df['group1_walk_speed_bout_sem']), color=group1_color, alpha=0.3)
if number_of_groups >= 2:
    axs[0].plot(x_coordinate, line_plots_df['group2_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group2_walk_speed_bout_mean']-line_plots_df['group2_walk_speed_bout_sem']),(line_plots_df['group2_walk_speed_bout_mean']+line_plots_df['group2_walk_speed_bout_sem']), color=group2_color, alpha=0.3)
if number_of_groups >= 3:
    axs[0].plot(x_coordinate, line_plots_df['group3_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[2]) + ' (' + str(number_flies[2])+')'), color=group3_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group3_walk_speed_bout_mean']-line_plots_df['group3_walk_speed_bout_sem']),(line_plots_df['group3_walk_speed_bout_mean']+line_plots_df['group3_walk_speed_bout_sem']), color=group3_color, alpha=0.3)
if number_of_groups >= 4:
    axs[0].plot(x_coordinate, line_plots_df['group4_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[3]) + ' (' + str(number_flies[3])+')'), color=group4_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group4_walk_speed_bout_mean']-line_plots_df['group4_walk_speed_bout_sem']),(line_plots_df['group4_walk_speed_bout_mean']+line_plots_df['group4_walk_speed_bout_sem']), color=group4_color, alpha=0.3)


axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)
fig.savefig((plot_path+"/"+str(experiment_name)+"_walk_speed.png"), format='png') 
plt.show()
"""