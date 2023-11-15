import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def validateInput(title, prompt, validate, error_message):
    while True:
        user_input = simpledialog.askstring(title, prompt)
        if user_input is None:
            # User canceled the input dialog
            return None
        if validate(user_input):
            return user_input
        else:
            messagebox.showerror('Error', error_message)

def isDate(date):
    try:
        pd.to_datetime(date, format='%Y-%m-%d')
        return True
    except ValueError:
        return False

def getInputFilePath(input_title):
    return filedialog.askopenfilename(title=input_title, filetypes=[('Excel files', '*.xlsx')])

def getOutputFilePath():
    return filedialog.asksaveasfilename(title='Create the output Excel file', filetypes=[('Excel files', '*.xlsx')], defaultextension='.xlsx')