from scripts.database import DatabaseHandler
from scripts.experiments import InputOutput

db = DatabaseHandler("databases/test_db.db")
all_experiments = db.get_experiments_from_db()
# io = InputOutput()

