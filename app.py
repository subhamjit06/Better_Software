from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# SQLite connection (simple file DB)
con = sqlite3.connect("tasks.db", check_same_thread=False)
con.row_factory = sqlite3.Row
con.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT
    )
    """
)
con.commit()

@app.get("/api/tasks")
def list_tasks():
    rows = con.execute(
        "SELECT id, title, description FROM tasks ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    description = data.get("description")
    cur = con.execute(
        "INSERT INTO tasks(title, description) VALUES (?, ?)", (title, description)
    )
    con.commit()
    return (
        jsonify({"id": cur.lastrowid, "title": title, "description": description}),
        201,
    )

@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}
    fields, values = [], []
    if "title" in data:
        fields.append("title = ?"); values.append(data["title"])
    if "description" in data:
        fields.append("description = ?"); values.append(data["description"])
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(task_id)
    con.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
    con.commit()
    row = con.execute(
        "SELECT id, title, description FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))

@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id: int):
    con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    con.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    # Optional direct run: py app.py
    app.run(debug=True)
