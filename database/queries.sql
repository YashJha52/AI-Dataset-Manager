-- ============================================================
-- queries.sql  — Useful analytical queries for AI Dataset Manager
-- (Updated to leverage VIEWs, FULLTEXT, and Stored Procedure)
-- ============================================================

-- 1. View all datasets with creator name, version count, and best accuracy
SELECT * FROM vw_dataset_summary;

-- 2. Best experiment per dataset (leverages vw_best_experiments VIEW)
SELECT dataset_name, model_name, algorithm, version_number, accuracy, loss
FROM vw_best_experiments
ORDER BY accuracy DESC;

-- 3. Top model by average accuracy
SELECT model_name, algorithm,
       ROUND(AVG(accuracy), 4) AS avg_accuracy,
       COUNT(*)                AS total_runs
FROM vw_best_experiments
GROUP BY model_name, algorithm
ORDER BY avg_accuracy DESC
LIMIT 5;

-- 4. Full-text search for datasets (requires FULLTEXT index)
SELECT dataset_id, dataset_name, description
FROM Datasets
WHERE MATCH(dataset_name, description) AGAINST ('protein' IN NATURAL LANGUAGE MODE);

-- 5. Call stored procedure — get all experiments for dataset #1
CALL GetDatasetExperiments(1);

-- 6. Version history with user names (handles NULL user for trigger-created logs)
SELECT v.version_number, c.change_description, c.change_date,
       IFNULL(u.name, 'System (Auto)') AS changed_by
FROM Dataset_Changes_Log c
JOIN  Dataset_Versions v ON c.version_id = v.version_id
LEFT JOIN Users u         ON c.changed_by = u.user_id
WHERE v.dataset_id = 1
ORDER BY c.change_date DESC;

-- 7. Experiments that used each dataset version
SELECT d.dataset_name, v.version_number, m.model_name, e.accuracy
FROM Experiments e
JOIN Models m           ON e.model_id   = m.model_id
JOIN Dataset_Versions v ON e.version_id = v.version_id
JOIN Datasets d         ON v.dataset_id = d.dataset_id
ORDER BY d.dataset_name, v.version_number;

-- 8. Dashboard aggregate stats (used by /stats endpoint)
SELECT
    (SELECT COUNT(*) FROM Datasets)           AS total_datasets,
    (SELECT COUNT(*) FROM Dataset_Versions)   AS total_versions,
    (SELECT COUNT(*) FROM Experiments)        AS total_experiments,
    (SELECT COUNT(*) FROM Models)             AS total_models,
    (SELECT COUNT(*) FROM Users)              AS total_users,
    (SELECT ROUND(AVG(accuracy), 4) FROM Experiments WHERE accuracy IS NOT NULL) AS avg_accuracy;