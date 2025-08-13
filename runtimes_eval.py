import os
import json
import pandas as pd
import re

root_dirs = [
    "executed_notebooks_edies_cleaner",
    "executed_notebooks_eval_algo_1",
    "executed_notebooks_eval_algo_2"
]

records = []

# Step 1: Walk through all dirs & collect runtimes
for root_dir in root_dirs:
    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".json"):
                fpath = os.path.join(subdir, fname)
                with open(fpath, "r") as f:
                    data = json.load(f)
                
                # Step 2: Extract cell 6 and 7 runtimes
                runtime_6 = next((d["execution_time_sec"] for d in data if d["cell_index"] == 6), None)
                runtime_7 = next((d["execution_time_sec"] for d in data if d["cell_index"] == 7), None)
                
                if runtime_6 is not None and runtime_7 is not None:
                    abs_diff = runtime_7 - runtime_6
                    pct_diff = (abs_diff / runtime_6) * 100 if runtime_6 > 0 else None
                    
                    records.append({
                        "file": fpath,
                        "edies": runtime_6,
                        "new_algo": runtime_7,
                        "abs_diff_sec": abs_diff,
                        "pct_diff": pct_diff
                    })

# Step 3: Make DataFrame
df = pd.DataFrame(records)

# Example: your current df has columns ['file', 'edies', 'runtime_cell_7', 'abs_diff_sec']
# Step 1: Extract just the postX part from the file path
df['post'] = df['file'].str.extract(r'(post\d+)')

# Step 2: Compute pct_diff as how much larger cell_6 is than cell_7
df['percentage_diff'] = ((df['edies'] / df['new_algo']) * 100)

# Step 3: Sort by post (you can convert 'postX' to int for proper numeric sort)
df['post_num'] = df['post'].str.extract(r'post(\d+)').astype(int)
df = df.sort_values('post_num').drop(columns='post_num')

# Step 4: Keep only relevant columns
df = df[['post', 'edies', 'new_algo','percentage_diff', 'abs_diff_sec',]]

df['edies'] = df['edies'].round(1)
df['new_algo'] = df['new_algo'].round(1)
df['abs_diff_sec'] = df['abs_diff_sec'].round(1)
df['percentage_diff'] = df['percentage_diff'].round(1)

# Overall averages
overall_avg_abs_diff = df['abs_diff_sec'].mean()
overall_avg_pct_diff = df['percentage_diff'].mean()

avg_row = {
    'post': 'AVERAGE',
    'edies': df['edies'].mean().round(1),
    'new_algo': df['new_algo'].mean().round(1),
    'abs_diff_sec': overall_avg_abs_diff,
    'percentage_diff': overall_avg_pct_diff
}

df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)

print(df)
