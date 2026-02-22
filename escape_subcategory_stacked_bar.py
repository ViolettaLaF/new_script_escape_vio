# -*- coding: utf-8 -*-
"""
Horizontal stacked bar plot of escape subcategories (pure + top mixed)
with chi-square and post-hoc z-tests.

Input CSVs: produced by plot_escape_combination_stacked_bar_active_only()
            i.e. *_escape_combinations_summary.csv

Author: Violetta 
"""

import tkinter, tkinter.filedialog
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


# ============================================================================
# PARAMETERS — EDIT HERE
# ============================================================================

experiment_name   = 'controls_5min_vs_30sec_escape_subcategories'

group1_file  = 'VLF-39347_5min_escape_combinations_summary.csv'
group2_file  = 'VLF-39347_30sec_escape_combinations_summary.csv'
group1_label = 'controls 5min'
group2_label = 'controls 30sec'

N_TOP_MIXED = 4   # how many of the most-frequent mixed categories to keep as separate bars

# Colour palette — pure escapes get fixed colours; mixed get purples; infrequent mix gets grey
PURE_COLORS = {
    'Run':        '#EE8A9E',   # DC143C at alpha=0.5 on white background → blended to this pink
    'Backwards':  '#FB6609',   # same as ethogram Backwards_Walk
    'Walk_Away':  '#00CED1',   # same as ethogram Walk_Away
    'Turn_Wall':  '#22C350',   # same as ethogram Turn
    'Turn_Floor': '#206233',   # same as ethogram Floor_Turn
    'Jump':       '#8756B2',   # same as ethogram Jump
}

MIXED_COLORS = [   # used in order for the top-N mixed categories — earthy reds
    '#922B21', '#A93226', '#C0392B', '#7B241C',
]

INFREQ_COLOR = '#5D6D7E'   # dark slate grey — neutral "leftover" category

# ============================================================================
# PATH LOADING
# ============================================================================

def load_path():
    root = tkinter.Tk()
    filename = tkinter.filedialog.askdirectory(
        parent=root, title='Choose parent folder (containing /plots subfolder)')
    root.destroy()
    return filename

exp_path  = load_path()
plot_path = exp_path + '/plots'
plot_path_pdf = exp_path + '/plots_pdf'
plot_path_escape = exp_path + '/plots/escape_plots'
plot_path_pdf_escape = exp_path + '/plots_pdf/escape_plots'

for p in [plot_path, plot_path_pdf, plot_path_escape, plot_path_pdf_escape]:
    os.makedirs(p, exist_ok=True)

# ============================================================================
# LOAD AND PARSE CSV
# ============================================================================

def parse_escape_csv(filepath):
    """
    Read *_escape_combinations_summary.csv and return:
        - total_active  : int   denominator (escape + mix trials only)
        - pure_counts   : dict  {label: count}  — only the PURE rows
        - mixed_counts  : dict  {label: count}  — only the MIXED rows
    """
    df = pd.read_csv(filepath)

    # --- denominator: active escapes (escape_only + mix, i.e. everything
    #     except freeze_only and no_response)
    overall = df[df['Category'] == 'OVERALL']
    total_active = int(overall.loc[overall['Escape_Type'] == 'Active Escapes', 'Count'].values[0])

    pure  = df[df['Category'] == 'PURE'].set_index('Escape_Type')['Count'].to_dict()
    mixed = df[df['Category'] == 'MIXED'].set_index('Escape_Type')['Count'].to_dict()

    # cast to int
    pure  = {k: int(v) for k, v in pure.items()}
    mixed = {k: int(v) for k, v in mixed.items()}

    return total_active, pure, mixed


