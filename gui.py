import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from tabulate import tabulate

import graph
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
    DEFAULT_NODES = 10
    DEFAULT_MAX_CAPACITY = 10
    NODE_RADIUS = 8

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

        self.btn_step = tk.Button(text="step", master=config_bar, command=self.step)
        self.btn_step.grid(row=0, column=6, padx=10)

        self.ent_time = utils.EntryWithPlaceholder(master=config_bar, placeholder="intervall in ms")
        self.ent_time.grid(row=0, column=7, padx=10)

        self.btn_start = tk.Button(text="start", master=config_bar, command=self.start)
        self.btn_start.grid(row=0, column=8, padx=10)

        self.btn_stop = tk.Button(text="stop", master=config_bar, command=self.stop)
        self.btn_stop.grid(row=0, column=9, padx=10)

        self.btn_help = tk.Button(text="help", master=config_bar, command=self.help)
        self.btn_help.grid(row=0, column=9, padx=11)

        config_bar.pack(anchor=tk.N)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(anchor=tk.CENTER, expand=True, fill="both")

        self._jop = None

        self.graph = random_graph.generate(self.DEFAULT_NODES, self.DEFAULT_MAX_CAPACITY)
        self.source, self.target = utils.get_source_and_target(self.graph)

        self.after(100, self.render)

    def render(self):
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()

        self.canvas.create_rectangle(0, 0, width, height, fill="white")

        self.render_edges()
        self.render_nodes()
        self.render_text()

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

    def render_text(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for edge in self.graph.get_edges():
            if not edge.reverse:
                p1 = utils.absolute_position(self.graph.get_nodes()[edge.start], width, height)
                p2 = utils.absolute_position(self.graph.get_nodes()[edge.end], width, height)

                offset = 10
                text_x = (p1[0] + p2[0]) // 2
                text_y = (p1[1] + p2[1]) // 2
                self.canvas.create_rectangle(text_x - offset, text_y - offset,
                                             text_x + offset, text_y + offset,
                                             fill="white", outline="white")
                self.canvas.create_text(text_x, text_y, text=f"{edge.flow}/{edge.capacity}")

    def get_edge_positions(self, edge: graph.Edge):
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()

        x1, y1 = utils.absolute_position(self.graph.get_nodes()[edge.start], window_width, window_height)
        x2, y2 = utils.absolute_position(self.graph.get_nodes()[edge.end], window_width, window_height)

        dx, dy = x2 - x1, y2 - y1
        length = (dx ** 2 + dy ** 2) ** 0.5

        dx /= length
        dy /= length

        x1, y1 = x1 + dx * self.NODE_RADIUS, y1 + dy * self.NODE_RADIUS
        x2, y2 = x2 - dx * self.NODE_RADIUS, y2 - dy * self.NODE_RADIUS

        return x1, y1, x2, y2

    def render_edges(self):
        for edge in self.graph.get_edges():
            if not edge.reverse:
                x1, y1, x2, y2 = self.get_edge_positions(edge)
                self.canvas.create_line(x1, y1, x2, y2, width=3, fill="black", arrow=tk.LAST, arrowshape=(10, 15, 5))

    def render_step(self, result):
        self.render()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        match self.algo_variable.get():
            case "Dinic":
                edges, level = result
                for node in self.graph.get_nodes():
                    position = utils.absolute_position(node, width, height)
                    self.canvas.create_text(*position,
                                            text=f"{level[node.node_id]}",
                                            fill="white",
                                            font=("Helvetica", "10", "bold"))
            case "Goldberg-Tarjan":
                edges = []  # todo
            case _:
                edges = result

        for edge in edges:
            x1, y1, x2, y2 = self.get_edge_positions(edge)
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill="red", arrow=tk.LAST, arrowshape=(10, 15, 5))
        self.render_text()

    def algorithm_terminated(self):
        self.btn_stop["state"] = tk.DISABLED
        self.btn_step["state"] = tk.DISABLED
        self.btn_start["state"] = tk.DISABLED
        self.ent_time["state"] = tk.DISABLED
        self.render()
        if self._jop is not None:
            window.after_cancel(self._jop)
            self._jop = None
        flow_value = sum(e.flow for e in self.graph.get_edges_by_node(self.source))
        messagebox.showinfo("Info", f"algorithm terminated!\nmax-flow value: {flow_value}")

    def reset(self):
        try:
            n = int(self.ent_nodes.get())
            capacity = int(self.ent_capacity.get())

            self.graph = random_graph.generate(n, capacity)
            self.source, self.target = utils.get_source_and_target(self.graph)
            self.render()

            self.opt_algorithm["state"] = tk.NORMAL
            self.btn_step["state"] = tk.NORMAL
            self.btn_start["state"] = tk.NORMAL
            self.btn_stop["state"] = tk.NORMAL
            self.ent_time["state"] = tk.NORMAL

            self.max_flow_algo = None
        except ValueError:
            messagebox.showerror("Error", "nodes and capacity must be an integer")

    def step(self):
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
            intervall = int(self.ent_time.get())

            self.opt_algorithm["state"] = tk.DISABLED
            self.btn_step["state"] = tk.DISABLED
            self.btn_start["state"] = tk.DISABLED
            self.ent_time["state"] = tk.DISABLED

            self._jop = window.after(intervall, self.start)
            self.step()
        except ValueError:
            messagebox.showerror("Error", "intervall must be an integer")

    def stop(self):
        self.btn_step["state"] = tk.NORMAL
        self.ent_time["state"] = tk.NORMAL

        if self._jop is not None:
            window.after_cancel(self._jop)
            self._jop = None

    def help(self):
        messagebox.showinfo("Help", """
Max-Flow Algorithms Visualization

notation:
n: number of nodes\tm: number of edges
F: max-flow value\tC: max capacity

implemented algorithms:
Ford-Fulkerson: O(m F)
Edmonds-Karp: O(n m^2)
Capacity Scaling: O(n m logC)
Dinic: O(m n^2)
Goldberg-Tarjan: O(n^3)

source: blue
target: purple
edge labels: flow/capacity
""")


