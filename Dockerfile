FROM python:3.13-slim
LABEL maintainer="AIwolfie <https://github.com/AIwolfie/Fenrir>"
LABEL author="AIwolfie"

# Install system dependencies including Tor
RUN apt-get update && apt-get install -y \
    tor \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Setup Tor entrypoint
RUN echo '#!/bin/bash\n\
service tor start\n\
echo "Waiting for Tor to bootstrap..."\n\
sleep 5\n\
exec python main.py "$@"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default mount point for databases and reports
VOLUME ["/app/storage", "/app/reports"]

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--web", "--host", "0.0.0.0", "--port", "8000"]
