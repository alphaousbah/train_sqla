import sys
from pathlib import Path
import win32com.client as win32

from engine.model.frequency_severity import (
    DistributionInput,
    DistributionType,
    get_modelyearloss_frequency_severity,
    LossType,
)


def open_excel_workbook(filepath: Path):
    """Opens an Excel workbook and returns the workbook object."""
    excel = win32.Dispatch("Excel.Application")
    return excel.Workbooks.Open(str(filepath))


def write_output_data(ws_output, df_output, table_output):
    """Writes the output data to the Excel worksheet."""
    # Clear existing data if present
    if table_output.DataBodyRange is not None:
        table_output.DataBodyRange.Delete()

    # Define range and write new data
    start_cell = table_output.Range.Cells(2, 1)
    end_cell = start_cell.Offset(len(df_output), len(df_output.columns))
    ws_output.Range(start_cell, end_cell).Value = df_output.to_numpy()

    ws_output.Select()


def main():
    """Main execution function."""
    # Step 1: Connect the Excel UI
    # Get workbook path from arguments or default to script name
    wb_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / f"{Path(__file__).stem}.xlsm"
    wb = open_excel_workbook(wb_path)

    # Step 2: Extract input data
    ws_input = wb.Worksheets("Input")
    threshold = ws_input.Range("threshold").Value
    frequency_distribution = ws_input.Range("frequency_distribution").Value
    frequency_params = [ws_input.Range(f"frequency_parameter_{i}").Value for i in range(5)]
    severity_distribution = ws_input.Range("severity_distribution").Value
    severity_params = [ws_input.Range(f"severity_parameter_{i}").Value for i in range(5)]
    cat_share = ws_input.Range("cat_share").Value
    simulated_years = int(ws_input.Range("simulated_years").Value)
    modelfile_id = int(ws_input.Range("modelfile_id").Value)

    # Step 3: Prepare inputs for the engine function
    frequency_input = DistributionInput(
        dist=DistributionType(frequency_distribution),
        threshold=threshold,
        params=frequency_params,
    )
    severity_input = DistributionInput(
        dist=DistributionType(severity_distribution),
        threshold=threshold,
        params=severity_params,
    )

    loss_type = LossType(loss_type)

    # Step 4: Get output data
    df_output = get_modelyearloss_frequency_severity(
        frequency_input=frequency_input,
        severity_input=severity_input,
        loss_type=loss_type,
        simulated_years=simulated_years,
        modelfile_id=modelfile_id,
    )

    # Step 5: Write output data back to the Excel UI
    ws_output = wb.Worksheets("Output")
    table_output = ws_output.ListObjects("table_output")
    write_output_data(ws_output, df_output, table_output)


if __name__ == "__main__":
    main()
