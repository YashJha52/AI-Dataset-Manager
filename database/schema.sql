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
CREATE TABLE Datasets (
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
CREATE TABLE Dataset_Versions (
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
CREATE TABLE Models (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100),
    algorithm VARCHAR(100)
);

-- ========================
-- Experiments Table
-- ========================
CREATE TABLE Experiments (
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
CREATE TABLE Dataset_Changes_Log (
    change_id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT,
    changed_by INT,
    change_description TEXT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES Dataset_Versions(version_id),
    FOREIGN KEY (changed_by) REFERENCES Users(user_id)
);