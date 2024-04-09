import os
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font

import pandas as pd
from pandastable import Table, RowHeader, TableModel

# Changelog Swimming Tracks Processing
# v1.0:     24.04.2021
#           Script written by Dennis Vettkötter
# v1.1:     28.04.2021
#           - Added more information displayed in console window (used as Log).
#               - Printing lists of combined and deleted tracks
#           - Threshold value of minimum time worms to be tracked set to 50%
# v1.2:     29.04.2021
#           - Create additional file when opening track files: filename_log.txt
#               - Saves lists of combined and deleted tracks for future reference
# v1.3:     02.06.2021
#           - Added support to save files if no changes have been made.
# v1.4:     17.11.2021
#           - Added undo button to undo an action (combine or delete) ONCE
#           - Added mean (BBPM), SEM, and n number to output excel file of
#             >50% tracked swimming cycles.
#



# Tooltip code
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify="left",
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


# Script funcions

# Get path to *_tracks.txt that should be processed
def get_track_path():
    # Set path variables for track files, name of trackfile and parent directory.
    trackfile_selected = filedialog.askopenfile(title="Select *_tracks.txt",
                                                filetypes=[("Track files", "*_tracks.txt")])
    trackfile_path.set(trackfile_selected.name)
    trackfile_name.set(os.path.basename(trackfile_path.get()))
    trackfile_dir.set(os.path.dirname(trackfile_path.get()))

    # Create directory for log files and processed tracks
    dir_root = trackfile_dir.get()
    Path(dir_root + "/tracks_processed/").mkdir(parents=True, exist_ok=True)

    # Open file in pandastable frame on GUI. Check if temporary file already exists.
    if os.path.exists(trackfile_path.get() + '.temp.xlsx'):
        df = pd.read_excel(trackfile_path.get() + '.temp.xlsx', index_col='Track')
        pt = Table(f, dataframe=df, editable=False)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        print("Processing " + trackfile_name.get() + ". Loaded temporary file.")
    else:
        df = pd.read_csv(trackfile_path.get(), delimiter="\t", index_col='Track ')
        pt = Table(f, dataframe=df, editable=False)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        print("Processing " + trackfile_name.get() + ". Temporary file will be created!")


# Function to combine tracks specified by user input
def combine_tracks():
    tracks_path = trackfile_path.get()
    temp_file_path = tracks_path + '.temp.xlsx'
    temp_undo_path = tracks_path + '.temp_undo.xlsx'
    tracks_entry = combine_tracks_entry.get()
    track_list = tracks_entry.split(",")
    track_list = list(map(int, track_list))

    # Log file variables
    dir_root = trackfile_dir.get()
    processed_root = dir_root + "/tracks_processed/"
    filename = trackfile_name.get().strip('_tracks.txt')
    log_file_name = filename + "_log.txt"
    log_root = os.path.join(processed_root, log_file_name)

    # Check if temporary files already exists, if not use .txt from trackfile_path
    if os.path.exists(temp_file_path):
        df = pd.read_excel(temp_file_path, index_col='Track')
        df.to_excel(temp_undo_path)
        for i in range(len(track_list)):
            df = df.rename(index={track_list[i]: track_list[0]})
        df = df.groupby('Track').sum()
        df.to_excel(temp_file_path)
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tTracks " + ', '.join(map(str, track_list)) + " combined to track " + str(track_list[0]) + "!")
        log_file.write("Tracks " + ', '.join(map(str, track_list)) + " combined to track " + str(track_list[0]) + "!\n")
        entry_combine_tracks.set("")
    else:
        df = pd.read_csv(tracks_path, delimiter="\t")
        df = df.rename(columns={"Track ": "Track"})
        df = df.set_index('Track')
        df.to_excel(tracks_path + '.temp_undo.xlsx')
        for i in range(len(track_list)):
            df = df.rename(index={track_list[i]: track_list[0]})
        df = df.groupby('Track').sum()
        df.to_excel(tracks_path + '.temp.xlsx')
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tTracks " + ', '.join(map(str, track_list)) + " combined to track " + str(track_list[0]) + "!")
        log_file.write("Tracks " + ', '.join(map(str, track_list)) + " combined to track " + str(track_list[0]) + "!\n")
        entry_combine_tracks.set("")
    return


