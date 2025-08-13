import pandas as pd
from pathlib import Path

# Only one directory to read from
base_dir = Path("output_eval_algo_1")

# Collect coverage files
coverage_files = list(base_dir.rglob("*_coverage.csv"))
print(f"Found {len(coverage_files)} coverage files.")

df_list = []
for file_path in coverage_files:
    df = pd.read_csv(file_path)

    # Drop rows where Coverage % is exactly 0
    df = df[df["Coverage %"] != 0]

    df_list.append(df)

# Combine all into one DataFrame
df_all = pd.concat(df_list, ignore_index=True)

# Group by Approx./Truth and take average coverage
df_avg = (
    df_all.groupby(["Approx.", "Truth"], as_index=False)["Coverage %"]
    .mean()
    .round(2)
)

# Sort by deviation from 100 (closest to 100 first)
df_avg["Deviation_from_100"] = (df_avg["Coverage %"] - 100).abs()
df_avg = df_avg.sort_values(by="Deviation_from_100", ascending=True)

# Drop the helper column before printing/saving
df_avg = df_avg.drop(columns=["Deviation_from_100"])

# Print in CSV-like style
print("Approx.,Truth,Coverage % avg across all files")
for _, row in df_avg.iterrows():
    print(f"{row['Approx.']},{row['Truth']},{row['Coverage %']}")


# Save to CSV
df_avg.to_csv("average_coverage_sorted.csv", index=False)
print("Saved sorted average coverage to average_coverage_sorted.csv")
