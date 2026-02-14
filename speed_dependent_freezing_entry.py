import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter
import tkinter.filedialog
from datetime import datetime


def simplify_behaviors(df_try):
    """Simplify behavior categories by combining similar behaviors."""
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


def check_freezing_by_type(behavior_val, freeze_type='all'):
    """Check if a behavior matches the specified freeze type."""
    if freeze_type == 'all':
        return behavior_val in ['Freeze', 'Resistant_Freeze']
    elif freeze_type == 'labile':
        return behavior_val == 'Freeze'
    elif freeze_type == 'resistant':
        return behavior_val == 'Resistant_Freeze'
    else:
        raise ValueError(f"Unknown freeze_type: {freeze_type}")


def get_dominant_behavior(df_window, behavior_column='Behavior'):
    """Get the most frequent behavior in a window."""
    if len(df_window) == 0:
        return None
    behavior_counts = df_window[behavior_column].value_counts()
    if len(behavior_counts) == 0:
        return None
    return behavior_counts.index[0]


def calculate_clean_speed(fly_df, loom_onset, window_sec=1.0, frame_rate=60):
    """
    Calculate average speed in window, excluding NaNs and jumps.
    
    Returns: average speed (mm/s) or np.nan if not enough valid data
    """
    window_frames = int(window_sec * frame_rate)
    
    if loom_onset < window_frames:
        return np.nan
    
    # Get the window
    window_start = loom_onset - window_frames
    window_end = loom_onset
    
    window_df = fly_df.iloc[window_start:window_end].copy()
    
    # Mask out only jump frames
    window_df['valid_speed'] = window_df['Speed'].copy()
    
    # Set jump frames to NaN
    window_df.loc[window_df['Behavior'] == 'Jump', 'valid_speed'] = np.nan
    
    # Calculate mean of valid speeds
    valid_speeds = window_df['valid_speed'].dropna()
    
    if len(valid_speeds) < window_frames * 0.2:  # Need at least 20% valid data
        return np.nan
    
    return valid_speeds.mean()


def assign_speed_bin(speed):
    """Assign speed to bin."""
    if pd.isna(speed):
        return None
    elif speed < 4:
        return '0-4'
    elif speed < 8:
        return '4-8'
    elif speed < 12:
        return '8-12'
    elif speed < 16:
        return '12-16'
    elif speed < 20:
        return '16-20'
    else:
        return '>20'


