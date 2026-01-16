FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Validate imports to catch path errors early
RUN python -c "from modules.ideas_extractor import IdeasExtractor; from modules.metrics_collector import MetricsCollector; from modules.llm_client import create_llm_client; from modules.idea_collector import IdeaCollector; print('✅ All imports validated successfully')" || (echo "❌ Import failed: wrong path in main.py or modules. Check imports!" && exit 1)

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



