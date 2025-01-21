# Use an official Python runtime as a parent image
FROM python:3.13-slim

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

# Create a virtual environment
RUN python -m venv /app/venv

# Set environment variable to use the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies within the virtual environment
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the default command to run the application within the virtual environment
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
