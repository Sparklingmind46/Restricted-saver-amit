# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies (including gcc) needed to build some Python packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
COPY requirements.txt /app/

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that your app will run on
EXPOSE 8000

# Run health check file and bot
CMD ["python", "health_check.py", "&", "python", "main.py"]
