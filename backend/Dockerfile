FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/media/uploads/csv /app/media/uploads/pdf /app/media/exports/pptx /app/staticfiles

# Expose port
EXPOSE 8000

# Default command (overridden in docker-compose.yml)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

