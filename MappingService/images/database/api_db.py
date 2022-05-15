from crypt import methods
import sqlite3
import json
from flask import Flask, request, jsonify
import time
import datetime
import os
from os.path import exists
import shutil

DATABASE = 'database.db'

time.sleep(1)
if not exists(os.environ['DATABASE_DIR']):
    time.sleep(1)
    shutil.copyfile('/database.db', os.environ['DATABASE_DIR'])

app = Flask(__name__)

def query_to_dict(query: str, conn: sqlite3.Connection, cur: sqlite3.Cursor=None) -> dict:
    """
    Basic query interaction, executes query, converts result to dict and returns it.
    """
    conn.row_factory = sqlite3.Row
    if cur is None:
        cur = conn.cursor()
    cur.execute(query)
    res = cur.fetchall()
    res = [dict(row) for row in res]
    return res

@app.route("/test", methods=['GET'])
def test():
    return "test"

@app.route("/files", methods=['GET'])
def get_files():
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict('SELECT * FROM tFiles', conn)
        return jsonify(results=res)

@app.route("/detections/fileid", methods=['GET'])
def get_detections_by_fileid():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tDetections WHERE file_id == "{int(data["file_id"])}"', conn)
        return jsonify(results=res)

@app.route("/detections/filepath", methods=['GET'])
def get_detections_by_filepath():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tDetections\
                                INNER JOIN tFiles\
                                ON tDetections.file_id == tFiles.id\
                                WHERE tFiles.filepath == "{data["filepath"]}"', conn)
        return jsonify(results=res)

@app.route("/file/id", methods=['GET'])
def get_file_by_id():
    """
    get file by id
    """
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tFiles WHERE id == "{int(data["id"])}"', conn)
        return jsonify(results=res)

@app.route("/file/path", methods=['GET'])
def file_status_get():
    """
    Gets file status by supplying filepath
    """
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tFiles WHERE filepath == "{data["filepath"]}"', conn)
        return jsonify(results=res)


@app.route("/file/status", methods=['POST'])
def file_status_update():
    """
    Called when a new file is discovered
    """
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = query_to_dict(f'SELECT * FROM tFiles WHERE filepath == "{data["filepath"]}"', conn, cur)

        # file does not exists yet
        if len(res) <= 0:
            cur.execute(f'INSERT INTO tFiles (filepath, last_searched, last_modified) VALUES (\"{data["filepath"]}\", 0, {data["last_modified"]})')
            conn.commit()
            return "file added"
        else:
            if 'last_searched' in data:
                cur.execute(f'UPDATE tFiles SET last_searched = {data["last_searched"]}, last_modified = {data["last_modified"]} WHERE filepath = \"{data["filepath"]}\"')
            else:
                cur.execute(f'UPDATE tFiles SET last_modified = {data["last_modified"]} WHERE filepath = \"{data["filepath"]}\"')
            conn.commit()
            return "file updated"
    return -1

@app.route("/file/removed", methods=['DELETE'])
def file_removed():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'DELETE FROM tFiles WHERE filepath == "{data["filepath"]}"')
        conn.commit()
        return "removed"

@app.route("/models", methods=['GET'])
def get_all_models():
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict('SELECT * FROM tModels', conn)
        return jsonify(results=res)

@app.route("/model/name", methods=['GET'])
def get_model_by_name_and_version():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tModels WHERE model_name == "{data["model_name"]}" AND version_string == "{data["version_string"]}"', conn)
        return jsonify(results=res)

@app.route("/model/add", methods=['POST'])
def add_model():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = query_to_dict(f'SELECT * FROM tModels WHERE model_name == "{data["model_name"]}" AND version_string == "{data["version_string"]}"', conn, cur)
        if len(res) <= 0:
            cur.execute(f'INSERT INTO tModels (model_name, description_text, added_timestamp, version_string) VALUES (\"{data["model_name"]}\", \"{data["description_text"]}\", "{int(data["added_timestamp"])}", \"{data["version_string"]}\")')
            return "added"
        else:
            cur.execute(f'UPDATE tModels SET description_text = "{data["description_text"]}" WHERE model_name = \"{data["model_name"]}\"')
            return "updated"

@app.route("/detections/add", methods=['POST'])
def add_detection():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'INSERT INTO tDetections (video_ts, category, model, file_id) VALUES ("{int(data["video_ts"])}", "{data["category"]}", "{int(data["model"])}", "{int(data["file_id"])}")')
        return "added"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)