# -*- coding: utf-8 -*- in this version solved bin problem and all the zerodivision error and max(nan)!!! So this code should always works
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
import tkinter, tkinter.filedialog
import math
from math import atan2
from scipy.stats import ttest_ind
from matplotlib.collections import PolyCollection, PathCollection
from matplotlib.lines import Line2D

#os.chdir( 'C:/Users/ricmi/Desktop/vTNTxpleGAL4')

def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files')
    root.destroy()
    return filename
exp_path = load_path()

plot_path = exp_path + '/plots'
plot_path_pdf = exp_path + '/plots_pdf'

plot_path_escape_plots = exp_path + '/plots/escape_plots'
plot_path_pdf_escape_plots = exp_path + '/plots_pdf/escape_plots'

#CHANGE EXPT NAME AND GROUP LABELS BELOW

experiment_name = '39347_tsh_gal80_luc_RNAi_TRIP-30secbase' #"Tsh_GAL80_DH44_GAL4_DH44_or_luc_RNAi_TRIP" #

group1_label = 'VLF-39347_tsh_gal80_luc_RNAi_TRIP-30secbase' #"Tsh_GAL80_DH44_GAL4_luc_RNAi_TRIP" #"Tsh_GAL80_DH44_GAL4_luc_RNAi_TRIP"
#group2_label = 'VLF-39347_tsh_gal80_DH44_RNAi_TRIP-30secbase' #"Tsh_GAL80_DH44_GAL4_DH44_RNAi_TRIP" #"Tsh_GAL80_DH44_GAL4_DH44_RNAi_TRIP"



#TIME SCALES
frame_rate = 60

#EXPERIMENT DURATION (in sec)
baseline  = 30#
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
#in frames
zoom_before_loom_onset = 120 #SCRUPOLI: but why in the plot is till 90 (-1.5) instead of 120 (-2)??? 
zoom_after_loom_onset = 600 #180 #this make sense!!! 

#For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate

bin_size_zoom_sec = 0.05
bin_size_zoom = bin_size_zoom_sec * frame_rate

#Zoom violin plots data interval selec 
before_loom_start = 60
before_loom_end = int(zoom_before_loom_onset) #120
before_loom_interval = int(before_loom_end - before_loom_start) #120 - 60 = 60 

after_loom_start = int(zoom_before_loom_onset + loom_duration) #120 + 30 = 150
after_loom_end = int(after_loom_start + before_loom_interval) #150 + 60 = 210

zoom_line_plots_df = pd.DataFrame()
zoom_violin_plots_df = pd.DataFrame()
#%%
'''try-out for angular speed calculation.
General idea: calculate delta(x) and delta(y) per frame. Calculate the the heading angle (direction of movement) at each time point
'''
def heading(dx, dy): #wait in all this script this function is never being used??!!! So I'm never really talking about angle but about desplacement
    degs_lst =[]
    for i in range(len(dx)):
        if isinstance(dx[i], str): #If the displacement was stored as a string (maybe due to bad parsing), it just marks that frame as "nan" instead of computing.
            degs_lst.append('nan')
        else:
            rads = atan2(dy[i], dx[i]) 
            rads %= 2*np.pi
            degs = math.degrees(rads)
            degs_lst.append(degs)
    return degs_lst

#%%
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
#%%
'''upload scored file'''

df_all = pd.DataFrame() #this will contain all excapes per loom in the end

path = exp_path
#Upper treshold for speed 2D
jump_velocity = 75

