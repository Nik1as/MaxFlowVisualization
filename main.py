import math
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from tabulate import tabulate

import max_flow
import random_graph
import utils

ALGORITHMS_MAP = {"Ford-Fulkerson": max_flow.ford_fulkerson,
                  "Edmonds-Karp": max_flow.edmonds_karp,
                  "Capacity Scaling": max_flow.capacity_scaling,
                  "Dinic": max_flow.dinic,
                  "Goldberg-Tarjan": max_flow.goldberg_tarjan
                  }
ALGORITHMS = list(ALGORITHMS_MAP.keys())


class Visualization(tk.Frame):
    DEFAULT_NODES = 16
    DEFAULT_MAX_CAPACITY = 10
    NODE_RADIUS = 20
    TEXT_OFFSET = 25
    ANGLE = 10

    def __init__(self, parent):
        super().__init__(parent)

        config_bar = tk.Frame(self)

        self.algo_variable = tk.StringVar(config_bar)
        self.algo_variable.set(ALGORITHMS[0])

        self.opt_algorithm = tk.OptionMenu(config_bar, self.algo_variable, *ALGORITHMS)
        self.opt_algorithm.config(width=20)
        self.opt_algorithm.grid(row=0, column=0, padx=10)
        self.max_flow_algo = None

        lbl_nodes = tk.Label(master=config_bar, text="Nodes:")
        lbl_nodes.grid(row=0, column=1)

        self.ent_nodes = tk.Entry(master=config_bar, width=10)
        self.ent_nodes.insert(0, str(self.DEFAULT_NODES))
        self.ent_nodes.grid(row=0, column=2, padx=5)

        lbl_nodes = tk.Label(master=config_bar, text="Capacity:")
        lbl_nodes.grid(row=0, column=3)

        self.ent_capacity = tk.Entry(master=config_bar, width=10)
        self.ent_capacity.insert(0, str(self.DEFAULT_MAX_CAPACITY))
        self.ent_capacity.grid(row=0, column=4, padx=5)

        self.btn_reset = tk.Button(text="reset", master=config_bar, command=self.reset)
        self.btn_reset.grid(row=0, column=5, padx=10)

        self.btn_reset = tk.Button(text="generate", master=config_bar, command=self.generate)
        self.btn_reset.grid(row=0, column=6, padx=10)

        self.btn_step = tk.Button(text="step", master=config_bar, command=self.step)
        self.btn_step.grid(row=0, column=7, padx=10)

        self.ent_time = utils.EntryWithPlaceholder(master=config_bar, placeholder="interval in ms")
        self.ent_time.grid(row=0, column=8, padx=10)

        self.btn_start = tk.Button(text="start", master=config_bar, command=self.start)
        self.btn_start.grid(row=0, column=9, padx=10)

        self.btn_stop = tk.Button(text="stop", master=config_bar, command=self.stop)
        self.btn_stop.grid(row=0, column=10, padx=10)

        self.btn_help = tk.Button(text="help", master=config_bar, command=self.help)
        self.btn_help.grid(row=0, column=11, padx=11)

        config_bar.pack(anchor=tk.N)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(anchor=tk.CENTER, expand=True, fill="both")

        self._jop = None

        self.source, self.target, self.graph = random_graph.generate(self.DEFAULT_NODES, self.DEFAULT_MAX_CAPACITY)
        self.graph.reset()

        self.after(100, self.render)

    def clear_canvas(self):
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()

        self.canvas.create_rectangle(0, 0, width, height, fill="white")

    def render(self):
        self.clear_canvas()
        self.render_nodes()

        for edge in self.graph.get_base_edges():
            self.render_edge(edge.start, edge.end, "black")

    def render_nodes(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for node in self.graph.get_nodes():
            absolute_x, absolute_y = utils.absolute_position(node, width, height)

            if node.node_id == self.source:
                color = "blue"
            elif node.node_id == self.target:
                color = "purple"
            else:
                color = "black"

            self.canvas.create_oval(absolute_x - self.NODE_RADIUS, absolute_y - self.NODE_RADIUS,
                                    absolute_x + self.NODE_RADIUS, absolute_y + self.NODE_RADIUS,
                                    fill=color)

    def render_single_edge(self, start: int, end: int, residual_capacity: int, prev_residual_capacity: int, color: str):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        x1, y1, x2, y2 = utils.edge_positions(
            utils.Point(*utils.absolute_position(self.graph.get_node(start), width, height)),
            utils.Point(*utils.absolute_position(self.graph.get_node(end), width, height)),
            self.NODE_RADIUS)

        self.canvas.create_line(x1, y1,
                                x2, y2,
                                width=3, fill=color, arrow=tk.LAST, arrowshape=(10, 15, 5))

        p1 = utils.Point(x1, y1)
        p2 = utils.Point(x2, y2)
        self.canvas.create_text(*utils.text_position(p1, p2, self.TEXT_OFFSET),
                                text=utils.edge_text(residual_capacity, prev_residual_capacity))

    def render_double_edge(self, start: int, end: int, residual_capacity: int, prev_residual_capacity: int, color: str):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        node1 = utils.Point(*utils.absolute_position(self.graph.get_node(start), width, height))
        node2 = utils.Point(*utils.absolute_position(self.graph.get_node(end), width, height))

        x1, y1, x2, y2 = utils.edge_positions(node1,
                                              node2,
                                              self.NODE_RADIUS)

        p1 = utils.Point(*utils.rotate(node1, utils.Point(x1, y1), math.radians(self.ANGLE)))
        p2 = utils.Point(*utils.rotate(node2, utils.Point(x2, y2), math.radians(-self.ANGLE)))

        self.canvas.create_line(p1.x, p1.y,
                                p2.x, p2.y,
                                width=3, fill=color, arrow=tk.LAST, arrowshape=(10, 15, 5))
        self.canvas.create_text(*utils.text_position(p1, p2, self.TEXT_OFFSET),
                                text=utils.edge_text(residual_capacity, prev_residual_capacity))

    def render_edge(self, start: int, end: int, color: str):
        residual_capacity, prev_residual_capacity = utils.aggregated_edge_values(self.graph, start, end)
        residual_capacity_reverse, prev_residual_capacity_reverse = utils.aggregated_edge_values(self.graph, end, start)

        if residual_capacity > 0 and residual_capacity_reverse > 0:
            self.render_double_edge(start, end, residual_capacity, prev_residual_capacity, color)
            self.render_double_edge(end, start, residual_capacity_reverse, prev_residual_capacity_reverse, color)
        elif residual_capacity > 0:
            self.render_single_edge(start, end, residual_capacity, prev_residual_capacity, color)
        elif residual_capacity_reverse > 0:
            self.render_single_edge(end, start, residual_capacity_reverse, prev_residual_capacity_reverse, color)

    def render_dinic(self, edges, level):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for node in self.graph.get_nodes():
            position = utils.absolute_position(node, width, height)
            if level[node.node_id] >= 0:
                self.canvas.create_text(*position,
                                        text=f"{level[node.node_id]}",
                                        fill="white",
                                        font=("Helvetica", "10", "bold"))

        n = self.graph.number_of_nodes()
        for start in range(n):
            for end in range(start + 1, n):
                if self.graph.has_edge(start, end):
                    color = "light grey"
                    if (level[start] + 1 == level[end] or level[end] + 1 == level[start]) and level[start] != -1 and level[end] != -1:
                        color = "black"
                    if utils.contains_edge(edges, start, end) or utils.contains_edge(edges, end, start):
                        color = "red"
                    self.render_edge(start, end, color)

    def render_goldberg_tarjan(self, edges, excess, label, node_id):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for node in self.graph.get_nodes():
            position = utils.absolute_position(node, width, height)
            self.canvas.create_text(*position,
                                    text=f"{label[node.node_id]} | {excess[node.node_id]}",
                                    fill="white",
                                    font=("Helvetica", "10", "bold"))

        absolute_x, absolute_y = utils.absolute_position(self.graph.get_node(node_id), width, height)
        self.canvas.create_oval(absolute_x - self.NODE_RADIUS, absolute_y - self.NODE_RADIUS,
                                absolute_x + self.NODE_RADIUS, absolute_y + self.NODE_RADIUS,
                                outline="red", width=3)

        n = self.graph.number_of_nodes()
        for start in range(n):
            for end in range(start + 1, n):
                if self.graph.has_edge(start, end):
                    color = "red" if utils.contains_edge(edges, start, end) or utils.contains_edge(edges, end, start) else "black"
                    self.render_edge(start, end, color)

    def render_ford_fulkerson(self, edges):
        n = self.graph.number_of_nodes()
        for start in range(n):
            for end in range(start + 1, n):
                if self.graph.has_edge(start, end):
                    color = "red" if utils.contains_edge(edges, start, end) or utils.contains_edge(edges, end, start) else "black"
                    self.render_edge(start, end, color)

    def render_step(self, result):
        self.render()

        match self.algo_variable.get():
            case "Dinic":
                self.render_dinic(*result)
            case "Goldberg-Tarjan":
                self.render_goldberg_tarjan(*result)
            case _:
                self.render_ford_fulkerson(result)

    def render_result(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.clear_canvas()
        self.render_nodes()

        for edge in self.graph.get_base_edges():
            node1 = utils.Point(*utils.absolute_position(self.graph.get_node(edge.start), width, height))
            node2 = utils.Point(*utils.absolute_position(self.graph.get_node(edge.end), width, height))

            x1, y1, x2, y2 = utils.edge_positions(node1,
                                                  node2,
                                                  self.NODE_RADIUS)

            self.canvas.create_line(x1, y1, x2, y2, width=3, fill="black", arrow=tk.LAST, arrowshape=(10, 15, 5))

            text_x, text_y = utils.text_position(utils.Point(x1, y1), utils.Point(x2, y2), 0)
            offset = 20
            self.canvas.create_rectangle(text_x - offset, text_y - offset,
                                         text_x + offset, text_y + offset,
                                         fill="white", outline="")
            self.canvas.create_text(text_x, text_y,
                                    text=f"{edge.flow}/{edge.capacity}")

    def algorithm_terminated(self):
        self.btn_stop["state"] = tk.DISABLED
        self.btn_step["state"] = tk.DISABLED
        self.btn_start["state"] = tk.DISABLED
        self.ent_time["state"] = tk.DISABLED
        self.render()
        if self._jop is not None:
            window.after_cancel(self._jop)
            self._jop = None

        messagebox.showinfo("Info", f"algorithm terminated!\nmax-flow value: {utils.flow_value(self.graph, self.source)}")

    def reset(self):
        if self._jop is not None:
            window.after_cancel(self._jop)
            self._jop = None

        self.graph.reset()
        self.graph.reset()

        self.max_flow_algo = None
        self.render()

        self.opt_algorithm["state"] = tk.NORMAL
        self.btn_step["state"] = tk.NORMAL
        self.btn_start["state"] = tk.NORMAL
        self.btn_stop["state"] = tk.NORMAL
        self.ent_time["state"] = tk.NORMAL

    def generate(self):
        self.reset()

        try:
            n = int(self.ent_nodes.get())
            capacity = int(self.ent_capacity.get())

            self.source, self.target, self.graph = random_graph.generate(n, capacity)
            self.graph.reset()
            self.render()

            self.max_flow_algo = None
        except ValueError:
            messagebox.showerror("Error", "nodes and capacity must be integers")

    def step(self):
        for edge in self.graph.get_edges():
            edge.prev_flow = edge.residual_capacity()

        if self.max_flow_algo is None:
            self.max_flow_algo = ALGORITHMS_MAP[self.algo_variable.get()](self.graph, self.source, self.target)
            self.opt_algorithm["state"] = tk.DISABLED

        try:
            result = next(self.max_flow_algo)
            self.render_step(result)
        except StopIteration:
            self.algorithm_terminated()

    def start(self):
        try:
            interval = int(self.ent_time.get())

            self.opt_algorithm["state"] = tk.DISABLED
            self.btn_step["state"] = tk.DISABLED
            self.btn_start["state"] = tk.DISABLED
            self.ent_time["state"] = tk.DISABLED

            self._jop = window.after(interval, self.start)
            self.step()
        except ValueError:
            messagebox.showerror("Error", "interval must be an integer")

    def stop(self):
        self.btn_step["state"] = tk.NORMAL
        self.btn_start["state"] = tk.NORMAL
        self.ent_time["state"] = tk.NORMAL

        if self._jop is not None:
            window.after_cancel(self._jop)
            self._jop = None

    def help(self):
        messagebox.showinfo("Help", """
Max-Flow Algorithms Visualization

notation:
n: number of nodes
m: number of edges
F: max-flow value
C: max capacity

implemented algorithms:
Ford-Fulkerson: O(m F)
Edmonds-Karp: O(n m^2)
Capacity Scaling: O(n m logC)
Dinic: O(m n^2)
Goldberg-Tarjan: O(n^3)

node colors:
source: blue
target: purple

node text:
Dinic: distance
Goldberg-Tarjan: label and excess
""")


class TestEnvironment(tk.Frame):
    EDGE_CHANGES = 5

    def __init__(self, parent):
        super().__init__(parent)

        self.btn_start = tk.Button(text="start", master=self, command=self.start_test)
        self.btn_start.pack(fill="x")

        lbl_info = tk.Label(text="Please enter one comma separated triple per line: instances, nodes, capacity",
                            master=self)
        lbl_info.pack(fill="x")

        self.txt_triples = tk.Text(master=self)
        self.txt_triples.insert(tk.END, "10, 5, 20")
        self.txt_triples.pack(fill="x")

        scroll_output = tk.Scrollbar(orient="vertical", master=self)
        scroll_output.pack(side=tk.RIGHT, fill="both")

        self.txt_output = tk.Text(yscrollcommand=scroll_output.set, master=self)
        self.txt_output.tag_configure("center", justify="center")
        self.txt_output.config(state=tk.DISABLED)
        scroll_output.config(command=self.txt_output.yview)
        self.txt_output.pack(fill="both", expand=True)

    def start_test(self):
        self.txt_output.config(state=tk.NORMAL)
        self.txt_output.delete(1.0, "end-1c")

        triples = self.txt_triples.get(1.0, "end-1c")
        for line in triples.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                instances, nodes, capacity = map(int, line.split(","))
                self.test_triple(instances, nodes, capacity)
            except ValueError:
                messagebox.showerror("Error", "invalid input")
                return

            self.txt_output.insert("end-1c", "\n\n")
        self.txt_output.config(state=tk.DISABLED)

    def test_triple(self, instances: int, nodes: int, capacity: int):
        self.txt_output.insert("end-1c", f"instances: {instances}\nnodes: {nodes}\ncapacity: {capacity}\n")

        for _ in range(instances):
            source, target, graph = random_graph.generate(nodes, capacity)

            results = []
            flow_values = []

            for name, algo_func in ALGORITHMS_MAP.items():
                graph.reset()

                for _ in algo_func(graph, source, target):
                    pass

                # capacity bound check
                capacity_bound = True
                flow_in = [0 for _ in range(graph.number_of_nodes())]
                flow_out = [0 for _ in range(graph.number_of_nodes())]

                for edge in graph.get_edges():
                    if not edge.reverse:
                        flow_out[edge.start] += edge.flow
                        flow_in[edge.end] += edge.flow
                        if edge.flow > edge.capacity:
                            capacity_bound = False

                # flow preservation check
                flow_preservation = all(flow_in[i] == flow_out[i] for i in range(graph.number_of_nodes())
                                        if i not in (source, target))

                saturated_cut = max_flow.bfs(graph, source, target) is None

                flow = flow_out[source] - flow_in[source]
                flow_values.append(flow)

                results.append([name, flow_preservation, capacity_bound, saturated_cut, flow])

            # change edge values (capacities)
            change_capacity_passed = True
            if len(set(flow_values)) == 1:
                flow_value = flow_values[0]

                for _ in range(self.EDGE_CHANGES):
                    graph_copy = graph.copy()
                    edge = random.choice(graph_copy.get_base_edges())
                    capacity_change = random.randint(1, capacity)

                    flow_values = []

                    edge.capacity += capacity_change

                    for name, algo_func in ALGORITHMS_MAP.items():
                        graph_copy.reset()
                        for _ in algo_func(graph_copy, source, target):
                            pass
                        flow_value_new = utils.flow_value(graph_copy, source)
                        flow_values.append(flow_value_new)

                        if not (flow_value <= flow_value_new <= flow_value + capacity_change):
                            change_capacity_passed = False

                    if len(set(flow_values)) != 1:
                        change_capacity_passed = False

            self.txt_output.insert("end-1c", "\n" +
                                   tabulate(results,
                                            headers=["Algorithm", "flow preservation", "capacity bound", "saturated cut", "max flow"],
                                            tablefmt="fancy_grid") +
                                   "\n" +
                                   f"identical max flow value: {len(set(flow_values)) == 1}\n" +
                                   f"edge value changes passed: {change_capacity_passed}\n")

            self.txt_output.tag_add("center", "1.0", "end")


window = tk.Tk()
window.title("Max-Flow Algorithms")

window_width = 1200
window_height = 1200
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
screen_x = int((screen_width / 2) - (window_width / 2))
screen_y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{window_width}x{window_height}+{screen_x}+{screen_y}")

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

style = ttk.Style(window)
style.configure("TNotebook.Tab", width=window.winfo_screenwidth())

tabs = ttk.Notebook(window)

frame_visualization = Visualization(tabs)
frame_visualization.pack()
tabs.add(frame_visualization, text="Visualization")

frame_test_environment = TestEnvironment(tabs)
frame_test_environment.pack()
tabs.add(frame_test_environment, text="Test environment")

tabs.pack(expand=True, fill="both")

window.mainloop()
