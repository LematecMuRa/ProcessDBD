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
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
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
        text_file = file_label.cget("text").replace("Selected file: ", "")
        output_file = output_file_label.cget("text").replace("Output File: ", "")

        if not text_file:
            raise ValueError("No input file selected.")
        if not output_file:
            raise ValueError("No output file selected.")

        # Process data or run the background script here
        def keep_unique_values(values, threshold=400):
            if not values:
                return []
            result = [values[0]]
            for num in values[1:]:
                if num - result[-1] > threshold:
                    result.append(num)
            return result

        def remove_values_above_range(values, threshold):
            return [num for num in values if int(num) < threshold]

        def main():
            val_linewidth = float(thickness_fig_entry.get())
            val_thickness = float(thickness_blank_entry.get())
            upper_trshld = round(1.3 * val_thickness, 3)
            lower_trshld = round(0.8 * val_thickness, 3)
            disp_stack_change = display_cell_swap_var.get()
            disp_dbd_single_figure = display_single_figure_var.get()
            disp_dbd_treshold = display_threshold_var.get()
            disp_vis_single_figure = display_single_figure_cor_var.get()

            data_dict = {}
            row_without_dbd_mes = []
            controller1 = []
            controller2 = []
            corrections = []
            cell = 0
            stack_change = []
            
            if controller_1_cb1_var.get(): 
                controller1.append('dbdTrspMeasurement[1]')
            if controller_1_cb2_var.get(): 
                controller1.append('dbdTrspMeasurement[2]')
            if controller_2_cb1_var.get(): 
                controller2.append('dbdTrspMeasurement[3]')
            if controller_2_cb2_var.get(): 
                controller2.append('dbdTrspMeasurement[4]')
            
            if correction_x_var.get():
                corrections.append('X')
            if correction_y_var.get():
                corrections.append('Y')
            if correction_rot_var.get():
                corrections.append('Rotation')
            
            # Regex pattern
            pattern = re.compile(
                r'bufferData\[(?P<buffer_index>\d+)\]\.(?:'
                r'(?P<blankFromCell>blankFromCell) := (?P<blankFromCell_value>\S+)|'  # blankFromCell
                r'dbdGtyMeasurement\[(?P<dbdGty_index>[13])\] := (?P<dbdGty_value>\S+)|'  # dbdGtyMeasurement[1] and [3]
                r'visionCorrectionData\[(?P<vision_index>1)\]\.(?P<vision_type>X|Y|Rotation|Quality) := (?P<vision_value>\S+)|'  # visionCorrectionData[1]
                r'dbdTrspMeasurement\[(?P<trsp_index>\d+)\] := (?P<trsp_value>\S+)|'  # dbdTrspMeasurement[1-4]
                r'dbdTrspTeachData\.dataController(?P<controller>[12])\.(?P<controller_type>charactVal1Blank|charactVal2Blank|teachOk|settlTime)\[?(?P<charact_index>\d+)?\]? := (?P<controller_value>\S+)'
                r')'
            )

            with open(text_file, "r") as file:
                for line in file:
                    match = pattern.search(line)
                    if match:
                        buffer_index = match.group("buffer_index")  # Always available

                        # Initialize the dictionary for this buffer_index if it doesn't exist
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
                                'C1_charactVal1Blank[1]': None,
                                'C1_charactVal1Blank[2]': None,
                                'C1_charactVal1Blank[3]': None,
                                'C1_charactVal1Blank[4]': None,
                                'C1_charactVal2Blank[1]': None,
                                'C1_charactVal2Blank[2]': None,
                                'C1_charactVal2Blank[3]': None,
                                'C1_charactVal2Blank[4]': None,
                                'C1_teachOk': None,
                                'C1_settlTime': None,
                                'C2_charactVal1Blank[1]': None,
                                'C2_charactVal1Blank[2]': None,
                                'C2_charactVal1Blank[3]': None,
                                'C2_charactVal1Blank[4]': None,
                                'C2_charactVal2Blank[1]': None,
                                'C2_charactVal2Blank[2]': None,
                                'C2_charactVal2Blank[3]': None,
                                'C2_charactVal2Blank[4]': None,
                                'C2_teachOk': None,
                                'C2_settlTime': None,
                            }

                        # Extract key-value pairs
                        for group_name in match.groupdict():
                            if match.group(group_name) and group_name not in ["buffer_index", "controller"]:
                                raw_value = match.group(group_name).rstrip(';')

                                # Convert to float if it doesn't start with "16#"
                                if not raw_value.startswith("16#"):
                                    try:
                                        value = float(raw_value)
                                    except ValueError:
                                        value = raw_value  # Keep as string if conversion fails
                                else:
                                    value = raw_value  # Keep as string if it's in hex format

                                # Update the dictionary based on the matched group
                                if group_name == "blankFromCell_value":
                                    data_dict[buffer_index]['blankFromCell'] = value
                                elif group_name == "dbdGty_value":
                                    dbdGty_index = match.group("dbdGty_index")
                                    data_dict[buffer_index][f'dbdGtyMeasurement[{dbdGty_index}]'] = value
                                elif group_name == "vision_value":
                                    vision_type = match.group("vision_type")
                                    data_dict[buffer_index][vision_type] = value
                                elif group_name == "trsp_value":
                                    trsp_index = match.group("trsp_index")
                                    data_dict[buffer_index][f'dbdTrspMeasurement[{trsp_index}]'] = value
                                elif group_name == "controller_value":
                                    controller = match.group("controller")
                                    controller_type = match.group("controller_type")
                                    charact_index = match.group("charact_index")
                                    if charact_index:
                                        key = f'C{controller}_{controller_type}[{charact_index}]'
                                    else:
                                        key = f'C{controller}_{controller_type}'
                                    data_dict[buffer_index][key] = value
            
            df_raw = pd.DataFrame.from_dict(data_dict, orient=index)
            df_raw.to_excel(output_file, index=False)

            filtered_dict = {k: v for k, v in data_dict.items() if v['blankFromCell'] is None or int(v['blankFromCell']) != 0}
            df_new = pd.DataFrame.from_dict(filtered_dict, orient='index')

            for index, row in df_new.iterrows():
                if (row['dbdTrspMeasurement[1]'] == 0 and row['dbdTrspMeasurement[2]'] == 0 
                    and row['dbdTrspMeasurement[3]'] == 0 and row['dbdTrspMeasurement[4]'] == 0
                    and row['X'] == 0 and row['Y'] == 0):
                    row_without_dbd_mes.append(index)

            df_dropped = df_new.drop(row_without_dbd_mes)
            #df_dropped.to_excel(output_file, index=False)

            for index, row in df_dropped.iterrows():
                if (int((row['blankFromCell'])) != cell):
                    if cell != 0:
                        stack_change.append(index)
                    cell = int(row['blankFromCell'])

            row_without_dbd_mes = keep_unique_values(row_without_dbd_mes)
            row_without_dbd_mes = remove_values_above_range(row_without_dbd_mes, len(df_dropped))
            stack_change = remove_values_above_range(stack_change, len(df_dropped))

            dbd_single_graph = len(controller1) > 0 or len(controller2) > 0
            dbd_dual_graph = len(controller1) > 0 and len(controller2) > 0 and not disp_dbd_single_figure
            
            if dbd_single_graph and not dbd_dual_graph:
                single_figure = controller1 + controller2
                if (len(single_figure) > 0):
                    fig, ax = plt.subplots()
                    df_dropped.plot(x='bufferData', y=single_figure, kind='line', ax=ax, linewidth = val_linewidth)
                    if disp_dbd_treshold:
                        ax.axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
                        ax.axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
                    ax.set_title("DBD measurements tracking")
                    ax.legend()
                    if disp_stack_change:
                        for idx in stack_change:
                                ax.axvline(x=idx, color='yellow', linestyle='--')
                    plt.show()

            if dbd_dual_graph:
                multiple_figure = [controller1, controller2]
                nmbr_figures = len(multiple_figure)
                fig, axes = plt.subplots(nmbr_figures, 1)
                for i in range (nmbr_figures):
                    df_dropped.plot(x='bufferData', y=multiple_figure[i], kind='line', ax=axes[i])
                    if disp_dbd_treshold:
                        axes[i].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
                        axes[i].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
                    axes[i].set_title(f"DBD controller {i+1} measurements tracking")
                    axes[i].legend()
                    if disp_stack_change:
                        for idx in stack_change:
                            axes[i].axvline(x=idx, color='yellow', linestyle='--')
                    plt.tight_layout()
                plt.show()
            
            vis_single_graph = len(corrections) > 0 
            vis_mult_graph = len(corrections) > 1 and not disp_vis_single_figure

            if vis_single_graph and not vis_mult_graph:
                fig, ax = plt.subplots()
                df_dropped.plot(x='bufferData', y=corrections, kind='line', ax=ax)
                ax.legend()
                if disp_stack_change:
                    for idx in stack_change:
                            ax.axvline(x=idx, color='yellow', linestyle='--')
                plt.show()

            if vis_mult_graph:
                nmbr_figures = len(corrections)
                fig, axes = plt.subplots(nmbr_figures, 1)
                for i in range (nmbr_figures):
                    df_dropped.plot(x='bufferData', y=corrections[i], kind='line', ax=axes[i])
                    axes[i].set_xlabel("")
                    axes[i].set_title(corrections[i])
                    axes[i].legend()
                    if disp_stack_change:
                        for idx in stack_change:
                            axes[i].axvline(x=idx, color='yellow', linestyle='--')
                    plt.tight_layout()
                plt.show()

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
window_width = 800
window_height = 600

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position_top = (screen_height // 2) - (window_height // 2)
position_right = (screen_width // 2) - (window_width // 2)

root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Configure grid layout for root window
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# File selection
file_label = tk.Label(root, text="No file selected")
file_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

select_button = tk.Button(root, text="Select Input File", command=select_file)
select_button.grid(row=1, column=0, columnspan=3, pady=5)

# Output file selection
output_file_label = tk.Label(root, text="Choose a folder to save your Excel file")
output_file_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

output_button = tk.Button(root, text="Choose Save Location", command=save_output_file)
output_button.grid(row=3, column=0, columnspan=3, pady=5)

# Frame for Numeric Inputs
input_frame = tk.Frame(root)
input_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
input_frame.columnconfigure((0, 1, 2), weight=1)

# Numeric input for Blank Thickness
thickness_blank_label = tk.Label(input_frame, text="Blank Thickness:")
thickness_blank_label.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

thickness_blank_entry = tk.Entry(input_frame, justify="center")
thickness_blank_entry.insert(0, "0.76")
thickness_blank_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Numeric input for Figure Line Thickness
thickness_fig_label = tk.Label(input_frame, text="Figure Line Thickness:")
thickness_fig_label.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

thickness_fig_entry = tk.Entry(input_frame, justify="center")
thickness_fig_entry.insert(0, "0.3")
thickness_fig_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Checkbox for Display Cell Swap
display_cell_swap_var = tk.BooleanVar(value=True)
display_cell_swap_cb = tk.Checkbutton(input_frame, text="Display Cell Swap", variable=display_cell_swap_var)
display_cell_swap_cb.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# Main Frame for Measurement & Correction Options
main_frame = tk.Frame(root)
main_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")
main_frame.columnconfigure((0, 1), weight=1)

# DBD Measurements Frame
dbd_frame = tk.LabelFrame(main_frame, text="DBD Measurements", padx=10, pady=10)
dbd_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# Configure dbd_frame to have two columns
dbd_frame.columnconfigure(0, weight=1)
dbd_frame.columnconfigure(1, weight=1)

# Controller 1 group
controller_1_frame = tk.LabelFrame(dbd_frame, text="Controller 1", padx=10, pady=10)
controller_1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

controller_1_cb1_var = tk.BooleanVar()
controller_1_cb1 = tk.Checkbutton(controller_1_frame, text="Sensor 1", variable=controller_1_cb1_var)
controller_1_cb1.pack(side="left", padx=5)

controller_1_cb2_var = tk.BooleanVar(value=True)
controller_1_cb2 = tk.Checkbutton(controller_1_frame, text="Sensor 2", variable=controller_1_cb2_var)
controller_1_cb2.pack(side="left", padx=5)

# Controller 2 group
controller_2_frame = tk.LabelFrame(dbd_frame, text="Controller 2", padx=10, pady=10)
controller_2_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

controller_2_cb1_var = tk.BooleanVar(value=True)
controller_2_cb1 = tk.Checkbutton(controller_2_frame, text="Sensor 3", variable=controller_2_cb1_var)
controller_2_cb1.pack(side="left", padx=5)

controller_2_cb2_var = tk.BooleanVar()
controller_2_cb2 = tk.Checkbutton(controller_2_frame, text="Sensor 4", variable=controller_2_cb2_var)
controller_2_cb2.pack(side="left", padx=5)

# Checkboxes aligned on the right
checkbox_frame = tk.Frame(dbd_frame)
checkbox_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")

# Display Threshold Checkbox
display_threshold_var = tk.BooleanVar(value=True)
display_threshold_cb = tk.Checkbutton(checkbox_frame, text="Display Threshold", variable=display_threshold_var)
display_threshold_cb.pack(anchor="w", pady=5)

# Display in Single Figure Checkbox
display_single_figure_var = tk.BooleanVar(value=True)
display_single_figure_cb = tk.Checkbutton(checkbox_frame, text="Single Figure DBD", variable=display_single_figure_var)
display_single_figure_cb.pack(anchor="w", pady=5)

# Display Corrections Frame
correction_frame = tk.LabelFrame(main_frame, text="Vision App Corrections", padx=10, pady=10)
correction_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

# X Correction
correction_x_var = tk.BooleanVar(value=True)
correction_x = tk.Checkbutton(correction_frame, text="X Correction", variable=correction_x_var)
correction_x.grid(row=0, column=0, padx=5, sticky="w")

# Y Correction
correction_y_var = tk.BooleanVar(value=True)
correction_y = tk.Checkbutton(correction_frame, text="Y Correction", variable=correction_y_var)
correction_y.grid(row=1, column=0, padx=5, sticky="w")

# Rotation Correction
correction_rot_var = tk.BooleanVar(value=True)
correction_rot = tk.Checkbutton(correction_frame, text="Rotation", variable=correction_rot_var)
correction_rot.grid(row=2, column=0, padx=5, sticky="w")

# Add space before the next checkbox
correction_frame.grid_rowconfigure(3, minsize=15)

display_single_figure_cor_var = tk.BooleanVar()
display_single_figure_cor = tk.Checkbutton(correction_frame, text="Single Figure Correction", variable=display_single_figure_cor_var)
display_single_figure_cor.grid(row=4, column=0, padx=5, sticky="w")

# Start Button
start_button = tk.Button(root, text="Start", font=("Arial", 14, "bold"), height=2, width=10, bg="#A9A9A9", command=start_process)
start_button.grid(row=8, column=0, columnspan=3, pady=20, sticky="ew")

# Adjust row/column weights to allow expansion
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure((0, 1, 2), weight=1)

# Start the Tkinter event loop
root.mainloop()