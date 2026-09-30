import heapq
from collections import deque
import math

class SearchAgent:
    def __init__(self, grid):
        self.grid = [list(row) for row in grid]
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = self.goal = None
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 'S':
                    self.start = (r, c)
                elif self.grid[r][c] == 'G':
                    self.goal = (r, c)

    def get_neighbors(self, state):
        r, c = state
        neighbors = []
        # The agent can move up, down, left, or right[cite: 1]
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            # Ensure valid bounds and not an obstacle ('#')[cite: 1]
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != '#':
                neighbors.append((nr, nc))
        return neighbors

    def search(self, algorithm='astar', heuristic_type='manhattan'):
        frontier = []
        if algorithm == 'astar':
            heapq.heappush(frontier, (0, 0, self.start, [self.start])) 
        else:
            frontier = deque([(self.start, [self.start])])
            
        explored = set()
        states_expanded = 0

        while frontier:
            if algorithm == 'astar':
                f, g, current, path = heapq.heappop(frontier)
            else:
                current, path = frontier.popleft()
                
            if current in explored:
                continue
            explored.add(current)
            states_expanded += 1

            if current == self.goal:
                return path, len(path) - 1, states_expanded

            for neighbor in self.get_neighbors(current):
                if neighbor not in explored:
                    new_path = path + [neighbor]
                    if algorithm == 'astar':
                        g_new = g + 1  # Every movement has cost 1[cite: 1]
                        if heuristic_type == 'manhattan':
                            h = abs(neighbor[0] - self.goal[0]) + abs(neighbor[1] - self.goal[1])
                        elif heuristic_type == 'zero':
                            h = 0
                        elif heuristic_type == 'euclidean':
                            h = math.sqrt((neighbor[0] - self.goal[0])**2 + (neighbor[1] - self.goal[1])**2)
                        elif heuristic_type == 'manhattan2x':
                            h = 2 * (abs(neighbor[0] - self.goal[0]) + abs(neighbor[1] - self.goal[1]))
                        f_new = g_new + h
                        heapq.heappush(frontier, (f_new, g_new, neighbor, new_path))
                    else:
                        frontier.append((neighbor, new_path))
        return None, 0, states_expanded

if __name__ == '__main__':
    # Modified grid to ensure goal is reachable
    grid_orig = [
        "#################",
        "#S....#.........#",
        "#.###.#.#######.#",
        "#...#.#.......#.#",
        "###.#.#######.#.#",
        "#...#.........#.#",
        "#.###########.#.#",
        "#.........#..G..#",
        "#################"
    ]

    agent = SearchAgent(grid_orig)
    path_a, cost_a, exp_a = agent.search('astar', 'manhattan')
    path_b, cost_b, exp_b = agent.search('bfs')
    
    print(f"BFS vs A*: BFS Cost={cost_b}, BFS Exp={exp_b} | A* Cost={cost_a}, A* Exp={exp_a}")