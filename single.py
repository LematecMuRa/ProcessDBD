import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os
import pandas as pd
import re
import matplotlib.pyplot as plt

# GUI layout and components
def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_label.config(text=f"Selected file: {file_path}")

def save_output_file():
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if output_path:
        output_file_label.config(text=f"Output File: {output_path}")
    return output_path

def start_process():
    try:
        # Get input values from the GUI
        thickness = float(thickness_entry.get())
        disp_stack_change = true_false_var.get()
        text_file = file_label.cget("text").replace("Selected file: ", "")
        output_file = output_file_label.cget("text").replace("Output File: ", "")

        if not text_file:
            raise ValueError("No input file selected.")
        if not output_file:
            raise ValueError("No output file selected.")

        # Get controller checkboxes binary values
        controller_1 = controller_1_cb1_var.get() | (controller_1_cb2_var.get() << 1)
        controller_2 = (controller_2_cb1_var.get() << 2) | (controller_2_cb2_var.get() << 3)
        controller_binary = controller_1 | controller_2

        # Process data or run the background script here
        def keep_unique_values(values, threshold=400):
            result = [values[0]]
            for num in values[1:]:
                if num - result[-1] > threshold:
                    result.append(num)
            return result

        def remove_values_above_range(values, threshold):
            return [num for num in values if num < threshold]

        def main():
            data_dict = {}
            row_without_dbd_mes = []
            controller1 = []
            controller2 = []
            sngle_controller = []
            cell = 0
            stack_change = []

            if controller_binary & 0b0001: 
                controller1.append('dbdTrspMeasurement[1]')
            if controller_binary & 0b0010: 
                controller1.append('dbdTrspMeasurement[2]')
            if controller_binary & 0b0100: 
                controller2.append('dbdTrspMeasurement[3]')
            if controller_binary & 0b1000: 
                controller2.append('dbdTrspMeasurement[4]')
            
            upper_trshld = round(1.3 * thickness, 3)
            lower_trshld = round(0.8 * thickness, 3)

            # Regex pattern
            pattern = re.compile(
                r'bufferData\[(\d+)\]\.(blankFromCell|'
                r'dbdGtyMeasurement\[(1|3)\]|'
                r'visionCorrectionData\[1\]\.(X|Y|Rotation|Quality)|'
                r'dbdTrspMeasurement\[(1|2|3|4)\]) := ([\d\.-]+);'
            )

            with open(text_file, "r") as file:
                for line in file:
                    match = pattern.search(line)
                    if match:
                        buffer_index = int(match.group(1))
                        key = match.group(2)
                        value = float(match.group(6))

                        if buffer_index not in data_dict:
                            data_dict[buffer_index] = {
                                'bufferData': buffer_index,
                                'blankFromCell': None,
                                'dbdGtyMeasurement[1]': None,
                                'dbdGtyMeasurement[3]': None,
                                'X': None,
                                'Y': None,
                                'Rotation': None,
                                'Quality': None,
                                'dbdTrspMeasurement[1]': None,
                                'dbdTrspMeasurement[2]': None,
                                'dbdTrspMeasurement[3]': None,
                                'dbdTrspMeasurement[4]': None,
                            }
                        if key.startswith("visionCorrectionData[1]."):
                            key = key.split(".")[-1]
                        data_dict[buffer_index][key] = value

            filtered_dict = {k: v for k, v in data_dict.items() if v['blankFromCell'] is None or int(v['blankFromCell']) != 0}
            df_new = pd.DataFrame.from_dict(filtered_dict, orient='index')

            for index, row in df_new.iterrows():
                if (row['dbdTrspMeasurement[1]'] == 0 and row['dbdTrspMeasurement[2]'] == 0 
                    and row['dbdTrspMeasurement[3]'] == 0 and row['dbdTrspMeasurement[4]'] == 0
                    and row['X'] == 0 and row['Y'] == 0):
                    row_without_dbd_mes.append(index)

            df_dropped = df_new.drop(row_without_dbd_mes)
            df_dropped.to_excel(output_file, index=False)

            for index, row in df_dropped.iterrows():
                if (int((row['blankFromCell'])) != cell):
                    if cell != 0:
                        stack_change.append(index)
                    cell = int(row['blankFromCell'])

            row_without_dbd_mes = keep_unique_values(row_without_dbd_mes)
            row_without_dbd_mes = remove_values_above_range(row_without_dbd_mes, len(df_dropped))

            if len(controller1) > 0 and len(controller2) > 0:
                fig, axes = plt.subplots(2, 1, figsize=(28, 10))
                df_dropped.plot(x='bufferData', y=controller1, kind='line', ax=axes[0])
                axes[0].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
                axes[0].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
                axes[0].set_title("DBD controller 1 measurements tracking")
                axes[0].legend()
                df_dropped.plot(x='bufferData', y=controller2, kind='line', ax=axes[1])
                axes[1].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
                axes[1].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
                axes[1].set_title("DBD controller 2 measurements tracking")
                axes[1].legend()
                if disp_stack_change:
                    for idx in stack_change:
                        axes[0].axvline(x=df_dropped['bufferData'].iloc[idx], color='yellow', linestyle='--')
                        axes[1].axvline(x=df_dropped['bufferData'].iloc[idx], color='yellow', linestyle='--')
                plt.tight_layout()
                plt.show()
            elif (len(controller1) > 0) ^ (len(controller2) > 0):
                sngle_controller = controller1 if len(controller1) > 0 else controller2
                fig, ax = plt.subplots()
                df_dropped.plot(x='bufferData', y=sngle_controller, kind='line', ax=ax)
                ax.axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
                ax.axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
                ax.legend()
                if disp_stack_change:
                   for idx in stack_change:
                        ax.axvline(x=df_dropped['bufferData'].iloc[idx], color='yellow', linestyle='--')
                plt.show()
            else:
                print("No controller selected, no plot will be shown.")
                print(len(controller1))
                print(len(controller2))

            print(stack_change)
        
        messagebox.showinfo("Processing", "Process started successfully!")
        main()

    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Set up the main window
