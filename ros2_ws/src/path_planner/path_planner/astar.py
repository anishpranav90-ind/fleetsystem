"""A* Path Planner — Global path planning on a warehouse grid.

Implements A* algorithm for multi-robot path planning.
Uses a grid representation of the warehouse where:
  '.' = free space
  '█' = obstacle
  'S' = start
  'G' = goal

The planned path is published as a ROS 2 Nav Path message.
Nav2 handles local movement and obstacle avoidance on top of this.
"""

import heapq
import math
from typing import List, Tuple, Optional


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    grid: List[List[str]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """A* pathfinding on a 2D grid.

    Args:
        grid: 2D list of characters ('.', '█', etc.)
        start: (row, col) start position
        goal: (row, col) goal position

    Returns:
        List of (row, col) from start to goal, or None if no path found.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if grid[start[0]][start[1]] == "█" or grid[goal[0]][goal[1]] == "█":
        return None

    # (f_score, (row, col))
    open_set: List[Tuple[float, Tuple[int, int]]] = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    # 4-directional movement
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            nr, nc = neighbor

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "█":
                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found


def grid_to_world(
    path: List[Tuple[int, int]], resolution: float = 1.0, origin_x: float = 0.0, origin_y: float = 0.0
) -> List[Tuple[float, float]]:
    """Convert grid coordinates to world coordinates.

    Args:
        path: List of (row, col) grid positions
        resolution: meters per grid cell
        origin_x: world x-coordinate of grid origin
        origin_y: world y-coordinate of grid origin

    Returns:
        List of (x, y) world coordinates
    """
    return [
        (col * resolution + origin_x, row * resolution + origin_y)
        for row, col in path
    ]


def print_grid_with_path(
    grid: List[List[str]], path: List[Tuple[int, int]]
) -> str:
    """Render a grid with a path overlaid for debug visualization."""
    display = [row[:] for row in grid]
    for row, col in path:
        if display[row][col] not in ("S", "G"):
            display[row][col] = "*"
    return "\n".join("".join(row) for row in display)


# Also handle the original grid with space-separated chars
def _clean_grid(raw: str) -> List[List[str]]:
    """Convert space-separated grid string to 2D list."""
    return [[c for c in line.split() if c] for line in raw.strip().split("\n")]


# --- Demo ---
if __name__ == "__main__":
    warehouse = [
        list("S . . █ █ . . ."),
        list(". . . █ █ . . ."),
        list(". . . . . . . ."),
        list("█ █ . . . . █ █"),
        list(". . . . . . . ."),
        list(". . . █ █ . G ."),
    ]

    # Use simple ASCII grid (X = obstacle)
    warehouse = [
        list(row)
        for row in [
            "S..XX...",
            "...XX...",
            "........",
            "XX....XX",
            "........",
            "...XX.G.",
        ]
    ]

    start = (0, 0)
    goal = (5, 6)

    path = astar(warehouse, start, goal)
    if path:
        print("Path found:")
        print(print_grid_with_path(warehouse, path))
        print(f"\nSteps: {len(path)}")
        world_path = grid_to_world(path)
        print(f"World coords: {world_path}")
    else:
        print("No path found!")
