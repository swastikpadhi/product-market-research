#!/bin/bash

# Read environment variables from backend .env file
export REACT_APP_BACKEND_PORT=$(grep '^PORT=' ../backend/.env | cut -d'=' -f2)
export REACT_APP_ENVIRONMENT=$(grep '^ENVIRONMENT=' ../backend/.env | cut -d'=' -f2)

# Start React development server
react-scripts start
