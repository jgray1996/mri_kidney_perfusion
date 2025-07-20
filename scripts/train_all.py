import sys
import subprocess

EPOCHS = 300

# T1
code1 = subprocess.call(
    [
        "python3", "U_net.py",
        "-t",
        "-e", f"{EPOCHS}",
        "-a", "0.00001",
        "-b", "28",
        "-s", "../models/T1.keras",
        "-d", "../data/pickles/T1.pkl",
        "-x", "192;192;1"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during T1 training"
    )

# ASL
code2 = subprocess.call(
    [
        "python3", "U_net.py",
        "-t",
        "-e", f"{EPOCHS}",
        "-a", "0.00001",
        "-b", "28",
        "-s", "../models/ASL.keras",
        "-d", "../data/pickles/ASL.pkl",
        "-x", "128;128;1"
    ]
)
if code2 != 0:
    sys.exit(
        "Error occured during ASL training"
    )

# DWI
code3 = subprocess.call(
    [
        "python3", "U_net.py",
        "-t",
        "-e", f"{EPOCHS}",
        "-a", "0.00001",
        "-b", "28",
        "-s", "../models/DWI.keras",
        "-d", "../data/pickles/DWI.pkl",
        "-x", "96;128;1"
    ]
)
if code3 != 0:
    sys.exit(
        "Error occured during DWI training"
    )

# T2
code4 = subprocess.call(
    [
        "python3", "U_net.py",
        "-t",
        "-e", f"{EPOCHS}",
        "-a", "0.00001",
        "-b", "28",
        "-s", "../models/T2.keras",
        "-d", "../data/pickles/T2.pkl",
        "-x", "320;320;1"
    ]
)
if code4 != 0:
    sys.exit(
        "Error occured during T2 training"
    )

# T2*
code5 = subprocess.call(
    [
        "python3", "U_net.py",
        "-t",
        "-e", f"{EPOCHS}",
        "-a", "0.00001",
        "-b", "28",
        "-s", "../models/T2star.keras",
        "-d", "../data/pickles/T2star.pkl",
        "-x", "128;256;1"
    ]
)
if code5 != 0:
    sys.exit(
        "Error occured during T2star training"
    )
