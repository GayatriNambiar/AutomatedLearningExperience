FROM ubuntu:latest
MAINTAINER Gayatri Nambiar "gayatri@getcaila.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /src
WORKDIR /src
RUN apt-get -y install python-pip libpq-dev python-dev && \
    pip install psycopg2 
RUN pip install -r /src/requirements.txt
ENTRYPOINT "python"
CMD "application.py"
