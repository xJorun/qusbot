# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create data files directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variable
ENV PORT=5000

# Run the application
CMD ["python", "main.py"] 
