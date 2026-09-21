"""Kiểm tra và vẽ chu trình/đường đi Euler bằng thuật toán Hierholzer."""

import math
import sys
import tkinter as tk
from tkinter import messagebox, ttk


class Graph:
	def __init__(self, vertices, edges):
		self.vertices = vertices
		self.edges = edges
		self.adjacency = {vertex: [] for vertex in vertices}
		for edge_id, (start, end) in enumerate(edges):
			self.adjacency[start].append((end, edge_id))
			self.adjacency[end].append((start, edge_id))

	def degrees(self):
		return {vertex: len(self.adjacency[vertex]) for vertex in self.vertices}

	def is_connected(self):
		active = [vertex for vertex in self.vertices if self.adjacency[vertex]]
		if not active:
			return False
		visited = {active[0]}
		stack = [active[0]]
		while stack:
			current = stack.pop()
			for neighbor, _ in self.adjacency[current]:
				if neighbor not in visited:
					visited.add(neighbor)
					stack.append(neighbor)
		return all(vertex in visited for vertex in active)

	def analyze(self):
		degree_map = self.degrees()
		odd_vertices = [vertex for vertex in self.vertices if degree_map[vertex] % 2]
		connected = self.is_connected()
		kind = "none"
		if self.edges and connected:
			if len(odd_vertices) == 0:
				kind = "circuit"
			elif len(odd_vertices) == 2:
				kind = "path"
		trail, trail_edges = self.find_trail(kind, odd_vertices, degree_map)
		return {
			"degrees": degree_map,
			"odd": odd_vertices,
			"connected": connected,
			"kind": kind,
			"trail": trail,
			"trail_edges": trail_edges,
		}

	def find_trail(self, kind, odd_vertices, degree_map):
		if kind == "none":
			return None, None
		start = odd_vertices[0] if kind == "path" else next(
			vertex for vertex in self.vertices if degree_map[vertex] > 0
		)
		remaining = {vertex: list(items) for vertex, items in self.adjacency.items()}
		used = set()
		stack = [(start, None)]
		reversed_vertices = []
		reversed_edges = []
		while stack:
			current, incoming_edge = stack[-1]
			next_item = next(
				(item for item in remaining[current] if item[1] not in used), None
			)
			if next_item is None:
				vertex, edge_id = stack.pop()
				reversed_vertices.append(vertex)
				if edge_id is not None:
					reversed_edges.append(edge_id)
			else:
				neighbor, edge_id = next_item
				used.add(edge_id)
				stack.append((neighbor, edge_id))
		trail = list(reversed(reversed_vertices))
		trail_edges = list(reversed(reversed_edges))
		if len(used) != len(self.edges) or len(trail) != len(self.edges) + 1:
			return None, None
		return trail, trail_edges


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
			raise ValueError(
				f"Cạnh ở dòng {line_number} phải gồm đúng 2 đỉnh đã khai báo."
			)
		edges.append((parts[0], parts[1]))
	return vertices, edges


def result_text(graph, result):
	names = {
		"circuit": "ĐÂY LÀ ĐỒ THỊ EULER: có chu trình Euler.",
		"path": "ĐÂY LÀ ĐƯỜNG ĐI EULER: không có chu trình Euler.",
		"none": "KHÔNG PHẢI ĐỒ THỊ EULER: không có chu trình hoặc đường đi Euler.",
	}
	lines = [names[result["kind"]], "", "Dữ liệu liên quan:"]
	lines.append(f"- Số đỉnh: {len(graph.vertices)}")
	lines.append(f"- Số cạnh: {len(graph.edges)}")
	lines.append(
		"- Bậc từng đỉnh: "
		+ ", ".join(f"{vertex}={degree}" for vertex, degree in result["degrees"].items())
	)
	lines.append(
		"- Đỉnh bậc lẻ: " + (", ".join(result["odd"]) if result["odd"] else "Không có")
	)
	lines.append(f"- Liên thông (bỏ qua đỉnh cô lập): {'Có' if result['connected'] else 'Không'}")
	if result["trail"]:
		lines.append("- Lộ trình Hierholzer: " + " -> ".join(result["trail"]))
	return "\n".join(lines)


class EulerApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Kiểm tra đồ thị Hierholzer")
		self.root.geometry("1050x760")
		self.root.minsize(820, 620)
		self.vertices_var = tk.StringVar(value="A B C")
		self.status_var = tk.StringVar(value="Hãy nhập dữ liệu rồi bấm Phân tích đồ thị.")
		self._build_ui()

	def _build_ui(self):
		root = ttk.Frame(self.root, padding=18)
		root.pack(fill="both", expand=True)
		ttk.Label(root, text="KIỂM TRA ĐỒ THỊ EULER / HIERHOLZER", font=("Segoe UI", 16, "bold")).pack(anchor="w")
		ttk.Label(root, text="Đường đi Euler có 2 đỉnh bậc lẻ; chu trình Euler có 0 đỉnh bậc lẻ.").pack(anchor="w", pady=(4, 14))

		input_frame = ttk.LabelFrame(root, text="Hướng dẫn nhập", padding=12)
		input_frame.pack(fill="x")
		ttk.Label(input_frame, text="Tên các đỉnh (cách nhau bằng dấu cách):").grid(row=0, column=0, sticky="w")
		ttk.Entry(input_frame, textvariable=self.vertices_var).grid(row=1, column=0, sticky="ew", pady=(4, 8))
		ttk.Label(input_frame, text="Danh sách cạnh: mỗi dòng nhập 2 đỉnh, ví dụ A B. Có thể nhập cạnh lặp hoặc A A.").grid(row=2, column=0, sticky="w")
		self.edge_text = tk.Text(input_frame, height=5, font=("Consolas", 10))
		self.edge_text.grid(row=3, column=0, sticky="nsew", pady=(4, 8))
		self.edge_text.insert("1.0", "A B\nB C\nC A")
		input_frame.columnconfigure(0, weight=1)
		ttk.Button(input_frame, text="Phân tích đồ thị", command=self.analyze).grid(row=4, column=0, sticky="e")

		self.canvas = tk.Canvas(root, height=380, background="#f7faf9", highlightthickness=1, highlightbackground="#d9e2e4")
		self.canvas.pack(fill="both", expand=True, pady=(14, 10))
		ttk.Label(root, textvariable=self.status_var, justify="left", wraplength=980).pack(fill="x", anchor="w")

	def analyze(self):
		try:
			vertices, edges = parse_input(self.vertices_var.get(), self.edge_text.get("1.0", "end"))
			graph = Graph(vertices, edges)
			result = graph.analyze()
		except ValueError as error:
			self.status_var.set(str(error))
			messagebox.showerror("Dữ liệu chưa hợp lệ", str(error))
			return
		self.draw_graph(graph, result)
		self.status_var.set(result_text(graph, result))

	def draw_graph(self, graph, result):
		self.canvas.delete("all")
		width = max(self.canvas.winfo_width(), 700)
		height = max(self.canvas.winfo_height(), 380)
		center_x, center_y = width / 2, height / 2
		radius = min(width, height) / 2 - 55
		positions = {}
		for index, vertex in enumerate(graph.vertices):
			angle = 2 * math.pi * index / len(graph.vertices) - math.pi / 2
			positions[vertex] = (center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
		highlighted = set(result["trail_edges"] or [])
		for edge_id, (start, end) in enumerate(graph.edges):
			x1, y1 = positions[start]
			x2, y2 = positions[end]
			color = "#d95f4f" if edge_id in highlighted else "#78888c"
			line_width = 4 if edge_id in highlighted else 2
			if start == end:
				self.canvas.create_oval(x1 - 24, y1 - 48, x1 + 24, y1, outline=color, width=line_width)
			else:
				self.canvas.create_line(x1, y1, x2, y2, fill=color, width=line_width)
		for vertex, (x, y) in positions.items():
			self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="#d8f0eb", outline="#087f78", width=2)
			self.canvas.create_text(x, y, text=vertex, fill="#18222d", font=("Segoe UI", 11, "bold"))


def run_tests():
	cases = [
		((["A", "B", "C"], [("A", "B"), ("B", "C"), ("C", "A")]), "circuit"),
		((["A", "B", "C"], [("A", "B"), ("B", "C")]), "path"),
		((["A", "B", "C", "D"], [("A", "B"), ("A", "C"), ("A", "D")]), "none"),
		((["A", "B", "C", "D"], [("A", "B"), ("C", "D")]), "none"),
	]
	for (vertices, edges), expected in cases:
		assert Graph(vertices, edges).analyze()["kind"] == expected
	print(f"Đã đạt {len(cases)}/{len(cases)} bài kiểm tra.")


if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
		run_tests()
	else:
		root = tk.Tk()
		EulerApp(root)
		root.mainloop()
