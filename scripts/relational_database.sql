CREATE TABLE IF NOT EXISTS Dicom (
    file_path TEXT UNIQUE NOT NULL,
    vivo TEXT NOT NULL,
    seq TEXT NOT NULL,
    experiment INT NOT NULL,
    placement TEXT NOT NULL,
    time_point INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Nrrd(
    file_path TEXT UNIQUE NOT NULL,
    file_path_segmentation TEXT,
    vivo TEXT NOT NULL,
    seq TEXT NOT NULL,
    experiment INT NOT NULL,
    placement TEXT NOT NULL,
    time_point INT NOT NULL
);