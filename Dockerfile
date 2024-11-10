# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make sure the start.sh script is executable
RUN chmod +x /app/start.sh

# Command to run the start script
CMD ["/app/start.sh"]
