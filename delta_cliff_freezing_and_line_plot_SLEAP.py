# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 11:30:57 2025

@author: User
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dabest
import tkinter, tkinter.filedialog
from datetime import datetime
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
        'Transient_Jump': 'Jump',}
    
    # Apply mapping
    df_try['Behavior'] = df_try['Behavior'].replace(behavior_mapping)    
    return df_try

#%%
# Define all groups

group_names  = ['luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase',
                   'DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase'] # use the group names as present in each filename (need to be inside the filename)
number_of_groups = len(group_names)


def load_path(): #need to be the folder containing classified_pose with all the csv in the same folder!!
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(parent=root, title='Choose parent folder to load files') #path is the scored folder!!
    root.destroy()
    return filename
rootdir = load_path()

# Create output directory for results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(rootdir, f"analysis_results_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

# TIME SCALES
frame_rate = 60
# EXPERIMENT DURATION (in sec) - DEFINE PER GROUP
baseline_group1 = 300  # 5 minutes
baseline_group2 = 30   # 30 seconds
# Calculate frames for each group
baseline_frames_group1 = baseline_group1 * frame_rate
baseline_frames_group2 = baseline_group2 * frame_rate


df_resist_freeze_all = pd.DataFrame()
df_freeze_all = pd.DataFrame()
for i in range(number_of_groups):
      fly_n=0
      
      group = group_names[i]
      for filename in sorted(os.listdir(rootdir)):
        if group not in filename:
            continue
        if not '.csv' in filename:
            continue
        # Read CSV with explicit keyword arguments
        fly_df = pd.read_csv(rootdir+'/'+filename,  usecols=['Behavior'])
        fly_df = simplify_behaviors(fly_df)
        if "30secbase" in filename:            
            resist_freeze_loom = (fly_df.loc[baseline_frames_group2:, 'Behavior'] == 'Resistant_Freeze').mean() #for freeze proportion per fly #
            freeze_loom = (fly_df.loc[baseline_frames_group2:, 'Behavior'] == 'Freeze').mean()
        elif "5minbase" in filename:            
            resist_freeze_loom = (fly_df.loc[baseline_frames_group1:, 'Behavior'] == 'Resistant_Freeze').mean() #for freeze proportion per fly        
            freeze_loom = (fly_df.loc[baseline_frames_group1:, 'Behavior'] == 'Freeze').mean()
        df_resist_freeze_all.loc[fly_n,group] = resist_freeze_loom
        df_freeze_all.loc[fly_n,group] = freeze_loom
        fly_n+=1

#%% Analysis 1: comparison within same RNAi (so comparing directly different baseline lenght)       FREEZE
multi_2group = dabest.load(df_freeze_all, idx=(
                                         ('luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase'),
                                         ('DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase'))) #copy and paste group_names 

# Plot and save figure
fig1 = multi_2group.cliffs_delta.plot(
    title=('Delta Freeze per baseline'), 
    swarmplot_kwargs={"size":0.2, "alpha": 0.6 })
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Freeze.pdf"), bbox_inches='tight')
print("Baseline comparison plot saved")

# Save statistics
stats1 = multi_2group.cliffs_delta
# Convert results to DataFrame and save
stats1_results = stats1.results.copy()
stats1_results.to_csv(os.path.join(output_dir, "diff_baseline_comparison_stats_Freeze.csv"))
print("diff_Baseline comparison statistics:")
print(stats1)

#%% Analysis 2: RNAi comparison within same baseline            FREEZE
multi_2group_rnai = dabest.load(df_freeze_all, idx=(
    ('luc_RNAi_TRIP-5minbase', 'DH44_RNAi_TRIP-5minbase'),
    ('luc_RNAi_TRIP-30secbase','DH44_RNAi_TRIP-30secbase')))

# Plot and save figure
fig2 = multi_2group_rnai.cliffs_delta.plot(
    title=('Delta Freeze per RNAi'), 
    swarmplot_kwargs={"size":0.2, "alpha": 0.6 })
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rnai_comparison_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "rnai_comparison_Freeze.pdf"), bbox_inches='tight')
print("RNAi comparison plot saved")

# Save statistics
stats2 = multi_2group_rnai.cliffs_delta
# Convert results to DataFrame and save
stats2_results = stats2.results.copy()
stats2_results.to_csv(os.path.join(output_dir, "rnai_comparison_stats_Freeze.csv"))
print("RNAi comparison statistics:")
print(stats2)
print()

# Save descriptive statistics
desc_stats = df_freeze_all.describe()
desc_stats.to_csv(os.path.join(output_dir, "descriptive_statistics_Freeze.csv"))
print(f"\nAll results saved to: {output_dir}")
plt.show()

#%% Analysis 1: comparison within same RNAi (so comparing directly different baseline lenght)       RESISTENT FREEZE 
multi_2group_resist = dabest.load(df_resist_freeze_all, idx=(
                                         ('luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase'),
                                         ('DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase'))) #copy and paste group_names 

# Plot and save figure
fig3 = multi_2group_resist.cliffs_delta.plot(
    title=('Delta Resistant Freeze per baseline'), 
    swarmplot_kwargs={"size":0.2, "alpha": 0.6 })
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Resistant_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison_Resistant_Freeze.pdf"), bbox_inches='tight')
print("Baseline comparison plot saved")

# Save statistics
stats3 = multi_2group_resist.cliffs_delta
# Convert results to DataFrame and save
stats3_results = stats3.results.copy()
stats3_results.to_csv(os.path.join(output_dir, "diff_baseline_comparison_stats_Resistant_Freeze.csv"))
print("diff_Baseline comparison statistics:")
print(stats3)

#%% Analysis 2: RNAi comparison within same baseline      RESISTENT FREEZE
multi_2group_rnai_resist = dabest.load(df_resist_freeze_all, idx=(
    ('luc_RNAi_TRIP-5minbase', 'DH44_RNAi_TRIP-5minbase'),
    ('luc_RNAi_TRIP-30secbase','DH44_RNAi_TRIP-30secbase')))

# Plot and save figure
fig4 = multi_2group_rnai_resist.cliffs_delta.plot(
    title=('Delta Resistant Freeze per RNAi'), 
    swarmplot_kwargs={"size":0.2, "alpha": 0.6 })
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rnai_comparison_Resistant_Freeze.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "rnai_comparison_Resistant_Freeze.pdf"), bbox_inches='tight')
print("RNAi comparison plot saved")

# Save statistics
stats4 = multi_2group_rnai_resist.cliffs_delta
# Convert results to DataFrame and save
stats4_results = stats4.results.copy()
stats4_results.to_csv(os.path.join(output_dir, "rnai_comparison_stats_Resistant_Freeze.csv"))
print("RNAi comparison statistics:")
print(stats4)
print()

# Save descriptive statistics
desc_stats_resist = df_resist_freeze_all.describe()
desc_stats_resist.to_csv(os.path.join(output_dir, "descriptive_statistics_Resistant_Freeze.csv"))
print(f"\nAll results saved to: {output_dir}")
plt.show()

