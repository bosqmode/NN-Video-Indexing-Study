FROM alpine:3.14
RUN apk update && apk upgrade
RUN apk add --no-cache sqlite~=3.35.5-r0

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install --no-cache Flask

WORKDIR /var/lib/database_mount
# ENTRYPOINT [ "sqlite3" ]