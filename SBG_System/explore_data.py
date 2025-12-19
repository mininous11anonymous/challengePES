import pandas as pd
import os
import zipfile

data_dir = r"c:\Users\21652\Documents\GitHub\challengePES\data"

# Load Excel file
excel_file = os.path.join(data_dir, "BatteryFailureDatabankV2.xlsx")
print("=" * 60)
print("EXCEL FILE ANALYSIS")
print("=" * 60)

try:
    xls = pd.ExcelFile(excel_file)
    print(f"\nSheet names: {xls.sheet_names}")

    for sheet in xls.sheet_names[:3]:  # First 3 sheets
        df = pd.read_excel(excel_file, sheet_name=sheet)
        print(f"\n{sheet}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)[:10]}...")  # First 10 cols
        print(f"  Sample row: {df.iloc[0].to_dict() if len(df) > 0 else 'Empty'}")
except Exception as e:
    print(f"Error: {e}")

# Examine ZIP file structure
zip_file = os.path.join(data_dir, "calce-dataset.zip")
print("\n" + "=" * 60)
print("ZIP FILE ANALYSIS")
print("=" * 60)

try:
    with zipfile.ZipFile(zip_file, 'r') as zf:
        file_list = zf.namelist()
        print(f"\nTotal files in ZIP: {len(file_list)}")
        print(f"First 15 files:")
        for f in file_list[:15]:
            print(f"  {f}")
except Exception as e:
    print(f"Error: {e}")
