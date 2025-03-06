import sys
from pathlib import Path

# import pandas as pd
from win32com.client import Dispatch

from engine.model.frequency_severity import (
    DistributionInput,
    DistributionType,
    get_modelyearloss_frequency_severity,
)

# --------------------------------------
# Step 1: Open the Excel file
# --------------------------------------

excel = Dispatch("Excel.Application")

try:
    wb_path = sys.argv[1]
    wb = excel.Workbooks.Open(wb_path)
except IndexError:
    wb = excel.Workbooks.Open(Path.cwd() / f"{Path(__file__).stem}.xlsm")

# --------------------------------------
# Step 2: Read the input data
# --------------------------------------

ws_input = wb.Worksheets("Input")

threshold: int = ws_input.Range("threshold").Value

# Extract frequency distribution and parameters
frequency_distribution = ws_input.Range("frequency_distribution").Value
frequency_params = [ws_input.Range(f"frequency_parameter_{i}").Value for i in range(5)]

# Extract severity distribution and parameters
severity_distribution = ws_input.Range("severity_distribution").Value
severity_params = [ws_input.Range(f"severity_parameter_{i}").Value for i in range(5)]

simulated_years: int = ws_input.Range("simulated_years").Value
peril_id: str = ws_input.Range("peril_id").Value
peril: str = ws_input.Range("peril").Value
region: str = ws_input.Range("region").Value
model_hash: str = ws_input.Range("model_hash").Value
model: str = ws_input.Range("model").Value
line_of_business: str = ws_input.Range("line_of_business").Value
modelfile_id: int = ws_input.Range("modelfile_id").Value

# df_layeryearloss = df_from_listobject(ws_input.ListObjects("LayerYearLoss"))

# --------------------------------------
# Step 3: Process the input data
# --------------------------------------

frequency_input = DistributionInput(
    dist=DistributionType(frequency_distribution),
    params=frequency_params,
)

severity_input = DistributionInput(
    dist=DistributionType(severity_distribution),
    params=severity_params,
)

# --------------------------------------
# Step 3: Get the output data
# --------------------------------------

df_output = get_modelyearloss_frequency_severity(
    frequency_input=frequency_input,
    severity_input=severity_input,
    modelfile_id=modelfile_id,
    simulated_years=int(simulated_years),
)

print(df_output)

# --------------------------------------
# Step 4: Write the output data
# --------------------------------------

# Define the output worksheet and table
ws_output = wb.Worksheets("Output")

table_output = ws_output.ListObjects("table_output")

# Clear the output table
if table_output.DataBodyRange is None:
    pass
else:
    table_output.DataBodyRange.Delete()

# Define the range for writing the output data, then write
cell_start = table_output.Range.Cells(2, 1)
cell_end = table_output.Range.Cells(2, 1).Offset(
    len(df_output),
    len(df_output.columns),
)
ws_output.Range(cell_start, cell_end).Value = df_output.to_numpy()

ws_output.Select()
