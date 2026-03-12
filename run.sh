#!/bin/bash

echo "Starting AI Dataset Manager..."

# Start MySQL service
echo "Starting MySQL..."
brew services start mysql

# Wait a few seconds for MySQL to start
sleep 3

# Create database if it doesn't exist
echo "Setting up database..."

mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS ai_dataset_manager;
USE ai_dataset_manager;
SOURCE database/schema.sql;
SOURCE database/sample_data.sql;
EOF

echo "Database ready."

# Start backend server
echo "Starting Flask backend..."

cd backend
python app.py