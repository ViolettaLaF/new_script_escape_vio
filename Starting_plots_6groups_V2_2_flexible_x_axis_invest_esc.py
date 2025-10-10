# -*- coding: utf-8 -*- in this version solved bin problem and all the zerodivision error and max(nan)!!! So this code should always works
#contain for the zoom plots of walking speed 10 second windows first 5 looms and last 5 looms!
"""
Created on Wed Nov 11 19:16:08 2020

@author: Matheus Farias




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
import math


#%%%

'''
EXPERIMENT PARAMETERS
'''
#
number_of_groups = 2
experiment_name = '39347_DH44_RNAi_KK-5minbase' ##nsyb_DH44_RNAi_KK' #'#'DH44_RNAi_kk_fresh' #'DH44_RNAi_VDRC_control' #'39347_DH44_RNAi' #'39347_tnt_vs_empty' #for group figure names


#GROUP NAME = FILE NAME START
group1 = 'VLF-39347_GFP_RNAi_KK-5minbase' #'VLF-CS_nsyb_gal4_GFP_RNAi' #'VLF-DH44gal4_DH44_RNAi_TRIP-1base' #'VLF-CSHF_DH44gal4_DH44_RNAi_VDRC'#'VLF-CSHF_DH44gal4_DH44_RNAi_VDRC' #'VLF-Tsh_39347_Gtacr1-20Looms'#  
group2 = 'VLF-39347_DH44_RNAi_KK-5minbase' #VLF-CS_nsyb_gal4_DH44_RNAi'#'VLF-DH44gal4_luc_RNAi_TRIP-1base' #'VLF-CSHF_DH44gal4_GFP_RNAi_VDRC' #'VLF-CSHF_DH44_RNAi_VDRC' #'VLF-Tsh_39347_Gtacr1-green_LED_all_stimulation'
group3 = 'VLF-DH44_PI_gal4_luc_RNAi'# #'VLF-CSHF_DH44_RNAi_VDRC' #'VLF-CSHF_GFP_RNAi_VDRC' # 'VLF-39347_DH44_RNAi_male'
group4 = 'VLF-DH44_PI_gal4_DH44_RNAi' #'VLF-CSHF_DH44gal4-5base'#'VLF-39347_luc_RNAi_male'
group5 = 'VLF-39347_luc_RNAi_male'
group6 = 'MF-LPLC2'

#Plots labels
#group1_label = 'Empty TNT'
group1_label = '39347_luc_RNAi_TRIP-5minbase'#'nsyb_gal4_GFP_RNAi'#'DH44gal4_DH44_RNAi_TRIP' #'DH44gal4_DH44_RNAi_VDRC' #'Tsh_39347_Gtacr1-LED-OFF'#'39347_DH44_RNAi_fem' #'39347_DH44_RNAi'#'DH44_gal4_tnt'#'39347-cytGFP' 
group2_label = '39347_DH44_RNAi_TRIP-5minbase'#'39347_tsh_gal80_DH44_RNAi_KK-5minbase' #'nsyb_gal4_DH44_RNAi'#'DH44gal4_luc_RNAi_TRIP' #'DH44_RNAi_VDRC' #'Tsh_39347_Gtacr1-LED_ON_stimulation'#'39347_luc_RNAi_fem' #'39347_luc_RNAi' #'Empty_TNT'#'Empty Attp2'
group3_label = 'DH44_PI_gal4_luc_RNAi'# #'GFP_RNAi_VDRC' #'39347_DH44_RNAi_male'
group4_label = 'DH44_PI_gal4_DH44_RNAi'# #'DH44gal4' #'VLF-39347_luc_RNAi_male'
group5_label = 'TH_GAL80_39347_luc_RNAi_TRIP'
group6_label = 'LPLC2 TNT'


#Change colors here
group1_color = 'C0' # 'firebrick'    
group2_color = 'C1' #'C1' #'firebrick'#'dimgrey' #'rosybrown'
group3_color = 'C7' # #'indigo'#'royalblue'#'goldenrod'
group4_color = 'firebrick' #'C7' #'skyblue'#'dimgrey'#'indigo'
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
baseline  = 300#
stimulation = 300 #600
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

zoom_before_loom_onset = 120 #is in frames
zoom_after_loom_onset = 600 #BE CAREFULL ORIGINALLY IS 180, I CHANGED BECAUSE I WANT TO PLOT TILL 10 SEC AFTER!! 

#For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate

bin_size_zoom_sec = 0.05
bin_size_zoom = bin_size_zoom_sec * frame_rate #3 FRAMES

#Zoom violin plots data interval selec 
before_loom_start = 60
before_loom_end = int(zoom_before_loom_onset)
before_loom_interval = int(before_loom_end - before_loom_start)

after_loom_start = int(zoom_before_loom_onset + loom_duration)
after_loom_end = int(after_loom_start + before_loom_interval)

#Upper treshold for speed 2D
jump_velocity = 75

#just useful for have correct size for the line plot and percentage behaviours
limit = tot_frame/bin_size

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

# SELECTING FIRST 5 LOOMS
def select_first_5_looms(variable_list):
    first5_loom_data = []
    for i in variable_list:
        loom_count = int(i[-2:])  # convert to int so '01' -> 1
        if 1 <= loom_count <= 5:
            first5_loom_data.append(i)
    return first5_loom_data

# SELECTING LAST 5 LOOMS
def select_last_5_looms(variable_list):
    # find the maximum loom number present
    loom_numbers = [int(i[-2:]) for i in variable_list]
    max_loom = max(loom_numbers)

    last5_loom_data = []
    for i in variable_list:
        loom_count = int(i[-2:])
        if loom_count > max_loom - 5:
            last5_loom_data.append(i)
    return last5_loom_data

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
        if (behavior[column][3] == 1): #what means 3???
            behaving.append(str(column)) 
        elif (behavior[column][3] == 0):
            notbehaving.append(str(column))
    return behaving, notbehaving
    
def during_loom_behavior(behavior):
    behaving = []
    notbehaving = []
    for column in behavior:
        if ((behavior[column][4:9].sum()) > 0): #what means 4 and 9???
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
        if counter_freezer != 0:
            count_occurences_probability_per_allflies_freezing.append((counter_startle/counter_freezer)*100)
        else:
            count_occurences_probability_per_allflies_freezing.append(0)

    startles_per_loom_probabilty_df['group'+(str(group_n))+'_all_'+startle_df] = count_occurences_probability_per_allflies_freezing


#function to solve binning problem assign loom - assign 1 only to the first occurrence of the maximum value within each subsequent sequence of non-zero values           
def assign_max_to_sequence(series):
    result = []
    non_zero_sequence = []  # To store the non-zero values in the current sequence

    for value in series:
        if value != 0:
            non_zero_sequence.append(value)  # Add non-zero values to the current sequence
        else:
            # If the sequence is not empty, assign 1 to the maximum value in the sequence
            if non_zero_sequence:
                max_value = max(non_zero_sequence)
                # Assign 1 only to the first occurrence of the maximum value in the sequence
                first_max_index = non_zero_sequence.index(max_value)
                result.extend([1 if i == first_max_index else 0 for i in range(len(non_zero_sequence))])
                non_zero_sequence = []  # Reset the sequence
            result.append(0)  # Add 0 for the current zero value

    # Handle the case where the series ends with a non-zero sequence
    if non_zero_sequence:
        max_value = max(non_zero_sequence)
        # Assign 1 only to the first occurrence of the maximum value in the sequence
        first_max_index = non_zero_sequence.index(max_value)
        result.extend([1 if i == first_max_index else 0 for i in range(len(non_zero_sequence))])

    return pd.Series(result)
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
    first_5_loom_zoom_speed2d = pd.DataFrame() 
    last_5_loom_zoom_speed2d = pd.DataFrame() 
    
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
        fly_df.loc[(fly_df['walk'] == 1), 'walk_speed'] = fly_df['velocity']
        walk_speed[str(flyid)] = fly_df['walk_speed']

        fly_df['walk_speed_bout'] = np.nan
        fly_df.loc[(fly_df['walk_bout'] == 1), 'walk_speed_bout'] = fly_df['velocity']
        walk_speed_bout[str(flyid)] = fly_df['walk_speed_bout']
        
        fly_df['speed2d'] = np.nan
        fly_df.loc[(fly_df['velocity'] < jump_velocity), 'speed2d'] = fly_df['velocity']
        fly_df.loc[(fly_df['velocity'] >= jump_velocity), 'speed2d'] = 75
    
    
        fly_df['pauses_flip'] = fly_df['pauses'].diff()
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
            
            if loom_counter <= 5: 
                  first_5_loom_zoom_speed2d[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['speed2d'].loc[zoom_start:zoom_end].values.astype(float)                  

            if loom_counter > 15: 
                  last_5_loom_zoom_speed2d[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['speed2d'].loc[zoom_start:zoom_end].values.astype(float)                  
            
            zoom_pauses_diff[str(flyid)+'_loom_n='+str("{0:0=2d}".format(loom_counter))] = fly_df['walk_speed_bout'].loc[zoom_start:zoom_end].values.astype(int)
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
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = looming['mean'].groupby(looming.index // bin_size).mean()
    #line_plots_df['group'+(str(group_n))+'_looming_mean'] = line_plots_df['group'+(str(group_n))+'_looming_mean'].round(0)
    line_plots_df['group'+(str(group_n))+'_looming_mean'] = assign_max_to_sequence(line_plots_df['group'+(str(group_n))+'_looming_mean'])
#%%%
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
    
    '''FIRST 5 LOOMs ZOOM PLOTS'''
    first_5looms_walker_x_walker = select_first_5_looms(walker_x_walker)    
    zoom_violin_plots_variables(first_5_loom_zoom_speed2d, first_5looms_walker_x_walker, 'first_5_loom_zoom_speed2d_walker_x_walker')
    zoom_line_plots_variables(first_5_loom_zoom_speed2d, first_5looms_walker_x_walker, 'first_5_loom_zoom_speed2d_walker_x_walker')
    
    '''LAST 5 LOOMs ZOOM PLOTS'''    
    last_5looms_walker_x_walker = select_last_5_looms(walker_x_walker)
    zoom_violin_plots_variables(last_5_loom_zoom_speed2d, last_5looms_walker_x_walker, 'last_5_loom_zoom_speed2d_walker_x_walker')
    zoom_line_plots_variables(last_5_loom_zoom_speed2d, last_5looms_walker_x_walker, 'last_5_loom_zoom_speed2d_walker_x_walker')       
#%%
    
    '''HEATMAPS VARIABLES'''
    heatmap_col_order = (freeze_bout_bined[(int(baseline_frames/bin_size)):] == 1).sum().sort_values(ascending=False).index.values.tolist()

    velocity_sorted = velocity_bined[heatmap_col_order]
    freezing_sorted = freeze_bout_bined[heatmap_col_order]
    jumps_sorted = jumps_bined[heatmap_col_order]
    freezing_pops = np.ma.masked_equal(freezing_sorted, 1)
#%%
    '''BEHAVIOR ENTRY AND EXIT PROBABILITY'''
    
    #GROUP PROPOTION
    walk_before_mean  = []
    freeze_before_mean = []
    low_vel_before_mean = []

    walk_after_mean  = []
    freeze_after_mean = []
    low_vel_after_mean = []

    for i in range(len(line_plots_df)):
        if line_plots_df['group'+(str(group_n))+'_looming_mean'][i] == 1:
            walk_before_mean.append(line_plots_df['group'+(str(group_n))+'_walk_bout_mean'][i-1])
            freeze_before_mean.append(line_plots_df['group'+(str(group_n))+'_freeze_bout_mean'][i-1])
            low_vel_before_mean.append(line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'][i-1])

            walk_after_mean.append(line_plots_df['group'+(str(group_n))+'_walk_bout_mean'][i+5])
            freeze_after_mean.append(line_plots_df['group'+(str(group_n))+'_freeze_bout_mean'][i+5])
            low_vel_after_mean.append(line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'][i+5])        


    walk_entry_probability = np.array(np.array(walk_after_mean)-np.array(walk_before_mean))*100
    freeze_entry_probability = np.array(np.array(freeze_after_mean)-np.array(freeze_before_mean))*100
    low_vel_entry_probability = np.array(np.array(low_vel_after_mean)-np.array(low_vel_before_mean))*100

    delta_behavior_plots_df['group'+(str(group_n))+'_walk_entry_probability'] = walk_entry_probability
    delta_behavior_plots_df['group'+(str(group_n))+'_freeze_entry_probability'] = freeze_entry_probability
    delta_behavior_plots_df['group'+(str(group_n))+'_low_vel_entry_probability'] = low_vel_entry_probability
    
    walk_before_extended_mean = walk_before_mean.copy()
    walk_before_extended_mean.append(line_plots_df['group'+(str(group_n))+'_walk_bout_mean'][(len(line_plots_df)-1)])
    walk_before_extended_mean.pop(0)
    walk_exit_probability = np.array(np.array(walk_after_mean)-np.array(walk_before_extended_mean))*100

    freeze_before_extended_mean = freeze_before_mean.copy()
    freeze_before_extended_mean.append(line_plots_df['group'+(str(group_n))+'_freeze_bout_mean'][(len(line_plots_df)-1)])
    freeze_before_extended_mean.pop(0)
    freeze_exit_probability = np.array(np.array(freeze_after_mean)-np.array(freeze_before_extended_mean))*100

    low_vel_before_extended_mean = low_vel_before_mean.copy()
    low_vel_before_extended_mean.append(line_plots_df['group'+(str(group_n))+'_low_vel_bout_mean'][(len(line_plots_df)-1)])
    low_vel_before_extended_mean.pop(0)
    low_vel_exit_probability = np.array(np.array(low_vel_after_mean)-np.array(low_vel_before_extended_mean))   *100

    delta_behavior_plots_df['group'+(str(group_n))+'_walk_exit_probability'] = walk_exit_probability
    delta_behavior_plots_df['group'+(str(group_n))+'_freeze_exit_probability'] = freeze_exit_probability
    delta_behavior_plots_df['group'+(str(group_n))+'_low_vel_exit_probability'] = low_vel_exit_probability
    
    
    
    '''BEHAVIOR ENTRY & EXIT PROBABILITY AROUND LOOM PER FLY'''

    walk_entry_probability_on_loom_perfly = behavior_probability_around_loom(notwalker_x_x, notwalker_x_walker)
    freeze_entry_probability_on_loom_perfly = behavior_probability_around_loom(notfreezer_x_x, notfreezer_x_freezer)
    low_vel_entry_probability_on_loom_perfly = behavior_probability_around_loom(notlow_vel_x_x, notlow_vel_x_low_vel)
    delta_behavior_violins_df['group'+(str(group_n))+'_walk_entry_probability'] = pd.Series(walk_entry_probability_on_loom_perfly).reset_index(drop=True)
    delta_behavior_violins_df['group'+(str(group_n))+'_freeze_entry_probability'] = pd.Series(freeze_entry_probability_on_loom_perfly).reset_index(drop=True)
    delta_behavior_violins_df['group'+(str(group_n))+'_low_vel_entry_probability'] = pd.Series(low_vel_entry_probability_on_loom_perfly).reset_index(drop=True)
    
    walk_exit_probability_on_loom_perfly = behavior_probability_around_loom(walker_x_x, walker_x_notwalker)
    freeze_exit_probability_on_loom_perfly = behavior_probability_around_loom(freezer_x_x, freezer_x_notfreezer)
    low_vel_exit_probability_on_loom_perfly = behavior_probability_around_loom(low_vel_x_x, low_vel_x_notlow_vel)

    
    '''SELECTING FLIES DEPENDENT ON THE BEHAVIOR INTER LOOM - 2.5SEC-3SEC AFTER LOOM ONSET (bin 5) & 0.5SEC-0SEC BEFORE NEXT LOOM ONSET (bin 9)'''

    inter_walker_x, inter_notwalker_x = inter_loom_after_behavior(inter_loom_walk_bout_bined)
    inter_walker_walker, inter_walker_notwalker = inter_loom_before_behavior(inter_loom_walk_bout_bined[inter_walker_x])
    inter_notwalker_walker, inter_notwalker_notwalker = inter_loom_before_behavior(inter_loom_walk_bout_bined[inter_notwalker_x])

    inter_freezer_x, inter_notfreezer_x = inter_loom_after_behavior(inter_loom_freeze_bout_bined)
    inter_freezer_freezer, inter_freezer_notfreezer = inter_loom_before_behavior(inter_loom_freeze_bout_bined[inter_freezer_x])
    inter_notfreezer_freezer, inter_notfreezer_notfreezer = inter_loom_before_behavior(inter_loom_freeze_bout_bined[inter_notfreezer_x])
    
    inter_low_vel_x, inter_notlow_vel_x = inter_loom_after_behavior(inter_loom_low_vel_bout_bined)
    inter_low_vel_low_vel, inter_low_vel_notlow_vel = inter_loom_before_behavior(inter_loom_low_vel_bout_bined[inter_low_vel_x])
    inter_notlow_vel_low_vel, inter_notlow_vel_notlow_vel = inter_loom_before_behavior(inter_loom_low_vel_bout_bined[inter_notlow_vel_x])
    
    
    walk_entry_probability_inter_loom_perfly = behavior_probability_around_loom(inter_notwalker_x, inter_notwalker_walker)
    freeze_entry_probability_inter_loom_perfly = behavior_probability_around_loom(inter_notfreezer_x, inter_notfreezer_freezer)
    low_vel_entry_probability_inter_loom_perfly = behavior_probability_around_loom(inter_notlow_vel_x, inter_notlow_vel_low_vel)
    
    walk_exit_probability_inter_loom_perfly = behavior_probability_around_loom(inter_walker_x, inter_walker_notwalker)
    freeze_exit_probability_inter_loom_perfly = behavior_probability_around_loom(inter_freezer_x, inter_freezer_notfreezer)
    low_vel_exit_probability_inter_loom_perfly = behavior_probability_around_loom(inter_low_vel_x, inter_low_vel_notlow_vel)
    delta_behavior_violins_df['group'+(str(group_n))+'_walk_exit_probability'] = pd.Series(walk_exit_probability_inter_loom_perfly).reset_index(drop=True)
    delta_behavior_violins_df['group'+(str(group_n))+'_freeze_exit_probability'] = pd.Series(freeze_exit_probability_inter_loom_perfly).reset_index(drop=True)
    delta_behavior_violins_df['group'+(str(group_n))+'_low_vel_exit_probability'] = pd.Series(low_vel_exit_probability_inter_loom_perfly).reset_index(drop=True)       
    

#%%%
    
    '''DURATION OF BEHAVIOR BOUTS'''

    walk_bout_duration_baseline, walk_bout_duration_baseline_cleaned = behavior_bout_duration(walk_bout_baseline, baseline_frames-1)
    walk_bout_duration_stimulation, walk_bout_duration_stimulation_cleaned = behavior_bout_duration(walk_bout_stimulation, baseline_frames-1)
    freeze_bout_duration_baseline, freeze_bout_duration_baseline_cleaned = behavior_bout_duration(freeze_bout_baseline, baseline_frames-1)
    freeze_bout_duration_stimulation, freeze_bout_duration_stimulation_cleaned = behavior_bout_duration(freeze_bout_stimulation, baseline_frames-1)
    low_vel_bout_duration_baseline, low_vel_bout_duration_baseline_cleaned = behavior_bout_duration(low_vel_bout_baseline, baseline_frames-1)
    low_vel_bout_duration_stimulation, low_vel_bout_duration_stimulation_cleaned = behavior_bout_duration(low_vel_bout_stimulation, baseline_frames-1)
    
    
#%%%
    
    '''BEHAVIOR ONSET AROUND LOOM'''

        
    walk_onset = behavior_onset_around_loom(zoom_walk_bout, notwalker_x_walker)
    freeze_onset = behavior_onset_around_loom(zoom_freeze_bout, notfreezer_x_freezer)
    low_vel_onset = behavior_onset_around_loom(zoom_low_vel_bout, notlow_vel_x_low_vel)
    jump_onset = behavior_onset_around_loom(zoom_jumps, x_jumper_x)
    
    if group_n == 1:
        group1_walk_onset = walk_onset
        group1_freeze_onset = freeze_onset
        group1_jump_onset = jump_onset
        group1_low_vel_onset = low_vel_onset
    if group_n == 2:
        group2_walk_onset = walk_onset
        group2_freeze_onset = freeze_onset
        group2_jump_onset = jump_onset
        group2_low_vel_onset = low_vel_onset
    if group_n == 3:
        group3_walk_onset = walk_onset
        group3_freeze_onset = freeze_onset
        group3_jump_onset = jump_onset
        group3_low_vel_onset = low_vel_onset
    if group_n == 4:
        group4_walk_onset = walk_onset
        group4_freeze_onset = freeze_onset
        group4_jump_onset = jump_onset
        group4_low_vel_onset = low_vel_onset
    if group_n == 5:
        group5_walk_onset = walk_onset
        group5_freeze_onset = freeze_onset
        group5_jump_onset = jump_onset
        group5_low_vel_onset = low_vel_onset
    if group_n == 6:
        group6_walk_onset = walk_onset
        group6_freeze_onset = freeze_onset
        group6_jump_onset = jump_onset
        group6_low_vel_onset = low_vel_onset
        
    
    walk_startle_onset = behavior_onset_around_loom(zoom_walk_bout, freezer_x_freezer)
    low_vel_startle_onset = behavior_onset_around_loom(zoom_low_vel_bout, freezer_x_freezer)
    jump_startle_onset = behavior_onset_around_loom(zoom_jumps, freezer_x_freezer)
    
    walker_jump_onset = behavior_onset_around_loom(zoom_jumps, walker_jumper_x)
    freezer_jump_onset = behavior_onset_around_loom(zoom_jumps, freezer_jumper_x)
    
    notfreezer_jumper_freezer_freeze_onset = behavior_onset_around_loom(zoom_freeze_bout, notfreezer_jumper_freezer)
    notfreezer_notjumper_freezer_freeze_onset = behavior_onset_around_loom(zoom_freeze_bout, notfreezer_notjumper_freezer)
    

#%%%
    
    '''SPEED-FREEZING DEPENDENCY'''                     
            
    speed_behavior_probability('notfreezer_x_freezer', notfreezer_x_x, notfreezer_x_freezer, 2)
    
    speed_behavior_probability('notfreezer_jumper_freezer', notfreezer_x_freezer, notfreezer_jumper_freezer, 2)
    speed_behavior_probability('notfreezer_notjumper_freezer', notfreezer_x_freezer, notfreezer_notjumper_freezer, 2)
            
    speed_behavior_probability('notfreezer_jumper_notfreezer', notfreezer_x_notfreezer, notfreezer_jumper_notfreezer, 2)
    speed_behavior_probability('notfreezer_notjumper_notfreezer', notfreezer_x_notfreezer, notfreezer_notjumper_notfreezer, 2)

    speed_behavior_probability('notfreezer_jumper_x', notfreezer_x_x, notfreezer_jumper_x, 2)
    speed_behavior_probability('notfreezer_notjumper_x', notfreezer_x_x, notfreezer_notjumper_x, 2)
                 
    speed_jump_probability('x_jumper_x', x_notjumper_x, x_jumper_x, 2)



#%%%
    '''STARTLES'''
            
    startles_per_loom_probabilty('startler_jumps', startler_jumps)
    startles_per_loom_probabilty('startler_walk', startler_walk)
    startles_per_loom_probabilty('startler_low_vel', startler_low_vel)
    startles_per_loom_probabilty('no_startler', freezer_all)

#%%
    '''Pauses'''
    
    pauses_start = np.array(pauses_loom_onset) - zoom_before_loom_onset

    early_pauses = 0
    late_pauses = 0
    
    for i in pauses_start:
        if i <= 13:
            early_pauses = early_pauses + 1
        else:
            late_pauses = late_pauses + 1
            
    proportion_early_pauses = round((early_pauses / (len(pauses_start)))*100, 1)
    proportion_late_pauses = round((late_pauses / (len(pauses_start)))*100, 1)

#%%
 
    '''INDIVIDUAL GROUP PLOTS'''
    
    median_loom_onset = looming_onset.median(axis=1)
    median_loom_offset =looming_offset.median(axis=1)
    median_loom = (median_loom_onset+median_loom_offset)/2

    loom_coordinate = [(i/bin_size) for i in median_loom]
    x_coordinate = [i for i in range(len(line_plots_df))]

#%%
    '''BEHAVIOR ENTRY AND EXIT PROBABILITY PLOTS'''
    
    '''GROUP DELTA'''
    
    variables_to_plot = (walk_entry_probability, low_vel_entry_probability, freeze_entry_probability, 
                             walk_exit_probability, low_vel_exit_probability, freeze_exit_probability)
    y_max = int(round(np.max(variables_to_plot)))
    y_min = int(round(np.min(variables_to_plot)))
    y_abs = 5 * round((max(y_max, abs(y_min)))/5)
    x1 = np.array(range(0,20))
    x2 = x1 + 0.75
    fig, axs = plt.subplots(figsize= (12, 7))
    axs.set_ylabel(('Δ Behavior %'), fontsize = 18)
    axs.set_xlabel(('Looming'), fontsize = 18)
    axs.set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(looming.columns)-1) + ')', fontsize = 20)
    axs.set_xlim(-0.5, 20.5)
    axs.set_ylim((-y_abs)-5, (y_abs)+5)
    axs.set_yticks(range(-y_abs-5, y_abs+(5*2), 10))
    axs.set_xticks(range(0,20))
    axs.set_xticklabels(range(1,21))
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
    plt.plot(walk_entry_probability, 'tomato', marker = 'o', label = ('Walking'))
    plt.plot(low_vel_entry_probability, 'y', marker = 'o', label = ('Low Vel'))
    plt.plot(freeze_entry_probability, 'darkcyan', marker = 'o', label = ('Freezing'))
    plt.plot(x2, walk_exit_probability, 'tomato', marker = 'o', markerfacecolor='none', linestyle = '--')
    plt.plot(x2, low_vel_exit_probability, 'y', marker = 'o', markerfacecolor='none', linestyle = '--')
    plt.plot(x2, freeze_exit_probability, 'darkcyan', marker = 'o', markerfacecolor='none', linestyle = '--')
    axs.hlines(0, -1, 100, linestyles='--', lw= 1, color='grey')
    axs.legend(loc="upper right", frameon = True, fontsize = 15, framealpha=0.3)
    fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+"_deltabehaviors.png"), format='png') 
    plt.show()
    
    
#%%%   
    '''PER FLY BEHAVIOR'''

    fig, axs = plt.subplots(2, 2, figsize= (10, 10), gridspec_kw={'width_ratios': [1, 1]}, sharey=True)
    plt.suptitle(str(groups_labels[(group_n-1)]) + ' (' + str(len(looming.columns)-1) + ')', fontsize = 24)
    fig.subplots_adjust(top=0.92)
    
    axs[0, 0].set_facecolor('white')
    axs[0, 0].axes.xaxis.set_visible(False)
    axs[0, 0].set_ylabel(('Around loom behavior (%)'), fontsize = 20)
    axs[0, 0].set_title('Entry', y=-0.06, fontsize = 18)
    axs[0, 0].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[0, 0].yaxis.grid(which='major', linestyle='--', color='grey')
    axs[0, 0].set_axisbelow(True)
    sns.despine(left=False, bottom=True, right=True)
    my_pal = {0: walk_color, 1: freeze_color, 2: low_vel_color}
    axs[0, 0] =  sns.boxplot(ax=axs[0, 0], data=(walk_entry_probability_on_loom_perfly, freeze_entry_probability_on_loom_perfly, low_vel_entry_probability_on_loom_perfly), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[0, 0] = sns.violinplot(ax=axs[0, 0], data=(walk_entry_probability_on_loom_perfly, freeze_entry_probability_on_loom_perfly, low_vel_entry_probability_on_loom_perfly), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
           
    
    axs[0, 1].set_facecolor('white')
    axs[0, 1].axes.xaxis.set_visible(False)
    axs[0, 1].set_title('Exit', y=-0.06, fontsize = 18)
    axs[0, 1].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[0, 1].yaxis.grid(which='major', linestyle='--', color='grey')
    axs[0, 1].set_axisbelow(True)
    sns.despine(left=True, bottom=True, right=True)
    my_pal = {0: walk_color, 1: freeze_color, 2: low_vel_color}
    axs[0, 1] =  sns.boxplot(ax=axs[0, 1], data=(walk_exit_probability_on_loom_perfly, freeze_exit_probability_on_loom_perfly, low_vel_exit_probability_on_loom_perfly), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[0, 1] = sns.violinplot(ax=axs[0, 1], data=(walk_exit_probability_on_loom_perfly, freeze_exit_probability_on_loom_perfly, low_vel_exit_probability_on_loom_perfly), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
           


    axs[1, 0].set_facecolor('white')
    axs[1, 0].axes.xaxis.set_visible(False)
    axs[1, 0].set_ylabel(('Inter loom behavior (%)'), fontsize = 20)
    axs[1, 0].set_title('Entry', y=-0.06, fontsize = 18)
    axs[1, 0].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[1, 0].yaxis.grid(which='major', linestyle='--', color='grey')
    axs[1, 0].set_axisbelow(True)
    sns.despine(left=False, bottom=True, right=True)
    my_pal = {0: walk_color, 1: freeze_color, 2: low_vel_color}
    axs[1, 0] =  sns.boxplot(ax=axs[1, 0], data=(walk_entry_probability_inter_loom_perfly, freeze_entry_probability_inter_loom_perfly, low_vel_entry_probability_inter_loom_perfly), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1, 0] = sns.violinplot(ax=axs[1, 0], data=(walk_entry_probability_inter_loom_perfly, freeze_entry_probability_inter_loom_perfly, low_vel_entry_probability_inter_loom_perfly), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
           
    
    axs[1, 1].set_facecolor('white')
    axs[1, 1].axes.xaxis.set_visible(False)
    axs[1, 1].set_title('Exit', y=-0.06, fontsize = 18)
    axs[1, 1].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[1, 1].yaxis.grid(which='major', linestyle='--', color='grey')
    axs[1, 1].set_axisbelow(True)
    sns.despine(left=True, bottom=True, right=True)
    my_pal = {0: walk_color, 1: freeze_color, 2: low_vel_color}
    axs[1, 1] =  sns.boxplot(ax=axs[1, 1], data=(walk_exit_probability_inter_loom_perfly, freeze_exit_probability_inter_loom_perfly, low_vel_exit_probability_inter_loom_perfly), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1, 1] = sns.violinplot(ax=axs[1, 1], data=(walk_exit_probability_inter_loom_perfly, freeze_exit_probability_inter_loom_perfly, low_vel_exit_probability_inter_loom_perfly), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

    fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+"_around_loom_behaviors.png"), format='png') 
    plt.show()    
#%%
    '''ZOOM LINE PLOTS'''

    loom_zoom_coordinate = [(zoom_before_loom_onset/bin_size_zoom), (int(zoom_before_loom_onset+loom_duration)/bin_size_zoom)]
    x_zoom_coordinate = [i for i in range(len(zoom_line_plots_df))]

 
    def speed2d_zoom_plots(title, var1, var1_list, var1_label, var1_color, 
                           var2, var2_list, var2_label, var2_color, yticksteps1, yticksteps2):

        fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
        fig.subplots_adjust(wspace = 0.2)

        #Delta violin plot
        list_to_plot1 = []
        list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var1+'_delta')].values.tolist())
        list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var2+'_delta')].values.tolist())
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
        #dashed = [0.5]
        #zeroline= [0]
        #axs[1].vlines(dashed, -20, 20, linestyles='-', lw= 0.5)
        #axs[1].hlines(zeroline, -30, 30, linestyles='-', lw= 1)
        axs[1].set_axisbelow(True)
        sns.despine(left=False, bottom=True, right=True)
        my_pal = {0: var1_color, 1: var2_color}
        axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_delta']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
        
        #Line plot
        list_to_plot0 = []
        list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var1+'_mean')].values.tolist())
        list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var2+'_mean')].values.tolist())
        list_to_plot0 = [x for x in list_to_plot0 if x == x]
        y_max = int(round(np.nanmax(list_to_plot0)))
        y_max1 = int((yticksteps1) * round(y_max/(yticksteps1)))
        y_min = int(round(np.nanmin(list_to_plot0)))
        y_min1 = int((yticksteps1) * round(y_min/(yticksteps1)))
        axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
        axs[0].set_xlabel('Time (sec)', fontsize = 18)
        axs[0].set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(zoom_looming.columns)) + ')' + str(title), fontsize = 20)
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
        axs[0].vlines(loom_zoom_coordinate, y_min1-1, y_max1+(yticksteps1), linestyles='--', lw= 1, color='grey')
        axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var1+'_mean')], 'k-', label = (str(var1_label)+'  (' + str(len(var1_list))+')'), color=var1_color)
        axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var1+'_sem']), color=var1_color, alpha=0.3)
        axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_zoom_speed2d_'+var2+'_mean')], 'k-', label = (str(var2_label)+'  (' + str(len(var2_list))+')'), color=var2_color)
        axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_zoom_speed2d_'+var2+'_sem']), color=var2_color, alpha=0.3)
        axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

        plt.show()
        fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+'_speed2d_zoom_'+str(title)+ '.png'), format='png') 


    speed2d_zoom_plots(' Walker (pauser) walker', 'walker_pauser_walker', walker_pauser_walker, 'Pauser', low_vel_color, 'walker_notpauser_walker', walker_notpauser_walker, 'Not pauser', walk_color, 5, 10)
    speed2d_zoom_plots(' Walker (pauser) X', 'walker_pauser_x', walker_pauser_x, 'Pauser', low_vel_color, 'walker_notpauser_x', walker_notpauser_x, 'Not pauser', walk_color, 5, 10)
    speed2d_zoom_plots(' Walker X (walker)', 'walker_x_walker', walker_x_walker, 'Walker', walk_color, 'walker_x_notwalker', walker_x_notwalker, 'Stop walking', low_vel_color, 5, 10)
    speed2d_zoom_plots(' Walker X (freezer)', 'walker_x_freezer', walker_x_freezer, 'Freezer', freeze_color, 'walker_x_notfreezer', walker_x_notfreezer, 'Not freezer', walk_color, 5, 10)
    speed2d_zoom_plots(' Walker (jumper) freezer', 'walker_jumper_freezer', walker_jumper_freezer, 'Jumper', jump_color, 'walker_notjumper_freezer', walker_notjumper_freezer, 'Not jumper', freeze_color, 5, 10)
    speed2d_zoom_plots(' Walker (jumper) X', 'walker_jumper_x', walker_jumper_x, 'jumper', jump_color, 'walker_notjumper_x', walker_notjumper_x, 'Not jumper', walk_color, 10, 10)
    speed2d_zoom_plots(' Walker pauser (jumper) X', 'walker_pauser_jumper_x', walker_pauser_jumper_x, 'jumper', jump_color, 'walker_pauser_notjumper_x', walker_pauser_notjumper_x, 'Not jumper', low_vel_color, 5, 10)
    speed2d_zoom_plots(' Walker jumper (pauser) X', 'walker_jumper_pauser_x', walker_jumper_pauser_x, 'pauser', jump_color, 'walker_jumper_notpauser_x', walker_jumper_notpauser_x, 'Not pauser', walk_color, 5, 5)


#%%
    '''ZOOM LINE PLOTS'''
    
    def contains_only_nan(lst):
        return np.all(np.isnan(lst))
    
    def first_loom_speed2d_zoom_plots(title, var1, var1_list, var1_label, var1_color, 
                           var2, var2_list, var2_label, var2_color, yticksteps1, yticksteps2):

        fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
        fig.subplots_adjust(wspace = 0.2)

        #Delta violin plot
        list_to_plot1 = []
        if not contains_only_nan(zoom_violin_plots_df[('group'+(str(group_n))+'_'+var1+'_delta')].values.tolist()):
            list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_'+var1+'_delta')].values.tolist())
        if not contains_only_nan(zoom_violin_plots_df[('group'+(str(group_n))+'_'+var2+'_delta')].values.tolist()):            
            list_to_plot1.append(zoom_violin_plots_df[('group'+(str(group_n))+'_'+var2+'_delta')].values.tolist())
        if list_to_plot1: # Check if the list is not empty
            y_max = int(round(np.nanmax(list_to_plot1)))
            y_max1 = (5) * round(y_max/(5))
            y_min = int(round(np.nanmin(list_to_plot1)))
            y_min1 = (5) * round(y_min/(5))
        else: # if the list is empty assine this value to the plot, anyway the plot will be empty but at least the code can continue and not entering into error!!
            y_max1 = 10
            y_min1 = -10            
            
        axs[1].set_facecolor('white')
        axs[1].axes.xaxis.set_visible(False)
        axs[1].set_title('Delta', y=-0.095, fontsize = 18)
        axs[1].set_ylim((y_min1)-(yticksteps2), (y_max1)+(yticksteps2))
        axs[1].set_yticks(range(int((y_min1)-(yticksteps2)), int((y_max1)+(yticksteps2)), yticksteps2))
        axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
        axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
        #dashed = [0.5]
        #zeroline= [0]
        #axs[1].vlines(dashed, -20, 20, linestyles='-', lw= 0.5)
        #axs[1].hlines(zeroline, -30, 30, linestyles='-', lw= 1)
        axs[1].set_axisbelow(True)
        sns.despine(left=False, bottom=True, right=True)
        my_pal = {0: var1_color, 1: var2_color}
        axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_'+var1+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_'+var2+'_delta']), palette=my_pal, 
           boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
           medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
        axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group'+(str(group_n))+'_'+var1+'_delta'], zoom_violin_plots_df['group'+(str(group_n))+'_'+var2+'_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
        
        #Line plot
        list_to_plot0 = []
        if not contains_only_nan(zoom_line_plots_df[('group'+(str(group_n))+'_'+var1+'_mean')].values.tolist()):
            list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_'+var1+'_mean')].values.tolist())
        if not contains_only_nan(zoom_line_plots_df[('group'+(str(group_n))+'_'+var2+'_mean')].values.tolist()):
            list_to_plot0.append(zoom_line_plots_df[('group'+(str(group_n))+'_'+var2+'_mean')].values.tolist())
        list_to_plot0 = [x for x in list_to_plot0 if x == x] #a way to filter out NaN values, but in my experinece didin't work 
        if list_to_plot0:
            y_max = int(round(np.nanmax(list_to_plot0))) #np.nanmax (to avoid problem with nan)
            y_max1 = int((yticksteps1) * round(y_max/(yticksteps1)))
            y_min = int(round(np.nanmin(list_to_plot0)))
            y_min1 = int((yticksteps1) * round(y_min/(yticksteps1)))
        else:
            y_max1 = 0
            y_min1 = 30
            
        
        axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
        axs[0].set_xlabel('Time (sec)', fontsize = 18)
        axs[0].set_title(str(groups_labels[(group_n-1)]) + ' (' + str(len(zoom_looming.columns)) + ')' + str(title), fontsize = 20)
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
        #axs[0].vlines(loom_zoom_coordinate, 0, 25, linestyles='--', lw= 1, color='grey')
        axs[0].vlines(loom_zoom_coordinate, y_min1-1, y_max1+(yticksteps1), linestyles='--', lw= 1, color='grey')
        axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_'+var1+'_mean')], 'k-', label = (str(var1_label)+'  (' + str(len(var1_list))+')'), color=var1_color)
        axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_'+var1+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_'+var1+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_'+var1+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_'+var1+'_sem']), color=var1_color, alpha=0.3)
        axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group'+(str(group_n))+'_'+var2+'_mean')], 'k-', label = (str(var2_label)+'  (' + str(len(var2_list))+')'), color=var2_color)
        axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group'+(str(group_n))+'_'+var2+'_mean']-zoom_line_plots_df['group'+(str(group_n))+'_'+var2+'_sem']),(zoom_line_plots_df['group'+(str(group_n))+'_'+var2+'_mean']+zoom_line_plots_df['group'+(str(group_n))+'_'+var2+'_sem']), color=var2_color, alpha=0.3)
        axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

        plt.show()
        fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+'_first_loom_speed2d_zoom_'+str(title)+ '.png'), format='png') 



    first_loom_speed2d_zoom_plots(' 1st Walker (pauser) walker', 'first_loom_zoom_speed2d_walker_pauser_walker', first_loom_walker_pauser_walker, 'Pauser', low_vel_color, 'first_loom_zoom_speed2d_walker_notpauser_walker', first_loom_walker_notpauser_walker, 'Not pauser', walk_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker (pauser) X', 'first_loom_zoom_speed2d_walker_pauser_x', first_loom_walker_pauser_x, 'Pauser', low_vel_color, 'first_loom_zoom_speed2d_walker_notpauser_x', first_loom_walker_notpauser_x, 'Not pauser', walk_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker X (walker)', 'first_loom_zoom_speed2d_walker_x_walker', first_loom_walker_x_walker, 'Walker', walk_color, 'first_loom_zoom_speed2d_walker_x_notwalker', first_loom_walker_x_notwalker, 'Stop walking', low_vel_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker X (freezer)', 'first_loom_zoom_speed2d_walker_x_freezer', first_loom_walker_x_freezer, 'Freezer', freeze_color, 'first_loom_zoom_speed2d_walker_x_notfreezer', first_loom_walker_x_notfreezer, 'Not freezer', walk_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker (jumper) freezer', 'first_loom_zoom_speed2d_walker_jumper_freezer', first_loom_walker_jumper_freezer, 'Jumper', jump_color, 'first_loom_zoom_speed2d_walker_notjumper_freezer', first_loom_walker_notjumper_freezer, 'Not jumper', freeze_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker (jumper) X', 'first_loom_zoom_speed2d_walker_jumper_x', first_loom_walker_jumper_x, 'jumper', jump_color, 'first_loom_zoom_speed2d_walker_notjumper_x', first_loom_walker_notjumper_x, 'Not jumper', walk_color, 10, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker pauser (jumper) X', 'first_loom_zoom_speed2d_walker_pauser_jumper_x', first_loom_walker_pauser_jumper_x, 'jumper', jump_color, 'first_loom_zoom_speed2d_walker_pauser_notjumper_x', first_loom_walker_pauser_notjumper_x, 'Not jumper', low_vel_color, 5, 10)
    first_loom_speed2d_zoom_plots(' 1st Walker jumper (pauser) X', 'first_loom_zoom_speed2d_walker_jumper_pauser_x', first_loom_walker_jumper_pauser_x, 'pauser', jump_color, 'first_loom_zoom_speed2d_walker_jumper_notpauser_x', first_loom_walker_jumper_notpauser_x, 'Not pauser', walk_color, 5, 5)

   
#%%%
    '''DURATION OF BEHAVIOR BOUTS PLOTS'''
    fig, axs = plt.subplots(3, 2, figsize= (15, 12), sharey = False, gridspec_kw={'width_ratios': [3, 2]})
    plt.suptitle(str(groups_labels[(group_n-1)]) + ' (' + str(len(looming.columns)-1) + ')', fontsize = 24)
    fig.subplots_adjust(top=0.92)
    fig.subplots_adjust(wspace = 0.15)

    axs[0, 0].set_facecolor('white')
    axs[0, 0].axes.xaxis.set_visible(False)
    axs[0, 0].set_ylabel('Frequency', fontsize = 18)
    axs[0, 0].set_title('Walking', fontsize = 18, x=0.1)
    axs[0, 0].set_xlim(0, 300)
    axs[0, 0].set_xticks(range(0, 300, 60))
    axs[0, 0].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[0, 0].set_axisbelow(True)
    sns.despine(left=False, bottom=True, right=True)
    axs[0, 0] =  sns.distplot(walk_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[0, 0])
    axs[0, 0] =  sns.distplot(walk_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[0, 0])

    axs[1, 0].set_facecolor('white')
    axs[1, 0].axes.xaxis.set_visible(False)
    axs[1, 0].set_ylabel('Frequency', fontsize = 18)
    axs[1, 0].set_title('Freezing', fontsize = 18, x=0.1)
    #axs[1, 0].set_ylim(0, 0.2)
    axs[1, 0].set_xlim(0, 300)
    axs[1, 0].set_xticks(range(0, 300, 60))
    axs[1, 0].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[1, 0].set_axisbelow(True)
    sns.despine(left=False, bottom=True, right=True)
    axs[1, 0] =  sns.distplot(freeze_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[1, 0])
    axs[1, 0] =  sns.distplot(freeze_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[1, 0])

        
    axs[2, 0].set_facecolor('white')
    axs[2, 0].set_title('Low velocity', fontsize = 18, x=0.15)
    axs[2, 0].set_xlabel('Time (min)', fontsize = 18)
    axs[2, 0].set_ylabel('Frequency', fontsize = 18)
    axs[2, 0].set_xlim(0, 300)
    axs[2, 0].set_xticks(range(0, 301, 60))
    axs[2, 0].set_xticklabels(range(0, 6, 1))
    axs[2, 0].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[2, 0].tick_params(axis='x', colors = 'k', labelsize=16)
    axs[2, 0].set_axisbelow(True)
    sns.despine(left=False, bottom=False, right=True)
    axs[2, 0] =  sns.distplot(low_vel_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[2, 0])
    axs[2, 0] =  sns.distplot(low_vel_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[2, 0])
    
  
    
    axs[0, 1].set_facecolor('white')
    axs[0, 1].axes.xaxis.set_visible(False)
    axs[0, 1].axes.yaxis.set_visible(False)
    axs[0, 1].set_xlim(0, 60)
    axs[0, 1].set_axisbelow(True)
    sns.despine(left=False, bottom=False, right=True)
    axs[0, 1] =  sns.distplot(walk_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[0, 1], label='Baseline')
    axs[0, 1] =  sns.distplot(walk_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[0, 1], label = 'Stimulation')
    axs[0, 1].legend(loc="upper right", frameon = True, fontsize = 15, framealpha=0.3)

    axs[1, 1].set_facecolor('white')
    axs[1, 1].axes.xaxis.set_visible(False)
    axs[1, 1].axes.yaxis.set_visible(False)
    axs[1, 1].set_xlim(0, 60)
    axs[1, 1].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[1, 1].set_axisbelow(True)
    sns.despine(left=False, bottom=True, right=True)
    axs[1, 1] =  sns.distplot(freeze_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[1, 1])
    axs[1, 1] =  sns.distplot(freeze_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[1, 1])

        
    axs[2, 1].set_facecolor('white')
    axs[2, 1].axes.yaxis.set_visible(False)
    axs[2, 1].set_xlabel('Time (sec)', fontsize = 18)
    axs[2, 1].set_ylabel('Frequency', fontsize = 18)
    axs[2, 1].set_xlim(0, 60)
    axs[2, 1].set_xticks(range(0, 60, 10))
    #axs[2, 1].set_xticklabels(range(0, 6, 1))
    axs[2, 1].tick_params(axis='y', colors = 'k', labelsize=16)
    axs[2, 1].tick_params(axis='x', colors = 'k', labelsize=16)
    axs[2, 1].set_axisbelow(True)
    sns.despine(left=False, bottom=False, right=True)
    axs[2, 1] =  sns.distplot(low_vel_bout_duration_baseline, hist = False, kde_kws=dict(linewidth=3), ax=axs[2, 1])
    axs[2, 1] =  sns.distplot(low_vel_bout_duration_stimulation, hist = False, kde_kws=dict(linewidth=3), ax=axs[2, 1])
    
    
    
    
    
    fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+"_bouts_duration.png"), format='png') 
    plt.show()    

#%%
''' MULTIPLE GROUPS PLOTS'''
    
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
axs[0].set_ylim(5, 20)
#axs[0].set_xticks([0, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200])
#axs[0].set_xticklabels([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
n_ticks = int(total_duration_min) + 2  # from 0 up to the final minute
xticks_bins = np.linspace(0, limit, n_ticks)
xticks_min = np.round(np.linspace(0, total_duration_min, n_ticks), 1)
axs[0].set_xticks(xticks_bins)
axs[0].set_xticklabels(xticks_min)
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
axs[0].set_ylim(5, 20)
axs[0].set_yticks([5, 10, 15, 20])
#axs[0].set_xticks([0, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200])
#axs[0].set_xticklabels([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#xticks_bins = np.linspace(0, limit, math.ceil(total_duration_min)+1, dtype=int) #X ticks: bins as positions, minutes as labels (rounded up)
#xticks_min = np.arange(0, math.ceil(total_duration_min)+1, 1)
n_ticks = int(total_duration_min) + 2  # from 0 up to the final minute
xticks_bins = np.linspace(0, limit, n_ticks)
xticks_min = np.round(np.linspace(0, total_duration_min, n_ticks), 1)

axs[0].set_xticks(xticks_bins)
axs[0].set_xticklabels(xticks_min)


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


#%%%

'''MULTIPLE GROUPS ZOOM PLOTS'''

fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
fig.subplots_adjust(wspace = 0.2)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].set_title('Delta', y=-0.095, fontsize = 18)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=False, bottom=True, right=True)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

#Line plot
axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (bins)', fontsize = 18)
axs[0].set_title('Walker_x_walker', fontsize = 20)
#axs[0].set_xlim(10, 100) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
axs[0].set_xlim(0, 240) # TO CHECK 10 SEC, SO PROBABLY TO REMOVE
axs[0].set_ylim(5, 25)
#axs[0].set_yticks(range(y_minuse, y_max1+yticksteps1, yticksteps1))
#axs[0].set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
#axs[0].set_xticklabels([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3])
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
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group1_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group1_label)), color=group1_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group1_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group1_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group1_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group1_zoom_speed2d_walker_x_walker_sem']), color=group1_color, alpha=0.3)
if number_of_groups >= 2:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group2_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group2_label)), color=group2_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group2_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group2_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group2_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group2_zoom_speed2d_walker_x_walker_sem']), color=group2_color, alpha=0.3)
if number_of_groups >= 3:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group3_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group3_label)), color=group3_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group3_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group3_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group3_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group3_zoom_speed2d_walker_x_walker_sem']), color=group3_color, alpha=0.3)
if number_of_groups >= 4:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group4_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group4_label)), color=group4_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group4_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group4_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group4_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group4_zoom_speed2d_walker_x_walker_sem']), color=group4_color, alpha=0.3)
if number_of_groups >= 5:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group5_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group5_label)), color=group5_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group5_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group5_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group5_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group5_zoom_speed2d_walker_x_walker_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group6_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group6_label)), color=group6_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group6_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group6_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group6_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group6_zoom_speed2d_walker_x_walker_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

plt.show()
fig.savefig((plot_path+"/"+str(groups_labels[(group_n-1)])+'_speed2d_zoom_groups.png'), format='png') 

#%%
'''MULTIPLE GROUPS ZOOM PLOTS 1st loom'''

fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
fig.subplots_adjust(wspace = 0.2)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].set_title('Delta', y=-0.095, fontsize = 18)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=False, bottom=True, right=True)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

#Line plot
axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (bins)', fontsize = 18)
axs[0].set_title('Walker_x_walker', fontsize = 20)
axs[0].set_xlim(0, 240) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
axs[0].set_ylim(5, 25)
#axs[0].set_yticks(range(y_minuse, y_max1+yticksteps1, yticksteps1))
#axs[0].set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
#axs[0].set_xticklabels([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
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
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group1_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group1_label)), color=group1_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group1_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group1_color, alpha=0.3)
if number_of_groups >= 2:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group2_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group2_label)), color=group2_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group2_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group2_color, alpha=0.3)
if number_of_groups >= 3:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group3_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group3_label)), color=group3_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group3_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group3_color, alpha=0.3)
if number_of_groups >= 4:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group4_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group4_label)), color=group4_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group4_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group4_color, alpha=0.3)
if number_of_groups >= 5:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group5_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group5_label)), color=group5_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group5_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group6_first_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group6_label)), color=group6_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group6_first_loom_zoom_speed2d_walker_x_walker_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

plt.show()
fig.savefig((plot_path+"/"+str(experiment_name)+'_first_loom_zoom_speed2d_groups.png'), format='png') 
#%%
'''MULTIPLE GROUPS ZOOM PLOTS first 5 looms'''

fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
fig.subplots_adjust(wspace = 0.2)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].set_title('Delta', y=-0.095, fontsize = 18)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=False, bottom=True, right=True)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

#Line plot
axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (bins)', fontsize = 18)
axs[0].set_title('Walker_x_walker_first5looms', fontsize = 20)
axs[0].set_xlim(0, 240) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
axs[0].set_ylim(5, 25)
#axs[0].set_yticks(range(y_minuse, y_max1+yticksteps1, yticksteps1))
#axs[0].set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
#axs[0].set_xticklabels([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
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
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group1_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group1_label)), color=group1_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group1_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group1_color, alpha=0.3)
if number_of_groups >= 2:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group2_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group2_label)), color=group2_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group2_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group2_color, alpha=0.3)
if number_of_groups >= 3:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group3_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group3_label)), color=group3_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group3_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group3_color, alpha=0.3)
if number_of_groups >= 4:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group4_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group4_label)), color=group4_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group4_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group4_color, alpha=0.3)
if number_of_groups >= 5:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group5_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group5_label)), color=group5_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group5_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group6_first_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group6_label)), color=group6_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group6_first_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

plt.show()
fig.savefig((plot_path+"/"+str(experiment_name)+'_first_5_loom_zoom_speed2d_groups.png'), format='png') 

#%%
'''MULTIPLE GROUPS ZOOM PLOTS last 5 looms'''

fig, axs = plt.subplots(1, 2, figsize= (14, 6), gridspec_kw={'width_ratios': [3, 1.5]}, sharey = False)
fig.subplots_adjust(wspace = 0.2)

axs[1].set_facecolor('white')
axs[1].axes.xaxis.set_visible(False)
axs[1].set_title('Delta', y=-0.095, fontsize = 18)
axs[1].tick_params(axis='y', colors = 'k', labelsize=16)
axs[1].yaxis.grid(which='major', linestyle='--', color='grey')
axs[1].set_axisbelow(True)
sns.despine(left=False, bottom=True, right=True)
if number_of_groups == 1:
    my_pal = {0: group1_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 2:
    my_pal = {0: group1_color, 1: group2_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 3:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 4:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 5:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)
if number_of_groups == 6:
    my_pal = {0: group1_color, 1: group2_color, 2: group3_color, 3: group4_color, 4: group5_color, 5: group6_color}
    axs[1] =  sns.boxplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_delta']), palette=my_pal, 
       boxprops={'facecolor':'None', 'edgecolor': 'k', 'linewidth': 3,  "zorder":10, 'alpha': 0.6}, whiskerprops={'color': 'k', 'linewidth': 3, "zorder":10, 'linestyle': '--', 'alpha': 0.6}, 
       medianprops= {'color': 'k', 'linewidth': 3, "zorder":10}, capprops={'color': 'k', 'linewidth': 3, "zorder":10}, width=0.25, zorder=10, fliersize=0)
    axs[1] = sns.violinplot(data=(zoom_violin_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_delta'], zoom_violin_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_delta']), bw =0.06, linewidth=1.3, width= 0.75, scale='width', inner=None, palette=my_pal, cut=0, alpha=0.7)

#Line plot
axs[0].set_ylabel('Speed 2D (mm/sec ±SEM)', fontsize = 18)
axs[0].set_xlabel('Time (bins)', fontsize = 18)
axs[0].set_title('Walker_x_walker_last5looms', fontsize = 20)
axs[0].set_xlim(0, 240) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
axs[0].set_ylim(5, 25)
#axs[0].set_yticks(range(y_minuse, y_max1+yticksteps1, yticksteps1))
#axs[0].set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
#axs[0].set_xticklabels([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]) #I COMMENTED TO CHECK 10 SEC, SO PROBABLY TO REMOVE
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
axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group1_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group1_label)), color=group1_color)
axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group1_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group1_color, alpha=0.3)
if number_of_groups >= 2:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group2_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group2_label)), color=group2_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group2_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group2_color, alpha=0.3)
if number_of_groups >= 3:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group3_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group3_label)), color=group3_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group3_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group3_color, alpha=0.3)
if number_of_groups >= 4:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group4_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group4_label)), color=group4_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group4_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group4_color, alpha=0.3)
if number_of_groups >= 5:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group5_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group5_label)), color=group5_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group5_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group5_color, alpha=0.3)
if number_of_groups == 6:
    axs[0].plot(x_zoom_coordinate, zoom_line_plots_df[('group6_last_5_loom_zoom_speed2d_walker_x_walker_mean')], 'k-', label = (str(group6_label)), color=group6_color)
    axs[0].fill_between(x_zoom_coordinate,(zoom_line_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_mean']-zoom_line_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_sem']),(zoom_line_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_mean']+zoom_line_plots_df['group6_last_5_loom_zoom_speed2d_walker_x_walker_sem']), color=group6_color, alpha=0.3)

axs[0].legend(loc="upper left", frameon = True, framealpha=0.3, fontsize = 15)

plt.show()
fig.savefig((plot_path+"/"+str(experiment_name)+'_last_5_loom_zoom_speed2d_groups.png'), format='png') 
