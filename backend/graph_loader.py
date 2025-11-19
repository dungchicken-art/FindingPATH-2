"""Utility helpers to load and cache the Khương Đình street graph."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import xml.etree.ElementTree as ET


GRAPH_FILE = Path(__file__).with_name("khuong_dinh.graphml")
GRAPHML_NS = {"g": "http://graphml.graphdrawing.org/xmlns"}


@dataclass
class GraphData:
    """A lightweight representation of an undirected weighted graph."""

    nodes: Dict[str, Dict[str, float]]
    adjacency: Dict[str, Dict[str, Dict[str, float]]]
    edges: List[Dict[str, float]]

    def neighbors(self, node_id: str) -> Iterable[Tuple[str, Dict[str, float]]]:
        return self.adjacency.get(node_id, {}).items()

    def heuristic(self, node_a: str, node_b: str) -> float:
        """Euclidean distance between two nodes based on lon/lat coordinates."""
        ax, ay = self._get_coords(node_a)
        bx, by = self._get_coords(node_b)
        return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    def _get_coords(self, node_id: str) -> Tuple[float, float]:
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node id {node_id}")
        node = self.nodes[node_id]
        return node["x"], node["y"]

    def serialize(self) -> Dict[str, List[Dict[str, float]]]:
        return {
            "nodes": [
                {"id": node_id, **node_attrs}
                for node_id, node_attrs in self.nodes.items()
            ],
            "edges": self.edges,
        }


_GRAPH_CACHE: GraphData | None = None


def load_graph() -> GraphData:
    """Load the GraphML file and compute derived weights."""
    global _GRAPH_CACHE
    if _GRAPH_CACHE is not None:
        return _GRAPH_CACHE

    if not GRAPH_FILE.exists():
        raise FileNotFoundError(
            "Graph file khuong_dinh.graphml was not found in the backend folder"
        )

    tree = ET.parse(GRAPH_FILE)
    root = tree.getroot()

    nodes: Dict[str, Dict[str, float]] = {}
    for node in root.findall(".//g:node", GRAPHML_NS):
        node_id = node.attrib["id"]
        x = float(_extract_data(node, "d0"))
        y = float(_extract_data(node, "d1"))
        nodes[node_id] = {"x": x, "y": y}

    adjacency: Dict[str, Dict[str, Dict[str, float]]] = {
        node_id: {} for node_id in nodes.keys()
    }
    edges: List[Dict[str, float]] = []

    for edge in root.findall(".//g:edge", GRAPHML_NS):
        source = edge.attrib["source"]
        target = edge.attrib["target"]
        length = float(_extract_data(edge, "d2"))
        flooded = _extract_bool(edge, "d3")
        blocked = _extract_bool(edge, "d4")
        weight = _compute_weight(length, flooded, blocked)
        attrs = {
            "length": length,
            "flooded": flooded,
            "blocked": blocked,
            "weight": weight,
            "u": source,
            "v": target,
        }
        edges.append(attrs)
        adjacency[source][target] = {
            "length": length,
            "flooded": flooded,
            "blocked": blocked,
            "weight": weight,
        }
        adjacency[target][source] = adjacency[source][target]

    _GRAPH_CACHE = GraphData(nodes=nodes, adjacency=adjacency, edges=edges)
    return _GRAPH_CACHE


def _extract_data(element: ET.Element, key: str) -> str:
    data = element.find(f"g:data[@key='{key}']", GRAPHML_NS)
    if data is None or data.text is None:
        raise ValueError(f"Missing GraphML data for key {key}")
    return data.text


def _extract_bool(element: ET.Element, key: str) -> bool:
    raw = _extract_data(element, key).strip().lower()
    return raw in {"1", "true", "yes"}


def _compute_weight(length: float, flooded: bool, blocked: bool) -> float:
    if blocked:
        return length * 50
    if flooded:
        return length * 10
    return length


def reset_cache() -> None:
    global _GRAPH_CACHE
    _GRAPH_CACHE = None


__all__ = ["GraphData", "load_graph", "reset_cache"]
