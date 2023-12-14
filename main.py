import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tqdm import tqdm

from portfolio_sim import runSim
from gui_utils import validateInput, isDate, getInputFilePath, getOutputFilePath

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # dict to store input dialog messages
    inputs = {
        'newsig': 'Select an Excel file of portfolio signals',
        'benchmarks': 'Select an Excel file of benchmark prices'
    }

    # dict to store dataframes
    dfs = {}

    for key, message in inputs.items():
        file_path = getInputFilePath(message)
        if not file_path:
            print(f'No input file for {key} selected. Exiting.')
            return
        dfs[key] = pd.read_excel(file_path, sheet_name='prices', skiprows=1)

    # Ensure pricing data starts 4 days after signal post (so we have previous price data on day one)
    dfs['newsig'].drop([0, 1, 2, 3], axis=1, inplace=True)

    while True:
        start_date = validateInput('Input', 'Enter Start Date (YYYY-MM-DD):', isDate, 'Invalid date format. Use YYYY-MM-DD.')

        if start_date is not None:
            break
        else:
            print('Start Date not provided. Exiting.')
            return

    while True:
        end_date = validateInput('Input', 'Enter End Date (YYYY-MM-DD):',
                                         lambda date: isDate(date) and pd.to_datetime(date) >= pd.to_datetime(start_date, format='%Y-%m-%d'),
                                         'Invalid End Date. It must be a valid date and greater than or equal to the Start Date.')
        if end_date is not None:
            break
        else:
            print('End Date not provided. Exiting.')
            return

    while True:
        buy_size = simpledialog.askfloat("Input", "Enter Buy Size (0-1):", minvalue=0, maxvalue=1)
        if buy_size is not None:
            break
        else:
            print('Buy Size not provided. Exiting.')
            return

    portfolio_df, daily_df, monthly_df, returns_df, sold_df = runSim(dfs['newsig'], dfs['benchmarks'], start_date, end_date, buy_size)

    output_excel_file = getOutputFilePath()

    if not output_excel_file:
        print('No output file selected. Exiting.')
        return
    
    output_dfs = {
        'Returns': returns_df,
        'Portfolio': portfolio_df,
        'Daily Summary': daily_df,
        'Monthly Summary': monthly_df,
        'Positions Sold': sold_df
    }

    with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
        for sheet_name, df, in tqdm(output_dfs.items()):
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print('Done!')

if __name__ == '__main__':
    main()