class TestEnviroment(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.btn_start = tk.Button(text="start", master=self, command=self.start_test)
        self.btn_start.pack(fill="x")

        lbl_info = tk.Label(text="Please enter one comma separated triple per line: instances, nodes, capacity",
                            master=self)
        lbl_info.pack(fill="x")

        self.txt_triples = tk.Text(master=self)
        self.txt_triples.insert(tk.END, "10, 5, 5")
        self.txt_triples.pack(fill="x")

        scroll_output = tk.Scrollbar(orient='vertical', master=self)
        scroll_output.pack(side=tk.RIGHT, fill='both')

        self.txt_output = tk.Text(yscrollcommand=scroll_output.set, master=self)
        scroll_output.config(command=self.txt_output.yview)
        self.txt_output.pack(fill="both")

    def start_test(self):
        self.txt_output.delete(1.0, "end-1c")

        triples = self.txt_triples.get(1.0, "end-1c")
        for line in triples.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                instances, nodes, capacity = map(int, line.split(","))
            except ValueError:
                messagebox.showerror("Error", "invalid input")
                return

            for _ in range(instances):
                graph = random_graph.generate(nodes, capacity)
                source, target = utils.get_source_and_target(graph)

                result = [["Algorithm", "flow preservation", "capacity bound", "max flow"]]
                flow_values = []

                for name, algo_func in ALGORITHMS_MAP.items():
                    result_graph = graph.copy()
                    algo = algo_func(result_graph, source, target)

                    for _ in algo:
                        pass

                    # capacity bound check
                    capacity_bound = True
                    flow_in = [0 for _ in range(result_graph.number_of_nodes())]
                    flow_out = [0 for _ in range(result_graph.number_of_nodes())]

                    for edge in result_graph.get_edges():
                        if not edge.reverse:
                            flow_out[edge.start] += edge.flow
                            flow_in[edge.end] += edge.flow
                            if edge.flow > edge.capacity:
                                capacity_bound = False

                    # flow preservation check
                    flow_preservation = all(flow_in[i] == flow_out[i] for i in range(result_graph.number_of_nodes())
                                            if i not in (source, target))

                    flow = sum(edge.flow for edge in result_graph.get_edges() if not edge.reverse)
                    flow_values.append(flow)

                    result.append([name, flow_preservation, capacity_bound, flow])

                self.txt_output.insert("end-1c", "\n" +
                                       tabulate(result, headers="firstrow", tablefmt="fancy_grid") +
                                       f"\nidetical max flow: {len(set(flow_values)) == 1}\n")


window = tk.Tk()
window.title("Max-Flow Algorithms")

width = 1200
height = 800
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = int((screen_width / 2) - (width / 2))
y = int((screen_height / 2) - (height / 2))
window.geometry(f"{width}x{height}+{x}+{y}")

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

style = ttk.Style(window)
style.configure("TNotebook.Tab", width=window.winfo_screenwidth())

tabs = ttk.Notebook(window)

frame_visualization = Visualization(tabs)
frame_visualization.pack()
tabs.add(frame_visualization, text="Visualization")

frame_test_envoirement = TestEnviroment(tabs)
frame_test_envoirement.pack()
tabs.add(frame_test_envoirement, text="Test enviroment")

tabs.pack(expand=True, fill="both")

window.mainloop()
