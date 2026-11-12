# 代码结构说明

## 1. 总体结构

```
src/
├── python/kruskal_gui.py   # 图形界面与算法演示
└── c/kruskal.c             # 命令行算法实现
tests/
└── test_kruskal.py         # 核心逻辑单元测试
```

两个实现共享同一套算法思路（排序 + 并查集），差异只在交互方式：Python 版负责可视化演示，C 版负责命令行验证与教学对照。

## 2. Python 版模块划分

| 组成 | 职责 |
| --- | --- |
| `Edge` | 边的数据类：起点、终点、权重 |
| `Graph` | 图的数据结构：顶点数、边列表、添加与去重 |
| `findSet / unionSet` | 并查集：路径压缩 + 按秩合并 |
| `KruskalGUI` | 界面构建、事件绑定、动画调度与绘制 |

### 2.1 关键流程

```
用户点击「开始」
  └─ run_kruskal()
       ├─ 排序所有边
       ├─ 预计算动画步骤（init / sort / consider / select / reject / complete）
       ├─ 记录每一步的 MST 边集、文本、状态
       └─ play_animation() 按 1200ms 间隔回放
```

动画采用「先预计算、后回放」的方式：算法一次跑完并把每步状态存入 `animation_steps`、`mst_edges_history`、`info_text_history`、`status_history`，回放时只做渲染。这样「上一步 / 下一步」可以任意跳转，不需要重复执行算法。

### 2.2 绘制逻辑

- `draw_graph()`：绘制普通状态
- `draw_graph_with_highlight()`：高亮当前考察的边
- `draw_graph_with_reject()`：用红色虚线标出被拒绝的成环边
- 生成树中的边统一用红色加粗显示

## 3. C 版模块划分

| 函数 | 职责 |
| --- | --- |
| `initGraph` / `addEdge` | 图初始化与边添加 |
| `findSet` / `unionSet` | 并查集（路径压缩 + 按秩合并） |
| `cmpEdge` | `qsort` 的权重比较函数 |
| `kruskal` | 主算法：排序、遍历、输出结果 |
| `debugPrint*` | 由 `DEBUG` 宏控制的调试输出 |

## 4. 测试策略

`tests/test_kruskal.py` 覆盖：

1. 重复边覆盖权重（无向边 `(u,v)` 与 `(v,u)` 视为同一条）
2. 并查集的合并与连通性判断
3. 图不连通时的边界行为

测试不实例化 tkinter 窗口，只导入模块并调用纯逻辑函数，因此可在无图形界面的 CI 环境运行。

## 5. 扩展方向

- 支持从文件 / JSON 导入图数据
- 增加 Prim 算法对照演示
- 导出最小生成树为图片或 DOT 格式
- 增加算法步骤日志导出，便于教学复盘