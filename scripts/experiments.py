from glob import glob
from typing import List, Tuple, OrderedDict
from os import PathLike, walk
from pathlib import Path
import numpy as np
import nrrd
from pydicom import dcmread, FileDataset

__author__ = "James Gray"
__version__ = 0.1

class InputOutput:

    """
    Class handling reading experimental dicom and nrrd files from disk
    and generalizing their type and filepath format.
    """

    def __init__(self) -> None:
        pass

    def get_nrrd_files(self, path: PathLike) -> Tuple[List[Path], List[Path]]:
        """
        This method reads all files from a directory which
        match a certain glob statement.
        """
        # Standard .seg.nrrd for segmentation
        segmentations: List[Path] = [Path(path) for path in glob(f"{path}*seg.nrrd")]
        # Renhui and Yous special convention
        if not len(segmentations):
            segmentations: List[Path] = [Path(path) for path in glob(f"{path}*label.nrrd")]
        all_files: List[Path] = [Path(path) for path in glob(f"{path}*.nrrd")]
        sequences: List[Path] = [file for file in all_files if not file in segmentations]

        segmentations.sort(), sequences.sort()

        del all_files

        assert len(segmentations) == len(sequences)
        return sequences, segmentations
    
    def get_dicom_files(self, path: PathLike) -> List[List]:
        """
        This method returns all dicom files.
        """

        dicom_files: List[List] = []

        for (root, _, files) in walk(path):
            for file in files:
                
                if file.endswith(".dcm"):
                    root_path: Path = Path(root)
                    total_path: Path = root_path/ Path(file)

                    if "exvivo" in root.lower():
                        parts: List = total_path.parent.stem.split("_")
                        experiment: str = parts[0].strip("Exp")
                        placement: str = parts[5]
                        time: str = parts[6].split("min")[0]
                        dicom_files.append([str(total_path), "exvivo", experiment, placement, time])
                    
                    if "invivo" in root.lower():
                        parts: List = total_path.parent.stem.split("_")
                        experiment: str = parts[0].strip("Exp")
                        placement: str = "both"
                        time: str = "0"
                        dicom_files.append([str(total_path), "invivo", experiment, placement, time])
        
        return dicom_files

    def read_sequences(self, sequences_in: List[Path]) -> Tuple[List[OrderedDict], List[np.ndarray]]:
        """
        This method takes a list of paths of nrrd sequence files and reads them in
        numpy array format and header format. This method returns a tuple of
        Lists each containing all headers and all sequences.
        """
        headers_out: List[OrderedDict] = []
        sequences_out: List[np.ndarray] = []

        assert len(sequences_in), \
            f"Empty list of sequence files passed..."

        for i, sequence in enumerate(sequences_in):
            # Declare types
            data: np.ndarray
            header: OrderedDict

            # Fill variables and lists
            data, header = nrrd.read(sequence)
            headers_out.append(header)
            sequences_out.append(data)

        return (headers_out, sequences_out)

    def read_segmentations(self, segmentations_in: List[Path]) -> Tuple[List[OrderedDict], List[np.ndarray]]:
        """
        This method takes a list of paths of nrrd segmentation files and reads them in
        numpy array format and header format. This method returns a tuple of
        Lists each containing all headers and all segmentations.
        """
        headers_out: List[OrderedDict] = []
        segmentations_out: List[np.ndarray] = []

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
    
    def create_nrrd(self, DICOM_in: List[Path]) -> List[np.ndarray]:
        """
        Convert list of dicom files in single nrrd file per experiment.
        """
        pass

io = InputOutput()

# sequences, segmentations = io.get_files(path="../ROI/DWI/exp*/")
# print(io.read_sequences(sequences))

io.get_dicom_files(path=r"C:\Users\James\Documents\MRI_data\DWI")
