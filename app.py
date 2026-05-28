from flask import Flask, render_template, request, jsonify
from boruvka import boruvka

app = Flask(__name__)

EXAMPLES = {
    1: {
        "name": "Простой граф (5 вершин)",
        "n": 5,
        "edges": [
            [0, 1, 4],
            [0, 2, 3],
            [1, 2, 1],
            [1, 3, 2],
            [2, 3, 4],
            [3, 4, 2],
            [2, 4, 5],
        ]
    },
    2: {
        "name": "Граф из лекции (7 вершин)",
        "n": 7,
        "edges": [
            [0, 1, 7],
            [0, 3, 5],
            [1, 2, 8],
            [1, 3, 9],
            [1, 4, 7],
            [2, 4, 5],
            [3, 4, 15],
            [3, 5, 6],
            [4, 5, 8],
            [4, 6, 9],
            [5, 6, 11],
        ]
    },
    3: {
        "name": "Полный граф K4",
        "n": 4,
        "edges": [
            [0, 1, 10],
            [0, 2, 6],
            [0, 3, 5],
            [1, 2, 15],
            [1, 3, 4],
            [2, 3, 12],
        ]
    },
    4: {
        "name": "Граф с одинаковыми весами",
        "n": 4,
        "edges": [
            [0, 1, 2],
            [1, 2, 2],
            [2, 3, 2],
            [0, 3, 2],
            [0, 2, 2],
        ]
    },
    5: {
        "name": "Несвязный граф (6 вершин, 2 компоненты)",
        "n": 6,
        "edges": [
            [0, 1, 3],
            [0, 2, 1],
            [1, 2, 4],
            [3, 4, 2],
            [3, 5, 5],
            [4, 5, 6],
        ]
    }
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    n = data.get("n")
    edges_raw = data.get("edges", [])

    if not isinstance(n, int) or n < 2:
        return jsonify({"error": "Число вершин должно быть целым числом ≥ 2"}), 400

    if n > 100:
        return jsonify({"error": "Число вершин не должно превышать 100"}), 400

    if not edges_raw:
        return jsonify({"error": "Список рёбер пуст"}), 400

    if len(edges_raw) > 500:
        return jsonify({"error": "Слишком много рёбер (максимум 500)"}), 400

    edges = []
    for i, e in enumerate(edges_raw):
        if not isinstance(e, (list, tuple)) or len(e) != 3:
            return jsonify({"error": f"Ребро #{i+1}: неверный формат. Ожидается [u, v, w]"}), 400
        u, v, w = int(e[0]), int(e[1]), int(e[2])
        if u < 0 or u >= n or v < 0 or v >= n:
            return jsonify({"error": f"Ребро #{i+1}: вершины должны быть от 0 до {n-1}"}), 400
        if u == v:
            return jsonify({"error": f"Ребро #{i+1}: петли (u == v) не допускаются"}), 400
        if w <= 0:
            return jsonify({"error": f"Ребро #{i+1}: вес должен быть положительным"}), 400
        edges.append((u, v, w))

    result = boruvka(n, edges)

    result["n"] = n
    result["edges_input"] = [{"u": u, "v": v, "w": w} for u, v, w in edges]

    return jsonify(result)


@app.route("/example/<int:example_id>")
def get_example(example_id: int):
    ex = EXAMPLES.get(example_id)
    if ex is None:
        return jsonify({"error": "Пример не найден"}), 404
    return jsonify(ex)


@app.route("/examples")
def list_examples():
    return jsonify([
        {"id": k, "name": v["name"], "n": v["n"], "edges_count": len(v["edges"])}
        for k, v in EXAMPLES.items()
    ])


if __name__ == "__main__":
    app.run(debug=True, port=5000)