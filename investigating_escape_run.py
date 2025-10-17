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
import pickle

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

experiment_name = '39347_tsh_gal80_GFP_RNAi_KK-5minbase'

group1_label = 'VLF-39347_tsh_gal80_GFP_RNAi_KK-5minbase'

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
#in frames
zoom_before_loom_onset = 120
zoom_after_loom_onset = 600

#For line plots
bin_size_sec = 0.5
bin_size = bin_size_sec * frame_rate

bin_size_zoom_sec = 0.05
bin_size_zoom = bin_size_zoom_sec * frame_rate

#Zoom violin plots data interval selec 
before_loom_start = 60
before_loom_end = int(zoom_before_loom_onset)
before_loom_interval = int(before_loom_end - before_loom_start)

after_loom_start = int(zoom_before_loom_onset + loom_duration)
after_loom_end = int(after_loom_start + before_loom_interval)

zoom_line_plots_df = pd.DataFrame()
zoom_violin_plots_df = pd.DataFrame()

#%%
def heading(dx, dy):
    degs_lst =[]
    for i in range(len(dx)):
        if isinstance(dx[i], str):
            degs_lst.append('nan')
        else:
            rads = atan2(dy[i], dx[i]) 
            rads %= 2*np.pi
            degs = math.degrees(rads)
            degs_lst.append(degs)
    return degs_lst

#%%
'''upload scored file'''

df_all = pd.DataFrame()

path = exp_path
jump_velocity = 75

# Dictionary to store aggregate results across all files
aggregate_window_data = {}
aggregate_p_values = {}

# Initialize aggregate dictionaries with window keys
window_starts_sec_init = np.arange(0.5, 8.5, 0.5)
for w_sec in window_starts_sec_init:
    w_key = f"{w_sec:.1f}s"
    aggregate_window_data[w_key] = {'escape_runs': 0, 'total_looms': 0}
    aggregate_p_values[w_key] = []

# Create temp directory for storing intermediate data
if not os.path.exists(plot_path + '/temp_data'):
    os.makedirs(plot_path + '/temp_data')