# Function to delete tracks by user input
def delete_tracks():
    tracks_path = trackfile_path.get()
    temp_file_path = tracks_path + '.temp.xlsx'
    temp_undo_path = tracks_path + '.temp_undo.xlsx'
    delete_entry = delete_tracks_entry.get()
    delete_list = delete_entry.split(",")
    delete_list = list(map(int, delete_list))

    # Log file variables
    dir_root = trackfile_dir.get()
    processed_root = dir_root + "/tracks_processed/"
    filename = trackfile_name.get().strip('_tracks.txt')
    log_file_name = filename + "_log.txt"
    log_root = os.path.join(processed_root, log_file_name)

    # Check if temporary files already exists, if not use .txt from trackfile_path
    if os.path.exists(temp_file_path):
        df = pd.read_excel(temp_file_path, index_col='Track')
        df.to_excel(temp_undo_path)
        df = df.drop(delete_list)
        df.to_excel(temp_file_path)
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tTrack(s) " + ', '.join(map(str, delete_list)) + " deleted!")
        log_file.write("Track(s) " + ', '.join(map(str, delete_list)) + " deleted!\n")
        entry_delete_tracks.set("")
    else:
        df = pd.read_csv(tracks_path, delimiter="\t")
        df = df.rename(columns={"Track ": "Track"})
        df = df.set_index('Track')
        df.to_excel(tracks_path + '.temp_undo.xlsx')
        df = df.drop(delete_list)
        df.to_excel(temp_file_path)
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tTrack(s) " + ', '.join(map(str, delete_list)) + " deleted!")
        log_file.write("Track(s) " + ', '.join(map(str, delete_list)) + " deleted!\n")
        entry_delete_tracks.set("")
    return

def undo():
    tracks_path = trackfile_path.get()
    temp_file_path = tracks_path + '.temp.xlsx'
    temp_undo_path = tracks_path + '.temp_undo.xlsx'


    # Log file variables
    dir_root = trackfile_dir.get()
    processed_root = dir_root + "/tracks_processed/"
    filename = trackfile_name.get().strip('_tracks.txt')
    log_file_name = filename + "_log.txt"
    log_root = os.path.join(processed_root, log_file_name)

    # Check if temporary files already exists, if not use .txt from trackfile_path
    if os.path.exists(temp_file_path):
        df = pd.read_excel(temp_undo_path, index_col='Track')
        df.to_excel(temp_file_path)
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tLast step undone!")
        log_file.write("Last step undone!\n")
    else:
        df = pd.read_excel(tracks_path, delimiter="\t")
        df = df.rename(columns={"Track ": "Track"})
        df = df.set_index('Track')
        df.to_excel(temp_file_path)
        pt = Table(f, dataframe=df)
        pt.show()
        pt.redraw()
        RowHeader(table=pt).toggleIndex()
        pt.redraw()
        log_file = open(log_root, "a")
        print("\tLast step undone!")
        log_file.write("Last step undone!\n")
    return

