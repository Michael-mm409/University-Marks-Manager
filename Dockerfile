# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y <your-system-packages>

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Streamlit (in case not in requirements.txt)
RUN pip install --no-cache-dir streamlit

# Copy the rest of the application code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables for Streamlit (optional, disables CORS/XSRF for local use)
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false

# Run the Streamlit app
CMD ["streamlit", "run", "src/main.py"]
