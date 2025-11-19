"""Flask application exposing pathfinding APIs for the visualizer."""
from __future__ import annotations

from flask import Flask, jsonify, request

from .algorithms import ALGORITHMS
from .graph_loader import load_graph


app = Flask(__name__)


def _get_graph():
    return load_graph()


@app.route("/graph", methods=["GET"])
def graph_info():
    graph = _get_graph()
    return jsonify(graph.serialize())


@app.route("/path/<algorithm>", methods=["GET"])
def run_algorithm(algorithm: str):
    graph = _get_graph()
    start = request.args.get("start")
    goal = request.args.get("goal")
    if not start or not goal:
        return jsonify({"error": "Missing start or goal parameter"}), 400

    algorithm = algorithm.lower()
    if algorithm not in ALGORITHMS:
        return jsonify({"error": f"Unsupported algorithm '{algorithm}'"}), 404

    try:
        result = ALGORITHMS[algorithm](graph, start, goal)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
