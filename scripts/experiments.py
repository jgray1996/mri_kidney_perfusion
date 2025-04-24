from glob import glob
from typing import OrderedDict
from os import PathLike, walk
from pathlib import Path
import numpy as np
import nrrd
from pydicom import dcmread, FileDataset
import re

__author__ = "James Gray"
__version__ = 0.1

class InputOutput:

    """
    Class handling reading experimental dicom and nrrd files from disk
    and generalizing their type and filepath format.
    """

    pattern = re.compile(r'(?:_?(left|right)[_ ](\d+)min|(\d+)min[_ ](left|right))', re.IGNORECASE)
    pattern_1 = re.compile(r'(left|right|straight)', re.IGNORECASE)

    def __init__(self) -> None:
        pass

    def get_nrrd_files(self, path: PathLike) -> tuple[list[Path], list[Path]]:
        """
        This method reads all files from a directory which
        match a certain glob statement.
        """
        # Standard .seg.nrrd for segmentation
        segmentations: list[Path] = [Path(path) for path in glob(f"{path}*seg.nrrd")]
        # Renhui and Yous special convention
        if not len(segmentations):
            segmentations: list[Path] = [Path(path) for path in glob(f"{path}*label.nrrd")]
        all_files: list[Path] = [Path(path) for path in glob(f"{path}*.nrrd")]
        sequences: list[Path] = [file for file in all_files if not file in segmentations]

        segmentations.sort(), sequences.sort()

        del all_files

        assert len(segmentations) == len(sequences)

        return sequences, segmentations

    def get_dicom_files_DWI(self, path: PathLike) -> list[tuple]:
        """
        This method returns all DWI dicom files.
        """

        dicom_files: list[list] = []
        sequence: str = "DWI"

        for (root, _, files) in walk(path):
            for file in files:
                
                if file.endswith(".dcm"):
                    root_path: Path = Path(root)
                    total_path: Path = root_path/ Path(file)

                    if "exvivo" in root.lower():
                        parts: list = total_path.parent.stem.split("_")
                        experiment: int = int(parts[0].strip("Exp"))
                        placement: str = parts[5]
                        time: int = int(parts[6].split("min")[0])
                        dicom_files.append((str(total_path), "exvivo", sequence,
                                            int(experiment), placement, time))
                    
                    if "invivo" in root.lower():
                        parts: list = total_path.parent.stem.split("_")
                        experiment: int = int(parts[0].strip("Exp"))
                        # Full pork in the toaster
                        placement: str = "both"
                        # Timepoint is always -10
                        time: int = -10
                        dicom_files.append((str(total_path), "invivo", sequence,
                                            int(experiment), placement, time))

        return dicom_files
    
    def get_dicom_files_T1(self, path: PathLike) -> list[tuple]:

        """
        This method returns all T1 dicom files.
        """

        dicom_files: list[list] = []
        sequence: str = "T1"
        dcm: FileDataset = None
        unknown_experiment: str = "UNKNOWN_"
        old_time: int = None
        old_dir: PathLike = None
        experiment_counter: int = 1

        for i, (root, _, files) in enumerate(walk(path)):
            new_dir: PathLike = Path(root).parts[-2]
            # Count each new experiment based on parent directory
            if new_dir != old_dir:
                experiment_counter += 1
            old_dir = new_dir
            
            for file in files:
                if file.endswith(".dcm"):
                    root_path: Path = Path(root)
                    total_path: Path = root_path/Path(file)
                    if "exvivo" in root.lower():
                        parts: list = total_path.parent.stem.split("_")
                        time: int = int(parts[-1].split()[-1])
                        if time != old_time:
                            dcm: FileDataset = dcmread(total_path)
                        old_time = time
                        try:
                            experiment: int = int(str(dcm.PatientName).split(" ")[1])
                        except:
                            experiment: int = unknown_experiment + str(experiment_counter)
                        placement: str = "both"
                        dicom_files.append((str(total_path), "exvivo", sequence,
                                            experiment, placement, time))

                    if "invivo" in root.lower():
                        parts: list = total_path.parent.stem.split("_")
                        time: int = int(parts[-1].split()[-1])
                        if time != old_time:
                            dcm: FileDataset = dcmread(total_path)
                        old_time = time
                        try:
                            experiment: int = int(str(dcm.PatientName).split(" ")[1])
                        except:
                            experiment: int = unknown_experiment + str(experiment_counter)
                        placement: str = "both"
                        dicom_files.append((str(total_path), "invivo", sequence,
                                            experiment, placement, -10))

        return dicom_files
    
    def get_dicom_files_T2(self, path: PathLike) -> list[tuple]:
        """
        This method returns all T2 dicom files.
        """
        dicom_files: list[tuple] = []
        sequence: str = "T2"
        old_time: int = None
        dcm: FileDataset = None
        old_dir: PathLike = None
        experiment_counter: int = 1
        transation_dict: dict = {"l": "left",
                                 "left": "left",
                                 "right": "right", 
                                 "r": "right", 
                                 "both": "both", 
                                 "straight": "both"}

        for (root, _, files) in walk(path):
            # Count each new experiment based on parent directory
            new_dir: PathLike = Path(root).parts[-2]
            if new_dir != old_dir:
                experiment_counter += 1
            old_dir = new_dir
            for file in files:
                if "exvivo" in root.lower():
                    if file.endswith(".dcm"):
                        root_path: Path = Path(root)
                        total_path: Path = root_path/Path(file)
                        metadata: str = root_path.parts[-1].split()
                        time: int = 0
                        side: str = ""
                        try:
                            match = self.pattern.findall(metadata[2])
                            group_1 = list(match[0][:2])
                            group_2 = list(match[0][2:])

                            if not set(group_1) == {""}:
                                group_1.sort()
                                time: int = int(group_1[0])
                                side: str = group_1[1]

                            elif not set(group_2) == {""}:
                                group_2.sort()
                                time: int = int(group_2[0])
                                side: str = group_2[1]
                            else:
                                print("No matches!")
                                pass
                        except:
                            pass

                        if time != old_time:
                            dcm: FileDataset = dcmread(total_path)
                        try:
                            experiment: int = int(str(dcm.PatientName).split(" ")[1])
                        except:
                            unknown_experiment_offset: int = 1e4
                            experiment: int = experiment_counter + unknown_experiment_offset
                        old_time = time
                        dicom_files.append((str(total_path), "exvivo", sequence,
                                                int(experiment), side, time))
                if "invivo" in root.lower():
                    if file.endswith(".dcm"):
                        root_path: Path = Path(root)
                        total_path: Path = root_path/Path(file)
                        metadata: str = root_path.parts[-1].split("_")
                        experiment: str = root_path.parts[-3].split("_")[-1]

                        if len(metadata) == 4 and experiment.isnumeric():
                            side: str = transation_dict[metadata[2]]
                            dicom_files.append((str(total_path), "invivo", sequence,
                                                    int(experiment), side, -10))
                        else:
                            dcm: FileDataset = dcmread(total_path)
                            side: str = transation_dict[self.pattern_1.findall(root_path.parts[-1])[0]]
                            try:
                                experiment: int = int(str(dcm.PatientName).split(" ")[1])
                            except:
                                unknown_experiment_offset: int = 1e4
                                experiment: int = experiment_counter + unknown_experiment_offset
                            dicom_files.append((str(total_path), "invivo", sequence,
                                                    int(experiment), side, -10))
        return dicom_files

    def read_sequences(self, sequences_in: list[Path]) -> tuple[list[OrderedDict], list[np.ndarray]]:
        """
        This method takes a list of paths of nrrd sequence files and reads them in
        numpy array format and header format. This method returns a tuple of
        Lists each containing all headers and all sequences.
        """
        headers_out: list[OrderedDict] = []
        sequences_out: list[np.ndarray] = []

        assert len(sequences_in), \
            f"Empty list of sequence files passed..."

        for sequence in sequences_in:
            # Declare types
            data: np.ndarray
            header: OrderedDict

            # Fill variables and lists
            data, header = nrrd.read(sequence)
            headers_out.append(header)
            sequences_out.append(data)

        return (headers_out, sequences_out)

    def read_segmentations(self, segmentations_in: list[Path]) -> tuple[list[OrderedDict], list[np.ndarray]]:
        """
        This method takes a list of paths of nrrd segmentation files and reads them in
        numpy array format and header format. This method returns a tuple of
        Lists each containing all headers and all segmentations.
        """
        headers_out: list[OrderedDict] = []
        segmentations_out: list[np.ndarray] = []

        assert len(segmentations_in), \
            f"Empty list of segmentation files passed..."
        
        for i, segmentation in enumerate(segmentations_in):
            # Declare types
            data: np.ndarray
            header: OrderedDict

            # Fill variables and lists
            data, header = nrrd.read(segmentation)
            headers_out.append(header)
            segmentations_out.append(data)

        return (headers_out, segmentations_out)
    
    def create_nrrd(self, DICOM_in: list[Path]) -> list[np.ndarray]:
        """
        Convert list of dicom files in single nrrd file per experiment.
        """
        # get a list of files belonging to a certain experiment
        # read files and headers
        # create a nested array to write to a nrrd file
        # create a fitting filename
        # write object and return filename 
        pass

if __name__ == "__main__":
    io = InputOutput()
    # sequences, segmentations = io.get_files(path="../ROI/DWI/exp*/")
    # print(io.read_sequences(sequences))
    DWI_dicom_DWI: list[list] = io.get_dicom_files_DWI(path="../MRI_data/DWI")
    # DWI_dicom_T1: list[list] = io.get_dicom_files_T1(path="../MRI_data/T1")
    # DWI_dicom_T2: list[list] = io.get_dicom_files_T2(path="../MRI_data/T2")
    print(DWI_dicom_DWI)
