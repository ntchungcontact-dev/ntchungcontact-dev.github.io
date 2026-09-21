"""
Kiểm tra một đồ thị (vô hướng, liên thông hay không) có phải là
đồ thị Euler hay không, và nếu có thì tìm ra:
  - Chu trình Euler (Eulerian Circuit): đi qua mọi cạnh đúng 1 lần,
    xuất phát và kết thúc tại cùng 1 đỉnh.
  - Đường đi Euler (Eulerian Path): đi qua mọi cạnh đúng 1 lần,
    nhưng điểm đầu và điểm cuối có thể khác nhau.

Lý thuyết dùng để kiểm tra (định lý Euler):
  1. Đồ thị phải liên thông (bỏ qua các đỉnh cô lập, bậc = 0).
  2. Đếm số đỉnh có bậc lẻ (odd degree):
       - 0 đỉnh bậc lẻ  -> có Chu trình Euler (Eulerian Circuit)
       - 2 đỉnh bậc lẻ  -> có Đường đi Euler (Eulerian Path), nhưng
                            không có chu trình
       - khác 0 hoặc 2  -> không phải đồ thị Euler

Sau khi biết đồ thị Euler, dùng thuật toán Hierholzer để dựng ra
chu trình/đường đi Euler cụ thể.
"""

import math
import sys
from collections import defaultdict, deque


class Graph:
    def __init__(self, vertices):
        self.vertices = list(vertices)
        self.adj = defaultdict(list)   # danh sách kề: v -> [u1, u2, ...]
        self.edges = []                # danh sách cạnh gốc (để in ra)

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.edges.append((u, v))

    def degree(self, v):
        return len(self.adj[v])

    def _get_connected_component(self, start):
        """Trả về tập đỉnh liên thông với start (chỉ xét đỉnh có bậc > 0)."""
        visited = set([start])
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for w in self.adj[u]:
                if w not in visited:
                    visited.add(w)
                    queue.append(w)
        return visited

    def is_connected_ignoring_isolated(self):
        """Kiểm tra liên thông, bỏ qua các đỉnh cô lập (bậc 0)."""
        non_isolated = [v for v in self.vertices if self.degree(v) > 0]
        if not non_isolated:
            return True  # không có cạnh nào
        start = non_isolated[0]
        reached = self._get_connected_component(start)
        return all(v in reached for v in non_isolated)

    def odd_degree_vertices(self):
        return [v for v in self.vertices if self.degree(v) % 2 == 1]

    def check_euler_conditions(self):
        """Kiểm tra và trả về (loại đồ thị, danh sách lý do)."""
        if not self.edges:
            return 'none', ['Đồ thị phải có ít nhất một cạnh.']

        if not self.is_connected_ignoring_isolated():
            return 'none', ['Các đỉnh có cạnh phải nằm trong cùng một thành phần liên thông.']

        odd_count = len(self.odd_degree_vertices())
        if odd_count == 0:
            return 'circuit', ['Có 0 đỉnh bậc lẻ.']
        if odd_count == 2:
            return 'path', ['Có đúng 2 đỉnh bậc lẻ.']
        return 'none', [f'Có {odd_count} đỉnh bậc lẻ; cần 0 hoặc 2 đỉnh.']

    def classify(self):
        """
        Trả về một trong ba chuỗi:
          'circuit'  - có chu trình Euler
          'path'     - có đường đi Euler (không có chu trình)
          'none'     - không phải đồ thị Euler
        """
        kind, _ = self.check_euler_conditions()
        return kind

    def find_euler_trail(self):
        """
        Dùng thuật toán Hierholzer để tìm chu trình/đường đi Euler.
        Trả về danh sách đỉnh theo thứ tự đi qua, hoặc None nếu
        đồ thị không phải là đồ thị Euler.
        """
        kind = self.classify()
        if kind == 'none':
            return None, kind

        # Sao chép danh sách kề để "tiêu thụ" dần các cạnh khi duyệt
        local_adj = {v: list(neighbors) for v, neighbors in self.adj.items()}

        odd = self.odd_degree_vertices()
        if kind == 'path':
            start = odd[0]           # đường đi Euler phải bắt đầu ở 1 đỉnh bậc lẻ
        else:
            # chu trình Euler: bắt đầu ở đỉnh bất kỳ có bậc > 0
            start = next(v for v in self.vertices if self.degree(v) > 0)

        stack = [start]
        trail = []

        while stack:
            v = stack[-1]
            if local_adj.get(v):
                u = local_adj[v].pop()
                local_adj[u].remove(v)   # xoá cạnh 2 chiều (vô hướng)
                stack.append(u)
            else:
                trail.append(stack.pop())

        trail.reverse()
        return trail, kind