def build_bar_categories(total_active, pure_counts, mixed_counts, n_top_mixed=4):
    """
    Build the ordered list of (label, count, color) for ONE group.

    Order:
        1. Pure escapes (fixed order from PURE_COLORS, skip if absent)
        2. Top-N mixed (by frequency)
        3. Infrequent Mix (everything else lumped)

    All fractions are relative to total_active (the denominator).
    """
    categories = []  # list of dicts: {label, count, color}

    # --- 1. Pure escapes (in canonical order)
    for pure_label, color in PURE_COLORS.items():
        count = pure_counts.get(pure_label, 0)
        if count > 0:           # only add if present
            categories.append({'label': pure_label, 'count': count, 'color': color})

    # --- 2. Top-N mixed
    sorted_mixed = sorted(mixed_counts.items(), key=lambda x: x[1], reverse=True)
    top_mixed    = sorted_mixed[:n_top_mixed]
    rest_mixed   = sorted_mixed[n_top_mixed:]

    for i, (label, count) in enumerate(top_mixed):
        color = MIXED_COLORS[i % len(MIXED_COLORS)]
        categories.append({'label': label, 'count': count, 'color': color})

    # --- 3. Infrequent Mix
    infreq_count = sum(c for _, c in rest_mixed)
    if infreq_count > 0:
        categories.append({'label': 'Infrequent Mix', 'count': infreq_count, 'color': INFREQ_COLOR})

    return categories


# ============================================================================
# ALIGN CATEGORIES ACROSS TWO GROUPS
# ============================================================================

def align_categories(cats1, cats2):
    """
    Ensure both groups have the SAME set of category labels in the SAME order.
    Missing categories get count=0 and inherit the colour from the other group.

    Returns updated (cats1_aligned, cats2_aligned).
    """
    # Build ordered union of labels (preserve order from group1 first, then any extras from group2)
    labels_g1 = [c['label'] for c in cats1]
    labels_g2 = [c['label'] for c in cats2]

    all_labels = list(dict.fromkeys(labels_g1 + [l for l in labels_g2 if l not in labels_g1]))

    color_map = {c['label']: c['color'] for c in cats1 + cats2}

    def fill(cats, labels):
        existing = {c['label']: c for c in cats}
        return [existing.get(l, {'label': l, 'count': 0, 'color': color_map[l]})
                for l in labels]

    return fill(cats1, all_labels), fill(cats2, all_labels)


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def perform_statistical_tests(cats1, cats2, total1, total2):
    """
    Chi-square test of independence on the full contingency table,
    followed by per-category two-proportion z-tests with Bonferroni correction.

    cats1 / cats2 : aligned list of dicts {label, count, color}
    total1/2      : total_active (denominator) for each group
    """
    labels  = [c['label'] for c in cats1]
    counts1 = np.array([c['count'] for c in cats1])
    counts2 = np.array([c['count'] for c in cats2])

    # Drop categories where BOTH groups have count=0 (chi-square can't handle these)
    valid_mask = ~((counts1 == 0) & (counts2 == 0))
    labels  = [l for l, v in zip(labels, valid_mask) if v]
    counts1 = counts1[valid_mask]
    counts2 = counts2[valid_mask]
    print(f"\nCategories included in stats ({sum(valid_mask)} of {len(valid_mask)}): {labels}")

    contingency = [counts1.tolist(), counts2.tolist()]

    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS — ESCAPE SUBCATEGORIES")
    print("=" * 70)

    # --- Chi-square
    chi2, p_chi, dof, expected = chi2_contingency(contingency)
    print(f"\n1. Chi-Square Test of Independence:")
    print(f"   χ² = {chi2:.3f}, df = {dof}, p = {p_chi:.4f}")

    if p_chi < 0.05:
        print(f"   *** SIGNIFICANT: Groups differ in escape distributions (p < 0.05)")
        run_posthoc = True
    else:
        print(f"   NOT SIGNIFICANT: Groups do not differ overall (p ≥ 0.05)")
        run_posthoc = False

    # --- Post-hoc z-tests
    n_cats           = len(labels)
    bonferroni_alpha = 0.05 / n_cats
    z_test_results   = {}

    if run_posthoc:
        print(f"\n2. Post-hoc Two-Proportion Z-Tests (Bonferroni α = {bonferroni_alpha:.4f}):")
        print(f"   {'Category':<35} {'z-stat':>8} {'p-value':>10} {'Sig?'}")
        print(f"   {'-' * 60}")

        for label, c1, c2 in zip(labels, counts1, counts2):
            # Skip if both counts are 0 (category absent in both groups)
            if c1 == 0 and c2 == 0:
                z_test_results[label] = {'z_stat': np.nan, 'p_value': 1.0, 'significant': False}
                continue

            z_stat, p_value = proportions_ztest([c1, c2], [total1, total2])
            is_sig = p_value < bonferroni_alpha
            sig_str = '***' if p_value < 0.001 else ('**' if p_value < 0.01 else ('*' if is_sig else ''))
            z_test_results[label] = {'z_stat': z_stat, 'p_value': p_value, 'significant': is_sig}
            print(f"   {label:<35} {z_stat:>8.3f} {p_value:>10.4f}   {sig_str}")
    else:
        print("\n2. Post-hoc tests not performed (chi-square not significant)")
        for label in labels:
            z_test_results[label] = {'z_stat': np.nan, 'p_value': 1.0, 'significant': False}

    print("=" * 70 + "\n")

    return {
        'chi2': chi2, 'p_chi': p_chi, 'dof': dof,
        'z_tests': z_test_results,
        'bonferroni_alpha': bonferroni_alpha,
        'n_cats': n_cats,
    }


