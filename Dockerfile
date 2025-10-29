FROM python:3.11-slim

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
RUN mkdir /django

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Remove unused packages from the container
RUN apt-get -y autoremove
WORKDIR /django

# Copy requirements and install dependencies
ADD ./requirements /django/requirements
RUN pip3 install -r /django/requirements/development.txt

# Copy project files and entrypoint.sh script
COPY ./docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Add user just like your example
RUN adduser restapi

# Give ownership of /django to the non-root user
RUN chown -R restapi:restapi /django

# Switch to restapi user
USER restapi
