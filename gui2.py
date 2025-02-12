import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

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
        disp_cell_swap = true_false_var.get()
        file_path = file_label.cget("text").replace("Selected file: ", "")
        output_path = output_file_label.cget("text").replace("Output File: ", "")

        if not file_path:
            raise ValueError("No input file selected.")
        if not output_path:
            raise ValueError("No output file selected.")

        # Get controller checkboxes binary values
        controller_1 = (controller_1_cb1_var.get() << 0) | (controller_1_cb2_var.get() << 1)
        controller_2 = (controller_2_cb1_var.get() << 2) | (controller_2_cb2_var.get() << 3)
        controller_binary = f"0b{controller_1 | controller_2:04b}"

        # Determine the correct path for text2.py (whether running from script or bundled)
        if getattr(sys, 'frozen', False):
            # If the application is frozen (i.e., bundled with cx_Freeze)
            current_dir = os.path.dirname(sys.executable)
            print(f"Running as a bundled EXE. Current directory: {current_dir}")  # Debug
        else:
            # Running as a script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"Running as a script. Current directory: {current_dir}")  # Debug

        text2_path = os.path.join(current_dir, "text2.py")

        # Verify if text2.py exists
        if not os.path.exists(text2_path):
            messagebox.showerror("Error", f"text2.py not found at {text2_path}")
            return

        # Debug to check if text2.py is found
        print(f"text2.py found at: {text2_path}")  # Debug

        # Run text2.py using the system's Python interpreter
        subprocess.run([sys.executable, text2_path, str(thickness), str(disp_cell_swap), file_path, output_path, controller_binary])

    except ValueError as e:
        messagebox.showerror("Input Error", f"Error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Execution Error", f"Error running text2.py: {str(e)}")
        
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
