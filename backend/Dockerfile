# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies (as root)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (HF Spaces best practice)
RUN useradd -m -u 1000 user

# Set PATH for user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY --chown=user ./requirements.txt requirements.txt

# Switch to non-root user
USER user

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY --chown=user . /app

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=7860

# Expose port (HF Spaces requires port 7860)
EXPOSE 7860

# Run the Flask application
# HF Spaces requires the app to listen on port 7860
CMD python app.py
