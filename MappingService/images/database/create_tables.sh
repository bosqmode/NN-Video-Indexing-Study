#!/bin/sh
FILE=/var/lib/database_mount/database.db
if [ ! -f "$FILE" ]; then
    sqlite3 /database.db < /db_create.sql
fi
