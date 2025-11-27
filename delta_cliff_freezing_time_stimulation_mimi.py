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

# Define all groups



group_names  = ['luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase',
                   'DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase'] # use the group names as present in each filename
number_of_groups = len(group_names)
rootdir = "F:/Experiments/DH44_manipulation/DH44_gal4_uas_RNAi/TRIP/5vs30secbase/already_tracked_no_sleep/5_min_30sec_together/scored" # folder wher the files are stored


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
            freeze_loom = fly_df.loc[300:,'freeze_bout'].mean() #for freeze proportion per fly
        elif "5minbase" in filename:            
            freeze_loom = fly_df.loc[18000:,'freeze_bout'].mean() #for freeze proportion per fly        
       
        df_freeze_all.loc[fly_n,group] = freeze_loom
        fly_n+=1

#%%
multi_2group = dabest.load(df_freeze_all, idx=(
                                         ('luc_RNAi_TRIP-5minbase','luc_RNAi_TRIP-30secbase'),
                                         ('DH44_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-30secbase')
                                       ))

multi_2group.cliffs_delta.plot(title=('delta freeze per baseline'), swarmplot_kwargs={"size":1});

print(multi_2group.cliffs_delta)

#%%
multi_2group = dabest.load(df_freeze_all, idx=(
                                         ('luc_RNAi_TRIP-5minbase','DH44_RNAi_TRIP-5minbase'),
                                         ('luc_RNAi_TRIP-30secbase','DH44_RNAi_TRIP-30secbase')
                                       ))

multi_2group.cliffs_delta.plot(title=('delta freeze per baseline'), swarmplot_kwargs={"size":1});

print(multi_2group.cliffs_delta)