# ============================================================================
# PLOTTING
# ============================================================================

def plot_horizontal_escape_comparison(cats1, cats2, total1, total2,
                                      group1_label, group2_label,
                                      stats_results, save_path, experiment_name):
    """
    Two horizontal stacked bars (one per group) with significance annotations.
    X-axis = fraction of active escape trials (sums to 1).
    """

    labels   = [c['label'] for c in cats1]
    n_cats   = len(labels)

    fig, axes = plt.subplots(2, 1, figsize=(16, 4.5), sharex=True)
    fig.subplots_adjust(hspace=0.03, left=0.08, right=0.72, top=0.88, bottom=0.18)

    groups = [
        (cats1, total1, group1_label, axes[0]),
        (cats2, total2, group2_label, axes[1]),
    ]

    # We'll draw significance markers after plotting both bars
    # Store cumulative mid-points for each category in each group
    cum_mids = {0: {}, 1: {}}   # cum_mids[group_idx][label] = x_midpoint

    for g_idx, (cats, total, g_label, ax) in enumerate(groups):
        left = 0.0
        for cat in cats:
            frac = cat['count'] / total if total > 0 else 0
            ax.barh(0, frac, left=left, color=cat['color'],
                    height=0.99, edgecolor='white', linewidth=0.8)

            mid = left + frac / 2
            cum_mids[g_idx][cat['label']] = mid

            if frac > 0.025:
                ax.text(mid, 0, f'{frac*100:.1f}%',
                        ha='center', va='center', fontsize=9,
                        fontweight='bold', color='white')

            left += frac

        ax.set_yticks([0])
        ax.set_yticklabels([g_label], fontsize=14)
        ax.set_ylim(-0.6, 0.9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False)
        ax.set_xlim(0, 1.0)

        # Only the bottom subplot gets the x-axis line and tick marks
        if g_idx == 0:
            ax.spines['bottom'].set_visible(False)
            ax.tick_params(bottom=False)
        else:
            ax.spines['bottom'].set_visible(True)
            ax.spines['bottom'].set_position(('outward', 5))
            ax.tick_params(axis='x', labelsize=14)

    axes[1].set_xlabel('Fraction of escape and mix responses trials', fontsize=16)

    # --- Significance stars between bars
    if stats_results['p_chi'] < 0.05:
        for label in stats_results['z_tests'].keys():
            if stats_results['z_tests'][label]['significant']:
                x1 = cum_mids[0].get(label, None)
                x2 = cum_mids[1].get(label, None)
                if x1 is None or x2 is None:
                    continue
                x_mid = (x1 + x2) / 2

                p_val = stats_results['z_tests'][label]['p_value']
                stars = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else '*')

                # Draw line from top bar bottom edge to bottom bar top edge
                axes[0].annotate('', xy=(x_mid, -0.28), xytext=(x_mid, -0.28),
                                  xycoords='data', textcoords='data')
                # Just put stars in the gap between the two bars
                fig.text(
                    # convert x from data to figure coords (rough, uses axes[0])
                    axes[0].transData.transform([x_mid, 0])[0] / fig.get_figwidth() / fig.dpi,
                    0.495,  # midpoint between the two subplots in figure coords
                    stars, ha='center', va='center', fontsize=12, color='black',
                    fontweight='bold'
                )

    # Title
    chi_text = (f"χ²={stats_results['chi2']:.2f}, p={stats_results['p_chi']:.4f}"
                + (" ***" if stats_results['p_chi'] < 0.05 else ""))
    fig.suptitle(f"{experiment_name}\n{chi_text}", fontsize=13, y=0.97)

    # Legend — outside to the right
    legend_ax = fig.add_axes([0.73, 0.05, 0.26, 0.88])
    legend_ax.axis('off')

    handles = []
    for cat in cats1:   # use cats1 for colours/labels (aligned, so same labels)
        if cat['count'] > 0 or any(c['label'] == cat['label'] and c['count'] > 0 for c in cats2):
            import matplotlib.patches as mpatches
            handles.append(mpatches.Patch(color=cat['color'], label=cat['label']))
    # also add any cats2-only categories
    cat1_labels = {c['label'] for c in cats1}
    for cat in cats2:
        if cat['label'] not in cat1_labels and cat['count'] > 0:
            import matplotlib.patches as mpatches
            handles.append(mpatches.Patch(color=cat['color'], label=cat['label']))

    legend_ax.legend(handles=handles, loc='center left', fontsize=13,
                     frameon=False, title='Category', title_fontsize=14)

    # Footnote
    fig.text(0.38, -0.01,
             f"* p<0.05, ** p<0.01, *** p<0.001 (Bonferroni α={stats_results['bonferroni_alpha']:.4f})",
             ha='center', fontsize=8, style='italic')

    # Save
    for sp, fmt in [(plot_path, 'png'), (plot_path_pdf, 'pdf'),
                    (plot_path_escape, 'png'), (plot_path_pdf_escape, 'pdf')]:
        os.makedirs(sp, exist_ok=True)
        plt.savefig(f"{sp}/{experiment_name}_escape_subcategory_comparison.{fmt}",
                    bbox_inches='tight', dpi=300 if fmt == 'png' else None)

    plt.show()
    print(f"✓ Saved comparison plot to: {plot_path}/{experiment_name}_escape_subcategory_comparison.png")


