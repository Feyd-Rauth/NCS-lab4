from contextlib import contextmanager
import html
import os
import re
import shlex
import sqlite3

# from https://stackoverflow.com/questions/10306690/what-is-a-regular-expression-which-will-match-a-valid-domain-name-without-a-subd
DOMAIN_NAME_REGEX = re.compile(r'^(((?!\-))(xn\-\-)?[a-z0-9\-_]{0,61}[a-z0-9]{1,1}\.)*(xn\-\-)?([a-z0-9\-]{1,61}|[a-z0-9\-]{1,30})\.[a-z]{2,}$')
_IPV4_ITEM = r'\d{1,3}'
IPV4_REGEX = re.compile(rf"^{_IPV4_ITEM}\.{_IPV4_ITEM}\.{_IPV4_ITEM}\.{_IPV4_ITEM}$")

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
            resp += "<li>" + html.escape(data) + "</li>"
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
        cur.execute(f'insert into todo (data) values (?)', (data,))

    return redirect("/")

@app.route("/ping")
def ping():
    host = request.args.get('host')
    if not host:
        return "Unknown host", 400

    if not (DOMAIN_NAME_REGEX.match(host) or IPV4_REGEX.match(host)):
        return "Bad host: " + html.escape(host)

    host = shlex.quote(host)

    with os.popen(f'ping -c3 {host}') as p:
        result = p.read()

    return f"<pre><code>{result}</code></pre>"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
