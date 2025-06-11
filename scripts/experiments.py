from typing import OrderedDict
from os import PathLike, walk
from shutil import copyfile
from pathlib import Path, PurePath
import numpy as np
import nrrd
from pydicom import dcmread, FileDataset
import re
from tqdm import tqdm
import sys

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

    def get_DICOM_files_ASL(self, path: PathLike) -> list[list]:

        names = []
        for (root, _, files) in walk(path):
            root = PurePath(root)
            for file in files:
                if file.endswith(".dcm"):
                    file = PurePath(file)
                    path = root/file
                    parts = root.parts
                    meta = parts[-1].split()[0].split('_')
                    experiment = meta[0].lower().strip("exp")
                    vivo = meta[1].lower()
                    if vivo.startswith("ex"):
                        placement = meta[2].lower()
                        if placement.startswith('r'):
                            placement = "right"
                        else:
                            placement = "left"
                        time = meta[3].lower().strip("min")
                    if vivo.startswith("in"):
                        placement = "both"
                        time = "-10"
                    names.append([str(path), "ASL", experiment, time, vivo, placement])
        return names
    
    def get_dicom_files_T2star(self, path: PathLike) -> list[list]:
        names = []

        for (root, _, files) in walk(path):
            if "cor " in root.lower():
                root = PurePath(root)
                for file in files:
                    if file.endswith(".dcm"):
                        file = PurePath(file)
                        path = root/file
                        parts = path.parts
                        vivo = parts[2].lower()
                        print(parts)
        return names


    def get_nrrd_files_DWI(self, path: PathLike) -> list[list]:
        """
        This function collects all pre processed nrrd files and formats
        them with meta data.
        """

        names: list = []
        for (root, _, files) in walk(path):
            for file in files:
                if file.endswith("_b0.nrrd"):
                    root: PurePath = PurePath(root)
                    file: PurePath = PurePath(file)
                    parts: list = root.parts
                    last_encoding: list = parts[-1].split('_')[1:3]
                    full_path: PurePath = root/file
                    vivo: str = parts[-2]
                    sequence: str = "DWI"
                    time: str = last_encoding[-1].strip("MIN")
                    experiment: str = parts[-3].split()[1]
                    if last_encoding[0].startswith("R"):
                        placement: str = "right"
                    elif last_encoding[0].startswith("L"):
                        placement: str = "left"
                    else:
                        vivo: str = "invivo"
                        placement: str = "both"
                        time: str = "-10"
                    name: list = [full_path, sequence, experiment, time, vivo.lower(), placement]
                    names.append(name)
        return names
    
    def move_and_rename(self, names: list[list], target: PathLike) -> None:
        """
        Moves nrrds and encodes the metadata in the filename
        """

        for name in tqdm(names):
            f_in: Path = name[0]
            target: Path = Path(target)
            f_out: str = '_'.join(name[1:]) + ".nrrd"
            target_f_out: Path = target/f_out
            copyfile(f_in, target_f_out)

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

    
    def create_nrrd(self, DICOM_in: list[Path], 
                    parameters: tuple, 
                    out_path: Path,
                    replace=True) -> None:
        """
        Convert list of dicom files in single nrrd file per experiment.
        """
        volume: list = []
        exp, seq, time, vivo, place = parameters
        filename: Path = Path(f"{seq}_{exp}_{time}_{vivo}_{place}.nrrd")
        f_out: Path = Path(out_path) / filename
        if not replace:
            if f_out.exists():
                return

        for img in DICOM_in:
            dcm: FileDataset = dcmread(img)
            volume.append(dcm.pixel_array)

        # catch that odd duck and skip it
        try:
            vol: np.ndarray = np.array(self.fix_volume_shape(volume))
        except ValueError:
            print(parameters)
            return

        nrrd.write(str(f_out), vol)
        pass


    def read_nrrds(self, path: PathLike) -> tuple[list[Path], list[Path]]:
        """
        This method takes a path of nrrd segmentation files and reads them in
        numpy array format and header format. Returns a tuple of lists containing
        all sequences and all segmentations.
        """
        all_files: list[Path] = []
        
        for root, dirs, files in walk(path):
            for file in files:
                if file.endswith(".nrrd"):
                    all_files.append(Path(root) / file)
        
        segmentations: list[Path] = [file for file in all_files if "seg" in file.name]

        if not segmentations:
            segmentations: list[Path] = [file for file in all_files if "label" in file.name]

        sequences: list[Path] = [file for file in all_files if file not in segmentations]

        segmentations.sort(), sequences.sort()

        return (sequences, segmentations)


    def nrrd_to_matrix(self, nrrds: list[Path]) -> np.ndarray:
        """
        This method converts a list of paths of nrrd files to a 3d array.
        """
        headers, sequences = self.read_sequences(nrrds)
        return headers, sequences
    
    def fix_volume_shape(self, volume: list[np.ndarray]) -> list[np.ndarray]:
        """
        This module fixes the shape of a passed volume if the
        dimensions are not n x n and certain orientations are twisted
        """
        def twist(vol: np.ndarray):
            shape: tuple = vol.shape
            x: int
            y: int
            x, y = shape[0], shape[1]
            if y > x:
                vol: np.ndarray = np.transpose(vol, (1, 0, 2))
            return vol

        return [twist(vol) for vol in volume]
    
    def sort_images(self, images: list[Path]) -> list[Path]:
        """
        Sort Images so nrrd volumes are sorted by z axis
        """
        images: list = [img[0] for img in images]
        images.sort()
        return images
    


if __name__ == "__main__":
    io = InputOutput()
    io.get_dicom_files_T2star("MRI_data/T2star")
    # io.create_nrrd()
    # names = io.get_nrrd_files_DWI(path="MRI_data/b0")
    # io.move_and_rename(names, "data/processed/nrrds")
