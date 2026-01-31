# pull official base image
FROM python:3.13-slim


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

    
# copy requirements file first for better caching
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

COPY . .

# Run the application
CMD ["python", "main.py"]
