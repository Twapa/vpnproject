from flask import Flask, jsonify
from whitenoise import WhiteNoise
import json
import sqlite3

app = Flask(__name__)
app.wsgi_app = WhiteNoise(
    app.wsgi_app, root="static/", index_file=True, autorefresh=True
)

def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data



@app.route('/data_api')
def root():
    
    with sqlite3.connect("vpn_servers.db") as conn:
        conn.row_factory = row_to_dict
        result = conn.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
        data = result.fetchall()     
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
