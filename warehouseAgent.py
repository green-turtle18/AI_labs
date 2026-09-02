"""
Warehouse Navigation Problem - Goal-Based Agent
=================================================

This program implements a GOAL-BASED AGENT that navigates an autonomous
warehouse vehicle from a starting position (S) to a goal/dispatch position (G),
while avoiding obstacles (shelving units, marked '#').

Why is this a GOAL-BASED agent (not a simple reflex agent)?
-------------------------------------------------------------
A simple reflex agent chooses actions based only on the CURRENT percept
(e.g. "if there is a wall to my right, turn left"). It has no memory of
the past and no model of the future.

A goal-based agent, by contrast:
    1. Maintains an internal model of the environment (the grid map).
    2. Has an explicit GOAL (reach position G).
    3. Considers the CONSEQUENCES of sequences of actions (not just the
       immediate percept) before acting - it plans a path.
    4. Chooses actions that will lead it towards achieving the goal.

Here, the vehicle cannot simply react to its immediate surroundings,
because a dead end or wrong turn might only become apparent several
moves later. It must search over possible future states (positions)
to find a sequence of actions (a path) that provably reaches the goal.
This need to reason about future states in order to satisfy an explicit
objective is exactly what characterises a goal-based agent.

Search Algorithm Chosen: Breadth-First Search (BFS)
-------------------------------------------------------------
BFS explores the state space (grid positions) level by level, expanding
all states reachable in 1 move, then all states reachable in 2 moves,
and so on, until the goal is found.

Why BFS is appropriate for this problem:
  - Every action (Up/Down/Left/Right) has the SAME cost (one grid step).
    When all step costs are equal, BFS is guaranteed to find a path with
    the SMALLEST NUMBER OF MOVES - i.e. an optimal (shortest) path.
  - The grid is small/finite, so BFS's memory usage (storing the frontier
    of visited states) is not a practical concern.
  - BFS is simple, complete (it will find a path if one exists), and
    optimal for unweighted graphs - more complex algorithms such as A*
    or Dijkstra's algorithm would add the overhead of a heuristic or
    priority queue without providing any benefit here, since there are
    no varying edge weights to exploit.

Author: (Laboratory Exercise Submission)
"""

from collections import deque


# ---------------------------------------------------------------------------
# 1. THE ENVIRONMENT
# ---------------------------------------------------------------------------
# The warehouse is represented as a two-dimensional grid of characters.
#   'S' = starting position of the vehicle
#   'G' = goal / dispatch position
#   '#' = obstacle (shelving unit) - cannot be entered
#   '.' = free space - can be entered

WAREHOUSE_MAP = [
    "#####################",
    "#S....#............G#",
    "#.##....##########..#",
    "#....##.............#",
    "#.######.###.#.###..#",
    "#........#..........#",
    "#####################",
]


class WarehouseEnvironment:
    """
    Represents the environment in which the goal-based agent operates.

    Responsibilities:
      - Parse the grid map into a usable internal representation.
      - Identify the start state and the goal state.
      - Report which grid cells are free (i.e. which actions are legal
        from a given state).
    """

    def __init__(self, grid_lines):
        self.grid = [list(row) for row in grid_lines]
        self.num_rows = len(self.grid)
        self.num_cols = len(self.grid[0])

        self.start = self._find_symbol('S')
        self.goal = self._find_symbol('G')

        if self.start is None:
            raise ValueError("No start position 'S' found in the warehouse map.")
        if self.goal is None:
            raise ValueError("No goal position 'G' found in the warehouse map.")

    def _find_symbol(self, symbol):
        """Return the (row, col) coordinates of the given symbol, or None."""
        for r in range(self.num_rows):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] == symbol:
                    return (r, c)
        return None

    def is_free(self, position):
        """
        A cell is enterable by the vehicle if it lies within the grid
        bounds and is NOT an obstacle ('#'). Both the start ('S') and
        goal ('G') cells count as free space for movement purposes.
        """
        r, c = position
        if r < 0 or r >= self.num_rows:
            return False
        if c < 0 or c >= len(self.grid[r]):
            return False
        return self.grid[r][c] != '#'

    def display_with_path(self, path):
        """
        Return a printable string of the warehouse map with the path
        the vehicle took marked with '*' (start and goal symbols are
        preserved so the route is easy to see).
        """
        display_grid = [row[:] for row in self.grid]
        for (r, c) in path:
            if display_grid[r][c] == '.':
                display_grid[r][c] = '*'
        return "\n".join("".join(row) for row in display_grid)


