import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from portfolio_sim import runSim
from gui_utils import input_with_validation, validate_date, get_input_file_path, get_output_file_path

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    newsig_file_path = get_input_file_path('Select an Excel file of portfolio signals')
    if not newsig_file_path:
        print('No input file selected. Exiting.')
        return

    newsig_df = pd.read_excel(newsig_file_path, sheet_name='prices')
    # Ensure pricing data starts 4 days after signal post (so we have previous price data on day one)
    newsig_df.drop([0, 1, 2, 3], axis=1, inplace=True)

    sp500_file_path = get_input_file_path('Select an Excel file of S&P500 prices')
    if not sp500_file_path:
        print('No input file2 selected. Exiting.')
        return

    sp500_df = pd.read_excel(sp500_file_path, sheet_name='prices')

    start_date = input_with_validation('Input', 'Enter Start Date (YYYY-MM-DD):', validate_date, 'Invalid date format. Use YYYY-MM-DD.')

    if start_date is None:
        print('Start Date not provided. Exiting.')
        return

    while True:
        end_date = input_with_validation('Input', 'Enter End Date (YYYY-MM-DD):',
                                         lambda date: validate_date(date) and pd.to_datetime(date) >= pd.to_datetime(start_date, format='%Y-%m-%d'),
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

    portfolio_df, daily_df, monthly_df, returns_df = runSim(newsig_df, sp500_df, start_date, end_date, buy_size)

    output_excel_file = get_output_file_path()

    if not output_excel_file:
        print('No output file selected. Exiting.')
        return

    with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
        portfolio_df.to_excel(writer, sheet_name='Portfolio', index=False)
        daily_df.to_excel(writer, sheet_name='Daily Summary', index=False)
        monthly_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
        returns_df.to_excel(writer, sheet_name='Returns', index=False)

if __name__ == '__main__':
    main()
