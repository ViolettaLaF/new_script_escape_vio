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
    behavior_mapping = {
        'Transient_Freeze': 'Freeze',
        'Sustained_Freeze': 'Freeze',
        'Resistant_Freeze': 'Freeze',      
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
 
#%% ============================================================
# EXPERIMENT CONFIGURATION — edit this section only
# ==============================================================
 
# --- Group names (must appear in filenames) ---
group_a = 'Tsh_Empty_Gtacr1-20Looms'
group_b = 'Tsh_Empty_Gtacr1-green_LED'
group_c = 'Tsh_39347_Gtacr1-20Looms'
group_d = 'Tsh_39347_Gtacr1-green_LED'
 
group_names = [group_a, group_b, group_c, group_d]
number_of_groups = len(group_names)
 
# --- Baseline mode ---
# Set to True  → different baselines per file (uses filename tags, see below)
# Set to False → all files share the same baseline length
DIFFERENT_BASELINES = False
 
# --- Baseline durations (seconds) ---
# Used when DIFFERENT_BASELINES = True: map filename tag → duration in seconds
baseline_tag_map = {
    '30secbase': 30,
    '5minbase': 300,
}
 
# Used when DIFFERENT_BASELINES = False: single baseline for all files
single_baseline_sec = 300  # e.g. for 5 min experiment
 
# --- Frame rate ---
frame_rate = 60
 
# --- Analysis comparisons (pairs of groups to compare) ---
# Analysis 1: e.g. LED ON vs LED OFF within same genotype
analysis_1_pairs = (
    (group_a, group_b),
    (group_c, group_d),
)
analysis_1_title = 'Delta Freeze — LED ON vs OFF'
analysis_1_filename = 'LED_comparison_ALL_Freeze'
 
# Analysis 2: e.g. genotype comparison within same condition
analysis_2_pairs = (
    (group_a, group_c),
    (group_b, group_d),
)
analysis_2_title = 'Delta Freeze — Empty vs Experimental'
analysis_2_filename = 'genotype_comparison_ALL_Freeze'
 
# --- Colour palette (one colour per group) ---
custom_palette = {
    group_a: 'C0',        # blue
    group_b: '#A9CCE3',   # light blue
    group_c: 'C1',        # orange
    group_d: '#FFB366',   # light orange
}
 
# ==============================================================
# END OF CONFIGURATION
# ==============================================================
 
#%% Load folder
def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(
        parent=root, title='Choose parent folder to load files')
    root.destroy()
    return filename
 
rootdir = load_path()
 
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(rootdir, f"analysis_results_{timestamp}")
os.makedirs(output_dir, exist_ok=True)
 
# Pre-compute baseline frames for the single-baseline case
single_baseline_frames = single_baseline_sec * frame_rate
 
#%% Load data
df_freeze_all = pd.DataFrame()
 
for i in range(number_of_groups):
    fly_n = 0
    group = group_names[i]
 
    for filename in sorted(os.listdir(rootdir)):
        if group not in filename:
            continue
        if not filename.endswith('.csv'):
            continue
 
        fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior'])
        fly_df = simplify_behaviors(fly_df)
 
        # --- Determine baseline frames ---
        if DIFFERENT_BASELINES:
            # Look for a matching tag in the filename
            matched_tag = None
            for tag in baseline_tag_map:
                if tag in filename:
                    matched_tag = tag
                    break
 
            if matched_tag is None:
                print(f"  WARNING: no baseline tag found in '{filename}'. "
                      f"Expected one of {list(baseline_tag_map.keys())}. Skipping file.")
                continue
 
            baseline_frames = baseline_tag_map[matched_tag] * frame_rate
        else:
            baseline_frames = single_baseline_frames
 
        # --- Compute freeze proportion after baseline ---
        freeze_loom = (fly_df.loc[baseline_frames:, 'Behavior'] == 'Freeze').mean()
        df_freeze_all.loc[fly_n, group] = freeze_loom
        fly_n += 1
 
print("Data loaded successfully.")
print(df_freeze_all)
 
#%% Analysis 1
multi_2group = dabest.load(df_freeze_all, idx=analysis_1_pairs)
 
fig1 = multi_2group.cliffs_delta.plot(
    title=analysis_1_title,
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette=custom_palette,
)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"{analysis_1_filename}.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, f"{analysis_1_filename}.pdf"), bbox_inches='tight')
print(f"Analysis 1 plot saved: {analysis_1_filename}")
 
stats1 = multi_2group.cliffs_delta
stats1.results.copy().to_csv(os.path.join(output_dir, f"{analysis_1_filename}_stats.csv"))
print("Analysis 1 statistics:")
print(stats1)
 
#%% Analysis 2
multi_2group_2 = dabest.load(df_freeze_all, idx=analysis_2_pairs)
 
fig2 = multi_2group_2.cliffs_delta.plot(
    title=analysis_2_title,
    swarmplot_kwargs={"size": 0.2, "alpha": 0.6},
    custom_palette=custom_palette,
)
# Nudge only the top of the effect size panel so the violin is not clipped.
# Reading dabest's auto-computed limits keeps the bottom data-driven.
es_ax2 = fig2.axes[1]
auto_bottom, auto_top = es_ax2.get_ylim()
es_ax2.set_ylim(auto_bottom, auto_top + 0.15)  # increase 0.15 if violin tip is still clipped
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"{analysis_2_filename}.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir, f"{analysis_2_filename}.pdf"), bbox_inches='tight')
print(f"Analysis 2 plot saved: {analysis_2_filename}")
 
stats2 = multi_2group_2.cliffs_delta
stats2.results.copy().to_csv(os.path.join(output_dir, f"{analysis_2_filename}_stats.csv"))
print("Analysis 2 statistics:")
print(stats2)
 
# Descriptive stats
desc_stats = df_freeze_all.describe()
desc_stats.to_csv(os.path.join(output_dir, "descriptive_statistics_ALL_Freeze.csv"))
print(f"\nAll results saved to: {output_dir}")
plt.show()