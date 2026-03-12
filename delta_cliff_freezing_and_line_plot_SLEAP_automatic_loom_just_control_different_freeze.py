# -*- coding: utf-8 -*- #can be used for 2 groups of different baseline lenght 
"""
Baseline Comparison Analysis - 5min vs 30sec
Simplified for 2 groups only: comparing baseline durations

For your thesis committee meeting - Good luck! 🎓
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dabest
import tkinter, tkinter.filedialog
from datetime import datetime
import re

#%% ==================== BEHAVIOR SIMPLIFICATION ====================

def simplify_behaviors(df_try):
    behavior_mapping = {
        'Transient_Freeze': 'Freeze',
        'Sustained_Freeze': 'Freeze',
        'Resistant_Freeze': 'Resistant_Freeze',      
        'Transient_Stationary': 'Stationary',
        'Sustained_Stationary': 'Stationary',
        'Resistant_Stationary': 'Stationary',        
        'Transient_Walk': 'Walk',
        'Sustained_Walk': 'Walk',
        'Resistant_Walk': 'Walk',        
        'Transient_Jump': 'Jump',
    }
    df_try['Behavior'] = df_try['Behavior'].replace(behavior_mapping)    
    return df_try

#%% ==================== LOOM DETECTION ====================

def detect_loom_times(rootdir, group_names, frame_rate=60):
    all_loom_onsets = []
    baseline_frames = {}
    
    print("\n" + "=" * 60)
    print("DETECTING LOOM TIMES FROM DATA")
    print("=" * 60)
    
    for group in group_names:
        group_loom_onsets = []
        
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
            
            try:
                fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['VisualStim'])
                loom_onset = fly_df.loc[fly_df['VisualStim'].diff() == -1].index.values.astype(int)
                
                if len(loom_onset) > 0:
                    group_loom_onsets.append(loom_onset)
                    all_loom_onsets.append(loom_onset)
                    
                    if group not in baseline_frames:
                        baseline_frames[group] = loom_onset[0]
                        
            except Exception as e:
                print(f"Warning: Could not read VisualStim from {filename}: {e}")
                continue
        
        if len(group_loom_onsets) > 0:
            avg_looms = np.array(group_loom_onsets[0])
            print(f"\n{group}:")
            print(f"  Baseline frames: {baseline_frames[group]}")
            print(f"  Baseline duration: {baseline_frames[group]/frame_rate:.1f} seconds")
            print(f"  Number of looms detected: {len(avg_looms)}")
    
    if len(all_loom_onsets) > 0:
        reference_looms = all_loom_onsets[0]
        first_loom_frame = reference_looms[0]
        relative_loom_frames = reference_looms - first_loom_frame
        relative_loom_times = relative_loom_frames / frame_rate
        
        print("\n" + "-" * 60)
        print("DETECTED LOOM PATTERN:")
        print(f"Loom times (seconds from first loom): {relative_loom_times}")
        print(f"Inter-loom intervals: {np.diff(relative_loom_times)}")
        print("-" * 60)
        
        return {
            'loom_frames': relative_loom_frames,
            'loom_times': relative_loom_times,
            'baseline_frames': baseline_frames
        }
    else:
        print("\n⚠️  WARNING: No looms detected!")
        return {
            'loom_frames': np.array([0, 600, 1200, 1800, 2400, 3000]),
            'loom_times': np.array([0, 10, 20, 30, 40, 50]),
            'baseline_frames': {group: 300*frame_rate if '5minbase' in group else 30*frame_rate 
                               for group in group_names}
        }

#%% ==================== TIMECOURSE FUNCTIONS ====================

def calculate_behavior_timecourse(rootdir, group_names, behavior_type, baseline_frames_dict, frame_rate=60, 
                                   bin_size_sec=0.5):
    bin_size_frames = int(bin_size_sec * frame_rate)
    group_data = {}
    max_total_length = 0
    max_baseline_frames = max(baseline_frames_dict.values())
    
    for group in group_names:
        group_flies = []
        baseline_frames = baseline_frames_dict[group]
        start_padding = max_baseline_frames - baseline_frames
        
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
                
            fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
            fly_df = simplify_behaviors(fly_df)
            
            if behavior_type == 'Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Freeze').astype(float)
            elif behavior_type == 'Resistant_Freeze':
                fly_df['target_behavior'] = (fly_df['Behavior'] == 'Resistant_Freeze').astype(float)
            elif behavior_type == 'All_Freeze':
                fly_df['target_behavior'] = ((fly_df['Behavior'] == 'Freeze') | 
                                            (fly_df['Behavior'] == 'Resistant_Freeze')).astype(float)
            else:
                raise ValueError(f"Unknown behavior_type: {behavior_type}")
            
            all_data = fly_df['target_behavior'].values
            
            if start_padding > 0:
                all_data = np.concatenate([np.full(start_padding, np.nan), all_data])
            
            group_flies.append(all_data)
            max_total_length = max(max_total_length, len(all_data))
        
        padded_flies = []
        for fly_data in group_flies:
            if len(fly_data) < max_total_length:
                padded = np.concatenate([fly_data, np.full(max_total_length - len(fly_data), np.nan)])
            else:
                padded = fly_data
            padded_flies.append(padded)
        
        group_data[group] = np.array(padded_flies)
    
    n_bins = int(np.ceil(max_total_length / bin_size_frames))
    timecourse_df = pd.DataFrame()
    
    for group in group_names:
        group_array = group_data[group]
        percentages = []
        
        for i in range(n_bins):
            start_frame = i * bin_size_frames
            end_frame = min((i + 1) * bin_size_frames, group_array.shape[1])
            bin_data = group_array[:, start_frame:end_frame]
            percentage = np.nanmean(bin_data) * 100
            percentages.append(percentage)
        
        timecourse_df[group] = percentages
    
    time_vector = np.arange(n_bins) * bin_size_sec - max_baseline_frames / frame_rate
    timecourse_df.insert(0, 'Time_sec', time_vector)
    
    return {
        'timecourse_data': timecourse_df,
        'aligned_time': time_vector,
        'baseline_frames': baseline_frames_dict,
        'bin_size_sec': bin_size_sec,
        'max_baseline_frames': max_baseline_frames,
        'n_per_group': {group: group_data[group].shape[0] for group in group_names}  # store n per group
    }


def plot_behavior_timecourse(timecourse_results, group_names, behavior_type, loom_times, colors=None, figsize=(12, 6),
                            title=None, ylabel=None, show_legend=True, save_path=None):

    ylabel_map = {
        'All_Freeze':       'Flies Freezing (%)',
        'Freeze':           'Flies Labile Freezing (%)',
        'Resistant_Freeze': 'Flies Resistant Freezing (%)',
    }

    df = timecourse_results['timecourse_data']
    n_per_group = timecourse_results.get('n_per_group', {})
    time = df['Time_sec'].values / 60
    loom_times_minutes = np.array(loom_times) / 60
    
    if colors is None:
        colors = sns.color_palette("husl", len(group_names))
    
    fig, ax = plt.subplots(figsize=figsize)
    
    for i, group in enumerate(group_names):
        n = n_per_group.get(group, '')
        label = f"{group} (n={n})" if n != '' else group
        ax.plot(time, df[group].values, 
               label=label,
               color=colors[i], 
               linewidth=2,
               alpha=0.8)
    
    for loom_time in loom_times_minutes:
        if loom_time >= time[0] and loom_time <= time[-1]:
            ax.axvline(x=loom_time, color='grey', linestyle='--', linewidth=1.5, alpha=0.6, zorder=0)
    
    ax.set_xlabel('Time (minutes)', fontsize=22)
    
    if ylabel is None:
        ylabel = ylabel_map.get(behavior_type, f'Flies showing {behavior_type} (%)')
    ax.set_ylabel(ylabel, fontsize=22)
    
    # No title
    ax.set_title('')

    ax.tick_params(axis='both', labelsize=16)
    ax.grid(True, alpha=0.3, linestyle=':')

    if show_legend:
        ax.legend(loc='best', frameon=False, fontsize=18)  # larger legend, no frame
    
    ax.set_ylim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(f"{save_path}.png", dpi=300, bbox_inches='tight')
        plt.savefig(f"{save_path}.pdf", bbox_inches='tight')
        print(f"Timecourse plot saved: {os.path.basename(save_path)}")
    
    return fig, ax

#%% ==================== SETUP ====================

group_A = 'GFP_RNAi'   # ⚠️ CHANGE THIS to match your filenames
group_B = 'DH44_RNAi'  # ⚠️ CHANGE THIS to match your filenames

group_names = [group_A, group_B]
frame_rate = 60

def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(
        parent=root, 
        title='Choose parent folder to load files'
    )
    root.destroy()
    return filename

rootdir = load_path()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(rootdir, f"baseline_comparison_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print(f"\nOutput directory: {output_dir}")
print(f"Groups: {group_names}")

#%% ==================== DETECT LOOM TIMES ====================

loom_info = detect_loom_times(rootdir, group_names, frame_rate)
loom_times = loom_info['loom_times']
baseline_frames_dict = loom_info['baseline_frames']

#%% ==================== CLIFF'S DELTA ANALYSIS ====================
print("\n" + "=" * 60)
print("CLIFF'S DELTA ANALYSIS")
print("=" * 60)

df_freeze           = pd.DataFrame()
df_resistant_freeze = pd.DataFrame()
df_all_freeze       = pd.DataFrame()
n_per_group = {}

for group in group_names:
    fly_n = 0
    group_baseline_frames = baseline_frames_dict[group]
    
    for filename in sorted(os.listdir(rootdir)):
        if group not in filename or '.csv' not in filename:
            continue
            
        fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
        fly_df = simplify_behaviors(fly_df)
        
        freeze = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Freeze').mean()
        resistant_freeze = (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Resistant_Freeze').mean()
        all_freeze = ((fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Freeze') | 
                      (fly_df.loc[group_baseline_frames:, 'Behavior'] == 'Resistant_Freeze')).mean()
        
        df_freeze.loc[fly_n, group]           = freeze
        df_resistant_freeze.loc[fly_n, group] = resistant_freeze
        df_all_freeze.loc[fly_n, group]       = all_freeze
        fly_n += 1
    
    n_per_group[group] = fly_n

print("\nNumber of flies per group:")
for group, n in n_per_group.items():
    print(f"  {group}: n={n}")

# Simple column names — no n embedded
df_combined = pd.DataFrame({
    f'Freezing_{group_A}':        df_all_freeze[group_A].values,
    f'Freezing_{group_B}':        df_all_freeze[group_B].values,
    f'Labile F._{group_A}':       df_freeze[group_A].values,
    f'Labile F._{group_B}':       df_freeze[group_B].values,
    f'Resistant F._{group_A}':    df_resistant_freeze[group_A].values,
    f'Resistant F._{group_B}':    df_resistant_freeze[group_B].values,
})

multi_behaviors = dabest.load(df_combined, idx=(
    (f'Freezing_{group_A}',     f'Freezing_{group_B}'),
    (f'Labile F._{group_A}',    f'Labile F._{group_B}'),
    (f'Resistant F._{group_A}', f'Resistant F._{group_B}'),
))

fig_cliff = multi_behaviors.cliffs_delta.plot(
    title='',
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6}
)

# Fix y-axis label on effect size axis
for ax in fig_cliff.axes:
    if 'value' in ax.get_ylabel().lower():
        ax.set_ylabel("Time (%)", fontsize=14)

# Strip (N=...) and behavior prefix, keep only group name
swarm_ax = fig_cliff.axes[0]
new_labels = []
for label in swarm_ax.get_xticklabels():
    text = label.get_text()
    text = re.sub(r'\n\(N=\d+\)', '', text)       # remove (N=...)
    text = re.sub(r'^[^_]*_', '', text)            # remove behavior prefix
    new_labels.append(text)
swarm_ax.set_xticklabels(new_labels, fontsize=10)

# Add group subtitles centered over each of the 3 comparisons
subplot_labels = ['Freezing', 'Labile F.', 'Resistant F.']
xlims = swarm_ax.get_xlim()
x_positions = np.linspace(xlims[0], xlims[1], 7)[1::2]  # centers of 3 groups
y_top = swarm_ax.get_ylim()[1]

for xpos, label in zip(x_positions, subplot_labels):
    swarm_ax.text(xpos, y_top * 1.02, label,
                  ha='center', va='bottom',
                  fontsize=15, fontweight='normal',
                  transform=swarm_ax.transData,
                  clip_on=False)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "cliffs_delta_all_behaviors.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "cliffs_delta_all_behaviors.pdf"), bbox_inches='tight')
print("✓ Combined Cliff's delta plot saved")

stats_all = multi_behaviors.cliffs_delta
stats_all.results.to_csv(os.path.join(output_dir, "cliffs_delta_all_behaviors_stats.csv"))
df_combined.describe().to_csv(os.path.join(output_dir, "descriptive_stats_all_behaviors.csv"))
#%% ==================== TIMECOURSE PLOTS ====================

# Map internal key → display title and ylabel
behavior_display = {
    'All_Freeze':       {'title': 'Freezing',          'ylabel': 'Flies Freezing (%)'},
    'Freeze':           {'title': 'Labile Freezing',    'ylabel': 'Flies Labile Freezing (%)'},
    'Resistant_Freeze': {'title': 'Resistant Freezing', 'ylabel': 'Flies Resistant Freezing (%)'},
}

for behavior, display in behavior_display.items():
    print(f"\n--- Processing {display['title']} ---")
    
    timecourse = calculate_behavior_timecourse(
        rootdir=rootdir,
        group_names=group_names,
        behavior_type=behavior,
        baseline_frames_dict=baseline_frames_dict,
        frame_rate=frame_rate,
        bin_size_sec=0.5
    )
    
    fig, ax = plot_behavior_timecourse(
        timecourse_results=timecourse,
        group_names=group_names,
        behavior_type=behavior,
        loom_times=loom_times,
        title=display['title'],
        ylabel=display['ylabel'],
        colors=['C0', 'C1'],
        save_path=os.path.join(output_dir, f"timecourse_{behavior}")
    )

# Save loom info
loom_info_df = pd.DataFrame({
    'Loom_Number': range(len(loom_times)),
    'Time_seconds': loom_times,
    'Frame': loom_info['loom_frames']
})
loom_info_df.to_csv(os.path.join(output_dir, "detected_loom_times.csv"), index=False)

#%% ==================== SUMMARY ====================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
plt.show()
