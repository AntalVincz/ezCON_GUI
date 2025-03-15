#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import subprocess
import os
import sys
import threading
import time
import shutil
from datetime import datetime
import re
from PIL import Image, ImageTk
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy import units as u

# ---------------- Global Settings ----------------
WORKING_DIR = r"E:\eZCON_GUI_develop"
last_output_folder = None  # Will hold the output folder after a run
DEBUG_MODE = False  # Set to True for detailed debug

# Keys to show in the main “Default Parameters” frame.
DISPLAY_KEYS = [
    ("-ezRAObsLat", "Observer Latitude"),
    ("-ezRAObsLon", "Observer Longitude"),
    ("-ezRAObsAmsl", "Observer Altitude (m)"),
    ("-ezRAObsName", "Observer Name"),
    ("-ezColAzimuth", "Antenna Azimuth"),
    ("-ezColElevation", "Antenna Elevation"),
    ("-ezColCenterFreqAnt", "Receiver CenterFreq Ant"),
    ("-ezColCenterFreqRef", "Receiver CenterFreq Ref"),
    ("-ezColBandWidth", "BandWidth")
]

# Advanced options split into two groups.
ADVANCED_OPTIONS_PROC = [
    ("-ezConRawSamplesUseL", "RawSamplesUseL (first last)"),
    ("-ezConRawFreqBinHide", "RawFreqBinHide"),
    ("-ezConRefMode", "RefMode"),
    ("-ezConAntSamplesUseL", "AntSamplesUseL (first last)"),
    ("-ezConAntPluck", "AntPluck"),
    ("-ezConAntAvgPluckQtyL", "AntAvgPluckQtyL (low high)"),
    ("-ezConAntAvgPluckFracL", "AntAvgPluckFracL (low high)"),
    ("-ezConAntFreqBinSmooth", "AntFreqBinSmooth")
]

ADVANCED_OPTIONS_DISP = [
    ("-ezConRefAvgPluckQtyL", "RefAvgPluckQtyL (low high)"),
    ("-ezConRefAvgPluckFracL", "RefAvgPluckFracL (low high)"),
    ("-ezConAntBaselineFreqBinsFracL", "AntBaselineFreqBinsFracL (4 numbers)"),
    ("-ezConAntRABaselineFreqBinsFracL", "AntRABaselineFreqBinsFracL (4 numbers)"),
    ("-ezConAntXInput", "AntXInput"),
    ("-ezConAntXTFreqBinsFracL", "AntXTFreqBinsFracL (start stop)"),
    ("-ezConUseVlsr", "UseVlsr"),
    ("-ezConAntXTVTFreqBinsFracL", "AntXTVTFreqBinsFracL (start stop)"),
    ("-ezConAntXTVTMaxPluckQtyL", "AntXTVTMaxPluckQtyL (low high)"),
    ("-ezConAntXTVTMaxPluckValL", "AntXTVTMaxPluckValL (low high)"),
    ("-ezConAntXTVTAvgPluckQtyL", "AntXTVTAvgPluckQtyL (low high)"),
    ("-ezConAntXTVTAvgPluckValL", "AntXTVTAvgPluckValL (low high)"),
    ("-ezConAntXTVTPluck", "AntXTVTPluck"),
    ("-ezConPlotRangeL", "PlotRangeL (start end)"),
    ("-ezConRawDispIndex", "RawDispIndex"),
    ("-ezConDispGrid", "DispGrid"),
    ("-ezConDispFreqBin", "DispFreqBin (1 or 2)"),
    ("-ezConHeatVMinMaxL", "HeatVMinMaxL (min max)"),
    ("-ezConAstroMath", "AstroMath (0,1,2)"),
    ("-ezConVelGLonEdgeFrac", "VelGLonEdgeFrac"),
    ("-ezConGalCrossingGLatCenter", "GalCrossingGLatCenter"),
    ("-ezConGalCrossingGLatCenterL", "GalCrossingGLatCenterL (start stop num)"),
    ("-ezConGalCrossingGLatNear", "GalCrossingGLatNear"),
    ("-ezConGalCrossingGLonCenter", "GalCrossingGLonCenter"),
    ("-ezConGalCrossingGLonCenterL", "GalCrossingGLonCenterL (start stop num)"),
    ("-ezConGalCrossingGLonNear", "GalCrossingGLonNear"),
    ("-ezCon399SignalSampleByFreqBinL", "399SignalSampleByFreqBinL (val1 val2)")
]

# Split the Display Options into two separate lists for two tabs.
half = len(ADVANCED_OPTIONS_DISP) // 2
ADVANCED_OPTIONS_DISP1 = ADVANCED_OPTIONS_DISP[:half]
ADVANCED_OPTIONS_DISP2 = ADVANCED_OPTIONS_DISP[half:]

