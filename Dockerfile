# Set the baseimage
FROM python:3.12-slim

# listen to port 5500
EXPOSE 5500/tcp 

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to working directory
COPY requirements.txt . 

# Install build dependencies
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content to local src directory to working directory
COPY . .

# Specify command to run on container start
CMD ["python", "./application.py"]