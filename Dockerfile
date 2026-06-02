# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies into the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image - Copy app and dependencies
FROM python:3.11-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user and a data directory
RUN addgroup --system nonroot && \
    adduser --system --ingroup nonroot nonroot && \
    mkdir -p /data && \
    chown -R nonroot:nonroot /data

# Copy the application code and give ownership to the nonroot user
COPY --chown=nonroot:nonroot . .

# Now switch to the nonroot user
USER nonroot

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables for Flask and the Database
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV DATABASE_URL=sqlite:////data/events.db

# Set the command to run, initializing the DB first
CMD ["sh", "-c", "flask init-db && flask run"]