def analyze_speed_dependent_freezing_entry(rootdir, group_names, frame_rate=60):
    """
    Analyze relationship between pre-loom speed and freezing entry probability.
    
    For each loom event where fly was NOT freezing before:
    - Calculate average speed in 1sec before loom
    - Check if freezing entry occurred
    - Bin by speed
    """
    
    freeze_types = ['all', 'labile', 'resistant']
    speed_bins = ['0-4', '4-8', '8-12', '12-16', '16-20', '>20']
    
    # Store data for each freeze type and group
    results = {
        f'{freeze_type}_{group}': {bin_name: {'entry': [], 'total': 0} for bin_name in speed_bins}
        for freeze_type in freeze_types
        for group in group_names
    }
    
    # Store all speeds for histogram - separate for each freeze type and group
    speed_distributions = {
        f'{freeze_type}_{group}': [] 
        for freeze_type in freeze_types 
        for group in group_names
    }
    
    # NEW: Store detailed event data with fly identity for logistic regression
    detailed_events = {
        f'{freeze_type}_{group}': []
        for freeze_type in freeze_types
        for group in group_names
    }
    
    print("\n" + "=" * 60)
    print("ANALYZING SPEED-DEPENDENT FREEZING ENTRY")
    print("=" * 60)
    
    for group in group_names:
        print(f"\nProcessing group: {group}")
        
        for filename in sorted(os.listdir(rootdir)):
            if group not in filename or '.csv' not in filename:
                continue
            
            # Extract fly ID from filename
            fly_id = filename.replace('.csv', '')
            
            # Load data
            fly_df = pd.read_csv(os.path.join(rootdir, filename), usecols=['Behavior', 'VisualStim', 'Speed'])
            fly_df = simplify_behaviors(fly_df)
            
            # Detect looms
            loom_onset = fly_df.loc[fly_df['VisualStim'].diff() == -1].index.values.astype(int)
            loom_offset = fly_df.loc[fly_df['VisualStim'].diff() == 1].index.values.astype(int)
            
            if len(loom_onset) == 0:
                continue
            
            # Analyze each loom
            for i in range(len(loom_onset)):
                onset = loom_onset[i]
                offset = loom_offset[i] if i < len(loom_offset) else onset + int(frame_rate * 0.5)
                
                # Check each freeze type
                for freeze_type in freeze_types:
                    window_1sec = int(frame_rate * 1.0)
                    
                    # Check if we have enough data
                    if onset < window_1sec or offset + window_1sec >= len(fly_df):
                        continue
                    
                    # PRE-LOOM CHECK: Must NOT be freezing
                    pre_window = fly_df.iloc[onset - window_1sec:onset]
                    dominant_pre = get_dominant_behavior(pre_window)
                    frames_before_loom = fly_df.iloc[onset - 3:onset]['Behavior'].values
                    
                    pre_not_freezing = (not check_freezing_by_type(dominant_pre, freeze_type)) and \
                                      all(not check_freezing_by_type(b, freeze_type) for b in frames_before_loom)
                    
                    if not pre_not_freezing:
                        continue  # Skip this loom for this freeze type
                    
                    # Calculate clean speed
                    avg_speed = calculate_clean_speed(fly_df, onset, window_sec=1.0, frame_rate=frame_rate)
                    
                    if pd.isna(avg_speed):
                        continue  # Not enough valid speed data
                    
                    # Assign to speed bin
                    speed_bin = assign_speed_bin(avg_speed)
                    
                    if speed_bin is None:
                        continue
                    
                    # POST-LOOM CHECK: Did freezing occur?
                    post_window = fly_df.iloc[offset:offset + window_1sec]
                    dominant_post = get_dominant_behavior(post_window)
                    
                    freezing_entry = check_freezing_by_type(dominant_post, freeze_type)
                    
                    # Store result
                    key = f'{freeze_type}_{group}'
                    results[key][speed_bin]['entry'].append(1.0 if freezing_entry else 0.0)
                    results[key][speed_bin]['total'] += 1
                    
                    # Store speed for histogram - FOR EACH FREEZE TYPE
                    speed_distributions[key].append({'speed': avg_speed, 'bin': speed_bin})
                    
                    # NEW: Store detailed event data with fly identity
                    detailed_events[key].append({
                        'fly_id': fly_id,
                        'group': group,
                        'loom_number': i + 1,
                        'loom_onset_frame': onset,
                        'avg_speed': avg_speed,
                        'speed_bin': speed_bin,
                        'freezing_entry': 1 if freezing_entry else 0
                    })
    
    # Calculate probabilities
    probabilities = {
        f'{freeze_type}_{group}': {
            bin_name: np.mean(data['entry']) if len(data['entry']) > 0 else np.nan
            for bin_name, data in bins.items()
        }
        for freeze_type in freeze_types
        for group in group_names
        for bins in [results[f'{freeze_type}_{group}']]
    }
    
    # Convert speed distributions to DataFrames
    speed_dist_dfs = {
        key: pd.DataFrame(speeds) if len(speeds) > 0 else pd.DataFrame()
        for key, speeds in speed_distributions.items()
    }
    
    # NEW: Convert detailed events to DataFrames
    detailed_events_dfs = {
        key: pd.DataFrame(events) if len(events) > 0 else pd.DataFrame()
        for key, events in detailed_events.items()
    }
    
    return probabilities, results, speed_dist_dfs, speed_bins, detailed_events_dfs


