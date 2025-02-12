import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys

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
        # Get the thickness as float (with default value 0.7)
        thickness = float(thickness_entry.get())
        # Get the value of the checkbox (True or False)
        disp_cell_swap = true_false_var.get()
        # Get the selected input file path
        file_path = file_label.cget("text").replace("Selected file: ", "")
        
        if not file_path:
            raise ValueError("No input file selected.")
        
        # Get the output file path from the label (after save button is clicked)
        output_path = output_file_label.cget("text").replace("Output File: ", "")
        if not output_path:
            raise ValueError("No output file selected.")
        
        # Get the controller checkboxes binary values
        controller_1 = (controller_1_cb1_var.get() << 0) | (controller_1_cb2_var.get() << 1)
        controller_2 = (controller_2_cb1_var.get() << 2) | (controller_2_cb2_var.get() << 3)
        
        # Combine the controller values into one 4-bit binary
        controller_binary = f"0b{controller_1 | controller_2:04b}"
        
        # Preparing the arguments to pass to text2.py
        args = [sys.executable, "text2.py", str(thickness), str(disp_cell_swap), str(file_path), str(output_path), controller_binary]
        
        # Run the external Python script with subprocess
        subprocess.run(args)
        
    except ValueError as e:
        messagebox.showerror("Input Error", f"Error: {str(e)}")

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

# Numeric input for blank thickness with a default value of 0.7
thickness_label = tk.Label(root, text="Enter Blank Thickness:")
thickness_label.pack(pady=5)

thickness_entry = tk.Entry(root)
thickness_entry.insert(0, "0.76")  # Set default value to 0.7
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