# Advanced options help texts.
advanced_options_help = {
    "-ezConRawSamplesUseL": "Example: 0 100 (first and last raw sample numbers)",
    "-ezConRawFreqBinHide": "Example: 129 (hide raw freq bin 129 by copying from bin 128)",
    "-ezConRefMode": "Example: 1 (1: REF = 1.0, 0: first sample, negative: previous sample)",
    "-ezConAntSamplesUseL": "Example: 25 102 (first and last Ant sample numbers)",
    "-ezConAntPluck": "Example: 29 (Ant sample to pluck)",
    "-ezConAntAvgPluckQtyL": "Example: 3 5 (pluck lowest 3 and highest 5)",
    "-ezConAntAvgPluckFracL": "Example: .02 .03 (pluck lowest 2% and highest 3%)",
    "-ezConAntFreqBinSmooth": "Example: 1.1 (RFI spur limiter multiplier)",
    "-ezConRefAvgPluckQtyL": "Example: 3 5",
    "-ezConRefAvgPluckFracL": "Example: .02 .03",
    "-ezConAntBaselineFreqBinsFracL": "Example: 0 0.2344 0.7657 1",
    "-ezConAntRABaselineFreqBinsFracL": "Example: 0 0.2344 0.7657 1",
    "-ezConAntXInput": "Example: 6 (-1 for Auto, 0/2/4/5/6 for specific choices)",
    "-ezConAntXTFreqBinsFracL": "Example: 0.2344 0.7657",
    "-ezConUseVlsr": "Example: 1 (use VLSr)",
    "-ezConAntXTVTFreqBinsFracL": "Example: 0.4 0.6",
    "-ezConAntXTVTMaxPluckQtyL": "Example: 3 5",
    "-ezConAntXTVTMaxPluckValL": "Example: .01 .03",
    "-ezConAntXTVTAvgPluckQtyL": "Example: 3 5",
    "-ezConAntXTVTAvgPluckValL": "Example: .01 .03",
    "-ezConAntXTVTPluck": "Example: 33",
    "-ezConPlotRangeL": "Example: 0 300",
    "-ezConRawDispIndex": "Example: 1",
    "-ezConDispGrid": "Example: 1",
    "-ezConDispFreqBin": "Example: 1 (or 2)",
    "-ezConHeatVMinMaxL": "Example: 1.0 1.4",
    "-ezConAstroMath": "Example: 1 (0, 1, or 2)",
    "-ezConVelGLonEdgeFrac": "Example: 0.5",
    "-ezConGalCrossingGLatCenter": "Example: 2.4",
    "-ezConGalCrossingGLatCenterL": "Example: -5.2 6.3 11",
    "-ezConGalCrossingGLatNear": "Example: 2.3",
    "-ezConGalCrossingGLonCenter": "Example: 72.4",
    "-ezConGalCrossingGLonCenterL": "Example: 69.6 82.4 13",
    "-ezConGalCrossingGLonNear": "Example: 2.7",
    "-ezCon399SignalSampleByFreqBinL": "Example: 18 1423"
}

# Global dictionaries for advanced options values and active states.
advanced_options = {}
advanced_options_active = {}