# Function to save completely processed track file and reset GUI window,
# to select next track file to be processed.
def save_file():
    # Log file variables
    dir_root = trackfile_dir.get()
    processed_root = dir_root + "/tracks_processed/"
    filename_base = trackfile_name.get().strip('_tracks.txt')
    log_file_name = filename_base + "_log.txt"
    log_root = os.path.join(processed_root, log_file_name)

    # Get path values
    tracks_path = trackfile_path.get()
    filename_tracks = trackfile_name.get().strip('.txt')
    temp_file_path = tracks_path + '.temp.xlsx'

    # Create dataframe for body bends per second and per minute
    # Check if temporary files already exists, if not use .txt from trackfile_path
    if os.path.exists(temp_file_path):
        df = pd.read_excel(temp_file_path, index_col='Track')
        selected_columns = df[["#Frames", "time(s)", "Bends"]]
        df2 = selected_columns.copy()
        df2['BBPS'] = df['Bends'].div(df['time(s)'], axis=0)
        df2['BBPM'] = df2['BBPS']*60
        df2['-'] = ''
        df2['mean (BBPM)'] = df2['BBPM'].mean()
        df2['mean (BBPM)'] = df2['mean (BBPM)'].drop_duplicates()
        df2['SEM'] = df2['BBPM'].sem()
        df2['SEM'] = df2['SEM'].drop_duplicates()
        df2['n'] = len(df2['BBPM'])
        df2['n'] = df2['n'].drop_duplicates()
    else:
        df = pd.read_csv(tracks_path, delimiter="\t")
        df = df.rename(columns={"Track ": "Track"})
        df = df.set_index('Track')
        selected_columns = df[["#Frames", "time(s)", "Bends"]]
        df2 = selected_columns.copy()
        df2['BBPS'] = df['Bends'].div(df['time(s)'], axis=0)
        df2['BBPM'] = df2['BBPS'] * 60
        df2['-'] = ''
        df2['mean (BBPM)'] = df2['BBPM'].mean()
        df2['mean (BBPM)'] = df2['mean (BBPM)'].drop_duplicates()
        df2['SEM'] = df2['BBPM'].sem()
        df2['SEM'] = df2['SEM'].drop_duplicates()
        df2['n'] = len(df2['BBPM'])
        df2['n'] = df2['n'].drop_duplicates()

    # Get maximum time tracked and only keep
    # tracks that have been tracked 90% of the maximum time.
    column = df['time(s)']
    max_value = column.max()
    threshold_value = max_value * 0.5
    df3 = df2.copy()
    df3.drop(df3.loc[df3['time(s)'] <= threshold_value].index, inplace=True)
    df3['-'] = ''
    df3['mean (BBPM)'] = df3['BBPM'].mean()
    df3['mean (BBPM)'] = df3['mean (BBPM)'].drop_duplicates()
    df3['SEM'] = df3['BBPM'].sem()
    df3['SEM'] = df3['SEM'].drop_duplicates()
    df3['n'] = len(df3['BBPM'])
    df3['n'] = df3['n'].drop_duplicates()

    # Saving processed track file to new directory "tracks_processed"
    with pd.ExcelWriter(processed_root + filename_tracks + "_processed.xlsx") as writer:
        df3.to_excel(writer, sheet_name='>50%_tracked_swimming_cycles')
        df2.to_excel(writer, sheet_name='all_swimming_cycles')
        df.to_excel(writer, sheet_name='all_data')

    print("Saving processed tracks as " + filename_tracks + "_processed.xlsx ... Done!")

    # Resetting variables in GUI.
    entry_combine_tracks.set("")
    entry_delete_tracks.set("")
    trackfile_path.set("")
    trackfile_name.set("")
    trackfile_dir.set("")
    df_empty = pd.DataFrame()
    pt = Table(f, dataframe=df_empty)
    pt.show()
    if os.path.exists(log_root):
        log_file = open(log_root, "r")
        log_file.close()
    else:
        log_file = open(log_root, "a")
        log_file.write("---\nNo changes to original track file made.\n"
                       "Saved without changes.\n---\n")
        log_file.close()
    return

def save_proceed():
    save_file()
    get_track_path()

def save_close():
    save_file()
    gui.destroy()


# GUI setup

# GUI window
gui = tk.Tk()
gui.geometry('600x490')
gui.title("Swimming Tracks Processing")
gui.iconbitmap('swim_tracks_ico.ico')

# GUI font styles
myFont = font.Font(family='Cambria', size=10, weight="bold")
fileFont = font.Font(size=9, weight="bold")


# trackfile_path GUI (Button, Entry)
trackfile_path = tk.StringVar()
trackfile_name = tk.StringVar()
trackfile_dir = tk.StringVar()

