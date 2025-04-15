from scripts.experiments import InputOutput
from scripts.database import DatabaseHandler

__author = "James Gray"
__version__ = 0.1

if __name__ == "__main__":
    # Initialize IO class for handling MRI formats
    io: InputOutput = InputOutput()
    # sequences, segmentations = io.get_files(path="../ROI/DWI/exp*/")
    DWI_dicom: list[list] = io.get_dicom_files(path=r"C:\Users\James\Documents\MRI_data\DWI")
    
    # initialize database to be working with
    db: DatabaseHandler = DatabaseHandler("databases/test_db.db")
    db.create_database()
    db.create_tables("scripts/relational_database.sql")
