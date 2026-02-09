# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disc
# PYTHONUNBUFFERED: Ensures that python output is sent straight to terminal without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# These are often required for building Python packages or handling databases
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We copy requirements.txt first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . /app/

# Collect static files
# This is required for Django to serve CSS, JS, and images in production
RUN python manage.py collectstatic --no-input

# Expose the port that the app runs on
# Render uses port 10000 by default
EXPOSE 10000

# Start the application using Gunicorn
# Replace 'final_project' with the name of your Django project directory (containing wsgi.py)
CMD ["gunicorn", "final_project.wsgi:application", "--bind", "0.0.0.0:10000"]