def plot_speed_probability_curves(probabilities, results, speed_bins, group_names, output_dir):
    """
    Create line plots showing relationship between speed and freezing entry probability.
    One plot per freeze type, with one line per group.
    """
    
    freeze_types = ['all', 'labile', 'resistant']
    freeze_type_labels = {
        'all': 'All Freezing (Freeze + Resistant_Freeze)',
        'labile': 'Labile Freezing (Freeze only)',
        'resistant': 'Resistant Freezing (Resistant_Freeze only)'
    }
    
    # Assign colors based on actual group names
    color_palette = ['C0', '#A9CCE3']  #blu and pale blu ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, orange, green, red
    colors = {group: color_palette[i] for i, group in enumerate(group_names)}
    
    print(f"\nDEBUG - Colors dictionary: {colors}")
    print(f"DEBUG - Group names parameter: {group_names}")
    
    for freeze_type in freeze_types:
        fig, ax = plt.subplots(figsize=(7, 6))  # Reduced width from 10 to 7
        
        # Collect all probabilities across groups to determine y-axis
        all_probs = []
        
        for group in group_names:
            print(f"DEBUG - Processing group: '{group}', assigned color: {colors.get(group, 'GRAY FALLBACK')}")
            key = f'{freeze_type}_{group}'
            
            # Get probabilities and sample sizes for each bin
            probs = []
            ns = []
            x_positions = []
            
            for i, speed_bin in enumerate(speed_bins):
                prob = probabilities[key][speed_bin]
                n = results[key][speed_bin]['total']
                
                if not pd.isna(prob) and n > 0:
                    probs.append(prob)
                    ns.append(n)
                    x_positions.append(i)
            
            if len(probs) > 0:
                all_probs.extend(probs)  # Collect all probs for y-axis calculation
                
                # Plot line (no n labels on line plot anymore)
                ax.plot(x_positions, probs, 'o-', linewidth=2, markersize=8, 
                       label=f'{group}', color=colors.get(group, 'gray'))
        
        # Formatting
        ax.set_xticks(range(len(speed_bins)))
        ax.set_xticklabels(speed_bins)
        ax.set_xlabel('Speed Before Loom (mm/s)', fontsize=13)
        ax.set_ylabel('Probability of Freezing Entry', fontsize=13)
        ax.set_title(f'{freeze_type_labels[freeze_type]}', fontsize=14)
        
        # Auto-adjust y-axis based on ALL data (both groups)
        if len(all_probs) > 0:
            max_prob = max(all_probs)
            y_max = min(1.05, max(0.3, max_prob + 0.15))  # At least 0.3, add 15% headroom
        else:
            y_max = 1.05
        ax.set_ylim(-0.05, y_max)
        
        ax.legend(fontsize=13, frameon=False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'speed_entry_probability_{freeze_type}.png'), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(output_dir, f'speed_entry_probability_{freeze_type}.pdf'), bbox_inches='tight')
        plt.close()
        
        print(f"✓ {freeze_type.capitalize()} probability curve saved")


def plot_speed_distributions(speed_dist_dfs, speed_bins, group_names, output_dir):
    """
    Create histograms showing distribution of speeds for each freeze type.
    One plot per freeze type, with one histogram per group.
    """
    
    freeze_types = ['all', 'labile', 'resistant']
    freeze_type_labels = {
        'all': 'All Freezing',
        'labile': 'Labile Freezing',
        'resistant': 'Resistant Freezing'
    }
    
    # Assign colors based on actual group names
    color_palette = ['C0', '#A9CCE3']  #blu and pale blu ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, orange, green, red
    colors = {group: color_palette[i] for i, group in enumerate(group_names)}
    
    for freeze_type in freeze_types:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))  # Reduced width from 14 to 10
        
        for idx, group in enumerate(group_names):
            ax = axes[idx]
            key = f'{freeze_type}_{group}'
            df = speed_dist_dfs.get(key, pd.DataFrame())
            
            if len(df) == 0:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=12)
                ax.set_title(f'{group}', fontsize=14)
                continue
            
            # Count looms per bin
            bin_counts = df['bin'].value_counts()
            
            # Ensure all bins are present
            counts = [bin_counts.get(bin_name, 0) for bin_name in speed_bins]
            
            # Create bar plot
            x_positions = range(len(speed_bins))
            bars = ax.bar(x_positions, counts, color=colors.get(group, 'gray'), alpha=0.7, edgecolor='black')
            
            # Add counts on top of bars with "n=" prefix, no bold
            for x, count in zip(x_positions, counts):
                if count > 0:
                    ax.text(x, count + max(counts) * 0.02, f'n={count}', ha='center', fontsize=9)
            
            # Formatting
            ax.set_xticks(x_positions)
            ax.set_xticklabels(speed_bins)
            ax.set_xlabel('Speed Bin (mm/s)', fontsize=12)
            ax.set_ylabel('Loom Count', fontsize=12)
            ax.set_title(f'{group}\n{freeze_type_labels[freeze_type]}', 
                        fontsize=14)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'speed_distribution_{freeze_type}.png'), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(output_dir, f'speed_distribution_{freeze_type}.pdf'), bbox_inches='tight')
        plt.close()
        
        print(f"✓ {freeze_type.capitalize()} speed distribution histogram saved")


