-- View all datasets
SELECT * FROM Datasets;

-- View dataset versions
SELECT dataset_name, version_number
FROM Datasets
JOIN Dataset_Versions
ON Datasets.dataset_id = Dataset_Versions.dataset_id;

-- View experiments with models
SELECT model_name, accuracy, loss
FROM Experiments
JOIN Models
ON Experiments.model_id = Models.model_id;

-- Best model accuracy
SELECT model_name, MAX(accuracy) AS best_accuracy
FROM Experiments
JOIN Models
ON Experiments.model_id = Models.model_id
GROUP BY model_name;

-- Experiments using a dataset
SELECT dataset_name, accuracy
FROM Experiments
JOIN Dataset_Versions
ON Experiments.version_id = Dataset_Versions.version_id
JOIN Datasets
ON Dataset_Versions.dataset_id = Datasets.dataset_id;