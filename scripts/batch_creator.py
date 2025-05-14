from pathlib import Path

class BatchCreator:

    def __init__(self, seg_path, seq_path, glob_pattern):
        self.seg_path = Path(seg_path)
        self.seq_path = Path(seq_path)
        self.glob_pattern = glob_pattern

    def create_batch_file(self, batch_file: Path):
        seg_files = list(self.seg_path.glob(self.glob_pattern))
        seq_files = list(self.seq_path.glob(self.glob_pattern))
        seg_files.sort(), seq_files.sort()

        with open(batch_file, "w") as f_out:
            f_out.write("Image,Mask\n")
            for img, msk in zip(seq_files, seg_files):
                f_out.write(f"{img},{msk}\n")

if __name__ == "__main__":
    bc = BatchCreator("../data/processed/segmentations",
                      "../data/processed/nrrds",
                      "T1*exvivo_both*")
    bc.create_batch_file("batch.csv")
