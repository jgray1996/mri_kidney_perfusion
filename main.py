from scripts.experiments import InputOutput
from scripts.database import DatabaseHandler

__author = "James Gray"
__version__ = 0.1

sequences: list = []

if __name__ == "__main__":
    # Initialize IO class for handling MRI formats
    io: InputOutput = InputOutput()
    # DWI_dicom: list[tuple] = io.get_dicom_files_DWI(path="MRI_data/DWI")
    # sequences.append(DWI_dicom)

    # T1_dicom: list[tuple] = io.get_dicom_files_T1(path="MRI_data/T1")
    # sequences.append(T1_dicom)

    # T2_dicom: list[tuple] = io.get_dicom_files_T2(path="MRI_data/T2")
    # sequences.append(T2_dicom)

    ASL_dicom: list[list] = io.get_DICOM_files_ASL(path="MRI_data/ASL_coreg")
    sequences.append(ASL_dicom)

    # initialize database to be working with
    db: DatabaseHandler = DatabaseHandler("databases/dicom.db")
    db.remove_database()
    db.create_database()
    db.create_tables("scripts/relational_database.sql")

    # write DICOM files to database
    for sequence in sequences:
        db.write_data(sequence, file_type="dicom")
    print("Done.")