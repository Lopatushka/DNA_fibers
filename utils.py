import pandas as pd
import numpy as np
import os
from scipy.stats import mannwhitneyu

def load_data(dir, pixel_size=1):
    dfs = []
    all_dirs = []

    for root, dirs, files in os.walk(dir):
        all_dirs.append(dirs)
    
        for filename in files:
            if filename.lower().endswith(".csv"):

                path = os.path.join(root, filename)
                df = pd.read_csv(path)
                
                # If everything ended up in one column, try semicolon
                if df.shape[1] == 1:
                    df = pd.read_csv(path, sep=";")

                # Optional metadata
                df["File"] = os.path.splitext(filename)[0].replace(" ", "_")
                df["Path"] = path

                dfs.append(df) 

    # Combine all tables
    data = pd.concat(dfs, ignore_index=True)

    # Convert Length in pixels into micrometers
    data['Length'] = data['Length'].apply(lambda x: x * pixel_size)

    # Create ROI column
    data['ROI'] = data['Label'].apply(lambda x: x.split(":")[1])

    # Create Sample name column empty (custom parsing of filenames)
    data['Sample_name'] = None

    # Delete first 3 columns
    data.drop(data.columns[[0, 1, 2]], axis=1, inplace=True)

    # Reorder columns
    data = data[
        [
            "Sample_name",
            "File",
            "Measurement_type",
            "Length",
            "ROI",
            "Path"
        ]
    ]
    
    return data


def data_subset(df, measurement_type):
    return df[df['Measurement_type']==measurement_type]

def speed_processing(df, conversion_factor, time):
    # Checking speed file
    counts = df.groupby("File").size()
    odd_files = counts[counts % 2 != 0].index.tolist()

    if len(odd_files) == 0:
        print("All files contain an even number of fibers.")
    else:
        print("The following files contain an odd number of fibers will be removed:")
        print(*odd_files, sep="\n")
        
        # Removing odd files from speed dataframe
        df = df[~df["File"].isin(odd_files)].copy()
        
    # Add extra inedex to group pairs of files
    df["Index"] = df.groupby("File").cumcount() // 2

    # Calculate sum of fiber length in pairs
    df_processed = df.groupby(["File", "Index"], as_index=False).agg(
            Total_Length=("Length", "sum"),
            ROI=("ROI", list),
            Path=("Path", "first"),
            Sample_name=("Sample_name", "first")
            )

    # Convert speed to kb/min
    df_processed['Speed_kb_min'] = df_processed['Total_Length'].apply(lambda x: x * conversion_factor / time)

    # Delete extra columns
    final = df_processed[['Sample_name', 'File', 'Speed_kb_min', 'ROI', 'Path']]
    
    return final

def iod_processing(df, conversion_factor):
    df['IOD_kb'] = df['Length'].apply(lambda x: x * conversion_factor)
    df = df[["Sample_name", "File", 'IOD_kb', 'ROI', 'Path']]
    return df

def description_stats(df, col):
    return df.groupby("Sample_name")[col].agg(
        Count="count",
        Mean="mean",
        Median="median",
        SD="std",
    )
    
def outliers(df, col, q1=0.25, q2=0.75):
    Q1 = df[col].quantile(q1)
    Q3 = df[col].quantile(q2)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    final = df[(df[col] < lower) | (df[col] > upper)]
    
    return final

def u_test(df, col, control_sample):
    # Subset of control data to compare with
    control_df = df.loc[
        df["Sample_name"] == control_sample,
        col
    ].dropna()

    experimental_samples = set(df["Sample_name"]) - {control_sample}

    results = []

    # Iteration through the experimental samples
    for sample in experimental_samples:
        # Subset of experimental sample
        sample_df = df.loc[
        df["Sample_name"] == sample,
        col
        ].dropna()
        
        # Statistics calculation
        stat, p = mannwhitneyu(
        control_df,
        sample_df
        )
        
        results.append({
        "Group_1": control_sample,
        "Group_2": sample,
        "Group_1_n": len(control_df),
        "Group_2_n": len(sample_df),
        "U": stat,
        "p-value": p,
        })

    # Convert data into dataframe
    final = pd.DataFrame(results)
    
    return final