# ---------------- Help Instructions (ezCon Help) ----------------
ezcon_help_text = """\
         For help, run
            ezCon.py -help

=================================================
 Local time = Sat Mar 15 10:13:02 2025
 programRevision = ezCon240615b.py

 This Python command = ezCon.py  -h

   ezConArgumentsFile(/home/ezRA/ezDefaults.txt) ===============
      success opening /home/ezRA/ezDefaults.txt

   ezConArgumentsFile(ezDefaults.txt) ===============
      success opening ezDefaults.txt

   ezConArgumentsCommandLine ===============

##############################################################################################

USAGE:
  Windows:   py      ezCon.py [optional arguments] radioDataFileDirectories
  Linux:     python3 ezCon.py [optional arguments] radioDataFileDirectories

  Easy Radio Astronomy (ezRA) ezCon data Condenser program
  to read ezCol format .txt radio data file(s),
  analyse them, optionally creating many .png plot files,
  and maybe write one Gal.npz Galaxy crossing velocity data file.

  "radioDataFileDirectories" may be one or more .txt radio data files:
         py ezCon.py bigDish220320_05.txt
         py ezCon.py bigDish220320_05.txt bigDish220321_00.txt
         py ezCon.py bigDish22032*.txt
  "radioDataFileDirectories" may be one or more directories:
         py ezCon.py bigDish2203
         py ezCon.py bigDish2203 bigDish2204
         py ezCon.py bigDish22*
  "radioDataFileDirectories" may be a mix of .txt radio data files and directories

  Arguments and "radioDataFileDirectories" may be in any mixed order.

  Arguments are read first from inside the ezCon program,
  then in order from the ezDefaults.txt in the ezCon.py's directory,
  then in order from the ezDefaults.txt in current directory,
  then in order from the command line. For duplicates, last read wins.

EXAMPLES:

  py ezCon.py -help                  (print this help)
  py ezCon.py -h                     (print this help)

    -ezRAObsName   Lebanon Kansas    (Observatory Name)
    -ezRAObsLat    39.8282           (Observatory Latitude (degrees))
    -ezRAObsLon    -98.5696          (Observatory Longitude (degrees))
    -ezRAObsAmsl   563.88            (Observatory Above Mean Sea Level (meters))

    -ezConAzimuth         180.4      (simulate data file's recorded Azimuth (degrees)
    -ezConElevation       35.7       (simulate data file's recorded Elevation (degrees)
    -ezConAddAzDeg        9.4        (add to data file's recorded Azimuth (degrees))
    -ezConAddElDeg        -2.6       (add to data file's recorded Elevation (degrees))

    -ezConInputdBm        1          (interpret power values as dBm (dB of 1 milliwatt)

    -ezConRawSamplesUseL  0 100      (first Raw Sample number last Raw Sample number)
    -ezConRawFreqBinHide  129        (hide Raw freqBin 129 by copying from freqBin 128)

    -ezConRefMode 1                  (Dicke Reference sample creation method, default = 10)
      -ezConRefMode N < 0: REF = spectrum from -Nth ANT sample
      -ezConRefMode -1403: REF = spectrum from ANT sample number 1403
      -ezConRefMode     0: REF = spectrum from first ANT sample, number 0
      -ezConRefMode     1: REF = 1.0 (no REF, neutral spectrum)
      -ezConRefMode     2: REF = spectrum from rawByFreqBinAvg spectrum average
      -ezConRefMode    10: REF = last REF sample marked in data, if none will use sample 0

    -ezConAntSamplesUseL    25   102  (first Ant Sample number last Ant Sample number)
    -ezConAntPluck          29        (Pluck (ignore) Ant Sample number)
    -ezConAntAvgPluckQtyL    3    5
         (Pluck (ignore) Ant samples with the 3 Quantity lowest, and 5 highest, sorted AntAvg values)
    -ezConAntAvgPluckFracL  .02  .03
         (Pluck (ignore) Ant samples with the lowest 2% and highest 3% AntAvg values (antLen Fractions))
    -ezConAntFreqBinSmooth  1.1        (RFI spur limiter: maximum muliplier over 4 neighboring freqBin of same Ant sample)

    -ezConRefAvgPluckQtyL    3    5
         (Pluck (ignore) Ref samples with the 3 Quantity lowest, and 5 highest, sorted RefAvg values)
    -ezConRefAvgPluckFracL  .02  .03
         (Pluck (ignore) Ref samples with the lowest 2% and highest 3% RefAvg values (antLen Fractions))

    -ezConAntBaselineFreqBinsFracL   0  0.2344  0.7657  1
         (AntBaseline FreqBin bands: start stop start stop (as fractions of bandwidth))

    -ezConAntRABaselineFreqBinsFracL 0  0.2344  0.7657  1
         (AntRABaseline FreqBin bands: start stop start stop (as fractions of bandwidth))

    -ezConAntXInput 6                (AntX choice: default -1 for Auto, 0/2/4/5/6 for Ant/Ref/AntB/AntRA/AntRB)

    -ezConAntXTFreqBinsFracL            0.2344  0.7657
         (AntXTFreqBinsFrac FreqBin band: start stop (as fractions of bandwidth))

    -ezConUseVlsr   1                (use VLSR for AntXTV and further processing)

    -ezConAntXTVTFreqBinsFracL          0.4     0.6
         (AntXTVTFreqBinsFrac FreqBin band: start stop (as fractions of bandwidth))

    -ezConAntXTVTMaxPluckQtyL   3    5
         (Pluck (ignore) AntXTVTMax samples with the 3 Quantity lowest, and 5 highest, sorted AntXTVTMax)
    -ezConAntXTVTMaxPluckValL  .01   .03
         (Pluck (ignore) AntXTVTMax samples with Values below .01 or above .03)

    -ezConAntXTVTAvgPluckQtyL   3    5
         (Pluck (ignore) AntXTVT samples with the 3 Quantity lowest, and 5 highest, sorted AntXTVT)
    -ezConAntXTVTAvgPluckValL  .01   .03
         (Pluck (ignore) AntXTVT samples with Values below .01 or above .03)

    -ezConAntXTVTPluck         33
         (Pluck (ignore) AntXTVTMax and AntXTVT sample 33)

    -ezConPlotRangeL     0  300      (save only this range of ezCon plots to file, to save time)
    -ezConRawDispIndex   1           (also Display the Raw sample Index on x axis)
    -ezConDispGrid       1           (turn on graphical display plot grids)
    -ezConDispFreqBin    1           (1 for display FreqBin numbers on Y axis, 2 for 0.0 to 1.0)
    -ezConHeatVMinMaxL   1.0 1.4     (heat map z scale)

    -ezConAstroMath      0           (astroMath choice)
      -ezConAstroMath  0: no math (good for faster plots, but AntXTV is wrong)
      -ezConAstroMath  1: using math from MIT Haystack SRT
      -ezConAstroMath  2: using math from authoritative slower AstroPy library

    -ezConVelGLonEdgeFrac 0.5       (velGLon level fraction for plotEzCon430velGLonEdges)

    -ezConGalCrossingGLatCenter 2.4  (adds center of GLat crossing in Galactic Latitude degrees)
    -ezConGalCrossingGLatCenterL -5.2 6.3 11
         (adds centers of GLat crossings, as np.linspace(-5.2, 6.3, num=11))
    -ezConGalCrossingGLatNear 2.3    (defines "close to GLat crossing")
    -ezConGalCrossingGLonCenter 72.4 (adds center of GLon crossing in Galactic Longitude degrees)
    -ezConGalCrossingGLonCenterL 69.6 82.4 13
         (adds centers of GLon crossings, as np.linspace(69.6, 82.4, num=13))
    -ezConGalCrossingGLonNear 2.7    (defines "close to GLon crossing")
    -ezCon399SignalSampleByFreqBinL 18 1423
         (plot antenna sample 1423 spectrum By FreqBin of signal 18)

    -ezDefaultsFile ../bigDish8.txt (additional file of ezRA arguments)

    -eXXXXXXXXXXXXXXzIgonoreThisWholeOneWord
         (any one word starting with -eX is ignored)

 programRevision = ezCon240615b.py

       The Society of Amateur Radio Astronomers (SARA)
                    radio-astronomy.org

##############################################################################################
"""

