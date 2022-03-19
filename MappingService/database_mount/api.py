import sqlite3
import json
from flask import Flask, request, jsonify
import time
import datetime

DATABASE = 'database.db'

app = Flask(__name__)

@app.route("/test", methods=['GET'])
def test():
    return "test"

@app.route("/file/status", methods=['POST'])
def file_status_update():
    data = json.loads(request.data)

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM tFiles WHERE filepath == "{data["filepath"]}"')
        res = cur.fetchall()
        res = [dict(row) for row in res]
        print(res)

        if len(res) <= 0:
            cur.execute(f'INSERT INTO tFiles (filepath) VALUES (\"{data["filepath"]}\")')
            conn.commit()
            cur.execute(f'SELECT * FROM tFiles WHERE filepath == "{data["filepath"]}"')
            res = cur.fetchall()
            res = [dict(row) for row in res]
            cur.execute(f'INSERT INTO tStatus (file_id, last_searched, model) VALUES ({res[0]["id"]}, 0, "none")')
            conn.commit()
            print('added')
        else:
            cur.execute(f'SELECT * FROM tStatus WHERE file_id == "{res[0]["id"]}"')
            res = cur.fetchall()
            res = [dict(row) for row in res]
            print(res)
            elem = datetime.datetime.strptime(res[0]['last_searched'], '%Y-%m-%d %H:%M:%S')
            last_ts = time.mktime(elem.timetuple())
            new_ts = data['modified']
            print(last_ts)
    

    #conn.commit()

    print("done")
    # conn = db_connection(f'INSERT INTO tStatus (filepath) VALUES {data["filepath"]}')
    return "hello world"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

# con = sqlite3.connect('database.db')
# cur = con.cursor()

# cur.execute("INSERT INTO tStatus (filepath) VALUES ('c://file1.mp4')")
# con.commit()

# for row in cur.execute('SELECT * FROM tFiles'):
#     print(row)

# print("done")