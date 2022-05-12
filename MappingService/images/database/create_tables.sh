#!/bin/sh
echo $DATABASE_DIR
sqlite3 $DATABASE_DIR < /db_create.sql