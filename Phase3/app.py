### RUN WITH: python3 app.py + python3 -m hhtp.server 8000

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
import sys

# create app
app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

# db vars
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "cs236db")
DB_USER = os.environ.get("DB_USER", "cs236user")
DB_PASS = os.environ.get("DB_PASS", "cs236pass")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# debug
print(f"Starting frontend with host={DB_HOST} port={DB_PORT} db={DB_NAME} user={DB_USER} password={'*' * len(DB_PASS)}")

# create engine
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # conn test
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except OperationalError as e:
    print("ERROR: Cannot connect to Postgres from frontend.")
    sys.exit(1)
except Exception as e:
    print("Unexpected error creating DB engine:", e)
    sys.exit(1)

# return ALL public tables in db
def list_tables():
    q = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type='BASE TABLE'
        ORDER BY table_name
    """)
    with engine.connect() as conn:
        rows = conn.execute(q).fetchall()
    return [r[0] for r in rows]

# return col names + types for SINGLE table
def columns_for_table(table):
    q = text("""
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_schema='public' AND table_name = :table
        ORDER BY ordinal_position
    """)
    with engine.connect() as conn:
        rows = conn.execute(q, {"table": table}).fetchall()
    return [{"name": r[0], "type": r[1]} for r in rows]

# serve index
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# list ALL tables
@app.route("/api/tables")
def api_tables():
    return jsonify({"tables": list_tables()})

# list all cols for SINGLE table
@app.route("/api/columns")
def api_columns():
    table = request.args.get("table")
    if not table:
        return jsonify({"error": "table param required"}), 400
    cols = columns_for_table(table)
    if not cols:
        return jsonify({"error": "table not found or has no columns"}), 404
    return jsonify({"columns": cols})

# fetch with filters + limit
@app.route("/api/data", methods=["GET", "POST"])
def api_data():
    if request.method == "GET":
        table = request.args.get("table")
        limit = int(request.args.get("limit", "100"))
        filters = []
    else:
        # read + filter POST body
        body = request.get_json() or {}
        table = body.get("table")
        limit = int(body.get("limit", 100))
        filters = body.get("filters", [])

    if not table:
        return jsonify({"error": "table required"}), 400

    # validate table
    cols = columns_for_table(table)
    if not cols:
        return jsonify({"error": "table not found"}), 404
    col_names = {c["name"] for c in cols}

    # validate input + create where clause
    allowed_ops = {"=": "=", ">": ">", "<": "<", ">=": ">=", "<=": "<=", "like": "LIKE"}
    where_clauses = []
    params = {}
    for i, f in enumerate(filters):
        col = f.get("column")
        op = f.get("op", "=").lower()
        val = f.get("value")
        if col not in col_names:
            return jsonify({"error": f"invalid column: {col}"}), 400
        if op not in allowed_ops:
            return jsonify({"error": f"invalid op: {op}"}), 400
        key = f"p{i}"

        # wildcard handling
        if allowed_ops[op] == "LIKE":
            params[key] = f"%{val}%"
        else:
            params[key] = val
        where_clauses.append(f'"{col}" {allowed_ops[op]} :{key}')

    # final query
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    sql = text(f'SELECT * FROM "{table}" {where_sql} LIMIT :_limit')
    params["_limit"] = limit

    # execute
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        rows = [dict(r._mapping) for r in result]

    return jsonify({"rows": rows, "count": len(rows)})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
