# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        portaudio19-dev \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Define the default command to run the application
# Adjust this command based on your framework (e.g., FastAPI with Uvicorn)
CMD ["uvicorn", "test-chat.main:app", "--host", "0.0.0.0", "--port", "8080"]
