import sys
import subprocess

# T1
code1 = subprocess.call(
    [
        "python", "U_net.py",
        "-p", "../models/T1.keras",
        "-i", "../data/processed/tensorflow_format_sequences/T1/",
        "-o", "../data/processed/tensorflow_format_proba/T1/"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during T1 classification"
    )

T2
code1 = subprocess.call(
    [
        "python", "U_net.py",
        "-p", "../manifest/models/T2.keras",
        "-i", "../data/processed/tensorflow_format_sequences/T2/",
        "-o", "../data/processed/tensorflow_format_proba/T2/"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during T2 classification"
    )

# ValueError: Input 0 of layer "functional" is incompatible with the layer: expected shape=(None, 128, 256, 1), found shape=(20, 256, 128)

# T2*
code1 = subprocess.call(
    [
        "python", "U_net.py",
        "-p", "../manifest/models/T2star.keras",
        "-i", "../data/processed/tensorflow_format_sequences/T2star/",
        "-o", "../data/processed/tensorflow_format_proba/T2star/"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during T2star classification"
    )

# ASL
code1 = subprocess.call(
    [
        "python", "U_net.py",
        "-p", "../manifest/models/ASL.keras",
        "-i", "../data/processed/tensorflow_format_sequences/ASL/",
        "-o", "../data/processed/tensorflow_format_proba/ASL/"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during ASL classification"
    )

# DWI
code1 = subprocess.call(
    [
        "python", "U_net.py",
        "-p", "../manifest/models/DWI.keras",
        "-i", "../data/processed/tensorflow_format_sequences/DWI/",
        "-o", "../data/processed/tensorflow_format_proba/DWI/"
    ]
)
if code1 != 0:
    sys.exit(
        "Error occured during DWI classification"
    )
