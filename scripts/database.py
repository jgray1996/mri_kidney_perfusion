import os
import sqlite3
from pathlib import Path
from os import PathLike

__author__ = "James Gray"
__version__ = 0.1

class DatabaseHandler:

    """
    This class handles the relational database
    which stores the mri experiments and related
    file paths and meta data.
    """

    def __init__(self, name: PathLike) -> None:
        """
        Initialize Database handler
        """
        self.name = Path(name)
        pass

    def create_tables(self, script: Path) -> None:
        """
        Create tables in database
        """
        with open(script, 'r') as f_in,\
                sqlite3.connect(self.name) as connection:
            table_script: str = f_in.read()
            connection.executescript(table_script)
            connection.commit()
            print(f"Succesfully wrote [{script}] to [{self.name}]!")
        pass

    def remove_database(self) -> None:
        """
        Remove the database
        """
        try:
            os.remove(self.name)
            print(f"Succesfully removed [{self.name}]!")
        except:
            print(f"Could not remove [{self.name}]!")
        pass

    def create_database(self) -> None:
        """
        Create database
        """
        with sqlite3.connect(self.name) as connection:
            print(f"Succesfully connected to [{self.name}]!")
        pass

    def write_data(self, data: list[tuple], file_type: str="dicom") -> None:
        """
        This method takes a multicursor compatable object and writes it
        to the database the DataBaseHandler was initialized with.
        """
        with sqlite3.connect(self.name) as connection:
            if file_type.lower() == "dicom":
                connection.executemany(
                    """
                    INSERT OR IGNORE INTO Dicom (
                        file_path, vivo, seq, experiment, placement, time_point
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """, data)
                connection.commit()
                print(f"{file_type} files written succesfully to {self.name}!")
        pass

if __name__ == "__main__":
    # test code
    dbh = DatabaseHandler("test_db.db")
    dbh.create_database()
    dbh.create_tables("relational_database.sql")
    dbh.remove_database()
    dbh.remove_database()