# ---------------------------------------------------------------------------
# 2. THE AGENT'S AVAILABLE ACTIONS
# ---------------------------------------------------------------------------
# Each action maps to a change in (row, col) coordinates.
# Row increases downward, column increases to the right.

ACTIONS = {
    "Up":    (-1, 0),
    "Down":  (1, 0),
    "Left":  (0, -1),
    "Right": (0, 1),
}


# ---------------------------------------------------------------------------
# 3. THE GOAL-BASED AGENT
# ---------------------------------------------------------------------------

class GoalBasedAgent:
    """
    A goal-based agent for the warehouse navigation problem.

    The agent maintains:
      - a model of the environment (the WarehouseEnvironment),
      - the current state (its position),
      - an explicit goal (the destination position),
      - a decision-making component (the search algorithm, `plan_path`)
        which looks ahead through possible future states to find an
        action sequence that satisfies the goal.
    """

    def __init__(self, environment):
        self.environment = environment
        self.current_state = environment.start
        self.goal_state = environment.goal

    def plan_path(self):
        """
        Decision-making component of the agent.

        Uses Breadth-First Search (BFS) over the grid of positions to
        find a shortest, collision-free sequence of moves from the
        current state to the goal state.

        Returns:
            (path, actions) tuple, where:
              - path is a list of (row, col) positions from start to goal
                (inclusive), or None if no path exists;
              - actions is the corresponding list of action names
                ("Up"/"Down"/"Left"/"Right"), or None if no path exists.
        """
        start = self.current_state
        goal = self.goal_state

        # The frontier holds states waiting to be expanded, in FIFO order,
        # which is what gives BFS its "level by level" exploration order.
        frontier = deque([start])

        # Records how each visited state was reached, so the path can be
        # reconstructed once the goal is found:
        #   came_from[state] = (previous_state, action_taken)
        came_from = {start: None}

        while frontier:
            current = frontier.popleft()

            if current == goal:
                return self._reconstruct_path(came_from, start, goal)

            for action_name, (d_row, d_col) in ACTIONS.items():
                neighbour = (current[0] + d_row, current[1] + d_col)

                if not self.environment.is_free(neighbour):
                    continue  # obstacle or out of bounds - illegal move

                if neighbour in came_from:
                    continue  # already visited/queued

                came_from[neighbour] = (current, action_name)
                frontier.append(neighbour)

        # Frontier exhausted without reaching the goal: no path exists.
        return None, None

    @staticmethod
    def _reconstruct_path(came_from, start, goal):
        """Walk backwards from the goal to the start using `came_from`,
        then reverse to obtain the forward path and action sequence."""
        path = []
        actions = []
        state = goal

        while state != start:
            path.append(state)
            previous_state, action_name = came_from[state]
            actions.append(action_name)
            state = previous_state

        path.append(start)
        path.reverse()
        actions.reverse()
        return path, actions


# ---------------------------------------------------------------------------
# 4. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main():
    environment = WarehouseEnvironment(WAREHOUSE_MAP)
    agent = GoalBasedAgent(environment)

    print("Warehouse map:")
    print("\n".join(WAREHOUSE_MAP))
    print()
    print(f"Start position (row, col): {environment.start}")
    print(f"Goal position  (row, col): {environment.goal}")
    print()

    path, actions = agent.plan_path()

    if path is None:
        print("No path exists from the start position to the goal position.")
        return

    print(f"Path found! Length: {len(actions)} move(s).")
    print(f"Action sequence: {actions}")
    print()
    print("Warehouse map with path marked ('*'):")
    print(environment.display_with_path(path))


if __name__ == "__main__":
    main()