from collections import deque

def solve_warehouse():
    # The warehouse is represented as a two-dimensional grid
    grid = [
        "#####################",
        "#..................G#",
        "#.##.....##########.#",
        "#S....#.............#",
        "#....##...........#.#",
        "#.######.###.#.###..#",
        "#.......#...........#",
        "#.....#.............#",
        "#####################"
    ]

    rows = len(grid)
    cols = len(grid[0])
    
    start = None
    goal = None
    
    # Locate Starting position (S) and Goal (G)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'G':
                goal = (r, c)
                
    def get_neighbors(r, c):
        # The vehicle may move Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # Ensure the agent avoids all obstacles and stays in bounds
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
                neighbors.append((nr, nc))
        return neighbors

    # Queue stores tuples of (current_position, path_taken)
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        current, path = queue.popleft()
        
        # Check if the objective has been reached
        if current == goal:
            return path, grid
            
        for neighbor in get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
                
    return None, grid

# Execute and test
path, grid = solve_warehouse()
if path:
    print(f"Path found with length {len(path)-1} steps.")
    print("Path coordinates:", path)
    print("\nVisualized Path (* = path):")
    
    grid_list = [list(row) for row in grid]
    for r, c in path:
        if grid_list[r][c] not in ('S', 'G'):
            grid_list[r][c] = '*'
            
    for row in grid_list:
        print("".join(row))
else:
    print("No path exists.")