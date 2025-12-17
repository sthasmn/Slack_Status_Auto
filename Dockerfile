# Use a lightweight Python image
FROM python:3.11-slim

# Set timezone
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY sync_bot.py .

# Create directory for config volume
RUN mkdir config

# Run the script
CMD ["python", "-u", "sync_bot.py"]