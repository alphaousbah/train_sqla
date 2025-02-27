import sys
from pathlib import Path

# import pandas as pd
from win32com.client import Dispatch
from engine.model.frequency_severity import get_modelyearloss_frequency_severity

# --------------------------------------
# Step 1: Open the Excel file
# --------------------------------------

excel = Dispatch("Excel.Application")

try:
    wb_path = sys.argv[1]
    wb = excel.Workbooks.Open(wb_path)
except IndexError:
    wb = excel.Workbooks.Open(f"{Path.cwd()}/run_freqsev_simulation.xlsm")

# --------------------------------------
# Step 2: Read the input data
# --------------------------------------

ws_input = wb.Worksheets("Input")

threshold: int = ws_input.Range("threshold").Value

frequency_distribution: str = ws_input.Range("frequency_distribution").Value
frequency_parameter_0: float = ws_input.Range("frequency_parameter_0").Value
frequency_parameter_1: float = ws_input.Range("frequency_parameter_1").Value
frequency_parameter_2: float = ws_input.Range("frequency_parameter_2").Value
frequency_parameter_3: float = ws_input.Range("frequency_parameter_3").Value
frequency_parameter_4: float = ws_input.Range("frequency_parameter_4").Value

severity_distribution: str = ws_input.Range("severity_distribution").Value
severity_parameter_0: float = ws_input.Range("severity_parameter_0").Value
severity_parameter_1: float = ws_input.Range("severity_parameter_1").Value
severity_parameter_2: float = ws_input.Range("severity_parameter_2").Value
severity_parameter_3: float = ws_input.Range("severity_parameter_3").Value
severity_parameter_4: float = ws_input.Range("severity_parameter_4").Value

simulated_years: int = ws_input.Range("simulated_years").Value
peril_id: str = ws_input.Range("peril_id").Value
peril: str = ws_input.Range("peril").Value
region: str = ws_input.Range("region").Value
model_hash: str = ws_input.Range("model_hash").Value
model: str = ws_input.Range("model").Value
line_of_business: str = ws_input.Range("line_of_business").Value

# df_layeryearloss = df_from_listobject(ws_input.ListObjects("LayerYearLoss"))

# --------------------------------------
# Step 3: Display the result instance
# --------------------------------------

# df = run_simulation(
#     simulation_years,
#     threshold,
#     severity_distribution,
#     severity_parameter_1,
#     severity_parameter_2,
#     frequency_parameter_1,
#     model_id,
#     loss_type,
# )

# --------------------------------------
# Step 4: Write the output data
# --------------------------------------

# Define the output worksheet and table
ws_output = wb.Worksheets("Output")

# table_output = ws_output.ListObjects("table_output")
#
# # Clear the output table
# if table_output.DataBodyRange is None:
#     pass
# else:
#     # pass
#     table_output.DataBodyRange.Delete()
#
# # Define the range for writing the output data, then write
# cell_start = table_output.Range.Cells(2, 1)
# cell_end = table_output.Range.Cells(2, 1).Offset(
#     len(df),
#     len(df.columns),
# )
# ws_output.Range(cell_start, cell_end).Value = df.values

ws_output.Select()