# ---------------- Help Window Function ----------------
def menu_ezcon_help():
    """Open a new window displaying the ezCon help instructions."""
    help_win = tk.Toplevel(root)
    help_win.title("Ezcon Help")
    help_win.geometry("800x600")
    help_win.grab_set()  # Make the window modal

    text_frame = tk.Frame(help_win)
    text_frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    help_text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    help_text_widget.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=help_text_widget.yview)
    help_text_widget.insert(tk.END, ezcon_help_text)
    help_text_widget.config(state=tk.DISABLED)

# ---------------- Functions for Reading Defaults ----------------
def read_defaults():
    """Reads ezDefaults.txt (ignoring comments) and returns a dict mapping keys to values."""
    defaults = {}
    defaults_file = os.path.join(WORKING_DIR, "ezDefaults.txt")
    if os.path.exists(defaults_file):
        with open(defaults_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if '#' in line:
                    line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                parts = line.split()
                key = parts[0]
                value = " ".join(parts[1:])
                defaults[key] = value
    return defaults

def update_default_parameters():
    """Update the main Default Parameters frame from ezDefaults.txt and show Galactic orientation."""
    defaults = read_defaults()
    for key, var in default_vars.items():
        var.set(defaults.get(key, ""))
    log_debug("Default parameters updated.")
    # Calculate Galactic orientation using astropy.
    try:
        lat = float(defaults.get("-ezRAObsLat", "0"))
        lon = float(defaults.get("-ezRAObsLon", "0"))
        alt = float(defaults.get("-ezRAObsAmsl", "0"))
        az = float(defaults.get("-ezColAzimuth", "0"))
        el = float(defaults.get("-ezColElevation", "0"))
        location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=alt*u.m)
        # Convert from AltAz to ICRS then to Galactic:
        icrs = SkyCoord(az=az*u.deg, alt=el*u.deg, frame=AltAz,
                        obstime=datetime.utcnow(), location=location).icrs
        gal = icrs.galactic
        gal_orientation = f"l = {gal.l.deg:.2f}°, b = {gal.b.deg:.2f}°"
    except Exception as e:
        gal_orientation = "Error computing Galactic orientation: " + str(e)
    if "Galactic Orientation" not in default_vars:
        var = tk.StringVar(value=gal_orientation)
        default_vars["Galactic Orientation"] = var
        row = tk.Frame(default_params_frame)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Galactic Orientation:", width=30, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(row, textvariable=var, state="readonly", width=30)
        entry.pack(side=tk.LEFT, padx=5)
    else:
        default_vars["Galactic Orientation"].set(gal_orientation)

def load_advanced_options():
    """Load advanced options from ezDefaults.txt into globals."""
    defaults = read_defaults()
    for key, _ in ADVANCED_OPTIONS_PROC + ADVANCED_OPTIONS_DISP:
        advanced_options[key] = defaults.get(key, "")
        advanced_options_active[key] = False
    log_debug("Advanced options loaded.")

# ---------------- Settings Save/Load ----------------
def save_settings():
    """Save the current working directory and advanced options to ezconguiset.txt in WORKING_DIR."""
    settings_file = os.path.join(WORKING_DIR, "ezconguiset.txt")
    _save_settings_to_file(settings_file)

