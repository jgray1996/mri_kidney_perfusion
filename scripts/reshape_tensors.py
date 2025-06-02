import nrrd
from sys import argv
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm


batch_file = argv[1]
output_directory = Path(argv[2])
batch_file_out = Path(argv[3])

batch = pd.read_csv(batch_file)

output_files = []

for file in tqdm(batch.Image):
    name = Path(file).name
    data, header = nrrd.read(file)
    tensor_reordered = np.transpose(data, (1, 2, 0))
    nrrd.write(str(output_directory/name), tensor_reordered)
    output_files.append(Path('.').cwd()/output_directory/name)

batch["Image"] = output_files
batch.to_csv(batch_file_out, index=False)