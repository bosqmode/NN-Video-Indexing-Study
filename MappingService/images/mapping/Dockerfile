FROM alpine:3.14
RUN apk update && apk upgrade
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install --no-cache requests

ENV SEARCH_ROOT=/home/bosqnux/Koodit/Oppari/data/testvideos
ENV DB_ENDPOINT=http://database:5000

COPY search.py /search.py
COPY crontabs /etc/crontabs/root

#RUN [ "crond", "start" ]
#ENTRYPOINT [ "crond", "start" ]
CMD ["crond", "-f", "-l", "2"]