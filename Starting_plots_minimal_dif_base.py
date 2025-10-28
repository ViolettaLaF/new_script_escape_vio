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



#Size scale
arena_raio_mm = 15

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

zoom_before_loom_onset = 120
zoom_after_loom_onset = 180

#For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate #every bin is 30 frames 
limit = int(tot_frames/bin_size) # useful for set_xlim in line_plot and % behaviours 
limit_min = int(limit/120) # useful for set_xtick and labels (min is for minutes)
my_label= np.arange(0, limit_min + 1).tolist() #  labels in min

bin_size_zoom_sec = 0.05
bin_size_zoom = bin_size_zoom_sec * frame_rate

#Zoom violin plots data interval selec 
before_loom_start = 60
before_loom_end = int(zoom_before_loom_onset)
before_loom_interval = int(before_loom_end - before_loom_start)

after_loom_start = int(zoom_before_loom_onset + loom_duration)
after_loom_end = int(after_loom_start + before_loom_interval)

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
zoom_line_plots_df = pd.DataFrame()
zoom_violin_plots_df = pd.DataFrame()
delta_behavior_plots_df = pd.DataFrame()
delta_behavior_violins_df = pd.DataFrame()
behavior_onset_df = pd.DataFrame()
speed_behavior_probability_df = pd.DataFrame()
speed_behavior_probability_df['speeds'] = np.array(range(0, 21, 2)) 

startles_per_loom_probabilty_df = pd.DataFrame()
loom_list =  np.array(range(1, number_of_looms+1))
loom_list_doubledigit = []
for i in loom_list:
    double = "{0:0=2d}".format(i)
    loom_list_doubledigit.append(double)
    
startles_per_loom_probabilty_df['loom'] = loom_list_doubledigit
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



#ZOOM AROUND LOOM FUNCTION TO GET MEAN TIME 'BEHAVIOR' DURING BASELINE OR STIMULATION PER FLY
def zoom_violin_plots_variables(variable, behavior, column_df):
    before_variable_behavior = variable[behavior][before_loom_start:before_loom_end].mean(axis=0).reset_index(drop=True)
    after_variable_behavior = variable[behavior][after_loom_start:after_loom_end].mean(axis=0).reset_index(drop=True)
    zoom_violin_plots_df['group'+(str(group_n))+'_'+column_df+'_before'] = before_variable_behavior
    zoom_violin_plots_df['group'+(str(group_n))+'_'+column_df+'_after'] = after_variable_behavior
    zoom_violin_plots_df['group'+(str(group_n))+'_'+column_df+'_delta'] = after_variable_behavior - before_variable_behavior