for filename in sorted(os.listdir(path+'/scored/')):

    if not filename.endswith('frames.csv'):
        continue
    capital_x = filename.replace('X','x')
    if not capital_x.startswith(group1_label):
        continue
    df_try = pd.read_csv(path+'/scored/'+filename)
            
    loom_onset = df_try.loc[df_try['looming_bout'].diff() == 1].index.values.astype(int)
    loom_offset = df_try.loc[df_try['looming_bout'].diff() == -1].index.values.astype(int)
   
    df_try['esc_turn'] = 0
    df_try['esc_run'] = 0
    df_try['esc_jump'] = 0
    df_try['esc_freeze'] = 0
    df_try['escape'] = 0
    df_try['turn_run'] = 0
    df_try['walk_speed'] = np.nan
    df_try['walk_speed_bout'] = np.nan
    df_try['speed2d'] = np.nan

    '''checking turns'''
    heading_x_before = []
    heading_y_before = []
    heading_x_after = []
    heading_y_after = []
    
    "CHANGING COORDINATE SYSTEM"
    df_try['fly_x_norm_mm'] = df_try['fly_x_norm_mm'] - 15
    df_try['fly_y_norm_mm'] = (df_try['fly_y_norm_mm'] - 15) * -1 
    
    df_try.loc[(df_try['walk'] == 1), 'walk_speed'] = df_try['velocity']
    df_try.loc[(df_try['walk_bout'] == 1), 'walk_speed_bout'] = df_try['velocity']
    df_try.loc[(df_try['velocity'] < jump_velocity), 'speed2d'] = df_try['velocity']
    
    for loom in range(len(df_try)):    
        if loom in loom_onset:
            if df_try.loc[loom,'freeze_bout'] == 1:
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

    '''checking jumps and freeze'''
    for i in range(len(loom_onset)):
        if df_try.loc[loom_onset[i]:(loom_onset[i]+120), 'jumps'].sum() > 0:
            df_try.loc[loom_offset[i], 'esc_jump'] = 1
 
        elif df_try.loc[loom_onset[i]:(loom_offset[i]+120), 'freeze_bout'].sum() > 0:
            df_try.loc[loom_offset[i], 'esc_freeze'] = 1
    
    #%% SLIDING WINDOW ANALYSIS FOR ESCAPE RUNNING
    window_size_sec = 2
    window_size_frames = window_size_sec * frame_rate

    start_window_sec = 0.5
    end_window_sec = 8
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
    baseline_speed = df_try.loc[0:baseline_frames, 'velocity']
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
            
            permutated_pre = df_try_window.loc[loom_onset[loom]-120:(loom_onset[loom]), 'velocity']
            permutated_post = df_try_window.loc[window_post_start:window_post_end, 'velocity']
            
            if len(permutated_pre) < 30 or len(permutated_post) < 30:
                p_values_per_loom.append(np.nan)
                escape_runs_per_loom.append(0)
                continue
            
            train_pre = []
            train_post = []
            
            for perm in range(100):
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
                df_try_window.loc[loom_offset[loom], 'esc_run_window'] = 1
                escape_runs_per_loom.append(1)
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

    #%% PLOT: P-VALUES ACROSS ALL WINDOWS (per file)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    n_escapes_per_window = [sum(window_escape_runs[w]) for w in window_results.keys()]
    ax.plot(window_starts_sec, n_escapes_per_window, 'o-', linewidth=2, markersize=8, color='steelblue')
    ax.set_xlabel('Window start time after loom onset (sec)', fontsize=12)
    ax.set_ylabel('Number of escape runs', fontsize=12)
    ax.set_title('Escape Runs Detected vs Window Position', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    mean_p_values = []
    for w in window_results.keys():
        p_vals = [window_p_values[w][i] for i in range(len(window_escape_runs[w])) 
                  if window_escape_runs[w][i] == 1 and window_p_values[w][i] < 0.05 and not np.isnan(window_p_values[w][i])]
        mean_p_values.append(np.mean(p_vals) if p_vals else np.nan)
    ax.plot(window_starts_sec, mean_p_values, 'o-', linewidth=2, markersize=8, color='coral')
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='p=0.05')
    ax.set_xlabel('Window start time after loom onset (sec)', fontsize=12)
    ax.set_ylabel('Mean p-value (escape runs only)', fontsize=12)
    ax.set_title('Statistical Significance vs Window Position\n(Escape Runs Only)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    p_vals_for_box = []
    for w in window_results.keys():
        p_vals = [window_p_values[w][i] for i in range(len(window_escape_runs[w])) 
                  if window_escape_runs[w][i] == 1]
        p_vals_for_box.append(p_vals)
    
    bp = ax.boxplot(p_vals_for_box, labels=[f"{w}" for w in window_results.keys()], patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='p=0.05')
    ax.set_xlabel('Window start time (sec)', fontsize=12)
    ax.set_ylabel('P-value', fontsize=12)
    ax.set_title('Distribution of P-values Across Windows\n(Escape Runs Only)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    ax = axes[1, 1]
    ax.axis('off')
    summary_data = []
    for w in window_results.keys():
        n_esc = sum(window_escape_runs[w])
        p_vals = [p for p in window_p_values[w] if p < 0.05 and not np.isnan(p)]
        mean_p = np.mean(p_vals) if p_vals else np.nan
        summary_data.append([w, n_esc, f"{mean_p:.4f}" if not np.isnan(mean_p) else "N/A"])

    table = ax.table(cellText=summary_data, 
                    colLabels=['Window (sec)', 'N Escapes', 'Mean p-value'],
                    cellLoc='center', loc='center', fontsize=10)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    plt.tight_layout()
    filename_base = filename.replace('_frames.csv', '')
    plt.savefig(plot_path + f'/sliding_window_analysis_{filename_base}.png', dpi=300, bbox_inches='tight')
    plt.savefig(plot_path_pdf + f'/sliding_window_analysis_{filename_base}.pdf', bbox_inches='tight')
    print(f"Saved: sliding_window_analysis_{filename_base}.png/pdf")
    plt.show()

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
            speed_window = df_try.loc[loom-120:loom+600, 'velocity'].values  # CHANGED: 10 sec after (600 frames)
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
    plt.savefig(plot_path + f'/speed_profiles_windows_{filename_base}.png', dpi=300, bbox_inches='tight')
    plt.savefig(plot_path_pdf + f'/speed_profiles_windows_{filename_base}.pdf', bbox_inches='tight')
    print(f"Saved: speed_profiles_windows_{filename_base}.png/pdf")
    plt.show()

    #%% MODIFICATION 2: INDIVIDUAL EXAMPLES
    example_window = '2.0s'  # Change this to your chosen window

    if example_window in window_results:
        escape_indices = [i for i in range(len(window_escape_runs[example_window])) 
                         if window_escape_runs[example_window][i] == 1]
        non_escape_indices = [i for i in range(len(window_escape_runs[example_window])) 
                             if window_escape_runs[example_window][i] == 0]
        
        n_examples = min(5, len(escape_indices), len(non_escape_indices))
        
        if n_examples > 0:
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            
            # Escape examples
            ax = axes[0]
            for i in range(n_examples):
                idx = escape_indices[i]
                loom = loom_offset[idx]
                speed_trace = df_try.loc[loom-120:loom+600, 'velocity'].values
                if len(speed_trace) == 721:
                    time_points = np.arange(len(speed_trace)) / frame_rate - 2
                    ax.plot(time_points, speed_trace, alpha=0.7, linewidth=1.5, label=f'Escape {i+1}')
            
            ax.axhline(y=speed_threshold, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Speed threshold')
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Loom onset')
            ax.set_ylabel('Velocity (mm/sec)', fontsize=12)
            ax.set_title(f'Individual Escape Run Examples (Window: {example_window})', fontsize=13, fontweight='bold')
            ax.legend(fontsize=9, ncol=3)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-2, 10)
            
            # Non-escape examples
            ax = axes[1]
            for i in range(n_examples):
                idx = non_escape_indices[i]
                loom = loom_offset[idx]
                speed_trace = df_try.loc[loom-120:loom+600, 'velocity'].values
                if len(speed_trace) == 721:
                    time_points = np.arange(len(speed_trace)) / frame_rate - 2
                    ax.plot(time_points, speed_trace, alpha=0.7, linewidth=1.5, label=f'Non-escape {i+1}')
            
            ax.axhline(y=speed_threshold, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Speed threshold')
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Loom onset')
            ax.set_xlabel('Time relative to loom onset (sec)', fontsize=12)
            ax.set_ylabel('Velocity (mm/sec)', fontsize=12)
            ax.set_title(f'Individual Non-Escape Examples (Window: {example_window})', fontsize=13, fontweight='bold')
            ax.legend(fontsize=9, ncol=3)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-2, 10)
            
            plt.tight_layout()
            plt.savefig(plot_path + f'/individual_examples_{filename_base}.png', dpi=300, bbox_inches='tight')
            plt.savefig(plot_path_pdf + f'/individual_examples_{filename_base}.pdf', bbox_inches='tight')
            print(f"Saved: individual_examples_{filename_base}.png/pdf")
            plt.show()

    #%% SUMMARY FOR THIS FILE
    print("\n" + "="*60)
    print(f"SLIDING WINDOW ANALYSIS SUMMARY - {filename}")
    print("="*60)
    for w in sorted(window_results.keys()):
        n_esc = sum(window_escape_runs[w])
        p_vals = [p for p in window_p_values[w] if p < 0.05 and not np.isnan(p)]
        mean_p = np.mean(p_vals) if p_vals else np.nan
        print(f"\nWindow: {w} after loom onset")
        print(f"  Escape runs: {n_esc}")
        print(f"  Mean p-value: {mean_p:.4f}" if not np.isnan(mean_p) else "  Mean p-value: N/A")
        
        # Aggregate data
        aggregate_window_data[w]['escape_runs'] += n_esc
        aggregate_window_data[w]['total_looms'] += len(loom_onset)
        aggregate_p_values[w].extend(p_vals)
    
    print("\n" + "="*60 + "\n")
    
    # Save window escape runs for aggregate plotting (MODIFICATION 3)
    with open(plot_path + f'/temp_data/escape_runs_{filename_base}.pkl', 'wb') as f:
        pickle.dump({
            'window_escape_runs': window_escape_runs,
            'loom_offset': loom_offset,
            'filename': filename
        }, f)

#%% AGGREGATE SUMMARY ACROSS ALL FILES
print("\n\n" + "="*70)
print("AGGREGATE SUMMARY - ALL FILES COMBINED")
print("="*70)

for w in sorted(aggregate_window_data.keys()):
    n_esc = aggregate_window_data[w]['escape_runs']
    total = aggregate_window_data[w]['total_looms']
    p_vals = aggregate_p_values[w]
    mean_p = np.mean(p_vals) if p_vals else np.nan
    percent_esc = (n_esc / total * 100) if total > 0 else 0
    
    print(f"\nWindow: {w} after loom onset")
    print(f"  Escape runs: {n_esc} / {total} ({percent_esc:.1f}%)")
    print(f"  Mean p-value (escape runs only): {mean_p:.4f}" if not np.isnan(mean_p) else "  Mean p-value: N/A")
    print(f"  Number of significant looms: {len(p_vals)}")

print("\n" + "="*70)

#%% AGGREGATE PLOT: BEST WINDOW ACROSS ALL FILES
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
windows_list = sorted(aggregate_window_data.keys())
escape_percentages = [(aggregate_window_data[w]['escape_runs'] / aggregate_window_data[w]['total_looms'] * 100) 
                      for w in windows_list]
window_positions = [float(w.replace('s', '')) for w in windows_list]
ax.plot(window_positions, escape_percentages, 'o-', linewidth=2, markersize=10, color='darkgreen')
ax.set_xlabel('Window start time after loom onset (sec)', fontsize=12)
ax.set_ylabel('% Escape Runs', fontsize=12)
ax.set_title('Escape Run Detection Rate Across All Files', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xticks(window_positions)

ax = axes[1]
mean_p_per_window = [np.mean(aggregate_p_values[w]) if aggregate_p_values[w] else np.nan 
                     for w in windows_list]
ax.plot(window_positions, mean_p_per_window, 'o-', linewidth=2, markersize=10, color='darkred')
ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='p=0.05')
ax.set_xlabel('Window start time after loom onset (sec)', fontsize=12)
ax.set_ylabel('Mean p-value', fontsize=12)
ax.set_title('Statistical Significance Across All Files', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(window_positions)

plt.tight_layout()
plt.savefig(plot_path + '/aggregate_window_analysis.png', dpi=300, bbox_inches='tight')
plt.savefig(plot_path_pdf + '/aggregate_window_analysis.pdf', bbox_inches='tight')
print("\nSaved: aggregate_window_analysis.png/pdf")
plt.show()

print("\n" + "="*70 + "\n")

#%% MODIFICATION 3: AGGREGATE SPEED PLOT ACROSS ALL DATASET
all_escape_speeds = []
all_non_escape_speeds = []
final_window = '2.0s'  # CHANGE THIS to your chosen window

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
        
        # Extract speed traces
        for i, loom in enumerate(loom_offset):
            speed_window = df_file.loc[loom-120:loom+600, 'velocity'].values  # 2 sec before to 10 sec after
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