def save_summary_statistics(probabilities, results, speed_bins, group_names, output_dir):
    """Save summary statistics to CSV."""
    
    freeze_types = ['all', 'labile', 'resistant']
    
    summary_file = os.path.join(output_dir, 'speed_entry_summary.csv')
    
    with open(summary_file, 'w') as f:
        f.write("SPEED-DEPENDENT FREEZING ENTRY - SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")
        
        for freeze_type in freeze_types:
            f.write(f"\n{freeze_type.upper()} FREEZING\n")
            f.write("-" * 80 + "\n\n")
            
            for group in group_names:
                key = f'{freeze_type}_{group}'
                f.write(f"\n{group}:\n")
                f.write(f"{'Speed Bin':<15} {'N Looms':<10} {'Entry Prob':<15}\n")
                f.write("-" * 40 + "\n")
                
                for speed_bin in speed_bins:
                    n = results[key][speed_bin]['total']
                    prob = probabilities[key][speed_bin]
                    
                    if pd.isna(prob):
                        f.write(f"{speed_bin:<15} {n:<10} {'N/A':<15}\n")
                    else:
                        f.write(f"{speed_bin:<15} {n:<10} {prob:.3f}\n")
                
                f.write("\n")
    
    print(f"✓ Summary statistics saved to: {summary_file}")


def save_detailed_events_for_regression(detailed_events_dfs, output_dir):
    """
    Save detailed event-level data with fly identity for logistic regression.
    Creates one CSV per freeze type with columns: fly_id, group, loom_number, 
    loom_onset_frame, avg_speed, speed_bin, freezing_entry
    """
    
    freeze_types = ['all', 'labile', 'resistant']
    
    for freeze_type in freeze_types:
        # Combine both groups for this freeze type
        combined_data = []
        
        for key, df in detailed_events_dfs.items():
            if freeze_type in key and len(df) > 0:
                combined_data.append(df)
        
        if len(combined_data) > 0:
            combined_df = pd.concat(combined_data, ignore_index=True)
            
            # Sort by group and fly_id
            combined_df = combined_df.sort_values(['group', 'fly_id', 'loom_number'])
            
            # Save to CSV
            output_file = os.path.join(output_dir, f'detailed_events_{freeze_type}_for_regression.csv')
            combined_df.to_csv(output_file, index=False, quoting=1)
            
            print(f"✓ Detailed events for {freeze_type} freezing saved: {len(combined_df)} events from {combined_df['fly_id'].nunique()} flies")


