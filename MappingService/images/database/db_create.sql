BEGIN; 
PRAGMA foreign_keys = ON;

CREATE TABLE  tFiles(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filepath TEXT,
    last_searched TIMESTAMP DEFAULT 0 NOT NULL,
    last_modified TIMESTAMP DEFAULT 0 NOT NULL,
    file_discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE tModels(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    description_text TEXT,
    added_timestamp TIMESTAMP,
    version_string TEXT NOT NULL
);

CREATE TABLE tDetections(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_ts TIMESTAMP NOT NULL,
    category TEXT NOT NULL,
    model INTEGER NOT NULL,
    file_id INTEGER,
    FOREIGN KEY (file_id)
    REFERENCES tFiles (file_id)
        ON UPDATE SET NULL
        ON DELETE SET NULL
);
COMMIT;