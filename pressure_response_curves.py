# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 09:37:57 2024

@author: Joshua
"""

import glob
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd


# Function to load and concatenate multiple CSV files
def load_data(file_pattern):
    files = glob.glob(file_pattern)  # Find all files matching the pattern
    df_list = [pd.read_csv(file) for file in files]  # Read each file into a DataFrame
    concatenated_df = pd.concat(
        df_list, ignore_index=True
    )  # Concatenate all DataFrames
    concatenated_df['Time'] = pd.to_datetime(
        concatenated_df['Time'], format='%m/%d/%Y %I:%M:%S %p'
    )  # Convert 'Time' column to datetime
    return concatenated_df


# Function to plot data for different time windows
def plot_multi_time_windows(data, time_windows, y_column, invert_y):
    fig = plt.figure(figsize=(10, 6))
    for window in time_windows:
        start_time, end_time, legend_label = window
        # Filter data within the specified time window
        mask = (data['Time'] >= start_time) & (data['Time'] <= end_time)
        filtered_data = data.loc[mask]

        # Plot the data
        plt.scatter(
            filtered_data['Source Pressure (mBar)'],
            filtered_data[y_column],
            label=f'{legend_label}',
        )

    plt.title(f'{plot_title_var.get()}')
    plt.xlabel('Source Pressure (mBar)')
    plt.ylabel(y_column)
    plt.legend()
    plt.grid(True)
    if invert_y:
        plt.gca().invert_yaxis()  # Invert Y-axis if checkbox is checked
    fig.show()


# Function to handle button click event
def plot_button_click():
    file_pattern = file_entry.get()
    try:
        data = load_data(file_pattern)
    except Exception as e:
        messagebox.showerror('File Error', f'Failed to load files: {str(e)}')
        return

    time_windows = []
    for i in range(len(start_times)):
        try:
            start_time = datetime.strptime(start_times[i].get(), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_times[i].get(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            messagebox.showerror(
                'Datetime Error',
                'Incorrect datetime format. Please use YYYY-MM-DD HH:MM:SS',
            )
            return
        legend_entry = legend_entries[i].get()
        time_windows.append((start_time, end_time, legend_entry))

    y_column = y_variable.get()  # Get the selected y-axis variable
    invert_y = invert_y_var.get()  # Get the value of the invert Y-axis checkbox

    plot_multi_time_windows(data, time_windows, y_column, invert_y)


# Function to handle export timestamps button click event
def export_button_click() -> None:
    with filedialog.asksaveasfile(mode='w', defaultextension='.txt') as file:
        if file:
            file.write(f'Data File Location: {file_entry.get()}\n\n')
            file.write(f'Title: {plot_title_var.get()}\n\n')
            file.write('Start Datetime\t\tEnd Datetime\t\tLabel\n')
            for i in range(len(start_times)):
                file.write(
                    f'{start_times[i].get()}\t{end_times[i].get()}\t{legend_entries[i].get()}\n'
                )


# Function to add a new row of start and end time entry boxes
def add_time_window() -> None:
    start_var = tk.StringVar()
    start_time_entry = ttk.Entry(time_frame, width=20, textvariable=start_var)
    start_time_entry.grid(
        row=len(start_times) + 1, column=0, padx=(10, 5), pady=5, sticky='w'
    )
    start_times.append(start_var)
    start_time_widgets.append(start_time_entry)

    end_var = tk.StringVar()
    end_time_entry = ttk.Entry(time_frame, width=20, textvariable=end_var)
    end_time_entry.grid(
        row=len(end_times) + 1, column=1, padx=(10, 5), pady=5, sticky='w'
    )
    end_times.append(end_var)
    end_time_widgets.append(end_time_entry)

    legend_var = tk.StringVar()
    legend_entry = ttk.Entry(time_frame, width=20, textvariable=legend_var)
    legend_entry.grid(
        row=len(legend_entries) + 1, column=2, padx=(10, 5), pady=5, sticky='w'
    )
    legend_entries.append(legend_var)
    legend_widgets.append(legend_entry)


def remove_time_window():
    if start_times:
        start_time_widgets.pop().destroy()
        start_times.pop()
    if end_times:
        end_time_widgets.pop().destroy()
        end_times.pop()
    if legend_entries:
        legend_widgets.pop().destroy()
        legend_entries.pop()


# Function to handle browse button click event
def browse_button_click():
    directory = filedialog.askdirectory()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, directory + '/*.csv')
    update_y_variable_options(directory)


# Function to update the options in the y-axis variable dropdown box
def update_y_variable_options(directory):
    files = glob.glob(directory + '/*.csv')
    if files:
        data = pd.read_csv(files[0])
        columns = list(data.columns)
        if 'Time' in columns:
            columns.remove('Time')  # Remove "Time" header
        if 'Source Pressure (mBar)' in columns:
            columns.remove(
                'Source Pressure (mBar)'
            )  # Remove "Source Pressure (mBar)" header
        y_variable['values'] = columns


# Create the main window
root = tk.Tk()
root.title('Pressure Response Curves')
root.columnconfigure(0, weight=1)

# Frame for file selection
file_frame = ttk.Frame(root)
file_frame.grid(row=0, column=0, padx=5, pady=(10, 5), columnspan=2)

# File selection
file_label = tk.Label(file_frame, text='Enter file directory:', anchor='w')
file_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='ew')
file_entry = ttk.Entry(file_frame, width=50)
file_entry.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='ew')
browse_button = ttk.Button(file_frame, text='Browse', command=browse_button_click)
browse_button.grid(row=0, column=2, padx=(0, 5), pady=5, sticky='ew')

# Plot title
plot_title_var = tk.StringVar()
plot_title_label = tk.Label(file_frame, text='Plot Title:', anchor='w')
plot_title_label.grid(row=1, column=0, padx=(0, 5), pady=5, sticky='ew')
plot_title_entry = ttk.Entry(file_frame, width=50, textvariable=plot_title_var)
plot_title_entry.grid(row=1, column=1, padx=(0, 5), pady=5, sticky='ew')

# Frame for time selection
time_label_frame = ttk.Frame(root)
time_label_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ns')

# Time window selection labels
start_label = tk.Label(time_label_frame, text='Start Datetime', anchor='center')
start_label.grid(row=0, column=0, padx=37, pady=5, sticky='ew', columnspan=1)
end_label = tk.Label(time_label_frame, text='End Datetime', anchor='center')
end_label.grid(row=0, column=1, padx=37, pady=5, sticky='ew', columnspan=1)
legend_label = tk.Label(time_label_frame, text='Legend Label', anchor='center')
legend_label.grid(row=0, column=2, padx=37, pady=5, stick='ew', columnspan=1)

start_times = []
end_times = []
legend_entries = []

start_time_widgets = []
end_time_widgets = []
legend_widgets = []

# Frame to contain time entry boxes
time_frame = ttk.Frame(root)
time_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Initial row of start and end time entry boxes
start_var = tk.StringVar()
start_time_entry = ttk.Entry(time_frame, width=20, textvariable=start_var)
start_time_entry.grid(row=0, column=0, padx=(10, 5), pady=5, sticky='ew')
start_times.append(start_var)
start_time_widgets.append(start_time_entry)

end_var = tk.StringVar()
end_time_entry = ttk.Entry(time_frame, width=20, textvariable=end_var)
end_time_entry.grid(row=0, column=1, padx=(10, 5), pady=5, sticky='ew')
end_times.append(end_var)
end_time_widgets.append(end_time_entry)

legend_var = tk.StringVar()
legend_entry = ttk.Entry(time_frame, width=20, textvariable=legend_var)
legend_entry.grid(row=0, column=2, padx=(10, 5), pady=5, sticky='ew')
legend_entries.append(legend_var)
legend_widgets.append(legend_entry)

# Frame for datetime example
datetime_example_frame = ttk.Frame(root)
datetime_example_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2)

# Datetime example label
datetime_example_label = ttk.Label(
    datetime_example_frame, text='Datetime Format: YYYY-MM-DD HH:MM:SS', anchor='w'
)
datetime_example_label.grid(row=0, column=0, padx=5, pady=2, sticky='w')

# Frame for y-axis variable selection
y_variable_frame = ttk.Frame(root)
y_variable_frame.grid(row=4, column=0, padx=5, pady=5, sticky='ns')

# Y-axis variable selection label
y_variable_label = ttk.Label(y_variable_frame, text='Select Y-Axis Variable:')
y_variable_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='ew')

# Dropdown box for selecting y-axis variable
y_variable = ttk.Combobox(y_variable_frame, width=30)
y_variable.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='ew')

# Checkbutton for inverting Y-axis
invert_y_var = tk.BooleanVar()
invert_y_checkbutton = ttk.Checkbutton(
    y_variable_frame, text='Invert Y-Axis', variable=invert_y_var
)
invert_y_checkbutton.grid(row=0, column=2, padx=(0, 5), pady=5, sticky='w')

# Frame for add and remove buttons
add_remove_frame = ttk.Frame(root)
add_remove_frame.grid(row=5, column=0, padx=5, pady=5, sticky='ns')

# Button to add more time windows
add_button = ttk.Button(
    add_remove_frame, text='Add Time Window', command=add_time_window
)
add_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

# Button to remove time windows
remove_button = ttk.Button(
    add_remove_frame, text='Remove Time Window', command=remove_time_window
)
remove_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

# Plot button
plot_button = ttk.Button(root, text='Plot', command=plot_button_click)
plot_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Export timestamps button
export_button = ttk.Button(root, text='Export Timestamps', command=export_button_click)
export_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
