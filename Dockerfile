# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container at /app
COPY . /app

# Install the necessary dependencies
RUN pip install .

# Run the application
CMD ["python", "-m", "hdd_lifetime_prediction.app.app"]
