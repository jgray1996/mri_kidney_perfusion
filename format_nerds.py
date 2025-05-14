from scripts.database import DatabaseHandler
from scripts.experiments import InputOutput
from tqdm import tqdm


db = DatabaseHandler("databases/test_db.db")
io = InputOutput()
all_experiments = db.get_experiments_from_db()

for exp in tqdm(all_experiments):
    imgs = db.get_images_from_experiment(exp)
    imgs = io.sort_images(imgs)
    io.create_nrrd(imgs, exp, "data/processed/nrrds", replace=False)

