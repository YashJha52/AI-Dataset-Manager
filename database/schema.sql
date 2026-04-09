CREATE DATABASE IF NOT EXISTS ai_dataset_manager;
USE ai_dataset_manager;

-- ========================
-- Users Table
-- ========================
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- ========================
-- Datasets Table
-- ========================
CREATE TABLE IF NOT EXISTS Datasets (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_name VARCHAR(150) NOT NULL,
    description TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES Users(user_id)
);

-- ========================
-- Dataset Versions
-- ========================
CREATE TABLE IF NOT EXISTS Dataset_Versions (
    version_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT,
    version_number INT,
    storage_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES Datasets(dataset_id)
);

-- ========================
-- Models Table
-- ========================
CREATE TABLE IF NOT EXISTS Models (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100),
    algorithm VARCHAR(100)
);

-- ========================
-- Experiments Table
-- ========================
CREATE TABLE IF NOT EXISTS Experiments (
    experiment_id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT,
    version_id INT,
    accuracy FLOAT,
    loss FLOAT,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES Models(model_id),
    FOREIGN KEY (version_id) REFERENCES Dataset_Versions(version_id)
);

-- ========================
-- Dataset Changes Log
-- ========================
CREATE TABLE IF NOT EXISTS Dataset_Changes_Log (
    change_id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT,
    changed_by INT,
    change_description TEXT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES Dataset_Versions(version_id),
    FOREIGN KEY (changed_by) REFERENCES Users(user_id)
);

-- ========================
-- INDEXES — Prevent full table scans on every JOIN/WHERE
-- ========================
CREATE INDEX IF NOT EXISTS idx_versions_dataset    ON Dataset_Versions(dataset_id);
CREATE INDEX IF NOT EXISTS idx_experiments_version ON Experiments(version_id);
CREATE INDEX IF NOT EXISTS idx_experiments_model   ON Experiments(model_id);
CREATE INDEX IF NOT EXISTS idx_log_version         ON Dataset_Changes_Log(version_id);
CREATE INDEX IF NOT EXISTS idx_datasets_created_by ON Datasets(created_by);

-- ========================
-- FULLTEXT INDEX — Native MySQL full-text search
-- ========================
ALTER TABLE Datasets ADD FULLTEXT INDEX IF NOT EXISTS ft_dataset_search (dataset_name, description);

-- ========================
-- VIEW: Dataset Summary
-- Aggregates version count, experiment count, and best accuracy per dataset
-- ========================
CREATE OR REPLACE VIEW vw_dataset_summary AS
SELECT
    d.dataset_id,
    d.dataset_name,
    d.description,
    u.name              AS created_by_name,
    d.created_at,
    COUNT(DISTINCT v.version_id)     AS total_versions,
    COUNT(DISTINCT e.experiment_id)  AS total_experiments,
    ROUND(MAX(e.accuracy), 4)        AS best_accuracy
FROM Datasets d
LEFT JOIN Users u              ON d.created_by  = u.user_id
LEFT JOIN Dataset_Versions v   ON d.dataset_id  = v.dataset_id
LEFT JOIN Experiments e        ON v.version_id  = e.version_id
GROUP BY d.dataset_id, d.dataset_name, d.description, u.name, d.created_at;

-- ========================
-- VIEW: Best Experiments
-- Joins experiments with model and dataset info for analytics queries
-- ========================
CREATE OR REPLACE VIEW vw_best_experiments AS
SELECT
    e.experiment_id,
    d.dataset_name,
    m.model_name,
    m.algorithm,
    v.version_number,
    ROUND(e.accuracy, 4) AS accuracy,
    ROUND(e.loss, 4)     AS loss,
    e.run_date
FROM Experiments e
JOIN Dataset_Versions v ON e.version_id = v.version_id
JOIN Datasets d         ON v.dataset_id = d.dataset_id
JOIN Models m           ON e.model_id   = m.model_id;

-- ========================
-- TRIGGER: Auto-log when a new version is inserted
-- Replaces app-level logging for system-generated version entries
-- ========================
DROP TRIGGER IF EXISTS trg_after_version_insert;
DELIMITER //
CREATE TRIGGER trg_after_version_insert
AFTER INSERT ON Dataset_Versions
FOR EACH ROW
BEGIN
    INSERT INTO Dataset_Changes_Log (version_id, changed_by, change_description)
    VALUES (
        NEW.version_id,
        NULL,
        CONCAT('Version ', NEW.version_number, ' created. File: ', IFNULL(NEW.storage_path, 'N/A'))
    );
END //
DELIMITER ;

-- ========================
-- STORED PROCEDURE: Get all experiments for a specific dataset
-- ========================
DROP PROCEDURE IF EXISTS GetDatasetExperiments;
DELIMITER //
CREATE PROCEDURE GetDatasetExperiments(IN p_dataset_id INT)
BEGIN
    SELECT
        e.experiment_id,
        m.model_name,
        m.algorithm,
        v.version_number,
        ROUND(e.accuracy, 4) AS accuracy,
        ROUND(e.loss, 4)     AS loss,
        e.run_date
    FROM Experiments e
    JOIN Models m           ON e.model_id   = m.model_id
    JOIN Dataset_Versions v ON e.version_id = v.version_id
    WHERE v.dataset_id = p_dataset_id
    ORDER BY e.run_date DESC;
END //
DELIMITER ;