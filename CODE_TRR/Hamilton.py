"""Kiểm tra và vẽ đường đi hoặc chu trình Hamilton bằng Python."""

import math
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from Hierholzer import Graph as EulerGraph


class Graph:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges
        self.adjacency = {vertex: set() for vertex in vertices}
        for start, end in edges:
            if start != end:
                self.adjacency[start].add(end)
                self.adjacency[end].add(start)

    def find_path(self):
        path = []
        visited = set()

        def search(current):
            path.append(current)
            visited.add(current)
            if len(path) == len(self.vertices):
                result = list(path)
            else:
                result = None
                for neighbor in self.adjacency[current]:
                    if neighbor not in visited:
                        result = search(neighbor)
                        if result:
                            break
            if result:
                return result
            visited.remove(current)
            path.pop()
            return None

        for vertex in self.vertices:
            result = search(vertex)
            if result:
                is_circuit = len(result) > 2 and result[0] in self.adjacency[result[-1]]
                return (result + [result[0]] if is_circuit else result), ("circuit" if is_circuit else "path")
        return None, "none"

    def analyze(self):
        route, kind = self.find_path()
        degrees = {vertex: len(self.adjacency[vertex]) for vertex in self.vertices}
        if kind == "circuit":
            reason = "Đỉnh cuối nối với đỉnh đầu, tạo thành chu trình Hamilton."
        elif kind == "path":
            reason = "Đã tìm được đường đi qua mỗi đỉnh đúng một lần."
        else:
            reason = "Không tìm được đường đi qua tất cả các đỉnh đúng một lần."
        return {"kind": kind, "route": route, "degrees": degrees, "reason": reason}