for filename in sorted(os.listdir(path+'/scored/')):  #folder with scored files you want to check

    if not filename.endswith('frames.csv'):
        continue
    capital_x = filename.replace('X','x')
    if not capital_x.startswith(group1_label):
        continue
    df_try = pd.read_csv(path+'/scored/'+filename ) #df_try has the info of the scored file  
            
    loom_onset = df_try.loc[df_try['looming_bout'].diff() == 1].index.values.astype(int)
    loom_offset = df_try.loc[df_try['looming_bout'].diff() == -1].index.values.astype(int)
   
    df_try['esc_turn'] = 0
    df_try['esc_run'] = 0
    df_try['esc_jump'] = 0
    df_try['esc_freeze'] = 0
    df_try['escape'] = 0
    df_try['turn_run'] = 0
    df_try['walk_speed'] = np.nan #velocity of walking flies 
    df_try['walk_speed_bout'] = np.nan #velocity of the fly while in a walking bout
    df_try['speed2d'] = np.nan #velocity of flies (regardless if they are walking or not) considering as a maximum speed the thresold for jumps

    '''checking turns'''
    heading_x_before = []
    heading_y_before = []
    heading_x_after = []
    heading_y_after = []
    
    "CHANGING COORDINATE SYSTEM TO BE WITH THE CENTER OF THE ARENA IN (0,0) INSTEAD OF (15,15) and the screen at y+ " # to check turn and the screen at y+
    df_try['fly_x_norm_mm'] = df_try['fly_x_norm_mm'] - 15
    df_try['fly_y_norm_mm'] = (df_try['fly_y_norm_mm'] - 15) * -1 
    
    df_try.loc[(df_try['walk'] == 1), 'walk_speed'] = df_try['velocity']  
    
    df_try.loc[(df_try['walk_bout'] == 1), 'walk_speed_bout'] = df_try['velocity']
    
    df_try.loc[(df_try['velocity'] < jump_velocity), 'speed2d'] = df_try['velocity']
    
    for loom in range(len(df_try)):    
        if loom in loom_onset:
            if df_try.loc[loom,'freeze_bout'] == 1: #ignore condition in whic they are freezing
                x_before = 'nan'
                y_before = 'nan'
                
            else:
                x_before = df_try.loc[loom,'fly_x_norm_mm'] - df_try.loc[loom-30,'fly_x_norm_mm'] #the displacement vector heading_before go from 30 frames before the loom to loom onset
                y_before = df_try.loc[loom,'fly_y_norm_mm'] - df_try.loc[loom-30,'fly_y_norm_mm']
            heading_x_before.append(x_before)
            heading_y_before.append(y_before)
    
        elif loom in loom_offset:
            if df_try.loc[loom:loom+30,'freeze_bout'].sum() >1: #ignore condition in whic they are freezing
                x_after = 'nan'
                y_after = 'nan'
            else:
                x_after = df_try.loc[loom+30,'fly_x_norm_mm'] - df_try.loc[loom,'fly_x_norm_mm'] #the displacement vector heading_after go from loom offset to 30 frames after loom offset 
                y_after = df_try.loc[loom+30,'fly_y_norm_mm'] - df_try.loc[loom,'fly_y_norm_mm']
            heading_x_after.append(x_after)
            heading_y_after.append(y_after)
            
    
    for i in range(len(heading_y_before)):
        if isinstance(heading_y_before[i], str) | isinstance(heading_y_after[i], str):#here we are taliking about desplacemnt, not heading (angle)!!
            continue
        elif (heading_y_before[i] > 0) & (heading_y_after[i] < 0): #because screen is at y+ (I changed from original script)
            df_try.loc[loom_offset[i], 'esc_turn'] = 1       


    '''checking jumps and freeze'''
    for i in range(len(loom_onset)):
        if df_try.loc[loom_onset[i]:(loom_onset[i]+120), 'jumps'].sum() > 0: #if there was a jump from loom onset till 2 seconds from loom onset
            df_try.loc[loom_offset[i], 'esc_jump'] = 1
 
        elif df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'freeze_bout'].sum() > 0: #if there was a freeze bout from loom onset till 2 seconds from  loom_offset
            df_try.loc[loom_offset[i], 'esc_freeze'] = 1
    

    '''checking increase in speed''' #This block is checking if flies significantly increase their running speed after the looming stimulus. It does this with a bootstrapping approach (sampling random subsets of velocities before and after) and then applying a t-test. If the increase is real and not just noise, it marks that loom as an “escape run.”
    for loom in range(len(loom_onset)):
        permutated_pre = df_try.loc[loom_onset[i]-120:(loom_onset[i]), 'velocity'] #velocities in the time window that goes from 2 second before loom onset to loom onset! 
        permutated_post = df_try.loc[loom_offset[i]:(loom_offset[i]+120), 'velocity'] #velocities in the time window that goes from loom offset to 2 second after!
        
        train_pre = []
        train_post = []
        ''' run 100 permutations of velocity per frame per loom(2 seconds before and after loom)'''
        for perm in range (100):
            df_sample_pre  = permutated_pre.sample(n=30) #df_sample_pre grabs 30 random frames from the 120 available
            row_pre = df_sample_pre.mean(axis=0) #mean of 30 frames
            train_pre.append(row_pre)
        
            df_sample_post  = permutated_post.sample(n=30)
            row_post = df_sample_post.mean(axis=0) #mean of 30 samples --> take unpaired t-test instead, if >0.05
            train_post.append(row_post)
    
        '''take t-test of 100 samples between groups'''            
        t, p = ttest_ind(train_pre, train_post)
        if (df_try.loc[loom_onset[loom],'freeze_bout']==0):
            if (t<0) & (p<0.05):
                df_try.loc[loom_offset[loom], 'esc_run'] = 1 #if t-test is significant, if yes --> 1
    
            
    '''slicing dataframe from esc_turn until end'''
    df_loom = df_try.loc[loom_offset, 'esc_turn':].copy().reset_index(drop=True)
    df_all = pd.concat([df_all,df_loom])

df_all = df_all.reset_index()
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
df_grouped = df_all.groupby('index').mean() #all rows in df_all that have the same value in the 'index' column (which represent looms) are put into the same group and the mean is calculated
df_grouped['loom'] = range(len(df_grouped)) #groupby('index') → groups rows by loom. .mean() → computes the fraction of flies engaging in this behaviours per loom.
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