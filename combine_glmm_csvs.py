# -*- coding: utf-8 -*-
"""
Combine GLMM CSVs from all 4 groups into two final dataframes:
  - combined_loom_responses_glmm.csv   (df1: all looms, mutually exclusive categories)
  - combined_escape_detail_glmm.csv    (df2: escape + mix looms only, combination string)

Run this AFTER running the main analysis script for all 4 groups.
"""

import pandas as pd
import os
import tkinter
import tkinter.filedialog


# ── SELECT FOLDER CONTAINING ALL 4 CSV FILES ─────────────────────────────────
def load_path():
    root = tkinter.Tk()
    folder = tkinter.filedialog.askdirectory(
        parent=root, title='Select folder containing all GLMM CSVs')
    root.destroy()
    return folder

folder = load_path()
print(f"Selected folder: {folder}")


# ── FIND AND LOAD CSVs ────────────────────────────────────────────────────────
all_files = os.listdir(folder)

loom_files   = sorted([f for f in all_files if f.endswith('_loom_responses_glmm.csv')])
escape_files = sorted([f for f in all_files if f.endswith('_escape_detail_glmm.csv')])

print(f"\nFound {len(loom_files)} loom_responses files:")
for f in loom_files:
    print(f"  {f}")

print(f"\nFound {len(escape_files)} escape_detail files:")
for f in escape_files:
    print(f"  {f}")

# Warn if not exactly 4
if len(loom_files) != 4:
    print(f"\n⚠ Warning: expected 4 loom_responses files, found {len(loom_files)}")
if len(escape_files) != 4:
    print(f"\n⚠ Warning: expected 4 escape_detail files, found {len(escape_files)}")


# ── CONCATENATE ───────────────────────────────────────────────────────────────
df_loom_combined   = pd.concat(
    [pd.read_csv(os.path.join(folder, f)) for f in loom_files],
    ignore_index=True
)

df_escape_combined = pd.concat(
    [pd.read_csv(os.path.join(folder, f)) for f in escape_files],
    ignore_index=True
)


# ── QUICK SANITY CHECK ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("COMBINED LOOM RESPONSES (df1)")
print(f"{'='*60}")
print(f"Total rows    : {len(df_loom_combined)}")
print(f"Unique flies  : {df_loom_combined['fly_id'].nunique()}")
print(f"\nRows per genotype x treatment:")
print(df_loom_combined.groupby(['genotype', 'treatment']).size().to_string())
print(f"\nResponse counts:")
print(df_loom_combined['response'].value_counts().to_string())

print(f"\n{'='*60}")
print("COMBINED ESCAPE DETAIL (df2)")
print(f"{'='*60}")
print(f"Total rows    : {len(df_escape_combined)}")
print(f"Unique flies  : {df_escape_combined['fly_id'].nunique()}")
print(f"\nRows per genotype x treatment:")
print(df_escape_combined.groupby(['genotype', 'treatment']).size().to_string())
print(f"\nTop 15 escape combinations:")
print(df_escape_combined['escape_combination'].value_counts().head(15).to_string())
print(f"{'='*60}\n")


# ── SAVE ──────────────────────────────────────────────────────────────────────
out_loom   = os.path.join(folder, 'combined_loom_responses_glmm.csv')
out_escape = os.path.join(folder, 'combined_escape_detail_glmm.csv')

df_loom_combined.to_csv(out_loom,   index=False)
df_escape_combined.to_csv(out_escape, index=False)

print(f"✓ Saved: {out_loom}")
print(f"✓ Saved: {out_escape}")
