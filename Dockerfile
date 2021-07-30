FROM ubuntu:latest
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3 -y && apt-get install python3-pip -y
COPY . .
RUN pip3 install -r requirements.txt
CMD python3 bot.py
