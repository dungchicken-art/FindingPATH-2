"""Implementations of DFS, BFS, Dijkstra and A* search for the graph."""
from __future__ import annotations

from collections import deque
import heapq
from typing import Callable, Dict, List, Tuple

from .graph_loader import GraphData


def dfs(graph: GraphData, start: str, goal: str) -> Dict[str, List]:
    _validate_nodes(graph, start, goal)
    stack: List[str] = [start]
    parents: Dict[str, str | None] = {start: None}
    visited_order: List[str] = []
    visited_set = set()
    steps: List[Dict[str, List[str]]] = []

    while stack:
        current = stack.pop()
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        steps.append(
            _build_step(current, visited_order, list(stack))
        )
        if current == goal:
            break
        for neighbor in sorted(graph.adjacency.get(current, {}).keys(), reverse=True):
            if neighbor in visited_set:
                continue
            if neighbor not in parents:
                parents[neighbor] = current
            stack.append(neighbor)

    path = _reconstruct_path(parents, goal)
    return {"path": path, "steps": steps}


def bfs(graph: GraphData, start: str, goal: str) -> Dict[str, List]:
    _validate_nodes(graph, start, goal)
    queue: deque[str] = deque([start])
    parents: Dict[str, str | None] = {start: None}
    visited_order: List[str] = []
    discovered = {start}
    steps: List[Dict[str, List[str]]] = []

    while queue:
        current = queue.popleft()
        visited_order.append(current)
        steps.append(
            _build_step(current, visited_order, list(queue))
        )
        if current == goal:
            break
        for neighbor in sorted(graph.adjacency.get(current, {}).keys()):
            if neighbor in discovered:
                continue
            discovered.add(neighbor)
            parents[neighbor] = current
            queue.append(neighbor)

    path = _reconstruct_path(parents, goal)
    return {"path": path, "steps": steps}


def dijkstra(graph: GraphData, start: str, goal: str) -> Dict[str, List]:
    _validate_nodes(graph, start, goal)
    queue: List[Tuple[float, str]] = [(0.0, start)]
    parents: Dict[str, str | None] = {start: None}
    distances: Dict[str, float] = {start: 0.0}
    visited_order: List[str] = []
    visited_set = set()
    steps: List[Dict[str, List[str]]] = []

    while queue:
        dist, current = heapq.heappop(queue)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        steps.append(
            _build_step(current, visited_order, _extract_frontier(queue))
        )
        if current == goal:
            break
        for neighbor, attrs in graph.neighbors(current):
            weight = attrs["weight"]
            new_dist = dist + weight
            if neighbor in visited_set and new_dist >= distances.get(neighbor, float("inf")):
                continue
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(queue, (new_dist, neighbor))

    path = _reconstruct_path(parents, goal)
    return {"path": path, "steps": steps}


def astar(graph: GraphData, start: str, goal: str) -> Dict[str, List]:
    _validate_nodes(graph, start, goal)
    queue: List[Tuple[float, str]] = [(0.0, start)]
    parents: Dict[str, str | None] = {start: None}
    g_costs: Dict[str, float] = {start: 0.0}
    visited_order: List[str] = []
    visited_set = set()
    steps: List[Dict[str, List[str]]] = []

    while queue:
        _, current = heapq.heappop(queue)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        steps.append(
            _build_step(current, visited_order, _extract_frontier(queue))
        )
        if current == goal:
            break
        for neighbor, attrs in graph.neighbors(current):
            tentative_g = g_costs[current] + attrs["weight"]
            if tentative_g >= g_costs.get(neighbor, float("inf")):
                continue
            parents[neighbor] = current
            g_costs[neighbor] = tentative_g
            f_score = tentative_g + graph.heuristic(neighbor, goal)
            heapq.heappush(queue, (f_score, neighbor))

    path = _reconstruct_path(parents, goal)
    return {"path": path, "steps": steps}


def _build_step(current: str, visited: List[str], frontier: List[str]) -> Dict[str, List[str]]:
    return {
        "current": current,
        "visited": list(visited),
        "frontier": list(frontier),
    }


def _extract_frontier(queue: List[Tuple[float, str]]) -> List[str]:
    return [node for _, node in queue]


def _validate_nodes(graph: GraphData, start: str, goal: str) -> None:
    missing = [node for node in (start, goal) if node not in graph.nodes]
    if missing:
        raise ValueError(f"Unknown node id(s): {', '.join(missing)}")


def _reconstruct_path(parents: Dict[str, str | None], goal: str) -> List[str]:
    if goal not in parents:
        return []
    path: List[str] = []
    current: str | None = goal
    while current is not None:
        path.append(current)
        current = parents.get(current)
    path.reverse()
    return path


ALGORITHMS: Dict[str, Callable[[GraphData, str, str], Dict[str, List]]] = {
    "dfs": dfs,
    "bfs": bfs,
    "dijkstra": dijkstra,
    "astar": astar,
}


__all__ = ["dfs", "bfs", "dijkstra", "astar", "ALGORITHMS"]
