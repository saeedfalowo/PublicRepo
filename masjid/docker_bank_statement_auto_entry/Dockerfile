FROM ubuntu:latest

RUN apt update
RUN apt install default-jdk -y

RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip install tabula-py
RUN pip install psycopg2-binary

WORKDIR /usr/app/src

COPY . ./

CMD ["python3", "./main.py"]
