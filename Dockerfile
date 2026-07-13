FROM python:3.13-slim

WORKDIR /app

# Copy bot handler
COPY bot_handler.py .

# Create non-root user
RUN useradd -m -s /bin/bash botuser
USER botuser

CMD ["python3", "-u", "bot_handler.py"]
