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

# Define all groups

group_names  = ['luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase',
                   'DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase'] # use the group names as present in each filename
number_of_groups = len(group_names)
#rootdir = "F:/Experiments/DH44_manipulation/DH44_gal4_uas_RNAi/TRIP/5vs30secbase/already_tracked_no_sleep/5_min_30sec_together/scored" # folder wher the files are stored



def load_path():
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



df_freeze_all = pd.DataFrame()
for i in range(number_of_groups):
      fly_n=0
   
      df_freeze_group= pd.DataFrame()
   
      group = group_names[i]
      for filename in sorted(os.listdir(rootdir)):
        if group not in filename:
            continue
        if not '.csv' in filename:
            continue
        # Read CSV with explicit keyword arguments
        fly_df = pd.read_csv(rootdir+'/'+filename,  usecols=['freeze_bout'])
        if "30secbase" in filename:            
            freeze_loom = fly_df.loc[baseline_frames_group2:,'freeze_bout'].mean() #for freeze proportion per fly #
        elif "5minbase" in filename:            
            freeze_loom = fly_df.loc[baseline_frames_group1:,'freeze_bout'].mean() #for freeze proportion per fly        
       
        df_freeze_all.loc[fly_n,group] = freeze_loom
        fly_n+=1

#%% Analysis 1: comparison within same RNAi (so comparing directly different baseline lenght)
multi_2group = dabest.load(df_freeze_all, idx=(
                                         ('luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase'),
                                         ('DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase')
                                       ))

# Plot and save figure
fig1 = multi_2group.cliffs_delta.plot(
    title=('Delta freeze per baseline'), 
    swarmplot_kwargs={"size":1}
)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "diff_baseline_comparison.pdf"), bbox_inches='tight')
print("Baseline comparison plot saved")

# Save statistics
stats1 = multi_2group.cliffs_delta
# Convert results to DataFrame and save
stats1_results = stats1.results.copy()
stats1_results.to_csv(os.path.join(output_dir, "diff_baseline_comparison_stats.csv"))
print("diff_Baseline comparison statistics:")
print(stats1)

#%% Analysis 2: RNAi comparison within same baseline
multi_2group_rnai = dabest.load(df_freeze_all, idx=(
    ('luc_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-5minbase'),
    ('luc_RNAi_TRIP-30secbase','DH44_RNAi_TRIP-30secbase')
))

# Plot and save figure
fig2 = multi_2group_rnai.cliffs_delta.plot(
    title=('Delta freeze per RNAi'), 
    swarmplot_kwargs={"size":1}
)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rnai_comparison.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "rnai_comparison.pdf"), bbox_inches='tight')
print("RNAi comparison plot saved")

# Save statistics
stats2 = multi_2group_rnai.cliffs_delta
# Convert results to DataFrame and save
stats2_results = stats2.results.copy()
stats2_results.to_csv(os.path.join(output_dir, "rnai_comparison_stats.csv"))
print("RNAi comparison statistics:")
print(stats2)
print()

# Save descriptive statistics
desc_stats = df_freeze_all.describe()
desc_stats.to_csv(os.path.join(output_dir, "descriptive_statistics.csv"))
print(f"\nAll results saved to: {output_dir}")
plt.show()