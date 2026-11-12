# -*- coding: utf-8 -*-
"""Kruskal MST Visualizer 核心逻辑测试。

只测试纯逻辑函数，不实例化 tkinter 窗口，
因此可以在无图形界面的 CI 环境中运行。
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

import kruskal_gui as kg  # noqa: E402


def make_graph(n, m):
    g = kg.Graph()
    g.initGraph(n, m)
    return g


def test_add_edge_new():
    g = make_graph(4, 5)
    assert g.addEdge(1, 2, 3) == 0
    assert g.numEdges == 1
    assert g.edges[0].weight == 3


def test_add_edge_overwrite_reversed():
    """无向边 (1,2) 与 (2,1) 视为同一条边，后写入的权重覆盖前者。"""
    g = make_graph(4, 5)
    assert g.addEdge(1, 2, 3) == 0
    assert g.addEdge(2, 1, 7) == 1
    assert g.numEdges == 1
    assert g.edges[0].weight == 7


def test_add_edge_capacity():
    g = make_graph(3, 1)
    assert g.addEdge(1, 2, 1) == 0
    assert g.addEdge(2, 3, 2) == -1


def test_find_and_union():
    parent = list(range(6))
    rank = [0] * 6

    assert kg.findSet(parent, 1) == 1
    assert kg.unionSet(parent, rank, 1, 2) is True
    assert kg.findSet(parent, 1) == kg.findSet(parent, 2)

    # 重复合并同一集合应返回 False
    assert kg.unionSet(parent, rank, 1, 2) is False

    assert kg.unionSet(parent, rank, 2, 3) is True
    assert kg.findSet(parent, 3) == kg.findSet(parent, 1)


def test_disconnected_components():
    parent = list(range(6))
    rank = [0] * 6

    kg.unionSet(parent, rank, 1, 2)
    kg.unionSet(parent, rank, 3, 4)

    assert kg.findSet(parent, 1) == kg.findSet(parent, 2)
    assert kg.findSet(parent, 1) != kg.findSet(parent, 3)
    assert kg.findSet(parent, 5) != kg.findSet(parent, 4)