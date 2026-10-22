import os
import sqlite3
import time

from flask import Flask, g, jsonify, request # type: ignore

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db")

BULK_DELAY_SECONDS = 2

SEED_CONTACTS = [
    ("Ada Lovelace", "ada@example.com", "555-0101", "Analytical engine"),
    ("Grace Hopper", "grace@example.com", "555-0102", "Compilers"),
    ("Alan Turing", "alan@example.com", "555-0103", "Computability"),
    ("Margaret Hamilton", "margaret@example.com", "555-0104", "Flight software"),
    ("Edsger Dijkstra", "edsger@example.com", "555-0105", "Structured programming"),
    ("Barbara Liskov", "barbara@example.com", "555-0106", "Abstraction"),
    ("Donald Knuth", "donald@example.com", "555-0107", "Algorithms"),
    ("Frances Allen", "frances@example.com", "555-0108", "Optimization"),
]

app = Flask(__name__, static_folder="static", static_url_path="")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS contacts (
               id    INTEGER PRIMARY KEY AUTOINCREMENT,
               name  TEXT NOT NULL,
               email TEXT NOT NULL DEFAULT '',
               phone TEXT NOT NULL DEFAULT '',
               notes TEXT NOT NULL DEFAULT ''
           )"""
    )
    if conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO contacts (name, email, phone, notes) VALUES (?, ?, ?, ?)",
            SEED_CONTACTS,
        )
    conn.commit()
    conn.close()


def read_fields(data):
    """Return (name, email, phone, notes) from a JSON body, or None if invalid."""
    name = (data.get("name") or "").strip()
    if not name:
        return None
    return (
        name,
        (data.get("email") or "").strip(),
        (data.get("phone") or "").strip(),
        (data.get("notes") or "").strip(),
    )


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/contacts")
def list_contacts():
    rows = get_db().execute("SELECT * FROM contacts ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/contacts")
def create_contact():
    fields = read_fields(request.get_json(silent=True) or {})
    if fields is None:
        return jsonify(error="Name is required"), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO contacts (name, email, phone, notes) VALUES (?, ?, ?, ?)", fields
    )
    db.commit()
    row = db.execute("SELECT * FROM contacts WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.put("/api/contacts/<int:contact_id>")
def update_contact(contact_id):
    fields = read_fields(request.get_json(silent=True) or {})
    if fields is None:
        return jsonify(error="Name is required"), 400
    db = get_db()
    cur = db.execute(
        "UPDATE contacts SET name = ?, email = ?, phone = ?, notes = ? WHERE id = ?",
        fields + (contact_id,),
    )
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="Not found"), 404
    row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    return jsonify(dict(row))


@app.delete("/api/contacts/<int:contact_id>")
def delete_contact(contact_id):
    db = get_db()
    cur = db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="Not found"), 404
    return jsonify(deleted=contact_id)


@app.post("/api/contacts/bulk-delete")
def bulk_delete():
    ids = (request.get_json(silent=True) or {}).get("ids") or []
    ids = [i for i in ids if isinstance(i, int)]
    if not ids:
        return jsonify(error="No ids given"), 400
    time.sleep(BULK_DELAY_SECONDS)
    db = get_db()
    marks = ",".join("?" * len(ids))
    db.execute(f"DELETE FROM contacts WHERE id IN ({marks})", ids)
    db.commit()
    return jsonify(deleted=ids)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)