root = tk.Tk()
root.title("DBD data processing")

# Set window size and center it on the screen
window_width = 600
window_height = 500

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate position to center window
position_top = (screen_height // 2) - (window_height // 2)
position_right = (screen_width // 2) - (window_width // 2)

# Set the geometry of the window
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# File selection
file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=10)

select_button = tk.Button(root, text="Select Input File", command=select_file)
select_button.pack(pady=5)

# Numeric input for blank thickness
thickness_label = tk.Label(root, text="Enter Blank Thickness:")
thickness_label.pack(pady=5)

thickness_entry = tk.Entry(root)
thickness_entry.insert(0, "0.76")  # Set default value
thickness_entry.pack(pady=5)

# True/False selection
true_false_var = tk.BooleanVar(value=True)
true_checkbox = tk.Checkbutton(root, text="Plot cell swap", variable=true_false_var, onvalue=True, offvalue=False)
true_checkbox.pack(pady=5)

# Output file selection
output_file_label = tk.Label(root, text="No output file selected")
output_file_label.pack(pady=10)

output_button = tk.Button(root, text="Select Output File", command=save_output_file)
output_button.pack(pady=5)

# Controller 1 group
controller_1_frame = tk.LabelFrame(root, text="Controller 1", padx=10, pady=10)
controller_1_frame.pack(pady=10, padx=10, fill="both")

controller_1_cb1_var = tk.BooleanVar(value=True)
controller_1_cb1 = tk.Checkbutton(controller_1_frame, text="Sensor 1", variable=controller_1_cb1_var)
controller_1_cb1.pack(side="left", padx=5)

controller_1_cb2_var = tk.BooleanVar(value=True)
controller_1_cb2 = tk.Checkbutton(controller_1_frame, text="Sensor 2", variable=controller_1_cb2_var)
controller_1_cb2.pack(side="left", padx=5)

# Controller 2 group
controller_2_frame = tk.LabelFrame(root, text="Controller 2", padx=10, pady=10)
controller_2_frame.pack(pady=10, padx=10, fill="both")

controller_2_cb1_var = tk.BooleanVar(value=True)
controller_2_cb1 = tk.Checkbutton(controller_2_frame, text="Sensor 3", variable=controller_2_cb1_var)
controller_2_cb1.pack(side="left", padx=5)

controller_2_cb2_var = tk.BooleanVar(value=True)
controller_2_cb2 = tk.Checkbutton(controller_2_frame, text="Sensor 4", variable=controller_2_cb2_var)
controller_2_cb2.pack(side="left", padx=5)

# Start button
start_button = tk.Button(root, text="Start", command=start_process)
start_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()