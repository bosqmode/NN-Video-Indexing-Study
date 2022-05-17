FROM ubuntu:focal
RUN apt-get update && yes | apt-get upgrade
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install nano
#RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache numpy
RUN pip install --no-cache tensorflow
#RUN pip install --no-cache opencv-python
RUN pip install --no-cache opencv-python-headless
RUN pip install --no-cache requests


ENV DB_ENDPOINT=http://database:5000
ENV MODEL='0'

COPY VideoScanner /VideoScanner

COPY label.py /label.py
RUN chmod 0644 /label.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod 0644 /entrypoint.sh

ENV DB_ENDPOINT=http://database:5000

CMD ["/bin/bash", "/entrypoint.sh"]