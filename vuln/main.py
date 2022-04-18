from contextlib import contextmanager
import os

import sqlite3

@contextmanager
def get_cur():
    try:
        con = sqlite3.connect('/app/db')
        cur = con.cursor()
        yield cur
    finally:
        con.commit()
        con.close()



with get_cur() as cur:
    # Create table
    cur.execute('''\
    CREATE TABLE IF NOT EXISTS todo (
        id serial PRIMARY KEY,
        data text
    )
    ''')

from flask import Flask, request, redirect
app = Flask(__name__)

@app.route("/")
def todo_list():
    resp = """<title>TODO LIST</title>"""
    resp += "<body><p><ul>"
    with get_cur() as cur:
        todos = cur.execute('''SELECT * FROM todo''')
        l = 0

        for id, data in todos:
            resp += "<li>" + data + "</li>"
            l += 1

    resp += "</ul></p>"
    if l == 0 :
        resp += "<p><b>No Todo items found</b></p>"

    resp += """\

<p>
Add todo item:
<form action="/add" method="GET">
    <input type=text name=data></input>
    <button>Submit</button>
</form>
</p>
<p>
Check service:
<form action="/ping" method="GET">
    <input type=text name=host></input>
    <button>Submit</button>
</form>
</p>
"""

    resp += "</body>"

    return resp

@app.route("/add")
def todo_add():
    data = request.args.get('data')
    if not data:
        return "Unable to add empty argument", 400
    data = str(data)

    with get_cur() as cur:
        cur.executescript(f'insert into todo (data) values ("{data}")')

    return redirect("/")

@app.route("/ping")
def ping():
    host = request.args.get('host')
    if not host:
        return "Unknown host", 400

    with os.popen(f'ping -c3 {host}') as p:
        result = p.read()

    return f"<pre><code>{result}</code></pre>"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
