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
EXPERIMENT PARAMETERS
'''

number_of_groups = 1
experiment_name = 'VLF-39347_DH44_RNAi_TRIP-5minbase' # 'TH_GAL80_DH44_GAL4_DH44_RNAi_VDRC' #  #' #for group figure names


#GROUP NAME = FILE NAME START
group1 = 'VLF-39347_DH44_RNAi_TRIP-5minbase'#  'VLF-TH_GAL80_DH44_GAL4_DH44_RNAi_VDRC' # 'VLF-39347_DH44_RNAi_fem'
group2 = 'VLF-Tsh_GAL80_DH44_GAL4_GFP_RNAi_VDRC'# 'VLF-TH_GAL80_DH44_GAL4_GFP_RNAi_VDRC' #'VLF-Tsh_GAL80_DH44_GAL4_GFP_RNAi_VDRC'#'VLF-39347_luc_RNAi_fem' 
group3 = 'VLF-DH44_GAL4_DH44_RNAi_VDRC' #'VLF-DH44_GAL4_DH44_RNAi_VDRC' # 'VLF-39347_DH44_RNAi_male'
group4 = 'VLF-DH44_GAL4_GFP_RNAi_VDRC' #'VLF-DH44_GAL4_GFP_RNAi_VDRC' #'VLF-39347_luc_RNAi_male'
group5 = 'VLF-TH_GAL80_39347_luc_RNAi'
group6 = 'MF-LPLC2'

#Plots labels
#group1_label = 'Empty TNT'
group1_label = '39347_DH44_RNAi_TRIP-5minbase' #'TH_GAL80_DH44_GAL4_DH44_RNAi' #'Tsh_GAL80_DH44_GAL4_DH44_RNAi'#'39347_DH44_RNAi_fem' 
group2_label = 'Tsh_GAL80_DH44_GAL4_GFP_RNAi' #'TH_GAL80_DH44_GAL4_GFP_RNAi' #'TH_GAL80_DH44_GAL4_GFP_RNAi' #'Tsh_GAL80_DH44_GAL4_GFP_RNAi'#'39347_luc_RNAi_fem'
group3_label = 'DH44_GAL4_DH44_RNAi' #'39347_DH44_RNAi_male'
group4_label = 'DH44_GAL4_GFP_RNAi' #'VLF-39347_luc_RNAi_male'
group5_label = 'TH_GAL80_39347_luc_RNAi'
group6_label = 'LPLC2 TNT'


#Change colors here
group1_color = 'firebrick'     
group2_color = 'rosybrown'
group3_color = 'indigo'#'royalblue'#'goldenrod'
group4_color = 'dimgrey'#'indigo'
group5_color = 'goldenrod'#'royalblue'
group6_color = 'forestgreen'

walk_color = 'tomato'
low_vel_color = 'y'
freeze_color = 'darkcyan'
jump_color = 'darkslateblue'


#TIME SCALES
frame_rate = 60

#EXPERIMENT DURATION (in sec)
baseline  =  300 # 180
stimulation =  300 # 1200

baseline_frames = baseline * frame_rate
stimulation_frames = stimulation * frame_rate
tot_frames = baseline_frames + stimulation_frames

#Zoom plots window
number_of_looms= 20 #20
loom_duration_sec = 0.5
loom_duration  = loom_duration_sec * frame_rate


#For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate #every bin is 30 frames 
limit = int(tot_frames/bin_size) # useful for set_xlim in line_plot and % behaviours 
limit_min = int(limit/120) # useful for set_xtick and labels (min is for minutes)
my_label= np.arange(0, limit_min + 1).tolist() #  labels in min

bin_size_zoom_sec = 0.05
bin_size_zoom = bin_size_zoom_sec * frame_rate


#Upper treshold for speed 2D
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

groups = []
if number_of_groups == 1:
    groups.append(group1)
if number_of_groups == 2:
    groups.append(group1)
    groups.append(group2)
if number_of_groups == 3:
    groups.append(group1)
    groups.append(group2)
    groups.append(group3)
if number_of_groups == 4:
    groups.append(group1)
    groups.append(group2)
    groups.append(group3)
    groups.append(group4)
if number_of_groups == 5:
    groups.append(group1)
    groups.append(group2)
    groups.append(group3)
    groups.append(group4)
    groups.append(group5)
if number_of_groups == 6:
    groups.append(group1)
    groups.append(group2)
    groups.append(group3)
    groups.append(group4)
    groups.append(group5)
    groups.append(group6)
    
groups_labels = []
if number_of_groups == 1:
    groups_labels.append(group1_label)
if number_of_groups == 2:
    groups_labels.append(group1_label)
    groups_labels.append(group2_label)
if number_of_groups == 3:
    groups_labels.append(group1_label)
    groups_labels.append(group2_label)
    groups_labels.append(group3_label)
if number_of_groups == 4:
    groups_labels.append(group1_label)
    groups_labels.append(group2_label)
    groups_labels.append(group3_label)
    groups_labels.append(group4_label)
if number_of_groups == 5:
    groups_labels.append(group1_label)
    groups_labels.append(group2_label)
    groups_labels.append(group3_label)
    groups_labels.append(group4_label)
    groups_labels.append(group5_label)
if number_of_groups == 6:
    groups_labels.append(group1_label)
    groups_labels.append(group2_label)
    groups_labels.append(group3_label)
    groups_labels.append(group4_label)
    groups_labels.append(group5_label)
    groups_labels.append(group6_label)


'''
GROUP DATAFRAMES FOR PLOTS
'''

line_plots_df = pd.DataFrame()
violin_plots_df = pd.DataFrame()
delta_behavior_plots_df = pd.DataFrame()
delta_behavior_violins_df = pd.DataFrame()

group_n = 0
number_flies = []
number_looms = []
number_runners = []
number_freezers = []


#%%%%
    
'''
DEFINING FUNCTIONS FOR ANALYSIS
'''

#FUNCTION TO DETECT OUTLIERS
def is_outlier(points, thresh=3.5):
    '''
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    '''
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh



#FUNCTION TO GET MEAN TIME 'BEHAVIOR' DURING BASELINE OR STIMULATION PER FLY
def violin_plots_variables(behavior, df_behavior):
    baseline_behavior_bout = behavior[:baseline_frames].mean(axis=0).reset_index(drop=True)
    stimulation_behavior_bout = behavior[baseline_frames:].mean(axis=0).reset_index(drop=True)
    violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'] = baseline_behavior_bout
    violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'] = stimulation_behavior_bout
    violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_baseline_'+df_behavior+'_mean'])]
    violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_stimulation_'+df_behavior+'_mean'])]
    violin_plots_df['group'+(str(group_n))+'_'+df_behavior+'_mean_delta'] = stimulation_behavior_bout - baseline_behavior_bout



#FUNCTION TO GET MEAN TIME 'BEHAVIOR' ACROSS THE GROUP
def line_plots_variables(behavior, df_behavior):
    behavior['mean'] = behavior.mean(axis=1)
    behavior['sem'] = behavior.sem(axis=1)
    line_plots_df['group'+(str(group_n))+'_'+df_behavior+'_mean'] = (behavior['mean'].groupby(behavior.index // bin_size).mean())
    line_plots_df['group'+(str(group_n))+'_'+df_behavior+'_sem'] = behavior['sem'].groupby(behavior.index // bin_size).mean()

#%%%%

'''
LOADING FILES
'''

for group in groups:
    group_n = group_n + 1
    '''VARIABLES'''
    list_of_flies = []
    looming = pd.DataFrame()
    redled = pd.DataFrame()
    greenled = pd.DataFrame()
    fly_x_norm_mm = pd.DataFrame()
    fly_y_norm_mm = pd.DataFrame()
    pixelchange = pd.DataFrame()
    velocity = pd.DataFrame()
    walk = pd.DataFrame()
    walk_bout = pd.DataFrame()
    freeze_bout = pd.DataFrame()
    jumps = pd.DataFrame()
    jumps_bout = pd.DataFrame()
    low_vel = pd.DataFrame()
    low_vel_bout = pd.DataFrame()
    pauses = pd.DataFrame()
    walk_speed = pd.DataFrame()
    walk_speed_bout = pd.DataFrame()
    speed2d = pd.DataFrame()
    pauses_loom_onset = []
    pauses_duration = []


    '''ZOOM VARIABLES'''
    looming_onset = pd.DataFrame()
    looming_offset = pd.DataFrame()

    
    for filename in glob.glob(os.path.join(path , str(group + '*'))):
        fly_df = pd.read_csv(filename, ',',  index_col=0)
        location, flyid  = filename.split('\\', 1)
        #print(filename)
        list_of_flies.append(flyid)
        looming[str(flyid)] = fly_df['looming_bout']
        redled[str(flyid)] = fly_df['redled']
        greenled[str(flyid)] = fly_df['greenled']
        fly_x_norm_mm[str(flyid)] = fly_df['fly_x_norm_mm']
        fly_y_norm_mm[str(flyid)] = fly_df['fly_y_norm_mm']
        pixelchange[str(flyid)] = fly_df['pixelchange']
        velocity[str(flyid)] = fly_df['velocity']
        walk[str(flyid)] = fly_df['walk']
        walk_bout[str(flyid)] = fly_df['walk_bout']
        freeze_bout[str(flyid)] = fly_df['freeze_bout']
        jumps[str(flyid)] = fly_df['jumps']
        jumps_bout[str(flyid)] = fly_df['jumps_bout']
        low_vel[str(flyid)] = fly_df['low_vel']
        low_vel_bout[str(flyid)] = fly_df['low_vel_bout']
        pauses[str(flyid)] = fly_df['pauses']
    
        fly_df['walk_speed'] = np.nan
        fly_df.loc[(fly_df['walk'] == 1), 'walk_speed'] = fly_df['velocity'] # => having speed of just walking flies
        walk_speed[str(flyid)] = fly_df['walk_speed']

        fly_df['walk_speed_bout'] = np.nan
        fly_df.loc[(fly_df['walk_bout'] == 1), 'walk_speed_bout'] = fly_df['velocity']
        walk_speed_bout[str(flyid)] = fly_df['walk_speed_bout']
        
        fly_df['speed2d'] = np.nan # => speed regardless behaviour, if jump speed = 75
        fly_df.loc[(fly_df['velocity'] < jump_velocity), 'speed2d'] = fly_df['velocity']
        fly_df.loc[(fly_df['velocity'] >= jump_velocity), 'speed2d'] = 75
    
    
        fly_df['pauses_flip'] = fly_df['pauses'].diff() # => to calculate onset and offset of pause!
        pauses_onset = fly_df.loc[fly_df['pauses_flip']==1].index.values.astype(int)
        pauses_offset = fly_df.loc[fly_df['pauses_flip']==-1].index.values.astype(int)
        for i in range(len(pauses_onset)):
            pauses_length = pauses_offset[i]-pauses_onset[i]
            pauses_duration.append(pauses_length)


        fly_df['looming_flip'] = fly_df['looming_bout'].diff()
        looming_onset[str(flyid)] = fly_df.loc[fly_df['looming_flip'] == 1].index.values.astype(int)
        looming_offset[str(flyid)] = fly_df.loc[fly_df['looming_flip'] == -1].index.values.astype(int)
        loom_counter = 0
            
    number_flies.append(len(looming.columns))

    
    
    
#%%%
    
    '''PLOTS VARIABLES'''
    
    looming['mean'] = looming.mean(axis=1)
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = looming['mean'].groupby(looming.index // bin_size).mean() #// = da solo l'intero della divisione!
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = line_plots_df['group'+(str(group_n))+'_looming_mean'].round(0) #to have integer!

    violin_plots_variables(walk_speed_bout, 'walk_speed_bout')
    violin_plots_variables(walk_bout, 'walk_bout')
    violin_plots_variables(freeze_bout, 'freeze_bout')
    violin_plots_variables(low_vel_bout, 'low_vel_bout')
    
    #Jumps violins is the sum of jumps not mean
    baseline_jumps = jumps[:baseline_frames].sum(axis=0).reset_index(drop=True)
    stimulation_jumps = jumps[baseline_frames:].sum(axis=0).reset_index(drop=True)
    violin_plots_df['group'+(str(group_n))+'_baseline_jumps_mean'] = baseline_jumps
    violin_plots_df['group'+(str(group_n))+'_stimulation_jumps_mean'] = stimulation_jumps
    violin_plots_df['group'+(str(group_n))+'_baseline_jumps_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_baseline_jumps_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_baseline_jumps_mean'])]
    violin_plots_df['group'+(str(group_n))+'_stimulation_jumps_mean_outliers'] = violin_plots_df['group'+(str(group_n))+'_stimulation_jumps_mean'][~is_outlier(violin_plots_df['group'+(str(group_n))+'_stimulation_jumps_mean'])]
    violin_plots_df['group'+(str(group_n))+'_jumps_mean_delta'] = stimulation_jumps - baseline_jumps
    
    line_plots_variables(walk_speed_bout, 'walk_speed_bout')
    line_plots_variables(walk_bout, 'walk_bout')
    line_plots_variables(freeze_bout, 'freeze_bout')
    line_plots_variables(low_vel_bout, 'low_vel_bout')
    line_plots_variables(jumps_bout, 'jumps_bout')

    line_plots_df['group'+(str(group_n))+'_cumulative_bout_1'] = line_plots_df['group'+(str(group_n))+'_walk_bout_mean'] + line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'] + line_plots_df['group'+(str(group_n))+'_freeze_bout_mean'] + line_plots_df['group'+(str(group_n))+'_jumps_bout_mean']
    line_plots_df['group'+(str(group_n))+'_cumulative_bout_2'] = line_plots_df['group'+(str(group_n))+'_walk_bout_mean'] + line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'] + line_plots_df['group'+(str(group_n))+'_freeze_bout_mean']
    line_plots_df['group'+(str(group_n))+'_cumulative_bout_3'] = line_plots_df['group'+(str(group_n))+'_walk_bout_mean'] + line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean']
    line_plots_df['group'+(str(group_n))+'_cumulative_bout_4'] = line_plots_df['group'+(str(group_n))+'_walk_bout_mean']



#%%%
    '''BINED VARIABLES'''
    
    x_bined = fly_x_norm_mm.groupby(fly_x_norm_mm.index // bin_size).mean()
    y_bined = fly_y_norm_mm.groupby(fly_y_norm_mm.index // bin_size).mean()
    looming_onset_bined = (looming_onset / bin_size).round(0)
    velocity_bined = (velocity.groupby(velocity.index // bin_size).mean())
    freeze_bout_bined = (freeze_bout.groupby(freeze_bout.index // bin_size).mean()).drop(columns=['mean', 'sem'])
    walk_bout_bined = (walk_bout.groupby(walk_bout.index // bin_size).mean()).drop(columns=['mean', 'sem'])
    low_vel_bout_bined = (low_vel_bout.groupby(low_vel_bout.index // bin_size).mean()).drop(columns=['mean', 'sem'])
    jumps_bined = jumps.groupby(jumps.index // bin_size).sum()
    pauses_bined = pauses.groupby(pauses.index // bin_size).mean()
    
    x_baseline_bined = x_bined[:(int(baseline_frames/bin_size))]
    y_baseline_bined = y_bined[:(int(baseline_frames/bin_size))]
    x_stimulation_bined = x_bined[(int(baseline_frames/bin_size)):]
    y_stimulation_bined = y_bined[(int(baseline_frames/bin_size)):]
    freezing_baseline_bined = (freeze_bout_bined[:(int(baseline_frames/bin_size))]).round(0)
    freezing_stimulation_bined = (freeze_bout_bined[(int(baseline_frames/bin_size)):]).round(0)
    walking_baseline_bined = (walk_bout_bined[:(int(baseline_frames/bin_size))]).round(0)
    walking_stimulation_bined = (walk_bout_bined[(int(baseline_frames/bin_size)):]).round(0)
    low_vel_baseline_bined = (low_vel_bout_bined[:(int(baseline_frames/bin_size))]).round(0)
    low_vel_stimulation_bined = (low_vel_bout_bined[(int(baseline_frames/bin_size)):]).round(0)
    

    '''BASELINE - STIMULATION VARIABLES '''
    
    walk_bout_baseline = walk_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    walk_bout_stimulation = walk_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)
    freeze_bout_baseline = freeze_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    freeze_bout_stimulation = freeze_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)
    low_vel_bout_baseline = low_vel_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    low_vel_bout_stimulation = low_vel_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)
 
    '''INDIVIDUAL GROUP PLOTS'''
    
    median_loom_onset = looming_onset.median(axis=1)
    median_loom_offset =looming_offset.median(axis=1)
    median_loom = (median_loom_onset+median_loom_offset)/2

    loom_coordinate = [(i/bin_size) for i in median_loom]
    x_coordinate = [i for i in range(len(line_plots_df))]

#%%
''' MULTIPLE GROUPS PLOTS'''


def multiple_groups_plots(title, behavior):
    fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
    fig.subplots_adjust(wspace = 0.15)

    axs[1].set_facecolor('white')
    axs[1].axes.xaxis.set_visible(False)
    axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
    axs[1].set_axisbelow(True)
    sns.despine(left=True, bottom=True, right=True)
    axs[1].set_title('Baseline      Stimulation', y=-0.09, fontsize = 16)
    axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
    if number_of_groups == 1:
        dashed = [0.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group1_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group1_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group1_stimulation_'+behavior+'_mean']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 2:
        dashed = [1.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group2_color, 2: group1_color, 3: group2_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 3:
        dashed = [2.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group1_color, 4: group2_color, 5: group3_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100), bw =0.06, 
            linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 4:
        dashed = [3.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group1_color, 5: group2_color, 6: group3_color, 7: group4_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100), 
           bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 5:
        dashed = [4.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group1_color, 6: group2_color, 7: group3_color, 8: group4_color, 9: group5_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100, violin_plots_df['group5_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100, violin_plots_df['group5_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100, violin_plots_df['group5_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100, violin_plots_df['group5_stimulation_'+behavior+'_mean']*100), 
           bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 6:
        dashed = [5.5]
        axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color, 6: group1_color, 7: group2_color, 8: group3_color, 9: group4_color, 10: group5_color, 11: group6_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100, violin_plots_df['group5_baseline_'+behavior+'_mean']*100, violin_plots_df['group6_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100, violin_plots_df['group5_stimulation_'+behavior+'_mean']*100, violin_plots_df['group6_stimulation_'+behavior+'_mean']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_'+behavior+'_mean']*100, violin_plots_df['group2_baseline_'+behavior+'_mean']*100, violin_plots_df['group3_baseline_'+behavior+'_mean']*100, violin_plots_df['group4_baseline_'+behavior+'_mean']*100, violin_plots_df['group5_baseline_'+behavior+'_mean']*100, violin_plots_df['group6_baseline_'+behavior+'_mean']*100,
           violin_plots_df['group1_stimulation_'+behavior+'_mean']*100, violin_plots_df['group2_stimulation_'+behavior+'_mean']*100, violin_plots_df['group3_stimulation_'+behavior+'_mean']*100, violin_plots_df['group4_stimulation_'+behavior+'_mean']*100, violin_plots_df['group5_stimulation_'+behavior+'_mean']*100, violin_plots_df['group6_stimulation_'+behavior+'_mean']*100), 
           bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)

    axs[0].set_ylabel(title+' %', fontsize = 18)
    axs[0].set_xlabel('Time (min)', fontsize = 18)
    axs[0].set_xlim(0, limit)
    axs[0].set_ylim(0, 100)
    axs[0].set_yticks([0,20, 40, 60, 80, 100])
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
    axs[0].plot(x_coordinate, line_plots_df['group1_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color)
    if number_of_groups >= 2:
        axs[0].plot(x_coordinate, line_plots_df['group2_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color)
    if number_of_groups >= 3:
        axs[0].plot(x_coordinate, line_plots_df['group3_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[2]) + ' (' + str(number_flies[2])+')'), color=group3_color)
    if number_of_groups >= 4:
        axs[0].plot(x_coordinate, line_plots_df['group4_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[3]) + ' (' + str(number_flies[3])+')'), color=group4_color)
    if number_of_groups >= 5:
        axs[0].plot(x_coordinate, line_plots_df['group5_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
    if number_of_groups == 6:
        axs[0].plot(x_coordinate, line_plots_df['group6_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)
    
    axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

    fig.savefig((plot_path+"/"+str(experiment_name)+'_'+title+'%.png'), format='png') 
    plt.show()

    
multiple_groups_plots('Walking', 'walk_bout')
multiple_groups_plots('Freezing', 'freeze_bout')
multiple_groups_plots('Low velocity', 'low_vel_bout')
    

'''WALKING SPEED'''
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
if number_of_groups == 5:
    dashed = [4.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group1_color, 6: group2_color, 7: group3_color, 8: group4_color, 9: group5_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'], violin_plots_df['group5_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean'], violin_plots_df['group5_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'], violin_plots_df['group5_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean'], violin_plots_df['group5_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 6:
    dashed = [5.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color, 6: group1_color, 7: group2_color, 8: group3_color, 9: group4_color, 10: group5_color, 11: group6_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'], violin_plots_df['group5_baseline_walk_speed_bout_mean'], violin_plots_df['group6_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean'], violin_plots_df['group5_stimulation_walk_speed_bout_mean'], violin_plots_df['group6_stimulation_walk_speed_bout_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_walk_speed_bout_mean'], violin_plots_df['group2_baseline_walk_speed_bout_mean'], violin_plots_df['group3_baseline_walk_speed_bout_mean'], violin_plots_df['group4_baseline_walk_speed_bout_mean'], violin_plots_df['group5_baseline_walk_speed_bout_mean'], violin_plots_df['group6_baseline_walk_speed_bout_mean'],
           violin_plots_df['group1_stimulation_walk_speed_bout_mean'], violin_plots_df['group2_stimulation_walk_speed_bout_mean'], violin_plots_df['group3_stimulation_walk_speed_bout_mean'], violin_plots_df['group4_stimulation_walk_speed_bout_mean'], violin_plots_df['group5_stimulation_walk_speed_bout_mean'], violin_plots_df['group6_stimulation_walk_speed_bout_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)


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
if number_of_groups >= 5:
    axs[0].plot(x_coordinate, line_plots_df['group5_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group5_walk_speed_bout_mean']-line_plots_df['group5_walk_speed_bout_sem']),(line_plots_df['group5_walk_speed_bout_mean']+line_plots_df['group5_walk_speed_bout_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_coordinate, line_plots_df['group6_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group6_walk_speed_bout_mean']-line_plots_df['group6_walk_speed_bout_sem']),(line_plots_df['group6_walk_speed_bout_mean']+line_plots_df['group6_walk_speed_bout_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)
fig.savefig((plot_path+"/"+str(experiment_name)+"_walk_speed.png"), format='png') 
plt.show()




'''Jumps %'''

fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
fig.subplots_adjust(wspace = 0.15)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
axs[1].set_ylim(0, 40)
#axs[1].set_yticks(range(0, 26, 5))
sns.despine(left=True, bottom=True, right=True)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].set_title('Baseline      Stimulation', y=-0.09, fontsize = 16)
if number_of_groups == 1:
    dashed = [0.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group1_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group1_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group1_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 2:
    dashed = [1.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group1_color, 3: group2_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 3:
    dashed = [2.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group1_color, 4: group2_color, 5: group3_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 4:
    dashed = [3.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group1_color, 5: group2_color, 6: group3_color, 7: group4_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 5:
    dashed = [4.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group1_color, 6: group2_color, 7: group3_color, 8: group4_color, 9: group5_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'], violin_plots_df['group5_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean'], violin_plots_df['group5_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'], violin_plots_df['group5_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean'], violin_plots_df['group5_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 6:
    dashed = [5.5]
    axs[1].vlines(dashed, 0, 100, linestyles='-', lw= 0.5)
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color, 6: group1_color, 7: group2_color, 8: group3_color, 9: group4_color, 10: group5_color, 11: group6_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'], violin_plots_df['group5_baseline_jumps_mean'], violin_plots_df['group6_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean'], violin_plots_df['group5_stimulation_jumps_mean'], violin_plots_df['group6_stimulation_jumps_mean']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_baseline_jumps_mean'], violin_plots_df['group2_baseline_jumps_mean'], violin_plots_df['group3_baseline_jumps_mean'], violin_plots_df['group4_baseline_jumps_mean'], violin_plots_df['group5_baseline_jumps_mean'], violin_plots_df['group6_baseline_jumps_mean'],
           violin_plots_df['group1_stimulation_jumps_mean'], violin_plots_df['group2_stimulation_jumps_mean'], violin_plots_df['group3_stimulation_jumps_mean'], violin_plots_df['group4_stimulation_jumps_mean'], violin_plots_df['group5_stimulation_jumps_mean'], violin_plots_df['group6_stimulation_jumps_mean']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)


axs[0].set_ylabel('Jumps %', fontsize = 18)
axs[0].set_xlabel('Time (min)', fontsize = 18)
axs[0].set_xlim(0, limit)
axs[0].set_ylim(0, 10)
#axs[0].set_yticks([0, 5, 10, 15, 20])
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
axs[0].plot(x_coordinate, line_plots_df['group1_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color)
if number_of_groups >= 2:
    axs[0].plot(x_coordinate, line_plots_df['group2_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color)
if number_of_groups >= 3:
    axs[0].plot(x_coordinate, line_plots_df['group3_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[2]) + ' (' + str(number_flies[2])+')'), color=group3_color)
if number_of_groups >= 4:
    axs[0].plot(x_coordinate, line_plots_df['group4_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[3]) + ' (' + str(number_flies[3])+')'), color=group4_color)
if number_of_groups >= 5:
    axs[0].plot(x_coordinate, line_plots_df['group5_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
if number_of_groups == 6:
    axs[0].plot(x_coordinate, line_plots_df['group6_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)
axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)
fig.savefig((plot_path+"/"+str(experiment_name)+"_jumps%.png"), format='png') 
plt.show()


#%%
'''MULTIPLE GROUPS PLOTS DELTAS'''


def multiple_groups_plots_delta(title, behavior):
    fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
    fig.subplots_adjust(wspace = 0.15)

    axs[1].set_facecolor('white')
    axs[1].axes.xaxis.set_visible(False)
    axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
    axs[1].set_axisbelow(True)
    sns.despine(left=True, bottom=True, right=True)
    axs[1].set_title('Delta', y=-0.09, fontsize = 16)
    axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
    if number_of_groups == 1:
        my_pal = {0: group1_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 2:
        my_pal = {0: group1_color, 1: group2_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 3:
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 4:
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 5:
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100, violin_plots_df['group5_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100, violin_plots_df['group5_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
    if number_of_groups == 6:
        my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
        axs[1] =  sns.boxplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100, violin_plots_df['group5_'+behavior+'_mean_delta']*100, violin_plots_df['group6_'+behavior+'_mean_delta']*100), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(violin_plots_df['group1_'+behavior+'_mean_delta']*100, violin_plots_df['group2_'+behavior+'_mean_delta']*100, violin_plots_df['group3_'+behavior+'_mean_delta']*100, violin_plots_df['group4_'+behavior+'_mean_delta']*100, violin_plots_df['group5_'+behavior+'_mean_delta']*100, violin_plots_df['group6_'+behavior+'_mean_delta']*100), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)

    axs[0].set_ylabel(title+' %', fontsize = 18)
    axs[0].set_xlabel('Time (min)', fontsize = 18)
    axs[0].set_xlim(0, limit)
    axs[0].set_ylim(0, 100)
    axs[0].set_yticks([0,20, 40, 60, 80, 100])
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
    axs[0].plot(x_coordinate, line_plots_df['group1_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color)
    if number_of_groups >= 2:
        axs[0].plot(x_coordinate, line_plots_df['group2_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color)
    if number_of_groups >= 3:
        axs[0].plot(x_coordinate, line_plots_df['group3_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[2]) + ' (' + str(number_flies[2])+')'), color=group3_color)
    if number_of_groups >= 4:
        axs[0].plot(x_coordinate, line_plots_df['group4_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[3]) + ' (' + str(number_flies[3])+')'), color=group4_color)
    if number_of_groups >= 5:
        axs[0].plot(x_coordinate, line_plots_df['group5_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
    if number_of_groups == 6:
        axs[0].plot(x_coordinate, line_plots_df['group6_'+behavior+'_mean']*100, 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)
    
    axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

    fig.savefig((plot_path+"/"+str(experiment_name)+'_'+title+'%_deltas.png'), format='png') 
    plt.show()

multiple_groups_plots_delta('Walking', 'walk_bout')
multiple_groups_plots_delta('Freezing', 'freeze_bout')
multiple_groups_plots_delta('Low velocity', 'low_vel_bout')



'''WALKING SPEED'''
fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
fig.subplots_adjust(wspace = 0.15)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=True, bottom=True, right=True)
axs[1].set_title('Delta', y=-0.09, fontsize = 16)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0, zorder=0)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0, zorder=0)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta'], violin_plots_df['group5_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta'], violin_plots_df['group5_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0, zorder=0)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta'], violin_plots_df['group5_walk_speed_bout_mean_delta'], violin_plots_df['group6_walk_speed_bout_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_walk_speed_bout_mean_delta'], violin_plots_df['group2_walk_speed_bout_mean_delta'], violin_plots_df['group3_walk_speed_bout_mean_delta'], violin_plots_df['group4_walk_speed_bout_mean_delta'], violin_plots_df['group5_walk_speed_bout_mean_delta'], violin_plots_df['group6_walk_speed_bout_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0, zorder=0)

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
if number_of_groups >= 5:
    axs[0].plot(x_coordinate, line_plots_df['group5_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group5_walk_speed_bout_mean']-line_plots_df['group5_walk_speed_bout_sem']),(line_plots_df['group5_walk_speed_bout_mean']+line_plots_df['group5_walk_speed_bout_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_coordinate, line_plots_df['group6_walk_speed_bout_mean'], 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)
    axs[0].fill_between(x_coordinate, (line_plots_df['group6_walk_speed_bout_mean']-line_plots_df['group6_walk_speed_bout_sem']),(line_plots_df['group6_walk_speed_bout_mean']+line_plots_df['group6_walk_speed_bout_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)
fig.savefig((plot_path+"/"+str(experiment_name)+"_walk_speed_deltas.png"), format='png') 
plt.show()







'''Jumps %'''

fig, axs = plt.subplots(1, 2, figsize= (15, 6), gridspec_kw={'width_ratios': [3, 1]}, sharey = False)
fig.subplots_adjust(wspace = 0.15)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].yaxis.grid(which='both', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
axs[1].set_ylim(-10, 30)
#axs[1].set_yticks(range(0, 26, 5))
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
sns.despine(left=True, bottom=True, right=True)
axs[1].set_title('Delta', y=-0.09, fontsize = 16)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta'], violin_plots_df['group5_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta'], violin_plots_df['group5_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta'], violin_plots_df['group5_jumps_mean_delta'], violin_plots_df['group6_jumps_mean_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10},
       width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(violin_plots_df['group1_jumps_mean_delta'], violin_plots_df['group2_jumps_mean_delta'], violin_plots_df['group3_jumps_mean_delta'], violin_plots_df['group4_jumps_mean_delta'], violin_plots_df['group5_jumps_mean_delta'], violin_plots_df['group6_jumps_mean_delta']), bw =0.06, linewidth=1.3, width= 0.9, scale='width', inner=None, palette=my_pal, cut=0)


axs[0].set_ylabel('Jumps %', fontsize = 18)
axs[0].set_xlabel('Time (min)', fontsize = 18)
axs[0].set_xlim(0, limit)
axs[0].set_ylim(0, 20)
axs[0].set_yticks([0, 5, 10, 15, 20])
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
axs[0].plot(x_coordinate, line_plots_df['group1_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[0]) + ' (' + str(number_flies[0])+')'), color=group1_color)
if number_of_groups >= 2:
    axs[0].plot(x_coordinate, line_plots_df['group2_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[1]) + ' (' + str(number_flies[1])+')'), color=group2_color)
if number_of_groups >= 3:
    axs[0].plot(x_coordinate, line_plots_df['group3_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[2]) + ' (' + str(number_flies[2])+')'), color=group3_color)
if number_of_groups >= 4:
    axs[0].plot(x_coordinate, line_plots_df['group4_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[3]) + ' (' + str(number_flies[3])+')'), color=group4_color)
if number_of_groups >= 5:
    axs[0].plot(x_coordinate, line_plots_df['group5_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[4]) + ' (' + str(number_flies[4])+')'), color=group5_color)
if number_of_groups == 6:
    axs[0].plot(x_coordinate, line_plots_df['group6_jumps_bout_mean']*100, 'k-', label = (str(groups_labels[5]) + ' (' + str(number_flies[5])+')'), color=group6_color)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)
fig.savefig((plot_path+"/"+str(experiment_name)+"_jumps%_deltas.png"), format='png') 
plt.show()
