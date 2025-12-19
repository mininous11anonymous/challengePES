import pandas as pd
import zipfile
import os

data_dir = r"c:\Users\21652\Documents\GitHub\challengePES\data"
zip_file = os.path.join(data_dir, "calce-dataset.zip")

print("=" * 60)
print("CALCE CSV FILE ANALYSIS")
print("=" * 60)

with zipfile.ZipFile(zip_file, 'r') as zf:
    # Get first CSV file
    csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
    
    for csv_file in csv_files[:3]:  # First 3 CSV files
        print(f"\n{csv_file}:")
        with zf.open(csv_file) as f:
            df = pd.read_csv(f)
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Data types:\n{df.dtypes}")
            print(f"  Sample:\n{df.head(3)}")
            print(f"  Numeric stats:\n{df.describe()}")