# ============================================================================
# SAVE STATS TO CSV
# ============================================================================

def save_stats_to_csv(stats_results, cats1, cats2, total1, total2, save_path, experiment_name):

    labels   = [c['label'] for c in cats1]
    counts1  = {c['label']: c['count'] for c in cats1}
    counts2  = {c['label']: c['count'] for c in cats2}

    chi_df = pd.DataFrame({
        'Test': ['Chi-Square'],
        'Statistic': [stats_results['chi2']],
        'df': [stats_results['dof']],
        'p_value': [stats_results['p_chi']],
        'Significant': [stats_results['p_chi'] < 0.05],
    })
    chi_df.to_csv(f"{save_path}/{experiment_name}_escape_subcat_chi_square.csv", index=False)

    rows = []
    for label in labels:
        if label not in stats_results['z_tests']:
            continue
        r = stats_results['z_tests'][label]
        rows.append({
            'Category':         label,
            f'Count_{group1_label}': counts1.get(label, 0),
            f'Count_{group2_label}': counts2.get(label, 0),
            f'Frac_{group1_label}':  counts1.get(label, 0) / total1 if total1 > 0 else 0,
            f'Frac_{group2_label}':  counts2.get(label, 0) / total2 if total2 > 0 else 0,
            'z_statistic':      r['z_stat'],
            'p_value':          r['p_value'],
            'Bonferroni_alpha': stats_results['bonferroni_alpha'],
            'Significant':      r['significant'],
        })
    pd.DataFrame(rows).to_csv(
        f"{save_path}/{experiment_name}_escape_subcat_z_tests.csv", index=False)

    print(f"✓ Saved chi-square results to: {save_path}/{experiment_name}_escape_subcat_chi_square.csv")
    print(f"✓ Saved z-test results to:     {save_path}/{experiment_name}_escape_subcat_z_tests.csv")


