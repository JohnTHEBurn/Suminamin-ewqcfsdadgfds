FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl unzip && apt-get clean

# Install ngrok
RUN curl -Lo /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip && \
    unzip -o /tmp/ngrok.zip -d /usr/local/bin && \
    rm /tmp/ngrok.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyngrok

# Copy application code
COPY . .

# Create sites directory
RUN mkdir -p sites

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for Flask server
EXPOSE 5000

# Create entry script
RUN echo '#!/bin/bash\n\
if [ -n "$NGROK_AUTHTOKEN" ]; then\n\
  echo "Configuring ngrok..."\n\
  ngrok config add-authtoken $NGROK_AUTHTOKEN\n\
  python setup_ngrok.py &\n\
  sleep 5\n\
fi\n\
python run.py\n\
' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Run the application
CMD ["/app/docker-entrypoint.sh"]