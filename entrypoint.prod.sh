#!/bin/bash

# Start NGINX
systemctl start nginx

# Start PostgreSQL
pg_ctlcluster 15 main start

# Function to check PostgreSQL readiness
check_postgres_ready() {
    until pg_isready -h localhost -p 5432; do
        echo "Waiting for PostgreSQL to start..."
        sleep 1
    done
}

# Check PostgreSQL readiness
check_postgres_ready

# Initialize PostgreSQL database
sudo -u postgres psql -c "CREATE USER $POSTGRES_USER WITH LOGIN PASSWORD '$POSTGRES_PASSWORD' CREATEDB CREATEROLE SUPERUSER;"
sudo -u postgres psql -c "ALTER USER $POSTGRES_USER SET ROLE $POSTGRES_USER;"
sudo -u postgres psql -c "CREATE DATABASE $POSTGRES_DB;"

# Start the application
gunicorn manage:app -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind 0.0.0.0:5000 --reload
