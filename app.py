from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "database.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            type TEXT
        )
        """)

init_db()

def run_query(q, args=(), fetch=False):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute(q, args)
        if fetch:
            return cur.fetchall()
        conn.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report")
def report():
    return render_template("report.html")

# ---------------- API ----------------

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    d = request.json
    run_query("""INSERT INTO transactions(date,category,description,amount,type)
                 VALUES(?,?,?,?,?)""",
              (d['date'], d['category'], d['description'], d['amount'], d['type']))
    return jsonify({"msg": "Added"})

@app.route("/transactions")
def transactions():
    rows = run_query("SELECT * FROM transactions ORDER BY date DESC", fetch=True)
    return jsonify([{
        "id": r[0], "date": r[1], "category": r[2],
        "description": r[3], "amount": r[4], "type": r[5]
    } for r in rows])

@app.route("/delete_transaction/<int:id>", methods=["DELETE"])
def delete(id):
    run_query("DELETE FROM transactions WHERE id=?", (id,))
    return jsonify({"msg": "Deleted"})

@app.route("/edit_transaction/<int:id>", methods=["PUT"])
def edit(id):
    d = request.json
    run_query("""UPDATE transactions
                 SET date=?,category=?,description=?,amount=?,type=?
                 WHERE id=?""",
              (d['date'], d['category'], d['description'], d['amount'], d['type'], id))
    return jsonify({"msg": "Updated"})

@app.route("/monthly_summary")
def monthly_summary():
    month = request.args.get("month")
    rows = run_query("""
        SELECT type, SUM(amount) FROM transactions
        WHERE strftime('%Y-%m', date)=?
        GROUP BY type
    """, (month,), True)

    income = expense = 0
    for r in rows:
        if r[0] == "Income":
            income = r[1]
        else:
            expense = r[1]

    return jsonify({
        "income": income or 0,
        "expense": expense or 0,
        "savings": (income or 0) - (expense or 0)
    })

@app.route("/category_report")
def category_report():
    month = request.args.get("month")
    rows = run_query("""
        SELECT category, SUM(amount) FROM transactions
        WHERE strftime('%Y-%m', date)=? AND type='Expense'
        GROUP BY category
    """, (month,), True)
    return jsonify({r[0]: r[1] for r in rows})

if __name__ == "__main__":
    app.run(debug=True)
