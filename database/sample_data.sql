USE ai_dataset_manager;

-- Insert Users (Forcing IDs 1 and 2)
INSERT IGNORE INTO Users (user_id, name, email)
VALUES
(1, 'Alice', 'alice@example.com'),
(2, 'Bob', 'bob@example.com');

-- Insert Dataset (Forcing ID 1)
INSERT IGNORE INTO Datasets (dataset_id, dataset_name, description, created_by)
VALUES
(1, 'Brain Tumor MRI', 'MRI images dataset', 1);

-- Insert Dataset Version (Forcing ID 1)
INSERT IGNORE INTO Dataset_Versions (version_id, dataset_id, version_number, storage_path)
VALUES
(1, 1, 1, '/datasets/dataset1/v1');

-- Insert Model (Forcing IDs 1 and 2)
INSERT IGNORE INTO Models (model_id, model_name, algorithm)
VALUES
(1, 'CNN_Model', 'CNN'),
(2, 'ResNet_Model', 'ResNet');

-- Insert Experiment (Forcing ID 1)
INSERT IGNORE INTO Experiments (experiment_id, model_id, version_id, accuracy, loss)
VALUES
(1, 1, 1, 0.86, 0.20);

-- Insert Change Log (Forcing ID 1)
INSERT IGNORE INTO Dataset_Changes_Log (change_id, version_id, changed_by, change_description)
VALUES
(1, 1, 2, 'Removed corrupted images');