#ZOOM AROUND LOOM FUNCTION TO GET MEAN TIME 'BEHAVIOR' ACROSS THE GROUP
def zoom_line_plots_variables(variable, behavior, column_df):
    variable[(str(behavior))+'_mean'] = variable[behavior].mean(axis=1)
    variable[(str(behavior))+'_sem'] = variable[behavior].sem(axis=1)
    zoom_line_plots_df['group'+(str(group_n))+'_'+column_df+'_mean'] = (variable[(str(behavior))+'_mean'].groupby(variable.index // bin_size_zoom).mean())
    zoom_line_plots_df['group'+(str(group_n))+'_'+column_df+'_sem'] = (variable[(str(behavior))+'_sem'].groupby(variable.index // bin_size_zoom).mean())
    

#SELECTING FIRST LOOM DATA
def select_first_loom(variable_list):
    first_loom_data = []
    for i in variable_list:
        loom_count = i[-2:]
        if loom_count == '01':
            first_loom_data.append(i)
        
    return first_loom_data

#SELECTING FLIES BASED ON THE BEHAVIOR AROUND LOOM
def same_behavior_around_loom(behavior):
    behaving = []
    switching = []
    for column in behavior:
        if (behavior[column].mean() == 1):
            behaving.append(str(column))
        else:
            switching.append(str(column))
    return behaving, switching
    
def before_loom_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if (behavior[column][3] == 1):
            behaving.append(str(column))
        elif (behavior[column][3] == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving
    
def during_loom_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if ((behavior[column][4:9].sum()) > 0):
            behaving.append(str(column))
        elif ((behavior[column][4:9].sum()) == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving
    
def after_loom_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if (behavior[column][9] == 1):
            behaving.append(str(column))
        elif (behavior[column][9] == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving


#BEHAVIOR ENTRY & EXIT PROBABILITY AROUND LOOM PER FLY
def behavior_probability_around_loom(behavior_before, behavior_after):
    behavior_before_no_loom_count = []
    for i in behavior_before:
        no_loom = i[:-10]
        behavior_before_no_loom_count.append(no_loom)
    remove_duplicates = list(dict.fromkeys(behavior_before_no_loom_count))

    behavior_after_no_loom_count = []
    for i in behavior_after:
        no_loom = i[:-10]
        behavior_after_no_loom_count.append(no_loom)
            
    count_occurences_probability = []
    for i in remove_duplicates:
        counter_before = behavior_before_no_loom_count.count(i)
        counter_after = behavior_after_no_loom_count.count(i)
        count_occurences_probability.append((counter_after/counter_before)*100)
        
    return count_occurences_probability



#BEHAVIOR ENTRY & EXIT PROBABILITY INTER LOOM PER FLY
def inter_loom_after_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if (behavior[column][5] == 1):
            behaving.append(str(column))
        elif (behavior[column][5] == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving
    
def inter_loom_before_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if (behavior[column][9] == 1):
            behaving.append(str(column))
        elif (behavior[column][9] == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving




#DURATION OF BEHAVIOR BOUTS
def behavior_bout_duration(behavior_df, last_index):
    duration_df = pd.DataFrame()
    for column in behavior_df:
        duration_df[column+'_flip'] = behavior_df[column].diff()
        duration_df[column+'_flip'][0] = behavior_df[column][0]
        
    duration_list = []
    for column in duration_df:
        onset = duration_df.loc[duration_df[column]==1].index.values.astype(int)
        offset = duration_df.loc[duration_df[column]==-1].index.values.astype(int)              
        if len(offset) <len(onset):
            offset = np.hstack((offset, last_index))
            
        duration = (offset - onset) / frame_rate
        duration_list.extend(duration)

    duration_list_cleaned = []
    for i in duration_list:
        over = i
        if i > 60:
            over = 60
        duration_list_cleaned.append(over)
            
    return duration_list, duration_list_cleaned    



#BEHAVIOR ONSET AROUND LOOM
def behavior_onset_around_loom(behavior_df, condition):
    onset_df = pd.DataFrame()
    for column in condition:
        onset_df[column+'_flip'] = behavior_df[column].diff()
            
    onset_list = []
    for column in onset_df:
        onset = onset_df.loc[onset_df[column]==1].index.values.astype(int)
        onset_list.extend(onset)
        
    after_loom_onset = []
    for i in onset_list:
        if i > zoom_before_loom_onset:
            after_loom_onset.append(i)
            
    return after_loom_onset



#SPEED-BERHAVIOR DEPENDENCY
def speed_behavior_probability(column_df, notbehavior_before, behavior_after, bin_value):
    notbehaving_x_before_loom_vel = []
    for column in zoom_bined_velocity[notbehavior_before]:
        if zoom_bined_velocity[column][3] > 20:
            vel = 20
        else:
            vel = zoom_bined_velocity[column][3]
        rounded = bin_value * round(vel/bin_value)
        notbehaving_x_before_loom_vel.append(int(rounded))

        
    notbehaving_behaving_before_loom_vel = []
    for column in zoom_bined_velocity[behavior_after]:
        if zoom_bined_velocity[column][3] > 20:
            vel = 20
        else:
            vel = zoom_bined_velocity[column][3]
        rounded = bin_value * round(vel/bin_value)
        notbehaving_behaving_before_loom_vel.append(int(rounded))   
        
    count_occurences_probability = []
    for i in speed_behavior_probability_df['speeds']:
        counter_before = notbehaving_x_before_loom_vel.count(i)
        counter_after = notbehaving_behaving_before_loom_vel.count(i)
        if counter_before == 0:
            count_occurences_probability.append(0)
        else:
            count_occurences_probability.append((counter_after/counter_before)*100)
        
    speed_behavior_probability_df['group'+(str(group_n))+'_'+column_df] = count_occurences_probability
            

def speed_jump_probability(column_df, notbehavior_before, behavior_after, bin_value):
    notbehaving_x_before_loom_vel = []
    for column in zoom_bined_velocity[notbehavior_before]:
        if zoom_bined_velocity[column][3] > 20:
            vel = 20
        else:
            vel = zoom_bined_velocity[column][3]
        rounded = bin_value * round(vel/bin_value)
        notbehaving_x_before_loom_vel.append(int(rounded))

        
    notbehaving_behaving_before_loom_vel = []
    for column in zoom_bined_velocity[behavior_after]:
        if zoom_bined_velocity[column][3] > 20:
            vel = 20
        else:
            vel = zoom_bined_velocity[column][3]
        rounded = bin_value * round(vel/bin_value)
        notbehaving_behaving_before_loom_vel.append(int(rounded))   
        
    count_occurences_probability = []
    for i in speed_behavior_probability_df['speeds']:
        counter_before = notbehaving_x_before_loom_vel.count(i)
        counter_after = notbehaving_behaving_before_loom_vel.count(i)
        counter_all = counter_before + counter_after
        if counter_all == 0:
            count_occurences_probability.append(0)
        else:
            count_occurences_probability.append((counter_after/counter_all)*100)       
                
    speed_behavior_probability_df['group'+(str(group_n))+'_'+column_df] = count_occurences_probability
                 

#Probability of startle per loom normalized by all flies freezing before and after each loom
def startles_per_loom_probabilty(startle_df, startle_list):
    loom_startle = []
    for i in startle_list:
        loom_count = i[-2:]
        loom_startle.append(loom_count)
            
    freezer_per_loom = []
    for i in freezer_x_freezer:
        freezer_loom = i[-2:]
        freezer_per_loom.append(freezer_loom)
        
    count_occurences_probability_per_allflies_freezing = []
    for i in startles_per_loom_probabilty_df['loom']:
        counter_startle = loom_startle.count(i)
        counter_freezer = freezer_per_loom.count(i)
        count_occurences_probability_per_allflies_freezing.append((counter_startle/counter_freezer)*100)

    startles_per_loom_probabilty_df['group'+(str(group_n))+'_all_'+startle_df] = count_occurences_probability_per_allflies_freezing
           

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
    zoom_looming = pd.DataFrame()
    zoom_redled = pd.DataFrame()
    zoom_greenled = pd.DataFrame()
    zoom_fly_x_norm_mm = pd.DataFrame()
    zoom_fly_y_norm_mm = pd.DataFrame()
    zoom_pixelchange = pd.DataFrame()
    zoom_velocity = pd.DataFrame()
    zoom_walk = pd.DataFrame()
    zoom_walk_bout = pd.DataFrame()
    zoom_freeze_bout = pd.DataFrame()
    zoom_jumps = pd.DataFrame()
    zoom_jumps_bout = pd.DataFrame()
    zoom_low_vel = pd.DataFrame()
    zoom_low_vel_bout = pd.DataFrame()
    zoom_pauses = pd.DataFrame()
    zoom_walk_speed = pd.DataFrame()
    zoom_walk_speed_bout = pd.DataFrame()
    zoom_speed2d = pd.DataFrame()
    zoom_pauses_diff = pd.DataFrame()
    inter_looming = pd.DataFrame()
    inter_loom_walk_bout = pd.DataFrame()
    inter_loom_freeze_bout = pd.DataFrame()
    inter_loom_low_vel_bout = pd.DataFrame()
    first_loom_zoom_speed2d = pd.DataFrame()
    
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
        for i in looming_onset[str(flyid)]:
            loom_counter = loom_counter + 1
            zoom_start = i - zoom_before_loom_onset
            zoom_end = i + zoom_after_loom_onset -1
        
            zoom_looming[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['looming_bout'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_redled[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['redled'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_greenled[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['greenled'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_fly_x_norm_mm[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['fly_x_norm_mm'].loc[zoom_start:zoom_end].values.astype(float)
            zoom_fly_y_norm_mm[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['fly_y_norm_mm'].loc[zoom_start:zoom_end].values.astype(float)
            zoom_pixelchange[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['pixelchange'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_velocity[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['velocity'].loc[zoom_start:zoom_end].values.astype(float)
            zoom_walk[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['walk'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_walk_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['walk_bout'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_freeze_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['freeze_bout'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_jumps[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['jumps'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_jumps_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['jumps_bout'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_low_vel[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['low_vel'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_low_vel_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['low_vel_bout'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_pauses[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['pauses'].loc[zoom_start:zoom_end].values.astype(int)
            zoom_walk_speed[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['walk_speed'].loc[zoom_start:zoom_end].values.astype(float)
            zoom_walk_speed_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['walk_speed_bout'].loc[zoom_start:zoom_end].values.astype(float)
            zoom_speed2d[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['speed2d'].loc[zoom_start:zoom_end].values.astype(float)
            if loom_counter == 1:
                  first_loom_zoom_speed2d[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['speed2d'].loc[zoom_start:zoom_end].values.astype(float)      
            
            zoom_pauses_diff[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['pauses_flip'].loc[zoom_start:zoom_end].values.astype(int)
            for i in range(len(zoom_pauses_diff)):
                if zoom_pauses_diff[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))][i]==1:
                    pauses_loom_onset.append(i)
        
        looming_onset_extended = looming_onset.copy()
        looming_onset_extended.loc[number_of_looms] = baseline_frames + stimulation_frames -1


        loom_counter = 0
        for i in range(0,number_of_looms):
            loom_counter = loom_counter + 1
            start = looming_onset_extended[str(flyid)][i]
            end = looming_onset_extended[str(flyid)][i+1]
            
            after_loom_looming = looming[str(flyid)].loc[start:start+zoom_after_loom_onset-1].values.tolist()
            before_loom_looming = looming[str(flyid)].loc[end-zoom_before_loom_onset:end-1].values.tolist()
            looming_list = after_loom_looming.copy()
            looming_list.extend(before_loom_looming)
            inter_looming[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = pd.Series(looming_list)
            
            after_loom_walk_bout = walk_bout[str(flyid)].loc[start:start+zoom_after_loom_onset-1].values.tolist()
            before_loom_walk_bout = walk_bout[str(flyid)].loc[end-zoom_before_loom_onset:end-1].values.tolist()
            walk_bout_list = after_loom_walk_bout.copy()
            walk_bout_list.extend(before_loom_walk_bout)
            inter_loom_walk_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = pd.Series(walk_bout_list)
            
            after_loom_freeze_bout = freeze_bout[str(flyid)].loc[start:start+zoom_after_loom_onset-1].values.tolist()
            before_loom_freeze_bout = freeze_bout[str(flyid)].loc[end-zoom_before_loom_onset:end-1].values.tolist()
            freeze_bout_list = after_loom_freeze_bout.copy()
            freeze_bout_list.extend(before_loom_freeze_bout)
            inter_loom_freeze_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = pd.Series(freeze_bout_list)
            
            after_loom_low_vel_bout = low_vel_bout[str(flyid)].loc[start:start+zoom_after_loom_onset-1].values.tolist()
            before_loom_low_vel_bout = low_vel_bout[str(flyid)].loc[end-zoom_before_loom_onset:end-1].values.tolist()
            low_vel_bout_list = after_loom_low_vel_bout.copy()
            low_vel_bout_list.extend(before_loom_low_vel_bout)
            inter_loom_low_vel_bout[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = pd.Series(low_vel_bout_list)
            

            
    number_flies.append(len(looming.columns))
    number_looms.append(len(zoom_looming.columns))
    number_inter_looms = len(inter_looming.columns)
    
    
    
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
    
    zoom_bined_looming = (zoom_looming.groupby(zoom_walk_bout.index // bin_size).mean()).round(0)
    zoom_bined_velocity = (zoom_velocity.groupby(zoom_velocity.index // bin_size).mean()).round(0)
    zoom_bined_walk_bout = (zoom_walk_bout.groupby(zoom_walk_bout.index // bin_size).mean())
    zoom_bined_freeze_bout = (zoom_freeze_bout.groupby(zoom_freeze_bout.index // bin_size).mean())
    zoom_bined_low_vel_bout = (zoom_low_vel_bout.groupby(zoom_low_vel_bout.index // bin_size).mean())
    zoom_bined_jumps_bout = (zoom_jumps_bout.groupby(zoom_jumps_bout.index // bin_size).mean())
    zoom_bined_pauses = (zoom_pauses.groupby(zoom_pauses.index // bin_size).mean())
    zoom_bined_fly_x_norm_mm = (zoom_fly_x_norm_mm.groupby(zoom_fly_x_norm_mm.index // bin_size).mean())
    zoom_bined_fly_y_norm_mm = (zoom_fly_y_norm_mm.groupby(zoom_fly_y_norm_mm.index // bin_size).mean())
    inter_loom_looming_bined = (inter_looming.groupby(inter_looming.index // bin_size).mean())
    inter_loom_walk_bout_bined = (inter_loom_walk_bout.groupby(inter_loom_walk_bout.index // bin_size).mean())
    inter_loom_freeze_bout_bined = (inter_loom_freeze_bout.groupby(inter_loom_freeze_bout.index // bin_size).mean())
    inter_loom_low_vel_bout_bined = (inter_loom_low_vel_bout.groupby(inter_loom_low_vel_bout.index // bin_size).mean())
    
    
    '''BASELINE - STIMULATION VARIABLES '''
    
    walk_bout_baseline = walk_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    walk_bout_stimulation = walk_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)
    freeze_bout_baseline = freeze_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    freeze_bout_stimulation = freeze_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)
    low_vel_bout_baseline = low_vel_bout[:baseline_frames].drop(columns=['mean', 'sem']).reset_index(drop=True)
    low_vel_bout_stimulation = low_vel_bout[baseline_frames:].drop(columns=['mean', 'sem']).reset_index(drop=True)



#%%  

    '''SELECTING FLIES DEPENDENT ON THE BEHAVIOR BEFORE AND AFTER LOOM - 0.5SEC-0SEC BEFORE LOOM ONSET & 2.5SEC-3SEC AFTER LOOM ONSET'''
    
    walker_all, walker_break = same_behavior_around_loom(zoom_bined_walk_bout)
    freezer_all, freezer_break = same_behavior_around_loom(zoom_bined_freeze_bout)
    low_vel_all, low_vel_break = same_behavior_around_loom(zoom_bined_low_vel_bout)
    
    walker_x_x, notwalker_x_x = before_loom_behavior(zoom_bined_walk_bout)
    freezer_x_x, notfreezer_x_x = before_loom_behavior(zoom_bined_freeze_bout)
    low_vel_x_x, notlow_vel_x_x = before_loom_behavior(zoom_bined_low_vel_bout)
    
    walker_x_walker, walker_x_notwalker = after_loom_behavior(zoom_bined_walk_bout[walker_x_x])
    freezer_x_freezer, freezer_x_notfreezer = after_loom_behavior(zoom_bined_freeze_bout[freezer_x_x])
    low_vel_x_low_vel, low_vel_x_notlow_vel = after_loom_behavior(zoom_bined_low_vel_bout[low_vel_x_x])

    notwalker_x_walker, notwalker_x_notwalker = after_loom_behavior(zoom_bined_walk_bout[notwalker_x_x])
    notfreezer_x_freezer, notfreezer_x_notfreezer = after_loom_behavior(zoom_bined_freeze_bout[notfreezer_x_x])
    notlow_vel_x_low_vel, notlow_vel_x_notlow_vel = after_loom_behavior(zoom_bined_low_vel_bout[notlow_vel_x_x])

    walker_pauser_walker, walker_notpauser_walker = during_loom_behavior(zoom_bined_pauses[walker_x_walker])
    walker_pauser_x, walker_notpauser_x = during_loom_behavior(zoom_bined_pauses[walker_x_x])
    walker_pauser_jumper_x, walker_pauser_notjumper_x = during_loom_behavior(zoom_bined_jumps_bout[walker_pauser_x])
    
    walker_x_freezer, walker_x_notfreezer = after_loom_behavior(zoom_bined_freeze_bout[walker_x_x])
    walker_pauser_freezer, walker_notpauser_freezer = during_loom_behavior(zoom_bined_pauses[walker_x_freezer])
    walker_jumper_freezer, walker_notjumper_freezer = during_loom_behavior(zoom_bined_jumps_bout[walker_x_freezer])
    
    walker_jumper_x, walker_notjumper_x = during_loom_behavior(zoom_bined_jumps_bout[walker_x_x])
    walker_jumper_pauser_x, walker_jumper_notpauser_x = during_loom_behavior(zoom_bined_pauses[walker_jumper_x]) 
    walker_jumper_walker, walker_notjumper_walker = during_loom_behavior(zoom_bined_jumps_bout[walker_x_walker])

    freezer_jumper_x, freezer_notjumper_x = during_loom_behavior(zoom_bined_jumps_bout[freezer_x_x])


    x_jumper_x, x_notjumper_x = during_loom_behavior(zoom_bined_jumps_bout)
    notfreezer_jumper_freezer, notfreezer_notjumper_freezer = during_loom_behavior(zoom_bined_jumps_bout[notfreezer_x_freezer])
    notfreezer_jumper_notfreezer, notfreezer_notjumper_notfreezer = during_loom_behavior(zoom_bined_jumps_bout[notfreezer_x_notfreezer])
    notfreezer_jumper_x, notfreezer_notjumper_x = during_loom_behavior(zoom_bined_jumps_bout[notfreezer_x_x])
    
    x_jumper_freezer, x_jumper_notfreezer = after_loom_behavior(zoom_bined_freeze_bout[x_jumper_x])
    x_notjumper_freezer, x_notjumper_notfreezer = after_loom_behavior(zoom_bined_freeze_bout[x_notjumper_x])
    
    
    startler_jumps = []
    startler_walk = []
    startler_low_vel = []
    for column in zoom_bined_freeze_bout:
        if (zoom_bined_freeze_bout[column][3] == 1) & (zoom_bined_freeze_bout[column][9] == 1) & (zoom_bined_freeze_bout[column].mean() != 1):
            if(zoom_bined_jumps_bout[column][4:9].sum()) > 0:
                startler_jumps.append(str(column))
            else:
                if(zoom_bined_walk_bout[column][4:9].sum()) > 0:
                    startler_walk.append(str(column))
                else:
                    startler_low_vel.append(str(column))

#%%
                    
    '''ZOOM PLOTS VARIABLES'''

    zoom_violin_plots_variables(zoom_speed2d, walker_x_walker, 'zoom_speed2d_walker_x_walker')
    zoom_violin_plots_variables(zoom_speed2d, walker_x_notwalker, 'zoom_speed2d_walker_x_notwalker')
    zoom_violin_plots_variables(zoom_speed2d, walker_x_freezer, 'zoom_speed2d_walker_x_freezer')
    zoom_violin_plots_variables(zoom_speed2d, walker_x_notfreezer, 'zoom_speed2d_walker_x_notfreezer')
    zoom_violin_plots_variables(zoom_speed2d, walker_jumper_x, 'zoom_speed2d_walker_jumper_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_notjumper_x, 'zoom_speed2d_walker_notjumper_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_pauser_x, 'zoom_speed2d_walker_pauser_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_notpauser_x, 'zoom_speed2d_walker_notpauser_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_pauser_walker, 'zoom_speed2d_walker_pauser_walker')
    zoom_violin_plots_variables(zoom_speed2d, walker_notpauser_walker, 'zoom_speed2d_walker_notpauser_walker')  
    zoom_violin_plots_variables(zoom_speed2d, walker_pauser_jumper_x, 'zoom_speed2d_walker_pauser_jumper_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_pauser_notjumper_x, 'zoom_speed2d_walker_pauser_notjumper_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_jumper_pauser_x, 'zoom_speed2d_walker_jumper_pauser_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_jumper_notpauser_x, 'zoom_speed2d_walker_jumper_notpauser_x')
    zoom_violin_plots_variables(zoom_speed2d, walker_jumper_freezer, 'zoom_speed2d_walker_jumper_freezer')
    zoom_violin_plots_variables(zoom_speed2d, walker_notjumper_freezer, 'zoom_speed2d_walker_notjumper_freezer')
    zoom_violin_plots_variables(zoom_speed2d, walker_notjumper_walker, 'zoom_speed2d_walker_notjumper_walker')

    zoom_line_plots_variables(zoom_speed2d, walker_x_walker, 'zoom_speed2d_walker_x_walker')
    zoom_line_plots_variables(zoom_speed2d, walker_x_notwalker, 'zoom_speed2d_walker_x_notwalker')
    zoom_line_plots_variables(zoom_speed2d, walker_x_freezer, 'zoom_speed2d_walker_x_freezer')
    zoom_line_plots_variables(zoom_speed2d, walker_x_notfreezer, 'zoom_speed2d_walker_x_notfreezer')
    zoom_line_plots_variables(zoom_speed2d, walker_jumper_x, 'zoom_speed2d_walker_jumper_x')
    zoom_line_plots_variables(zoom_speed2d, walker_notjumper_x, 'zoom_speed2d_walker_notjumper_x')
    zoom_line_plots_variables(zoom_speed2d, walker_pauser_x, 'zoom_speed2d_walker_pauser_x')
    zoom_line_plots_variables(zoom_speed2d, walker_notpauser_x, 'zoom_speed2d_walker_notpauser_x')
    zoom_line_plots_variables(zoom_speed2d, walker_pauser_walker, 'zoom_speed2d_walker_pauser_walker')
    zoom_line_plots_variables(zoom_speed2d, walker_notpauser_walker, 'zoom_speed2d_walker_notpauser_walker')  
    zoom_line_plots_variables(zoom_speed2d, walker_pauser_jumper_x, 'zoom_speed2d_walker_pauser_jumper_x')
    zoom_line_plots_variables(zoom_speed2d, walker_pauser_notjumper_x, 'zoom_speed2d_walker_pauser_notjumper_x')
    zoom_line_plots_variables(zoom_speed2d, walker_jumper_pauser_x, 'zoom_speed2d_walker_jumper_pauser_x')
    zoom_line_plots_variables(zoom_speed2d, walker_jumper_notpauser_x, 'zoom_speed2d_walker_jumper_notpauser_x')
    zoom_line_plots_variables(zoom_speed2d, walker_jumper_freezer, 'zoom_speed2d_walker_jumper_freezer')
    zoom_line_plots_variables(zoom_speed2d, walker_notjumper_freezer, 'zoom_speed2d_walker_notjumper_freezer')
    zoom_line_plots_variables(zoom_speed2d, walker_notjumper_walker, 'zoom_speed2d_walker_notjumper_walker')
    zoom_line_plots_variables(zoom_pixelchange, freezer_all, 'zoom_pixelchange_freezer_all')
    zoom_line_plots_variables(zoom_pixelchange, startler_jumps, 'zoom_pixelchange_startler_jumps')
    zoom_line_plots_variables(zoom_pixelchange, startler_walk, 'zoom_pixelchange_startler_walk')
    zoom_line_plots_variables(zoom_pixelchange, startler_low_vel, 'zoom_pixelchange_startler_low_vel')

    zoom_walk_bout['mean'] = zoom_walk_bout.mean(axis=1)
    zoom_freeze_bout['mean'] = zoom_freeze_bout.mean(axis=1)
    zoom_low_vel_bout['mean'] = zoom_low_vel_bout.mean(axis=1)
    zoom_jumps_bout['mean'] = zoom_jumps_bout.mean(axis=1)


#%%%
    
    '''FIRST LOOM ZOOM PLOTS'''
    
    first_loom_walker_x_walker = select_first_loom(walker_x_walker)
    first_loom_walker_x_notwalker = select_first_loom(walker_x_notwalker)
    first_loom_walker_x_freezer = select_first_loom(walker_x_freezer)
    first_loom_walker_x_notfreezer = select_first_loom(walker_x_notfreezer)
    first_loom_walker_jumper_x = select_first_loom(walker_jumper_x)
    first_loom_walker_notjumper_x = select_first_loom(walker_notjumper_x)
    first_loom_walker_pauser_x = select_first_loom(walker_pauser_x)
    first_loom_walker_notpauser_x = select_first_loom(walker_notpauser_x)
    first_loom_walker_pauser_walker = select_first_loom(walker_pauser_walker)
    first_loom_walker_notpauser_walker = select_first_loom(walker_notpauser_walker)
    first_loom_walker_pauser_jumper_x = select_first_loom(walker_pauser_jumper_x)
    first_loom_walker_pauser_notjumper_x = select_first_loom(walker_pauser_notjumper_x)
    first_loom_walker_jumper_pauser_x = select_first_loom(walker_jumper_pauser_x)
    first_loom_walker_jumper_notpauser_x = select_first_loom(walker_jumper_notpauser_x)
    first_loom_walker_jumper_freezer = select_first_loom(walker_jumper_freezer)
    first_loom_walker_notjumper_freezer = select_first_loom(walker_notjumper_freezer)
    first_loom_walker_notjumper_walker = select_first_loom(walker_notjumper_walker)

    
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_walker, 'first_loom_zoom_speed2d_walker_x_walker')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_notwalker, 'first_loom_zoom_speed2d_walker_x_notwalker')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_freezer, 'first_loom_zoom_speed2d_walker_x_freezer')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_notfreezer, 'first_loom_zoom_speed2d_walker_x_notfreezer')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_x, 'first_loom_zoom_speed2d_walker_jumper_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_x, 'first_loom_zoom_speed2d_walker_notjumper_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_x, 'first_loom_zoom_speed2d_walker_pauser_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notpauser_x, 'first_loom_zoom_speed2d_walker_notpauser_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_walker, 'first_loom_zoom_speed2d_walker_pauser_walker')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notpauser_walker, 'first_loom_zoom_speed2d_walker_notpauser_walker')  
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_jumper_x, 'first_loom_zoom_speed2d_walker_pauser_jumper_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_notjumper_x, 'first_loom_zoom_speed2d_walker_pauser_notjumper_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_pauser_x, 'first_loom_zoom_speed2d_walker_jumper_pauser_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_notpauser_x, 'first_loom_zoom_speed2d_walker_jumper_notpauser_x')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_freezer, 'first_loom_zoom_speed2d_walker_jumper_freezer')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_freezer, 'first_loom_zoom_speed2d_walker_notjumper_freezer')
    zoom_violin_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_walker, 'first_loom_zoom_speed2d_walker_notjumper_walker')

    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_walker, 'first_loom_zoom_speed2d_walker_x_walker')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_notwalker, 'first_loom_zoom_speed2d_walker_x_notwalker')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_freezer, 'first_loom_zoom_speed2d_walker_x_freezer')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_x_notfreezer, 'first_loom_zoom_speed2d_walker_x_notfreezer')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_x, 'first_loom_zoom_speed2d_walker_jumper_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_x, 'first_loom_zoom_speed2d_walker_notjumper_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_x, 'first_loom_zoom_speed2d_walker_pauser_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notpauser_x, 'first_loom_zoom_speed2d_walker_notpauser_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_walker, 'first_loom_zoom_speed2d_walker_pauser_walker')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notpauser_walker, 'first_loom_zoom_speed2d_walker_notpauser_walker')  
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_jumper_x, 'first_loom_zoom_speed2d_walker_pauser_jumper_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_pauser_notjumper_x, 'first_loom_zoom_speed2d_walker_pauser_notjumper_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_pauser_x, 'first_loom_zoom_speed2d_walker_jumper_pauser_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_notpauser_x, 'first_loom_zoom_speed2d_walker_jumper_notpauser_x')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_jumper_freezer, 'first_loom_zoom_speed2d_walker_jumper_freezer')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_freezer, 'first_loom_zoom_speed2d_walker_notjumper_freezer')
    zoom_line_plots_variables(first_loom_zoom_speed2d, first_loom_walker_notjumper_walker, 'first_loom_zoom_speed2d_walker_notjumper_walker')
    

#%%
    
    '''HEATMAPS VARIABLES'''
    heatmap_col_order = (freeze_bout_bined[(int(baseline_frames/bin_size)):] == 1).sum().sort_values(ascending=False).index.values.tolist()

    velocity_sorted = velocity_bined[heatmap_col_order]
    freezing_sorted = freeze_bout_bined[heatmap_col_order]
    jumps_sorted = jumps_bined[heatmap_col_order]
    freezing_pops = np.ma.masked_equal(freezing_sorted, 1)
    
 
    '''INDIVIDUAL GROUP PLOTS'''
    
    median_loom_onset = looming_onset.median(axis=1)
    median_loom_offset =looming_offset.median(axis=1)
    median_loom = (median_loom_onset+median_loom_offset)/2

    loom_coordinate = [(i/bin_size) for i in median_loom]
    x_coordinate = [i for i in range(len(line_plots_df))]
#%%
    '''Behaviors %'''

    fig, axs = plt.subplots(figsize= (12, 7))
    axs.set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(looming.columns)-1) + ')', fontsize = 20)
    axs.set_ylabel(('Behaviors %'), fontsize = 18)
    axs.set_xlabel(('Time (min)'), fontsize = 18)
    axs.set_xlim(0, limit)
    axs.set_ylim(0, 100)
    axs.set_yticks([0,20, 40, 60, 80, 100])
    axs.set_xticks(np.arange(0, limit+1, 120))#so it's flexible for experiment with different lenght 
    axs.set_xticklabels(my_label) #I commented here so it's flexible for experiment with different lenght 
    axs.spines['left'].set_visible(True)
    axs.spines['bottom'].set_visible(True)
    axs.spines['right'].set_visible(False)
    axs.spines['top'].set_visible(False)
    axs.spines['left'].set_position(('outward', 5))
    axs.spines['bottom'].set_position(('outward', 5))
    axs.spines['left'].set_color('dimgrey')
    axs.spines['bottom'].set_color('dimgrey')
    axs.tick_params(axis='x', colors = 'k', labelsize=16)
    axs.tick_params(axis='y', colors = 'k', labelsize=16)
    axs.xaxis.label.set_color('k')
    axs.yaxis.label.set_color('k')
    plt.plot(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_4']*100, color=walk_color, label = ('Walking'))
    plt.fill_between(x_coordinate, 0, line_plots_df['group'+(str(group_n))+'_cumulative_bout_4']*100, color=walk_color, alpha=0.7)
    plt.plot(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_3']*100, color=low_vel_color, label = ('Low Vel'))
    plt.fill_between(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_4']*100, line_plots_df['group'+(str(group_n))+'_cumulative_bout_3']*100, color=low_vel_color, alpha=0.7)
    plt.plot(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_2']*100, color=jump_color, label = ('Freezing'))
    plt.fill_between(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_3']*100, line_plots_df['group'+(str(group_n))+'_cumulative_bout_2']*100, color=freeze_color, alpha=0.6)
    plt.plot(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_1']*100, color=jump_color, label = ('Jumping'))
    plt.fill_between(x_coordinate, line_plots_df['group'+(str(group_n))+'_cumulative_bout_2']*100, line_plots_df['group'+(str(group_n))+'_cumulative_bout_1']*100, color=jump_color)
    axs.vlines(loom_coordinate, 0, 100, linestyles='--', lw= 1, color='grey')
    axs.legend(loc="lower left", frameon = True, fontsize = 15, framealpha=0.3)
    leg= axs.get_legend()
    leg.legendHandles[2].set_color('darkcyan')
    fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+"_behaviors%.png"), format='png') 
    plt.show()

#%%
    '''HEATMAPS'''

    fig, axs = plt.subplots(figsize=(15, 15))
    axs.xaxis.set_visible(False)
    axs.yaxis.set_visible(False)
    axs.set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(looming.columns)-1) + ')', fontsize = 20)
    axs.vlines(loom_coordinate, -6, 500, linestyles='-', lw= 0.5, color='white')
    sns.heatmap(np.transpose(freezing_sorted), cmap="Greys" , cbar=False, alpha = 0.35, linewidths=0)
    sns.heatmap(np.transpose(velocity_sorted), mask=np.transpose(freezing_pops), cmap='viridis', vmin=0, vmax=20, cbar=False, linewidths=0)
    fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+"_heatmap.png"), format='png') 
    plt.show()

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
#%%
'''ZOOM LINE PLOTS'''
"""
yticksteps1 = 5
yticksteps2 = 10 

fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
fig.subplots_adjust(wspace = 0.2)

#Delta violin plot
list_to_plot1 = []
list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_delta')].values.tolist())
list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_delta')].values.tolist())
y_max = int(round(np.nanmax(list_to_plot1)))
y_max1 = (5) * round(y_max/(5))
y_min = int(round(np.nanmin(list_to_plot1)))
y_min1 = (5) * round(y_min/(5)) 
axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].set_title('Delta', y=-0.095, fontsize = 18)
axs[1].set_ylim((y_min1)-(yticksteps2), (y_max1)+(yticksteps2))
axs[1].set_yticks(range(int((y_min1)-(yticksteps2)), int((y_max1)+(yticksteps2)), yticksteps2))
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=False, bottom=True, right=True)
my_pal = {0: jump_color, 1: freeze_color}
axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_delta']), palette=my_pal, 
   boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
   medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

#Line plot
list_to_plot0 = []
list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_mean')].values.tolist())
list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_mean')].values.tolist())
list_to_plot0 = [x for x in list_to_plot0 if x == x]
y_max = int(round(np.nanmax(list_to_plot0)))
y_max1 = int((yticksteps1) * round(y_max/(yticksteps1)))
y_min = int(round(np.nanmin(list_to_plot0)))
y_min1 = int((yticksteps1) * round(y_min/(yticksteps1)))
axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (sec)', fontsize = 18)
#axs[0].set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(zoom_looming.columns)) + ')' + str(title), fontsize = 20)
axs[0].set_xlim(10, 100)
axs[0].set_ylim(y_min1-1, y_max1+(yticksteps1))
#axs[0].set_yticks(range(y_minuse, y_max1+yticksteps1, yticksteps1))
axs[0].set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
axs[0].set_xticklabels([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3])
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
axs[0].vlines(loom_zoom_coordinate, 0, 25, linestyles='--', lw= 1, color='grey')
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_mean')], 'k-', label = (str('Jumper')+'  (' + str(len(first_loom_walker_jumper_freezer))+')'), color=jump_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_jumper_freezer'+'_sem']), color=jump_color, alpha=0.3)
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_mean')], 'k-', label = (str('Not jumper')+'  (' + str(len(first_loom_walker_notjumper_freezer))+')'), color=freeze_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_'+'first_loom_zoom_speed2d_walker_notjumper_freezer'+'_sem']), color=freeze_color, alpha=0.3)
axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

plt.show()
    
"""