def parse_input(vertex_text, edge_text):
    vertices = vertex_text.split()
    if not vertices:
        raise ValueError("Bạn cần nhập ít nhất một đỉnh.")
    if len(vertices) != len(set(vertices)):
        raise ValueError("Tên các đỉnh không được trùng nhau.")
    vertex_set = set(vertices)
    edges = []
    for line_number, line in enumerate(edge_text.splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 2 or any(vertex not in vertex_set for vertex in parts):
            raise ValueError(f"Cạnh ở dòng {line_number} phải gồm đúng 2 đỉnh đã khai báo.")
        edges.append((parts[0], parts[1]))
    return vertices, edges


def describe(graph, result):
    titles = {"circuit": "ĐÂY LÀ CHU TRÌNH HAMILTON", "path": "ĐÂY LÀ ĐƯỜNG ĐI HAMILTON", "none": "KHÔNG PHẢI ĐỒ THỊ HAMILTON"}
    lines = [titles[result["kind"]], "", "Dữ liệu liên quan:"]
    lines.append(f"- Số đỉnh: {len(graph.vertices)}")
    lines.append(f"- Số cạnh: {len(graph.edges)}")
    lines.append("- Bậc từng đỉnh: " + ", ".join(f"{v}={d}" for v, d in result["degrees"].items()))
    lines.append("- Lý do: " + result["reason"])
    if result["route"]:
        lines.append("- Lộ trình Hamilton: " + " -> ".join(result["route"]))
    return "\n".join(lines)


def analyze_both(vertices, edges):
    hamilton = Graph(vertices, edges).analyze()
    euler = EulerGraph(vertices, edges).analyze()
    euler_names = {"circuit": "Chu trình Euler", "path": "Đường đi Euler", "none": "Không phải Euler"}
    hamilton_names = {"circuit": "Chu trình Hamilton", "path": "Đường đi Hamilton", "none": "Không phải Hamilton"}
    lines = [f"Euler: {euler_names[euler['kind']]}", f"Hamilton: {hamilton_names[hamilton['kind']]}", "", "Dữ liệu liên quan:"]
    lines.append(f"- Số đỉnh: {len(vertices)}")
    lines.append(f"- Số cạnh: {len(edges)}")
    lines.append("- Bậc từng đỉnh: " + ", ".join(f"{v}={d}" for v, d in euler["degrees"].items()))
    if euler["trail"]:
        lines.append("- Lộ trình Euler: " + " -> ".join(euler["trail"]))
    if hamilton["route"]:
        lines.append("- Lộ trình Hamilton: " + " -> ".join(hamilton["route"]))
    return "\n".join(lines), euler, hamilton


class HamiltonApp:
    def __init__(self, root):
        self.root = root
        root.title("Phân loại đồ thị Euler và Hamilton")
        root.geometry("1050x760")
        root.minsize(820, 620)
        self.vertices = tk.StringVar(value="A B C")
        self.status = tk.StringVar(value="Hãy nhập dữ liệu rồi bấm Phân tích đồ thị.")
        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="PHÂN LOẠI ĐỒ THỊ EULER VÀ HAMILTON", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Chương trình kiểm tra cả hai loại: Euler đi qua cạnh, Hamilton đi qua đỉnh.").pack(anchor="w", pady=(4, 14))
        inputs = ttk.LabelFrame(frame, text="Hướng dẫn nhập", padding=12)
        inputs.pack(fill="x")
        ttk.Label(inputs, text="Tên các đỉnh (cách nhau bằng dấu cách):").grid(row=0, column=0, sticky="w")
        ttk.Entry(inputs, textvariable=self.vertices).grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Label(inputs, text="Mỗi dòng nhập một cạnh, ví dụ A B.").grid(row=2, column=0, sticky="w")
        self.edges = tk.Text(inputs, height=5, font=("Consolas", 10))
        self.edges.grid(row=3, column=0, sticky="nsew", pady=(4, 8))
        self.edges.insert("1.0", "A B\nB C\nC A")
        inputs.columnconfigure(0, weight=1)
        ttk.Button(inputs, text="Phân tích đồ thị", command=self.analyze).grid(row=4, column=0, sticky="e")
        self.canvas = tk.Canvas(frame, height=380, background="#f7faf9", highlightthickness=1, highlightbackground="#d9e2e4")
        self.canvas.pack(fill="both", expand=True, pady=(14, 10))
        ttk.Label(frame, textvariable=self.status, justify="left", wraplength=980).pack(fill="x", anchor="w")

    def analyze(self):
        try:
            vertices, edges = parse_input(self.vertices.get(), self.edges.get("1.0", "end"))
            graph = Graph(vertices, edges)
            summary, euler, hamilton = analyze_both(vertices, edges)
        except ValueError as error:
            self.status.set(str(error))
            messagebox.showerror("Dữ liệu chưa hợp lệ", str(error))
            return
        self.draw(graph, {"route": hamilton["route"] or euler["trail"]})
        self.status.set(summary)

    def draw(self, graph, result):
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 380)
        center = (width / 2, height / 2)
        radius = min(width, height) / 2 - 55
        positions = {vertex: (center[0] + radius * math.cos(2 * math.pi * index / len(graph.vertices) - math.pi / 2), center[1] + radius * math.sin(2 * math.pi * index / len(graph.vertices) - math.pi / 2)) for index, vertex in enumerate(graph.vertices)}
        route = result["route"] or []
        route_pairs = set(zip(route, route[1:]))
        for start, end in graph.edges:
            x1, y1 = positions[start]
            x2, y2 = positions[end]
            active = (start, end) in route_pairs or (end, start) in route_pairs
            if start == end:
                self.canvas.create_oval(x1 - 24, y1 - 48, x1 + 24, y1, outline="#d95f4f" if active else "#78888c", width=4 if active else 2)
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill="#d95f4f" if active else "#78888c", width=4 if active else 2)
        for vertex, (x, y) in positions.items():
            self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="#d8f0eb", outline="#087f78", width=2)
            self.canvas.create_text(x, y, text=vertex, fill="#18222d", font=("Segoe UI", 11, "bold"))


def run_tests():
    cases = [
        ((["A", "B", "C"], [("A", "B"), ("B", "C"), ("C", "A")]), "circuit"),
        ((["A", "B", "C"], [("A", "B"), ("B", "C")]), "path"),
        ((["A", "B", "C", "D"], [("A", "B"), ("C", "D")]), "none"),
    ]
    for (vertices, edges), expected in cases:
        assert Graph(vertices, edges).analyze()["kind"] == expected
    print(f"Đã đạt {len(cases)}/{len(cases)} bài kiểm tra.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        run_tests()
    else:
        window = tk.Tk()
        HamiltonApp(window)
        window.mainloop()