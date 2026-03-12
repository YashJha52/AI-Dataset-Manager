USE ai_dataset_manager;

-- Insert Users
INSERT INTO Users (name, email)
VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com');

-- Insert Dataset
INSERT INTO Datasets (dataset_name, description, created_by)
VALUES
('Brain Tumor MRI', 'MRI images dataset', 1);

-- Insert Dataset Version
INSERT INTO Dataset_Versions (dataset_id, version_number, storage_path)
VALUES
(1, 1, '/datasets/dataset1/v1');

-- Insert Model
INSERT INTO Models (model_name, algorithm)
VALUES
('CNN_Model', 'CNN'),
('ResNet_Model', 'ResNet');

-- Insert Experiment
INSERT INTO Experiments (model_id, version_id, accuracy, loss)
VALUES
(1, 1, 0.86, 0.20);

-- Insert Change Log
INSERT INTO Dataset_Changes_Log (version_id, changed_by, change_description)
VALUES
(1, 2, 'Removed corrupted images');