from crypt import methods
import sqlite3
import json
from flask import Flask, request, jsonify
import time
import datetime
import os

DATABASE = 'database.db'

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

@app.route("/statuses", methods=['GET'])
def get_statuses():
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict('SELECT * FROM tStatus', conn)
        return jsonify(results=res)

@app.route("/detections", methods=['GET'])
def get_detections():
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict('SELECT * FROM tDetections', conn)
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

@app.route("/file/status", methods=['GET'])
def file_status_get():
    """
    Gets file status by supplying file_id
    """
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        res = query_to_dict(f'SELECT * FROM tStatus WHERE file_id == "{int(data["file_id"])}"', conn)
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
            cur.execute(f'INSERT INTO tFiles (filepath) VALUES (\"{data["filepath"]}\")')
            conn.commit()
            res = query_to_dict(f'SELECT * FROM tFiles WHERE filepath == "{data["filepath"]}"', conn, cur)
            cur.execute(f'INSERT INTO tStatus (file_id, last_searched, model) VALUES ({res[0]["id"]}, 0, "none")')
            conn.commit()
            return 200
        else:
            return 201
        # file exists, update tStatus
        # else:
        #     res = query_to_dict(f'SELECT * FROM tStatus WHERE file_id == "{res[0]["id"]}"', conn, cur)
        #     cur.execute(f'UPDATE tStatus SET last_searched = {data["last_searched"]} WHERE id == {res[]} ')
        #     # elem = datetime.datetime.strptime(res[0]['last_searched'], '%Y-%m-%d %H:%M:%S')
        #     # last_ts = time.mktime(elem.timetuple())
        #     # new_ts = data['modified']
        #     # print(last_ts)


@app.route("/detection/finished", methods=['POST'])
def detection_finished():
    """
    When a detection finishes, call this to update tStatus' last_searched and model
    """
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'UPDATE tStatus SET last_searched = {int(time.time())}, model = \"{data["model"]}\" WHERE id == {data["id"]}')


@app.route("/file/removed", methods=['POST'])
def file_removed():
    data = json.loads(request.data)
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'DELETE FROM tFiles WHERE filepath == "{data["filepath"]}"')
        conn.commit()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