def save_settings_as():
    """Open a Save As dialog so the user can save settings to a custom file."""
    settings_file = filedialog.asksaveasfilename(
        title="Save Settings As",
        defaultextension=".txt",
        initialdir=WORKING_DIR,
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if settings_file:
        _save_settings_to_file(settings_file)

def _save_settings_to_file(settings_file):
    """Helper function to write settings to the specified file."""
    settings = {"WORKING_DIR": working_dir_var.get().strip()}
    for key in advanced_options:
        settings[key] = advanced_options.get(key, "")
        settings[key + "_active"] = advanced_options_active.get(key, False)
    try:
        with open(settings_file, "w") as f:
            for k, v in settings.items():
                f.write(f"{k} = {v}\n")
        log_debug("Settings saved to " + settings_file)
    except Exception as e:
        log_debug("Error saving settings: " + str(e))
        messagebox.showerror("Save Settings Error", str(e))

def load_settings():
    """Load settings from ezconguiset.txt in WORKING_DIR and update the working directory and advanced options."""
    global WORKING_DIR
    settings_file = os.path.join(WORKING_DIR, "ezconguiset.txt")
    try:
        with open(settings_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "WORKING_DIR":
                    working_dir_var.set(value)
                    WORKING_DIR = value
                else:
                    if key.endswith("_active"):
                        real_key = key[:-7]
                        advanced_options_active[real_key] = (value.lower() in ["true", "1", "yes"])
                    else:
                        advanced_options[key] = value
        log_debug("Settings loaded from " + settings_file)
    except Exception as e:
        log_debug("No settings file found or error loading settings: " + str(e))

# ---------------- Debug Output ----------------
def log_debug(msg):
    """Append a message to the debug text widget."""
    debug_text.config(state=tk.NORMAL)
    debug_text.insert(tk.END, msg + "\n")
    debug_text.see(tk.END)
    debug_text.config(state=tk.DISABLED)

def read_stream(stream, prefix=""):
    """Read lines from a stream and update the debug window."""
    for line in iter(stream.readline, ''):
        if line:
            if not DEBUG_MODE:
                if prefix.startswith("STDOUT:") or prefix.startswith("STDERR:"):
                    continue
            else:
                if prefix.startswith("STDOUT:") and not show_stdout_var.get():
                    continue
                if prefix.startswith("STDERR:") and not show_stderr_var.get():
                    continue
            root.after(0, log_debug, prefix + line.rstrip())
    stream.close()

# ---------------- Build Command Line ----------------
def build_command_line(data_file_rel, ezcon_path_norm):
    """
    Build and return the command line as a list to run ezCon.py.
    Append any active advanced option (key and its tokenized value).
    """
    cmd = [sys.executable, ezcon_path_norm, data_file_rel]
    for key in advanced_options:
        if advanced_options_active.get(key, False):
            val = advanced_options.get(key, "").strip()
            if val:
                cmd.append(key)
                cmd.extend(val.split())
    return cmd

# ---------------- Command Line Preview ----------------
def update_cmd_preview():
    """Update the command line preview text widget on the main window."""
    data_file = file_entry.get().strip()
    if not data_file:
        cmd_preview_text.config(state=tk.NORMAL)
        cmd_preview_text.delete("1.0", tk.END)
        cmd_preview_text.insert(tk.END, "No file selected.")
        cmd_preview_text.config(state=tk.DISABLED)
        return
    ezcon_path = os.path.join(WORKING_DIR, "ezCon.py")
    if not os.path.exists(ezcon_path):
        cmd_preview_text.config(state=tk.NORMAL)
        cmd_preview_text.delete("1.0", tk.END)
        cmd_preview_text.insert(tk.END, "ezCon.py not found.")
        cmd_preview_text.config(state=tk.DISABLED)
        return
    abs_working = os.path.abspath(WORKING_DIR)
    abs_file = os.path.abspath(data_file)
    if abs_file.startswith(abs_working):
        data_file_rel = os.path.relpath(data_file, WORKING_DIR)
    else:
        data_file_rel = data_file
    data_file_rel = os.path.normpath(data_file_rel)
    ezcon_path_norm = os.path.normpath(ezcon_path)
    cmd = build_command_line(data_file_rel, ezcon_path_norm)
    preview_str = " ".join(cmd)
    cmd_preview_text.config(state=tk.NORMAL)
    cmd_preview_text.delete("1.0", tk.END)
    cmd_preview_text.insert(tk.END, preview_str)
    cmd_preview_text.config(state=tk.DISABLED)

# ---------------- Thumbnail Update ----------------
THUMBNAIL_FILES = [
    "ezCon114antBAvg.png",
    "ezCon247antBAvg.png",
    "ezCon282antRBTVAvg.png",
    "ezCon301rawByFreqAvg.png"
]
thumbnail_images = []

def update_thumbnails():
    """Update the Processed Images frame with thumbnails from the output folder."""
    global thumbnail_images
    for widget in thumb_frame.winfo_children():
        widget.destroy()
    thumbnail_images = []
    folder = last_output_folder if last_output_folder and os.path.exists(last_output_folder) else WORKING_DIR
    for fname in THUMBNAIL_FILES:
        fpath = os.path.join(folder, fname)
        frame = tk.Frame(thumb_frame, padx=5, pady=5)
        frame.pack(side=tk.LEFT, padx=5, pady=5)
        if os.path.exists(fpath):
            try:
                img = Image.open(fpath)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                thumbnail_images.append(photo)
                tk.Label(frame, image=photo).pack()
                tk.Label(frame, text=fname, wraplength=100).pack()
            except Exception as e:
                log_debug("Error loading thumbnail for " + fname + ": " + str(e))
                tk.Label(frame, text=fname+"\n(Error)", wraplength=100, fg="red").pack()
        else:
            tk.Label(frame, text=fname+"\n(Not found)", wraplength=100, fg="red").pack()

# ---------------- Running ezCon ----------------
def run_ezcon():
    """
    Run ezCon.py with the selected data file and advanced options.
    After a successful run, move new .png files into an output folder.
    The folder is created under an "EZCONPNG_FILES" folder and then a subfolder
    based on a date string. If the "Use ddmmyyyy folder style" checkbutton is selected,
    the date string is in ddmmyyyy format; otherwise, it is in yyyymmdd format.
    A progress meter is displayed during the run.
    """
    global last_output_folder
    data_file = file_entry.get().strip()
    if not data_file:
        messagebox.showerror("Error", "Please select a .txt data file first!")
        return
    if not os.path.exists(data_file):
        messagebox.showerror("File Not Found", f"Data file not found:\n{data_file}")
        return
    ezcon_path = os.path.join(WORKING_DIR, "ezCon.py")
    if not os.path.exists(ezcon_path):
        messagebox.showerror("File Not Found", f"Cannot find ezCon.py at:\n{ezcon_path}")
        return

    abs_working = os.path.abspath(WORKING_DIR)
    abs_file = os.path.abspath(data_file)
    if abs_file.startswith(abs_working):
        data_file_rel = os.path.relpath(data_file, WORKING_DIR)
    else:
        data_file_rel = data_file
    data_file_rel = os.path.normpath(data_file_rel)
    ezcon_path_norm = os.path.normpath(ezcon_path)

    # Determine subfolder name based on folder_style_var.
    # If folder_style_var is True, use ddmmyyyy format (ignoring any filename match).
    if folder_style_var.get():
        try:
            timestamp = os.path.getmtime(data_file)
            subfolder_name = datetime.fromtimestamp(timestamp).strftime("%d%m%Y")
        except Exception as e:
            log_debug("Error determining subfolder name: " + str(e))
            subfolder_name = "UnknownDate"
    else:
        base_name = os.path.basename(data_file)
        match = re.search(r'(\d{6})(?!\d)', base_name)
        if match:
            subfolder_name = match.group(1)
            if not subfolder_name.startswith("20"):
                subfolder_name = "20" + subfolder_name
        else:
            try:
                timestamp = os.path.getmtime(data_file)
                subfolder_name = datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
            except Exception as e:
                log_debug("Error determining subfolder name: " + str(e))
                subfolder_name = "UnknownDate"

    # Create the full output folder under EZCONPNG_FILES.
    output_folder = os.path.join(WORKING_DIR, "EZCONPNG_FILES", subfolder_name)
    try:
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            log_debug("Output folder created: " + output_folder)
            last_output_folder = output_folder
    except Exception as e:
        log_debug("Error creating output folder: " + str(e))
        output_folder = None

    cmd = build_command_line(data_file_rel, ezcon_path_norm)
    update_cmd_preview()
    log_debug("DEBUG: Running command:")
    log_debug("  " + " ".join(cmd))
    log_debug("DEBUG: Working directory: " + WORKING_DIR)
    run_start_time = time.time()

    # Start the progress bar (indeterminate mode)
    progress_bar.start(10)

    try:
        process = subprocess.Popen(
            cmd,
            cwd=WORKING_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        log_debug("Exception while running subprocess: " + str(e))
        messagebox.showerror("Execution Error", str(e))
        progress_bar.stop()
        return

    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT: "))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR: "))
    stdout_thread.start()
    stderr_thread.start()

    def wait_for_process():
        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        progress_bar.stop()
        log_debug("Process finished with return code: " + str(process.returncode))
        if process.returncode != 0:
            messagebox.showerror("ezCon Error",
                                 f"ezCon.py failed with return code {process.returncode}.\nCheck debug output for details.")
        else:
            moved_files = []
            if output_folder:
                for f in os.listdir(WORKING_DIR):
                    if f.lower().endswith(".png"):
                        fpath = os.path.join(WORKING_DIR, f)
                        try:
                            if os.path.getmtime(fpath) >= run_start_time:
                                shutil.move(fpath, os.path.join(output_folder, f))
                                moved_files.append(f)
                        except Exception as e:
                            log_debug("Error moving file " + f + ": " + str(e))
                log_debug("Moved .png files: " + ", ".join(moved_files))
            messagebox.showinfo("ezCon Output",
                                "ezCon.py completed successfully.\nCheck debug output for details.")
            update_thumbnails()

    threading.Thread(target=wait_for_process).start()

# ---------------- File Selection ----------------
def select_file():
    chosen_file = filedialog.askopenfilename(
        title="Select a Radio Data File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if chosen_file:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, chosen_file)
        log_debug("Selected file: " + chosen_file)
        update_cmd_preview()

def clear_debug():
    debug_text.config(state=tk.NORMAL)
    debug_text.delete("1.0", tk.END)
    debug_text.config(state=tk.DISABLED)

# ---------------- Helper: Create Scrollable Frame ----------------
def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return scrollable_frame

# ---------------- Advanced Options Dialog ----------------
def open_advanced_options_dialog():
    """Open a new window with three tabs for advanced options."""
    adv_win = tk.Toplevel(root)
    adv_win.title("Advanced Options")
    adv_win.geometry("600x700")
    adv_win.grab_set()

    notebook = ttk.Notebook(adv_win)
    notebook.pack(fill="both", expand=True)
    proc_tab = tk.Frame(notebook)
    disp_tab1 = tk.Frame(notebook)
    disp_tab2 = tk.Frame(notebook)
    notebook.add(proc_tab, text="Processing Options")
    notebook.add(disp_tab1, text="Display Options 1")
    notebook.add(disp_tab2, text="Display Options 2")

    proc_scroll = create_scrollable_frame(proc_tab)
    disp_scroll1 = create_scrollable_frame(disp_tab1)
    disp_scroll2 = create_scrollable_frame(disp_tab2)

    temp_vars = {}
    temp_active_vars = {}

    def populate_tab(frame, options_list):
        for (key, friendly) in options_list:
            row_frame = tk.Frame(frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            active_var = tk.BooleanVar(value=advanced_options_active.get(key, False))
            temp_active_vars[key] = active_var
            cb = tk.Checkbutton(row_frame, variable=active_var)
            cb.grid(row=0, column=0, padx=(0,5))
            tk.Label(row_frame, text=friendly + ":", width=30, anchor="w").grid(row=0, column=1, sticky="w")
            var = tk.StringVar(value=advanced_options.get(key, ""))
            temp_vars[key] = var
            tk.Entry(row_frame, textvariable=var, width=30).grid(row=0, column=2, padx=5)
            help_text = advanced_options_help.get(key, "")
            if help_text:
                tk.Label(row_frame, text=help_text, font=("Arial", 8), fg="gray").grid(row=1, column=0, columnspan=3, sticky="w")
    populate_tab(proc_scroll, ADVANCED_OPTIONS_PROC)
    populate_tab(disp_scroll1, ADVANCED_OPTIONS_DISP1)
    populate_tab(disp_scroll2, ADVANCED_OPTIONS_DISP2)

    btn_frame = tk.Frame(adv_win)
    btn_frame.pack(fill="x", pady=5)
    def on_ok():
        for key, var in temp_vars.items():
            advanced_options[key] = var.get().strip()
        for key, active_var in temp_active_vars.items():
            advanced_options_active[key] = active_var.get()
        log_debug("Advanced options updated.")
        adv_win.destroy()
        update_cmd_preview()
    def on_cancel():
        adv_win.destroy()
    tk.Button(btn_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.RIGHT, padx=5)

# ---------------- Menu Commands ----------------
def menu_open_file():
    select_file()

def menu_clear_debug():
    clear_debug()

def menu_reload_defaults():
    update_default_parameters()
    load_advanced_options()
    update_cmd_preview()

def menu_save_settings():
    save_settings()

def menu_load_settings():
    load_settings()
    update_cmd_preview()

def menu_exit():
    root.quit()

def menu_about():
    messagebox.showinfo("About", "ezCon GUI with Advanced Options\nVersion 1.0\nDeveloped by Antal Vincz")

def menu_advanced_options():
    open_advanced_options_dialog()

def menu_ezcon_help():
    # Open the Ezcon Help window without recursion
    help_win = tk.Toplevel(root)
    help_win.title("Ezcon Help")
    help_win.geometry("800x600")
    help_win.grab_set()
    text_frame = tk.Frame(help_win)
    text_frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    help_text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    help_text_widget.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=help_text_widget.yview)
    help_text_widget.insert(tk.END, ezcon_help_text)
    help_text_widget.config(state=tk.DISABLED)

# ---------------- Main Window Setup ----------------
root = tk.Tk()
root.title("ezCon GUI 1.0")
root.geometry("1000x1000")  # Change main window size here

# Set the window icon to a satellite dish icon if available.
icon_path = os.path.join(WORKING_DIR, "satellite.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# Create folder_style_var AFTER root is created.
folder_style_var = tk.BooleanVar(root, value=False)

# Top menu bar.
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Data File...", command=menu_open_file)
file_menu.add_command(label="Clear Debug", command=menu_clear_debug)
file_menu.add_command(label="Reload Defaults", command=menu_reload_defaults)
file_menu.add_command(label="Save Settings", command=menu_save_settings)
file_menu.add_command(label="Save Settings As...", command=save_settings_as)
file_menu.add_command(label="Load Settings", command=menu_load_settings)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=menu_exit)
menu_bar.add_cascade(label="File", menu=file_menu)

if DEBUG_MODE:
    filters_menu = tk.Menu(menu_bar, tearoff=0)
    show_stdout_var = tk.BooleanVar(root, value=True)
    show_stderr_var = tk.BooleanVar(root, value=True)
    filters_menu.add_checkbutton(label="Show STDOUT", variable=show_stdout_var, command=update_cmd_preview)
    filters_menu.add_checkbutton(label="Show STDERR", variable=show_stderr_var, command=update_cmd_preview)
    menu_bar.add_cascade(label="Filters", menu=filters_menu)

options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Advanced Options...", command=menu_advanced_options)
# Add the new checkbutton for folder style under Options.
options_menu.add_checkbutton(label="Use ddmmyyyy folder style", variable=folder_style_var)
menu_bar.add_cascade(label="Options", menu=options_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="ezCon GUI Help", command=menu_about)
help_menu.add_command(label="Ezcon Help", command=menu_ezcon_help)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Working Directory Frame.
working_dir_frame = tk.Frame(root, padx=10, pady=5)
working_dir_frame.pack(fill=tk.X)
tk.Label(working_dir_frame, text="Working Directory:").pack(side=tk.LEFT)
working_dir_var = tk.StringVar(value=WORKING_DIR)
working_dir_entry = tk.Entry(working_dir_frame, textvariable=working_dir_var, width=50)
working_dir_entry.pack(side=tk.LEFT, padx=5)
def change_working_dir():
    global WORKING_DIR
    new_dir = filedialog.askdirectory(title="Select Working Directory", initialdir=WORKING_DIR)
    if new_dir:
        working_dir_var.set(new_dir)
        WORKING_DIR = new_dir
        update_cmd_preview()
        log_debug("Working directory changed to: " + new_dir)
tk.Button(working_dir_frame, text="Change", command=change_working_dir).pack(side=tk.LEFT, padx=5)

# Top Frame: Default Parameters and Processed Images side by side.
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=5)
default_params_frame = tk.LabelFrame(top_frame, text="Default Parameters", padx=10, pady=10)
default_params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
default_vars = {}
for key, label_text in DISPLAY_KEYS:
    row = tk.Frame(default_params_frame)
    row.pack(fill=tk.X, pady=2)
    tk.Label(row, text=label_text + ":", width=30, anchor="w").pack(side=tk.LEFT)
    var = tk.StringVar()
    entry = tk.Entry(row, textvariable=var, state="readonly", width=30)
    entry.pack(side=tk.LEFT, padx=5)
    default_vars[key] = var
# The Galactic orientation field is added automatically by update_default_parameters().
thumb_frame = tk.LabelFrame(top_frame, text="Processed Images", padx=10, pady=10)
thumb_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
# Thumbnails will be updated after a run.

# File Selection Frame.
file_frame = tk.Frame(root, padx=10, pady=10)
file_frame.pack(fill=tk.X)
tk.Label(file_frame, text="Data File:").pack(anchor=tk.W)
file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
browse_button = tk.Button(file_frame, text="Browse...", command=select_file)
browse_button.pack(side=tk.LEFT, padx=5)
file_entry.bind("<FocusOut>", lambda event: update_cmd_preview())

# Run Button.
run_button = tk.Button(root, text="Run ezCon", command=run_ezcon, padx=10, pady=5)
run_button.pack(pady=10)

# Add a Progress Meter (Progressbar) under the Run button.
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="indeterminate")
progress_bar.pack(fill=tk.X, padx=10, pady=(0,10))

# Command Line Preview Frame.
cmd_preview_frame = tk.Frame(root, padx=10, pady=10)
cmd_preview_frame.pack(fill=tk.X)
tk.Label(cmd_preview_frame, text="Command Line Preview:").pack(anchor=tk.W)
cmd_preview_text = tk.Text(cmd_preview_frame, height=3, state=tk.DISABLED, wrap=tk.WORD)
cmd_preview_text.pack(fill=tk.X, expand=True)

# Debug Output Window.
debug_frame = tk.Frame(root, padx=10, pady=10)
debug_frame.pack(fill=tk.BOTH, expand=True)
tk.Label(debug_frame, text="Process output:").pack(anchor=tk.W)
debug_text = tk.Text(debug_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
debug_text.pack(fill=tk.BOTH, expand=True)
debug_scrollbar = tk.Scrollbar(debug_frame, command=debug_text.yview)
debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
debug_text.config(yscrollcommand=debug_scrollbar.set)

# ---------------- Initialization ----------------
load_settings()             # Automatically load settings at startup.
update_default_parameters()
load_advanced_options()
update_cmd_preview()
update_thumbnails()

root.mainloop()