def perform_chi_square_tests(speed_dist_dfs, speed_bins, group_names, output_dir):
    """
    Perform chi-square tests comparing speed distributions between groups.
    One test per freeze type.
    """
    from scipy.stats import chi2_contingency
    
    freeze_types = ['all', 'labile', 'resistant']
    freeze_type_labels = {
        'all': 'All Freezing',
        'labile': 'Labile Freezing',
        'resistant': 'Resistant Freezing'
    }
    
    results_file = os.path.join(output_dir, 'chi_square_tests.txt')
    
    with open(results_file, 'w') as f:
        f.write("CHI-SQUARE TESTS FOR SPEED DISTRIBUTIONS\n")
        f.write("=" * 80 + "\n\n")
        f.write("Test: Are the speed distributions different between the two groups?\n")
        f.write("Null hypothesis: Speed distributions are the same between groups\n\n")
        
        for freeze_type in freeze_types:
            f.write(f"\n{freeze_type_labels[freeze_type].upper()}\n")
            f.write("-" * 80 + "\n\n")
            
            # Get data for both groups
            group1_key = f'{freeze_type}_{group_names[0]}'
            group2_key = f'{freeze_type}_{group_names[1]}'
            
            df1 = speed_dist_dfs.get(group1_key, pd.DataFrame())
            df2 = speed_dist_dfs.get(group2_key, pd.DataFrame())
            
            if len(df1) == 0 or len(df2) == 0:
                f.write("Insufficient data for chi-square test\n\n")
                continue
            
            # Count looms per bin for each group
            counts1 = [df1[df1['bin'] == bin_name].shape[0] for bin_name in speed_bins]
            counts2 = [df2[df2['bin'] == bin_name].shape[0] for bin_name in speed_bins]
            
            # Create contingency table
            contingency_table = np.array([counts1, counts2])
            
            # Display contingency table
            f.write("Contingency Table:\n")
            f.write(f"{'Speed Bin':<15} {group_names[0]:<20} {group_names[1]:<20}\n")
            f.write("-" * 55 + "\n")
            for i, bin_name in enumerate(speed_bins):
                f.write(f"{bin_name:<15} {counts1[i]:<20} {counts2[i]:<20}\n")
            f.write(f"{'TOTAL':<15} {sum(counts1):<20} {sum(counts2):<20}\n\n")
            
            # Perform chi-square test
            try:
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                
                f.write(f"Chi-square statistic: {chi2:.4f}\n")
                f.write(f"Degrees of freedom: {dof}\n")
                f.write(f"P-value: {p_value:.4f}\n")
                
                if p_value < 0.001:
                    f.write(f"Result: HIGHLY SIGNIFICANT (p < 0.001) ***\n")
                elif p_value < 0.01:
                    f.write(f"Result: SIGNIFICANT (p < 0.01) **\n")
                elif p_value < 0.05:
                    f.write(f"Result: SIGNIFICANT (p < 0.05) *\n")
                else:
                    f.write(f"Result: NOT SIGNIFICANT (p >= 0.05)\n")
                
                f.write(f"\nInterpretation: ")
                if p_value < 0.05:
                    f.write(f"The speed distributions are significantly different between groups.\n")
                else:
                    f.write(f"No significant difference in speed distributions between groups.\n")
                
            except Exception as e:
                f.write(f"Error performing chi-square test: {str(e)}\n")
            
            f.write("\n")
    
    print(f"✓ Chi-square tests saved to: {results_file}")


#%% ==================== MAIN ====================

if __name__ == "__main__":
    # Define groups
    group_1 = '5minbase' #'luc_RNAi_TRIP-5'
    group_2 = '30secbase' #'DH44_RNAi_TRIP-5'
    group_names = [group_1, group_2]
    
    frame_rate = 60
    
    # Load directory
    def load_path():
        root = tkinter.Tk()
        filename = tkinter.filedialog.askdirectory(
            parent=root, 
            title='Choose parent folder to load files'
        )
        root.destroy()
        return filename
    
    rootdir = load_path()
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(rootdir, f"speed_dependent_freezing_entry_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📁 Output directory: {output_dir}")
    
    # Analyze speed-dependent freezing entry
    probabilities, results, speed_dist_dfs, speed_bins, detailed_events_dfs = analyze_speed_dependent_freezing_entry(
        rootdir, group_names, frame_rate
    )
    
    # Create plots
    plot_speed_probability_curves(probabilities, results, speed_bins, group_names, output_dir)
    plot_speed_distributions(speed_dist_dfs, speed_bins, group_names, output_dir)
    
    # Save statistics
    save_summary_statistics(probabilities, results, speed_bins, group_names, output_dir)
    
    # Save detailed event data for logistic regression
    save_detailed_events_for_regression(detailed_events_dfs, output_dir)
    
    # Perform chi-square tests on speed distributions
    perform_chi_square_tests(speed_dist_dfs, speed_bins, group_names, output_dir)
    
    print("\n" + "=" * 60)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\nAll results saved to: {output_dir}")
