from pathlib import Path
from glob import glob
from tqdm import tqdm

files = glob("./data/processed/nrrds/*_ASL_*")

for file in tqdm(files):
    file = Path(file)
    name = file.name
    parts = file.stem.split('_')
    new_name = parts[3] + '_' + parts[0] + "_" + parts[1] + '_' + parts[-1] + "_" + parts[2] + ".nrrd"
    rename = file.parent/new_name
    file.rename(rename)