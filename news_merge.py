import pandas as pd
import os

# Initialize an empty DataFrame to store the merged data
merged_df = pd.DataFrame()

# Directory containing the .xlsx files
directory = r"d:\coding"

# Loop through all .xlsx files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(directory, filename)
        df = pd.read_excel(file_path)
        merged_df = merged_df.append(df, ignore_index=True)

# Save the merged DataFrame to a new .xlsx file
merged_df.to_excel("news_merged.xlsx", index=False)
