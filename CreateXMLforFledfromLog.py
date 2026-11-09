import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def browse_log_files():
    # Allow the user to select multiple files
    files = filedialog.askopenfilenames(
        title="Select .LOG File(s)",
        filetypes=[("Log files", "*.log *.LOG"), ("All files", "*.*")]
    )
    if files:
        log_listbox.delete(0, tk.END)  # Clear existing entries
        for f in files:
            log_listbox.insert(tk.END, f)  # Add each file on a new line


def browse_data_dir():
    # Folder selection
    folder = filedialog.askdirectory(title="Select Folder with Actual Data")

    if folder:
        data_entry.delete("1.0", tk.END)
        data_entry.insert("1.0", folder)

        # Show the user the contents of the folder they just selected
        try:
            folder_contents = os.listdir(folder)
            if folder_contents:
                preview = ", ".join(folder_contents[:10])  # Preview first 10 files
                if len(folder_contents) > 10:
                    preview += f"... (+{len(folder_contents) - 10} more files)"
                data_preview_label.config(text=f"Contains: {preview}")
            else:
                data_preview_label.config(text="Contains: (Folder is empty)")
        except Exception as e:
            data_preview_label.config(text="Could not read folder contents.")


def process_files():
    # Get all items from the listbox
    raw_log_files = log_listbox.get(0, tk.END)
    data_dir = data_entry.get("1.0", tk.END).strip()

    # Validate inputs
    if not raw_log_files:
        messagebox.showerror("Error", "Please select at least one .LOG file.")
        return
    if not data_dir or not os.path.isdir(data_dir):
        messagebox.showerror("Error", "Please select a valid folder for the actual data.")
        return

    # Filter out any issues and ensure the files actually exist
    log_files = [Path(f) for f in raw_log_files if f and os.path.isfile(f)]

    if not log_files:
        messagebox.showwarning("No Logs Found", "None of the selected log files could be found.")
        return

    processed_count = 0

    for log_file in log_files:
        # Read the file names from the log file, ignoring empty lines
        with open(log_file, 'r') as fd:
            file_names = [line.strip() for line in fd if line.strip()]

        # Generate output filename and save it in the exact same directory as that specific log file
        out_name = log_file.parent / f"out-{log_file.stem}.xml"

        # Write the XML
        with open(out_name, 'w') as g:
            g.write('<!DOCTYPE DMagicFileList>\n')
            g.write('<DMagicFileList>\n')

            for file_name in file_names:
                # Safely combine the selected data path and the file name
                full_path = os.path.join(data_dir, file_name)
                g.write(f'   <FileElement FileName="{full_path}"/>\n')

            g.write('</DMagicFileList>\n')

        processed_count += 1

    # Notify the user when the script finishes and show only the directory path
    if processed_count > 0:
        # Since the files are saved next to the logs, we just grab the folder path of the first log file
        save_directory = log_files[0].parent
        messagebox.showinfo("Complete",
                            f"Successfully processed {processed_count} log file(s)!\n\nSaved in:\n{save_directory}")


# --- Main GUI Setup ---
root = tk.Tk()
root.title("DMagic XML Generator - LCDR M ESTROPIA")
# Maintained height to accommodate scrollbars and wrapped text
root.geometry("700x350")
root.resizable(False, False)

# Configure grid layout to make listbox and entry expand
root.columnconfigure(1, weight=1)

# Row 0: Log Files Label & Button
tk.Label(root, text="Selected .LOG File(s):").grid(row=0, column=0, padx=10, pady=(15, 5), sticky="w")
tk.Button(root, text="Browse Logs...", command=browse_log_files).grid(row=0, column=2, padx=10, pady=(15, 5))

# Row 1: Frame for Listbox and Scrollbars
log_frame = tk.Frame(root)
log_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky="nsew")
log_frame.columnconfigure(0, weight=1)
log_frame.rowconfigure(0, weight=1)

# Add X and Y scrollbars
y_scroll = tk.Scrollbar(log_frame, orient=tk.VERTICAL)
x_scroll = tk.Scrollbar(log_frame, orient=tk.HORIZONTAL)

log_listbox = tk.Listbox(log_frame, height=5, selectmode=tk.EXTENDED,
                         yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

y_scroll.config(command=log_listbox.yview)
x_scroll.config(command=log_listbox.xview)

# Grid the listbox and scrollbars inside the frame
log_listbox.grid(row=0, column=0, sticky="nsew")
y_scroll.grid(row=0, column=1, sticky="ns")
x_scroll.grid(row=1, column=0, sticky="ew")

# Row 2: Data Directory
tk.Label(root, text="Actual Data Folder:").grid(row=2, column=0, padx=10, pady=(15, 5), sticky="e")
# Using tk.Text to allow wrapping long paths
data_entry = tk.Text(root, height=2, wrap=tk.CHAR)
data_entry.grid(row=2, column=1, padx=5, pady=(15, 5), sticky="ew")
tk.Button(root, text="Browse Folder...", command=browse_data_dir).grid(row=2, column=2, padx=10, pady=(15, 5))

# Row 3: Folder Content Preview Label
# Wraplength forces the text to drop to the next line instead of clipping
data_preview_label = tk.Label(root, text="Contains: (No folder selected)", fg="gray", font=("Arial", 8), justify="left",
                              wraplength=500)
data_preview_label.grid(row=3, column=1, columnspan=2, padx=5, pady=(0, 10), sticky="w")

# Row 4: Run Button
tk.Button(root, text="Generate XML", command=process_files, bg="#4CAF50", fg="black", font=("Arial", 10, "bold")).grid(
    row=4, column=0, columnspan=3, pady=15)

# Start the application
root.mainloop()