trackfile_entry = tk.Entry(gui, textvariable=trackfile_name, state='readonly',
                           font=fileFont)
trackfile_entry.grid(row=1, column=1, ipadx=90, padx=2, pady=10)
btn_select_trackfile = ttk.Button(gui, text="Select track file",
                                  command=get_track_path)
btn_select_trackfile.grid(row=1, column=0)


# GUI Seperator1
ttk.Separator(gui, orient="horizontal").grid(row=2, column=0, columnspan=3,
                                             padx=15, sticky='ew')

# Display tracks using pandastable
f = tk.Frame(gui)
f.grid(row=3, column=0, columnspan=3)
df_empty = pd.DataFrame()
pt = Table(f, dataframe=df_empty)
pt.show()
print("Starting Swimming Tracks Processing v1.3 by Dennis Vettkötter")
print("Use 'STProcessing' ImageJ Plugin to open videos.")
print("Log:")

# GUI Seperator2
ttk.Separator(gui, orient="horizontal").grid(row=4, column=0, columnspan=3,
                                             padx=15, sticky='ew')

# track combine GUI
entry_combine_tracks = tk.StringVar()

combine_tracks_label = tk.Label(gui, text="Combine tracks")
combine_tracks_label.grid(row=5, column=0, sticky="ew")
combine_tracks_entry = tk.Entry(gui, textvariable=entry_combine_tracks)
combine_tracks_entry.grid(row=5, column=1, ipadx=100, padx=2, pady=10)
btn_combine_tracks = ttk.Button(gui, text="Combine", command=combine_tracks)
btn_combine_tracks.grid(row=5, column=2)

# track combineing info button
combine_tracks_info = "Specify track numbers to be combined separated by commas.\n" \
                    "Do not use spaces after comma!\n" \
                    "e.g. '2,7,12,23,50'\n" \
                    "Repeat for next track until finished."
combine_tracks_infobutton = tk.Button(gui, text='i', font=myFont,
                                     bg='white', fg='blue', bd=0)
CreateToolTip(combine_tracks_infobutton, text=combine_tracks_info)
combine_tracks_infobutton.grid(row=5, column=3, padx=5)


# track deleting GUI
entry_delete_tracks = tk.StringVar()

delete_tracks_label = tk.Label(gui, text="Delete tracks")
delete_tracks_label.grid(row=6, column=0, sticky="ew")
delete_tracks_entry = tk.Entry(gui, textvariable=entry_delete_tracks)
delete_tracks_entry.grid(row=6, column=1, ipadx=100, padx=2, pady=20)
btn_delete_tracks = ttk.Button(gui, text="Delete", command=delete_tracks)
btn_delete_tracks.grid(row=6, column=2)

# track deleting info button
delete_tracks_info = "Specify track numbers to be deleted separated by commas.\n" \
                     "Do not use spaces after comma!\n" \
                     "e.g. '1,5,9,10,27'"
delete_tracks_infobutton = tk.Button(gui, text='i', font=myFont,
                                     bg='white', fg='blue', bd=0)
CreateToolTip(delete_tracks_infobutton, text=delete_tracks_info)
delete_tracks_infobutton.grid(row=6, column=3, padx=5)

# undo button
return_arrow = tk.PhotoImage(file = r"arrow_mini.png")
return_image = return_arrow.subsample(4, 4)
btn_undo = tk.Button(gui, text=' Undo', image=return_image,
                     compound='left', relief='groove', command=undo)
btn_undo.grid(row=7, column=0)

# Save file and select next file button
btn_next = tk.Button(gui, text="Save & proceed",
                     relief='groove', activebackground='#99ccff',
                     command=save_proceed)
btn_next.grid(row=7, column=1, padx=80, sticky="w")

# Save file and close program button
btn_close = tk.Button(gui, text="Save & close",
                      bg='#ff6666', relief='groove',
                      command=save_close)
btn_close.grid(row=7, column=1, padx=80, sticky="e")

# GUI window loop
gui.mainloop()