def describe_edges(trail):
    return " -> ".join(trail)


def draw_graph(vertices, edge_list, trail=None):
    """Vẽ đồ thị bằng tkinter sau khi người dùng nhập xong."""
    try:
        import tkinter as tk
    except ImportError:
        print("Không thể mở hình vẽ vì máy chưa có tkinter.")
        return

    window = tk.Tk()
    window.title("Hình đồ thị Euler")
    width, height = 800, 600
    canvas = tk.Canvas(window, width=width, height=height, bg="white")
    canvas.pack()

    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 2 - 90
    positions = {}
    for index, vertex in enumerate(vertices):
        angle = (2 * math.pi * index / len(vertices)) - math.pi / 2
        positions[vertex] = (
            center_x + radius * math.cos(angle),
            center_y + radius * math.sin(angle),
        )

    highlighted_edges = set()
    if trail and len(trail) > 1:
        for start, end in zip(trail, trail[1:]):
            highlighted_edges.add(frozenset((start, end)))

    for start, end in edge_list:
        start_x, start_y = positions[start]
        end_x, end_y = positions[end]
        edge_color = "#d94841" if frozenset((start, end)) in highlighted_edges else "#4a5568"
        edge_width = 4 if edge_color == "#d94841" else 2
        if start == end:
            canvas.create_oval(
                start_x - 25, start_y - 45, start_x + 25, start_y + 5,
                outline=edge_color, width=edge_width,
            )
        else:
            canvas.create_line(
                start_x, start_y, end_x, end_y,
                fill=edge_color, width=edge_width,
            )

    for vertex, (x, y) in positions.items():
        canvas.create_oval(x - 24, y - 24, x + 24, y + 24,
                           fill="#d9f0ff", outline="#1769aa", width=2)
        canvas.create_text(x, y, text=vertex, font=("Arial", 12, "bold"))

    canvas.create_text(
        width // 2, 25,
        text="Đường đi Euler" if trail else "Đồ thị đã nhập",
        fill="#d94841" if trail else "#1a202c",
        font=("Arial", 16, "bold"),
    )
    window.mainloop()


def run_test(name, vertices, edge_list):
    print("=" * 60)
    print(f"ĐỒ THỊ: {name}")
    print("=" * 60)

    g = Graph(vertices)
    for u, v in edge_list:
        g.add_edge(u, v)

    print("Danh sách cạnh:", edge_list)
    print("Bậc của từng đỉnh:")
    for v in vertices:
        print(f"  deg({v}) = {g.degree(v)}")

    odd = g.odd_degree_vertices()
    print(f"Số đỉnh bậc lẻ: {len(odd)} -> {odd}")

    connected = g.is_connected_ignoring_isolated()
    print(f"Liên thông (bỏ qua đỉnh cô lập)? {connected}")

    condition_kind, reasons = g.check_euler_conditions()
    print("Kiểm tra điều kiện Euler:")
    for reason in reasons:
        print(f"  - {reason}")

    trail, kind = g.find_euler_trail()

    if kind == 'circuit':
        print(">> Đây LÀ đồ thị Euler, tồn tại CHU TRÌNH EULER.")
        print("   Chu trình tìm được:", describe_edges(trail))
    elif kind == 'path':
        print(">> Đây LÀ đồ thị nửa-Euler (semi-Eulerian), tồn tại ĐƯỜNG ĐI EULER")
        print("   (không có chu trình Euler).")
        print("   Đường đi tìm được:", describe_edges(trail))
    else:
        print(">> Đây KHÔNG phải là đồ thị Euler (không có chu trình lẫn đường đi Euler).")
    print()


