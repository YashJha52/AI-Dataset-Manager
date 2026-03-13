#!/bin/bash

# 1. Define the cleanup function
cleanup() {
    echo -e "\nCaught Ctrl+C! Shutting down gracefully..."
    echo "Stopping MySQL service..."
    brew services stop mysql
    echo "AI Dataset Manager safely stopped."
    exit 0
}

trap cleanup SIGINT

echo "Starting AI Dataset Manager..."

# Start MySQL service
echo "Starting MySQL..."
brew services start mysql

# Wait a few seconds for MySQL to fully boot up
sleep 4

echo "Loading credentials from .env and setting up database..."

# 2. Source the .env file directly (safest method)
if [ -f "backend/.env" ]; then
    source backend/.env
else
    echo "❌ Error: backend/.env file not found!"
    exit 1
fi

# 3. Create DB and run SQL scripts
# If this fails, it will print a clear error in your terminal instead of skipping ahead
MYSQL_PWD="$DB_PASSWORD" mysql -u "$DB_USER" <<EOF
CREATE DATABASE IF NOT EXISTS ai_dataset_manager;
USE ai_dataset_manager;
SOURCE database/schema.sql;
SOURCE database/sample_data.sql; 
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database created and seeded successfully."
else
    echo "❌ MySQL setup failed! Check your credentials in backend/.env."
    exit 1
fi

# Start backend server
echo "Starting Flask backend..."
cd backend
python app.py