# ============================================================================
# MAIN
# ============================================================================

# --- Load CSVs
total1, pure1, mixed1 = parse_escape_csv(os.path.join(plot_path, group1_file))
total2, pure2, mixed2 = parse_escape_csv(os.path.join(plot_path, group2_file))

print(f"\nGroup 1 ({group1_label}): {total1} active escape trials")
print(f"Group 2 ({group2_label}): {total2} active escape trials")

# --- Determine top-N mixed using COMBINED counts (so both groups share the same top categories)
combined_mixed = {}
for label, count in {**mixed1, **mixed2}.items():
    combined_mixed[label] = mixed1.get(label, 0) + mixed2.get(label, 0)
sorted_combined = sorted(combined_mixed.items(), key=lambda x: x[1], reverse=True)
top_mixed_labels = [l for l, _ in sorted_combined[:N_TOP_MIXED]]

print(f"\nTop {N_TOP_MIXED} mixed categories (combined ranking): {top_mixed_labels}")

# Override mixed dicts so that top-N is consistent across groups
def split_mixed_by_top(mixed_counts, top_labels):
    top  = {l: mixed_counts.get(l, 0) for l in top_labels}
    rest = {l: c for l, c in mixed_counts.items() if l not in top_labels}
    return top, rest

top_mixed1, rest_mixed1 = split_mixed_by_top(mixed1, top_mixed_labels)
top_mixed2, rest_mixed2 = split_mixed_by_top(mixed2, top_mixed_labels)

# Rebuild cats using the shared top-N
def build_aligned_cats(pure_counts, top_mixed_counts, rest_mixed_counts):
    cats = []
    for pure_label, color in PURE_COLORS.items():
        count = pure_counts.get(pure_label, 0)
        #if count > 0:
        cats.append({'label': pure_label, 'count': count, 'color': color})
    for i, label in enumerate(top_mixed_labels):
        count = top_mixed_counts.get(label, 0)
        cats.append({'label': label, 'count': count, 'color': MIXED_COLORS[i % len(MIXED_COLORS)]})
    infreq = sum(rest_mixed_counts.values())
    if infreq > 0:
        cats.append({'label': 'Infrequent Mix', 'count': infreq, 'color': INFREQ_COLOR})
    return cats

cats1 = build_aligned_cats(pure1, top_mixed1, rest_mixed1)
cats2 = build_aligned_cats(pure2, top_mixed2, rest_mixed2)

# Align so both lists have identical labels in identical order
cats1, cats2 = align_categories(cats1, cats2)

print(f"\nFinal categories ({len(cats1)}):")
for c1, c2 in zip(cats1, cats2):
    print(f"  {c1['label']:<35}  g1={c1['count']:4d} ({c1['count']/total1*100:5.1f}%)   "
          f"g2={c2['count']:4d} ({c2['count']/total2*100:5.1f}%)")

# Verify fractions sum to 1
frac_sum1 = sum(c['count'] for c in cats1) / total1
frac_sum2 = sum(c['count'] for c in cats2) / total2
print(f"\nFraction sums — Group1: {frac_sum1:.4f}  Group2: {frac_sum2:.4f}  (both should be 1.0)")

# --- Stats
stats_results = perform_statistical_tests(cats1, cats2, total1, total2)

# --- Plot
plot_horizontal_escape_comparison(
    cats1, cats2, total1, total2,
    group1_label, group2_label,
    stats_results, plot_path, experiment_name
)

# --- Save stats CSVs
save_stats_to_csv(stats_results, cats1, cats2, total1, total2, exp_path, experiment_name)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE!")
print("=" * 70)