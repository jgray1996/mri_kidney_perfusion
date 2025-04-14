CREATE TABLE IF NOT EXISTS Dicom (
    file_path TEXT UNIQUE NOT NULL,
    vivo TEXT NOT NULL,
    experiment TEXT NOT NULL,
    placement TEXT NOT NULL,
    time_point TEXT NOT NULL
);