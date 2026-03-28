#!/usr/bin/env python3
"""Simple shared leaderboard API for Dragon Maze."""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json, os, threading

app = Flask(__name__)
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
lock = threading.Lock()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return jsonify({"status": "Dragon Maze Leaderboard API"})

@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    return jsonify(load_data())

@app.route("/api/leaderboard/<board_key>", methods=["GET"])
def get_board(board_key):
    return jsonify(load_data().get(board_key, []))

@app.route("/api/leaderboard/<board_key>", methods=["POST"])
def add_entry(board_key):
    entry = request.get_json()
    if not entry or "name" not in entry or "time" not in entry or "moves" not in entry:
        return jsonify({"error": "Need name, time, moves"}), 400
    name = str(entry["name"])[:15].strip()
    try:
        t = round(float(entry["time"]), 2)
        m = int(entry["moves"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data"}), 400
    if not name or t < 0 or m < 0:
        return jsonify({"error": "Invalid data"}), 400
    with lock:
        data = load_data()
        if board_key not in data:
            data[board_key] = []
        data[board_key].append({"name": name, "time": t, "moves": m})
        data[board_key].sort(key=lambda e: e["time"])
        data[board_key] = data[board_key][:10]
        save_data(data)
    rank = next((i+1 for i, e in enumerate(data[board_key]) if e["name"]==name and e["time"]==t), None)
    return jsonify({"ok": True, "rank": rank})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5555))
    app.run(host="0.0.0.0", port=port)
