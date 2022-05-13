FROM alpine:3.14
RUN apk update && apk upgrade
RUN apk add --no-cache sqlite~=3.35.5-r0

ENV PYTHONUNBUFFERED=1
ENV DATABASE_DIR=/var/lib/database_mount/database.db
ENV FLASK_APP=/api_db.py
ENV FLASK_ENV=development

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install --no-cache Flask

COPY db_create.sql /db_create.sql
COPY api_db.py /api_db.py
COPY create_tables.sh /create_tables.sh

RUN chmod 777 /create_tables.sh
WORKDIR /var/lib/database_mount


RUN ["/bin/sh", "/create_tables.sh"]

ENTRYPOINT ["python3", "-m", "flask", "run", "--host=0.0.0.0"]