# pull official base image
FROM python:3.11.4-slim-buster AS base

# set work directory
WORKDIR /usr/src/server

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN echo cat /etc/os-release
# install system dependencies

RUN apt-get update && apt-get install -y netcat sudo && apt update 

RUN apt-get -y install git curl gnupg apt-transport-https ca-certificates software-properties-common 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN curl https://packages.microsoft.com/config/debian/10/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN apt install unixodbc -y
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y libgssapi-krb5-2

RUN apt-get update
RUN apt-get -y install git curl gnupg apt-transport-https ca-certificates software-properties-common
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN curl https://packages.microsoft.com/config/debian/10/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN apt install unixodbc -y
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y libgssapi-krb5-2

# install dependencies
RUN pip install --upgrade pip
COPY . .
COPY ./requirements.txt .

RUN pip install -r requirements.txt


RUN apt-get update -yq \
    && apt-get -yq install curl gnupg ca-certificates \
    && curl -L https://deb.nodesource.com/setup_18.x | bash \
    && apt-get update -yq \
    && apt-get install -yq \
        nodejs
RUN apt install unixodbc -y

# create directory for the app files
RUN mkdir -p /usr/src/server/app/files/bqkeys
RUN mkdir -p /usr/src/server/app/files/sqlite

# Create non-root user
RUN groupadd -r turbular && useradd -r -g turbular turbular
RUN chown -R turbular:turbular /usr/src/server/app/files


# Copy project
COPY . .

# Development target
FROM base as dev
CMD ["uvicorn", "app.main:app", "--log-level", "debug", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--reload" ]

# Production target
FROM base as prod

# Switch to non-root user
USER turbular

# Create startup script
COPY scripts/start-prod.sh /usr/src/server/start-prod.sh
RUN chmod +x /usr/src/server/start-prod.sh

# Run with gunicorn in production
CMD ["/usr/src/server/start-prod.sh"]
