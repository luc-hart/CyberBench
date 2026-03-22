# Use slim Python 3.12 base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all project files into container
COPY . /app

# Install curl (needed to install uv)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies from uv.lock
RUN uv sync

# Expose Flask port
EXPOSE 5000

# Run Flask app inside uv environment
ENV PYTHONPATH="/app:${PYTHONPATH}"
CMD ["uv", "run", "python", "ui/ui.py"]