def run_condition_tests():
    """Kiểm tra các trường hợp chính của định lý Euler."""
    test_cases = [
        (
            'chu trình Euler',
            ['A', 'B', 'C'],
            [('A', 'B'), ('B', 'C'), ('C', 'A')],
            'circuit',
        ),
        (
            'đường đi Euler',
            ['A', 'B', 'C'],
            [('A', 'B'), ('B', 'C')],
            'path',
        ),
        (
            'quá nhiều đỉnh bậc lẻ',
            ['A', 'B', 'C', 'D'],
            [('A', 'B'), ('A', 'C'), ('A', 'D')],
            'none',
        ),
        (
            'không liên thông',
            ['A', 'B', 'C', 'D'],
            [('A', 'B'), ('C', 'D')],
            'none',
        ),
        (
            'không có cạnh',
            ['A', 'B'],
            [],
            'none',
        ),
    ]

    for name, vertices, edge_list, expected in test_cases:
        graph = Graph(vertices)
        for u, v in edge_list:
            graph.add_edge(u, v)
        actual = graph.classify()
        assert actual == expected, (
            f'{name}: mong đợi {expected}, nhận được {actual}'
        )

    print(f'Đã đạt {len(test_cases)}/{len(test_cases)} test điều kiện Euler.')


def read_graph_from_input():
    """Nhập một đồ thị vô hướng từ bàn phím."""
    print("NHẬP DỮ LIỆU ĐỒ THỊ EULER")
    print("Ví dụ một đồ thị tam giác:")
    print("  Tên đỉnh: A B C")
    print("  Số cạnh: 3")
    print("  Cạnh 1: A B")
    print("  Cạnh 2: B C")
    print("  Cạnh 3: C A")
    print("Lưu ý: mỗi cạnh nhập đúng 2 tên đỉnh, cách nhau bằng dấu cách.")

    while True:
        vertices = input("Nhập tên các đỉnh (ví dụ: A B C): ").split()
        if vertices and len(vertices) == len(set(vertices)):
            break
        print("Danh sách đỉnh không được rỗng hoặc trùng tên. Vui lòng nhập lại.")

    vertex_set = set(vertices)
    while True:
        try:
            edge_count = int(input("Nhập số lượng cạnh (ví dụ: 3): "))
            if edge_count < 0:
                raise ValueError
            break
        except ValueError:
            print("Số lượng cạnh phải là một số nguyên không âm.")

    edge_list = []
    print("Nhập từng cạnh theo dạng: đỉnh_đầu đỉnh_cuối (ví dụ: A B)")
    for index in range(edge_count):
        while True:
            edge = input(f"Cạnh {index + 1}/{edge_count}: ").split()
            if len(edge) == 2 and all(vertex in vertex_set for vertex in edge):
                edge_list.append((edge[0], edge[1]))
                break
            print("Cạnh phải gồm đúng 2 đỉnh đã có trong danh sách. Vui lòng nhập lại.")

    return vertices, edge_list


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        run_condition_tests()
    else:
        vertices, edge_list = read_graph_from_input()
        run_test("Đồ thị do người dùng nhập", vertices, edge_list)
        graph = Graph(vertices)
        for u, v in edge_list:
            graph.add_edge(u, v)
        trail, _ = graph.find_euler_trail()
        draw_graph(vertices, edge_list, trail)