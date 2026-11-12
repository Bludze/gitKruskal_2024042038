# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import math

MAX = 100

class Edge:
    def __init__(self, start, end, weight):
        self.start = start
        self.end = end
        self.weight = weight

class Graph:
    def __init__(self):
        self.numVertices = 0
        self.numEdges = 0
        self.maxEdges = 0
        self.edges = []
    
    def initGraph(self, vertices, max_edges):
        self.numVertices = vertices
        self.numEdges = 0
        self.maxEdges = max_edges
        self.edges = []
    
    def addEdge(self, s, e, w):
        # 检查是否已存在相同顶点对的无向边（不考虑方向）
        for edge in self.edges:
            if (edge.start == s and edge.end == e) or (edge.start == e and edge.end == s):
                edge.weight = w  # 覆盖更新权重
                return 1  # 返回1表示覆盖更新
        
        # 不存在该边，正常添加
        if self.numEdges >= self.maxEdges:
            return -1  # 超出容量
        self.edges.append(Edge(s, e, w))
        self.numEdges += 1
        return 0  # 返回0表示新增成功

def findSet(parent, x):
    if parent[x] != x:
        parent[x] = findSet(parent, parent[x])
    return parent[x]

def unionSet(parent, rank, x, y):
    rx = findSet(parent, x)
    ry = findSet(parent, y)
    if rx == ry:
        return False
    if rank[rx] < rank[ry]:
        parent[rx] = ry
    elif rank[rx] > rank[ry]:
        parent[ry] = rx
    else:
        parent[ry] = rx
        rank[rx] += 1
    return True

class KruskalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("克鲁斯卡尔算法 - 最小生成树")
        self.root.geometry("900x700")
        
        self.graph = Graph()
        self.canvas = None
        self.vertex_positions = {}
        self.mst_edges = []
        self.step_index = 0
        self.animation_steps = []
        self.is_paused = False
        self.after_id = None
        self.is_playing = False
        self.steps_precomputed = False
        self.mst_edges_history = []
        self.info_text_history = []
        self.status_history = []
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        input_frame = ttk.LabelFrame(main_frame, text="图设置", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="顶点数:").grid(row=0, column=0, padx=5, pady=5)
        self.vertex_entry = ttk.Entry(input_frame, width=10)
        self.vertex_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="边数:").grid(row=0, column=2, padx=5, pady=5)
        self.edge_entry = ttk.Entry(input_frame, width=10)
        self.edge_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(input_frame, text="初始化图", command=self.init_graph).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(input_frame, text="加载预设图", command=self.load_preset_graph).grid(row=0, column=5, padx=5, pady=5)
        
        edge_input_frame = ttk.LabelFrame(main_frame, text="边输入", padding="10")
        edge_input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(edge_input_frame, text="起点:").grid(row=0, column=0, padx=5, pady=5)
        self.start_entry = ttk.Entry(edge_input_frame, width=8)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edge_input_frame, text="终点:").grid(row=0, column=2, padx=5, pady=5)
        self.end_entry = ttk.Entry(edge_input_frame, width=8)
        self.end_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(edge_input_frame, text="权重:").grid(row=0, column=4, padx=5, pady=5)
        self.weight_entry = ttk.Entry(edge_input_frame, width=8)
        self.weight_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(edge_input_frame, text="添加边", command=self.add_edge).grid(row=0, column=6, padx=5, pady=5)
        
        self.canvas = tk.Canvas(main_frame, width=600, height=400, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.grid(row=2, column=0, pady=10)
        
        control_frame = ttk.LabelFrame(main_frame, text="控制", padding="10")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="开始", command=self.run_kruskal).grid(row=0, column=0, padx=5, pady=5)
        self.pause_button = ttk.Button(control_frame, text="暂停", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5, pady=5)
        self.prev_button = ttk.Button(control_frame, text="上一步", command=self.prev_step, state=tk.DISABLED)
        self.prev_button.grid(row=0, column=2, padx=5, pady=5)
        self.next_button = ttk.Button(control_frame, text="下一步", command=self.next_step, state=tk.DISABLED)
        self.next_button.grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(control_frame, text="从头开始", command=self.reset_algorithm).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(control_frame, text="重置边", command=self.reset_edges).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(control_frame, text="清空", command=self.clear_all).grid(row=0, column=6, padx=5, pady=5)
        
        self.info_text = tk.Text(main_frame, height=5, width=80)
        self.info_text.grid(row=4, column=0, pady=5)
        
        self.status_label = ttk.Label(main_frame, text="状态: 就绪")
        self.status_label.grid(row=5, column=0, pady=5)
    
    def init_graph(self):
        try:
            n = int(self.vertex_entry.get())
            m = int(self.edge_entry.get())
            
            if n <= 0 or n > MAX:
                messagebox.showerror("错误", f"顶点数必须在1到{MAX}之间")
                return
            if m < 0 or m > MAX:
                messagebox.showerror("错误", f"边数必须在0到{MAX}之间")
                return
            
            # 【新增】校验顶点数与边数的关系：n个顶点的简单图最多有 n*(n-1)/2 条边
            max_possible_edges = n * (n - 1) // 2
            if m > max_possible_edges:
                messagebox.showerror("错误", f"边数过多，{n}个顶点最多{max_possible_edges}条边")
                return
            
            self.graph.initGraph(n, m)
            self.vertex_positions = {}
            self.mst_edges = []
            self.animation_steps = []
            self.step_index = 0
            
            self.calculate_vertex_positions(n)
            self.draw_graph()
            self.update_status(f"图已初始化: {n}个顶点，{m}条边，请添加边")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"图已初始化，顶点数: {n}，边数限制: {m}\n")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")
    
    def calculate_vertex_positions(self, n):
        center_x, center_y = 300, 200
        radius = 150
        
        for i in range(1, n + 1):
            angle = 2 * math.pi * (i - 1) / n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.vertex_positions[i] = (x, y)
    
    def draw_graph(self):
        self.canvas.delete("all")
        
        for edge in self.graph.edges:
            x1, y1 = self.vertex_positions[edge.start]
            x2, y2 = self.vertex_positions[edge.end]
            
            is_mst = False
            for mst_edge in self.mst_edges:
                if (edge.start == mst_edge.start and edge.end == mst_edge.end) or \
                   (edge.start == mst_edge.end and edge.end == mst_edge.start):
                    is_mst = True
                    break
            
            color = "red" if is_mst else "black"
            width = 3 if is_mst else 1
            
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y - 10, text=str(edge.weight), 
                                   fill=color, font=("Arial", 10, "bold"))
        
        for v, (x, y) in self.vertex_positions.items():
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="white", outline="blue", width=2)
            self.canvas.create_text(x, y, text=str(v), fill="blue", font=("Arial", 12, "bold"))
    
    def add_edge(self):
        try:
            start = int(self.start_entry.get())
            end = int(self.end_entry.get())
            weight = int(self.weight_entry.get())
            
            if start < 1 or start > self.graph.numVertices:
                messagebox.showerror("错误", f"起点必须在1到{self.graph.numVertices}之间")
                return
            if end < 1 or end > self.graph.numVertices:
                messagebox.showerror("错误", f"终点必须在1到{self.graph.numVertices}之间")
                return
            if start == end:
                messagebox.showerror("错误", "起点和终点不能相同（不允许自环边）")
                return
            if weight <= 0:
                messagebox.showerror("错误", "权重必须大于0")
                return
            
            result = self.graph.addEdge(start, end, weight)
            if result == -1:
                messagebox.showerror("错误", "边数已达到上限")
                return
            
            # 根据返回值显示不同提示
            self.draw_graph()
            if result == 1:
                self.info_text.insert(tk.END, f"更新边: {start} -- {end} (新权重: {weight})\n")
            else:
                self.info_text.insert(tk.END, f"添加边: {start} -- {end} (权重: {weight})\n")
            
            self.start_entry.delete(0, tk.END)
            self.end_entry.delete(0, tk.END)
            self.weight_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")
    
    def run_kruskal(self):
        if self.graph.numVertices <= 0:
            messagebox.showerror("错误", "请先初始化图")
            return
        if self.graph.numEdges == 0:
            messagebox.showerror("错误", "请添加边")
            return
        
        # 重置状态
        self.is_paused = False
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        self.animation_steps = []
        self.mst_edges_history = []
        self.info_text_history = []
        self.status_history = []
        self.step_index = 0
        self.mst_edges = []
        
        n = self.graph.numVertices
        m = self.graph.numEdges
        
        sorted_edges = sorted(self.graph.edges, key=lambda e: e.weight)
        
        parent = list(range(n + 1))
        rank = [0] * (n + 1)
        
        mst_result = []
        current_info_text = ""
        current_status = ""
        
        # 步骤0: 初始状态
        self.mst_edges_history.append([])
        current_info_text = "开始克鲁斯卡尔算法\n"
        current_status = "开始克鲁斯卡尔算法"
        self.info_text_history.append(current_info_text)
        self.status_history.append(current_status)
        self.animation_steps.append(("init",))
        
        # 步骤1: 开始排序
        self.mst_edges_history.append([])
        current_info_text += "按权重排序所有边\n"
        current_status = "按权重排序所有边"
        self.info_text_history.append(current_info_text)
        self.status_history.append(current_status)
        self.animation_steps.append(("sort_start",))
        
        # 步骤2~m+1: 排序过程高亮
        for i, edge in enumerate(sorted_edges):
            self.mst_edges_history.append([])
            current_info_text += f"  排序第{i + 1}位: {edge.start} -- {edge.end} (权重: {edge.weight})\n"
            current_status = f"排序: 边 {edge.start} -- {edge.end} (权重: {edge.weight})"
            self.info_text_history.append(current_info_text)
            self.status_history.append(current_status)
            self.animation_steps.append(("sort_highlight", edge, i + 1, m))
        
        # 步骤m+2: 排序完成
        self.mst_edges_history.append([])
        current_info_text += "排序完成\n\n"
        current_status = "排序完成"
        self.info_text_history.append(current_info_text)
        self.status_history.append(current_status)
        self.animation_steps.append(("sort_end",))
        
        # 处理每条边
        for i, edge in enumerate(sorted_edges):
            u, v, w = edge.start, edge.end, edge.weight
            ru = findSet(parent, u)
            rv = findSet(parent, v)
            
            # 考虑边
            self.mst_edges_history.append(list(self.mst_edges))
            current_info_text += f"考虑边 {i + 1}/{m}: {edge.start} -- {edge.end} (权重: {edge.weight})\n"
            current_status = f"正在考虑: {edge.start} -- {edge.end}"
            self.info_text_history.append(current_info_text)
            self.status_history.append(current_status)
            self.animation_steps.append(("consider", edge, i + 1, m))
            
            if ru != rv:
                unionSet(parent, rank, ru, rv)
                mst_result.append(edge)
                self.mst_edges.append(edge)
                
                # 选中边
                self.mst_edges_history.append(list(self.mst_edges))
                current_info_text += f"✓ 选中边(加入MST): {edge.start} -- {edge.end} (权重: {edge.weight})\n"
                current_status = f"选中边: {edge.start} -- {edge.end} (加入MST)"
                self.info_text_history.append(current_info_text)
                self.status_history.append(current_status)
                self.animation_steps.append(("select", edge))
            else:
                # 拒绝边
                self.mst_edges_history.append(list(self.mst_edges))
                current_info_text += f"✗ 拒绝边(形成环): {edge.start} -- {edge.end}\n"
                current_status = f"拒绝边(形成环): {edge.start} -- {edge.end}"
                self.info_text_history.append(current_info_text)
                self.status_history.append(current_status)
                self.animation_steps.append(("reject", edge))
        
        # 最终结果
        total_weight = sum(e.weight for e in mst_result)
        
        if len(mst_result) == n - 1:
            self.mst_edges_history.append(list(self.mst_edges))
            current_info_text += f"\n最小生成树已完成\n总权重: {total_weight}\n"
            current_info_text += "最小生成树边:\n"
            for e in mst_result:
                current_info_text += f"  {e.start} -- {e.end} (权重: {e.weight})\n"
            current_status = f"最小生成树完成，总权重: {total_weight}"
            self.info_text_history.append(current_info_text)
            self.status_history.append(current_status)
            self.animation_steps.append(("complete", total_weight, mst_result))
        else:
            self.mst_edges_history.append(list(self.mst_edges))
            current_info_text += f"\n无法形成最小生成树，图不连通\n已选边数: {len(mst_result)}, 需要边数: {n - 1}\n"
            current_status = "图不连通，无法形成最小生成树"
            self.info_text_history.append(current_info_text)
            self.status_history.append(current_status)
            self.animation_steps.append(("incomplete", len(mst_result), n - 1))
        
        self.steps_precomputed = True
        self.is_paused = False
        self.pause_button.config(text="暂停", state=tk.NORMAL)
        self.prev_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.update_status("算法步骤已预加载，共{}步".format(len(self.animation_steps)))
        self.info_text.delete(1.0, tk.END)
        
        # 显示初始状态
        self.show_step(0)
        self.is_playing = True
        self.play_animation()
    
    def play_animation(self):
        if self.is_paused:
            return
        if self.step_index < len(self.animation_steps):
            self.show_step(self.step_index)
            self.step_index += 1
            self.update_navigation_buttons()
            self.after_id = self.root.after(1200, self.play_animation)
        else:
            self.pause_button.config(text="暂停", state=tk.DISABLED)
            self.is_playing = False
            self.update_status("动画播放完成")
    
    def show_step(self, index):
        """显示指定步骤的状态"""
        if index < 0 or index >= len(self.animation_steps):
            return
        
        step = self.animation_steps[index]
        
        # 更新文本和状态
        if index < len(self.info_text_history):
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, self.info_text_history[index])
            self.update_status(self.status_history[index])
        
        # 更新MST边集
        if index < len(self.mst_edges_history):
            self.mst_edges = list(self.mst_edges_history[index])
        
        # 根据步骤类型绘制
        step_type = step[0]
        if step_type == "init":
            self.draw_graph()
        elif step_type == "sort_start":
            self.draw_graph()
        elif step_type == "sort_highlight":
            edge = step[1]
            self.draw_graph_with_highlight(edge, "orange")
        elif step_type == "sort_end":
            self.draw_graph()
        elif step_type == "consider":
            edge = step[1]
            self.draw_graph_with_highlight(edge, "yellow")
        elif step_type == "select":
            self.draw_graph()
        elif step_type == "reject":
            self.draw_graph_with_reject(step[1])
        elif step_type == "complete":
            self.draw_graph()
        elif step_type == "incomplete":
            self.draw_graph()
    
    def toggle_pause(self):
        if not self.steps_precomputed:
            return
            
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="暂停")
            self.update_status("继续动画")
            self.is_playing = True
            self.play_animation()
        else:
            if not self.is_playing:
                self.is_playing = True
                self.play_animation()
            else:
                self.is_paused = True
                self.pause_button.config(text="继续")
                self.update_status("动画已暂停")
                if self.after_id:
                    self.root.after_cancel(self.after_id)
    
    def process_step(self, step):
        """处理单步动画（用于上一步/下一步）"""
        step_type = step[0]
        
        if step_type == "init":
            self.draw_graph()
        elif step_type == "sort_start":
            self.draw_graph()
        elif step_type == "sort_highlight":
            edge = step[1]
            self.draw_graph_with_highlight(edge, "orange")
        elif step_type == "sort_end":
            self.draw_graph()
        elif step_type == "consider":
            edge = step[1]
            self.draw_graph_with_highlight(edge, "yellow")
        elif step_type == "select":
            self.draw_graph()
        elif step_type == "reject":
            self.draw_graph_with_reject(step[1])
        elif step_type == "complete":
            self.draw_graph()
        elif step_type == "incomplete":
            self.draw_graph()
    
    def draw_graph_with_highlight(self, highlight_edge, color):
        self.canvas.delete("all")
        
        for edge in self.graph.edges:
            x1, y1 = self.vertex_positions[edge.start]
            x2, y2 = self.vertex_positions[edge.end]
            
            is_highlight = (edge.start == highlight_edge.start and edge.end == highlight_edge.end) or \
                          (edge.start == highlight_edge.end and edge.end == highlight_edge.start)
            
            is_mst = False
            for mst_edge in self.mst_edges:
                if (edge.start == mst_edge.start and edge.end == mst_edge.end) or \
                   (edge.start == mst_edge.end and edge.end == mst_edge.start):
                    is_mst = True
                    break
            
            if is_mst:
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
            
            if is_highlight:
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=4, dash=(5, 5))
            elif not is_mst:
                self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=1)
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y - 10, text=str(edge.weight), 
                                   fill="black", font=("Arial", 10, "bold"))
        
        for v, (x, y) in self.vertex_positions.items():
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="white", outline="blue", width=2)
            self.canvas.create_text(x, y, text=str(v), fill="blue", font=("Arial", 12, "bold"))
    
    def draw_graph_with_reject(self, reject_edge):
        """绘制拒绝的边（红色虚线）"""
        self.canvas.delete("all")
        
        for edge in self.graph.edges:
            x1, y1 = self.vertex_positions[edge.start]
            x2, y2 = self.vertex_positions[edge.end]
            
            is_reject = (edge.start == reject_edge.start and edge.end == reject_edge.end) or \
                       (edge.start == reject_edge.end and edge.end == reject_edge.start)
            
            is_mst = False
            for mst_edge in self.mst_edges:
                if (edge.start == mst_edge.start and edge.end == mst_edge.end) or \
                   (edge.start == mst_edge.end and edge.end == mst_edge.start):
                    is_mst = True
                    break
            
            if is_mst:
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
            elif is_reject:
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, dash=(3, 3))
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=1)
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y - 10, text=str(edge.weight), 
                                   fill="black", font=("Arial", 10, "bold"))
        
        for v, (x, y) in self.vertex_positions.items():
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="white", outline="blue", width=2)
            self.canvas.create_text(x, y, text=str(v), fill="blue", font=("Arial", 12, "bold"))
    
    def prev_step(self):
        if not self.steps_precomputed:
            return
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.pause_button.config(text="继续")
            if self.after_id:
                self.root.after_cancel(self.after_id)
        
        if self.step_index > 0:
            self.step_index -= 1
            self.show_step(self.step_index)
            self.update_navigation_buttons()
    
    def next_step(self):
        if not self.steps_precomputed:
            return
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.pause_button.config(text="继续")
            if self.after_id:
                self.root.after_cancel(self.after_id)
        
        if self.step_index < len(self.animation_steps):
            self.show_step(self.step_index)
            self.step_index += 1
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.step_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.step_index < len(self.animation_steps) else tk.DISABLED)
    
    def reset_algorithm(self):
        self.is_paused = False
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.pause_button.config(text="暂停", state=tk.DISABLED)
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.mst_edges = []
        self.animation_steps = []
        self.mst_edges_history = []
        self.info_text_history = []
        self.status_history = []
        self.step_index = 0
        self.steps_precomputed = False
        self.draw_graph()
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"算法已重置，顶点数: {self.graph.numVertices}，边数: {self.graph.numEdges}\n")
        self.update_status("算法已重置")
    
    def reset_edges(self):
        if self.graph.numVertices <= 0:
            messagebox.showerror("错误", "请先初始化图")
            return
        
        self.is_paused = False
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.pause_button.config(text="暂停", state=tk.DISABLED)
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.graph.edges = []
        self.graph.numEdges = 0
        self.mst_edges = []
        self.animation_steps = []
        self.mst_edges_history = []
        self.info_text_history = []
        self.status_history = []
        self.step_index = 0
        self.steps_precomputed = False
        self.draw_graph()
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"边已重置，顶点数: {self.graph.numVertices}\n")
        self.update_status("边已重置，请添加边")
    
    def clear_all(self):
        self.is_paused = False
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.pause_button.config(text="暂停", state=tk.DISABLED)
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        
        self.graph.numVertices = 0
        self.graph.numEdges = 0
        self.graph.maxEdges = 0
        self.graph.edges = []
        self.vertex_positions = {}
        self.mst_edges = []
        self.animation_steps = []
        self.mst_edges_history = []
        self.info_text_history = []
        self.status_history = []
        self.step_index = 0
        self.steps_precomputed = False
        
        self.vertex_entry.delete(0, tk.END)
        self.edge_entry.delete(0, tk.END)
        
        self.canvas.delete("all")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "已清空所有内容，请重新初始化图\n")
        self.update_status("已清空，请输入顶点数和边数")
    
    def load_preset_graph(self):
        """加载预设的测试图（4个顶点，5条边）"""
        self.graph.initGraph(4, 5)
        self.vertex_positions = {}
        self.mst_edges = []
        self.animation_steps = []
        self.step_index = 0
        self.is_paused = False
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.pause_button.config(text="暂停", state=tk.DISABLED)
        
        self.calculate_vertex_positions(4)
        
        self.graph.addEdge(1, 2, 1)
        self.graph.addEdge(1, 3, 2)
        self.graph.addEdge(1, 4, 3)
        self.graph.addEdge(2, 3, 3)
        self.graph.addEdge(3, 4, 1)
        
        self.vertex_entry.delete(0, tk.END)
        self.vertex_entry.insert(0, "4")
        self.edge_entry.delete(0, tk.END)
        self.edge_entry.insert(0, "5")
        
        self.draw_graph()
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "已加载预设图（4顶点5边）\n")
        self.info_text.insert(tk.END, "边列表:\n")
        self.info_text.insert(tk.END, "  1 -- 2 (权重: 1)\n")
        self.info_text.insert(tk.END, "  1 -- 3 (权重: 2)\n")
        self.info_text.insert(tk.END, "  1 -- 4 (权重: 3)\n")
        self.info_text.insert(tk.END, "  2 -- 3 (权重: 3)\n")
        self.info_text.insert(tk.END, "  3 -- 4 (权重: 1)\n")
        self.update_status("预设图已加载，可点击开始运行算法")
    
    def update_status(self, text):
        self.status_label.config(text=f"状态: {text}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KruskalGUI(root)
    root.mainloop()
