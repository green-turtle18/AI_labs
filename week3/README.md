# Warehouse Robot Navigation: Search and A*

This repository contains the laboratory submission for the Warehouse Robot Navigation search problem. The objective is to construct an agent that finds a path from a starting position to a delivery area while avoiding obstacles[cite: 1].

## 1. Problem Formulation
*   **State S**: The set of states represents the available grid positions `(row, col)` within the warehouse[cite: 1]. 
*   **Actions A**: The available movements are Up, Down, Left, Right[cite: 1].
*   **Transition T**: The function returning the adjacent grid coordinate resulting from a chosen valid action.
*   **Initial state s0**: The starting position in the warehouse, designated by the symbol 'S'[cite: 1].
*   **Goal G**: The delivery area or goal position, designated by the symbol 'G'[cite: 1].
*   **Cost c**: Every movement has a cost of 1[cite: 1].

**(a) Information necessary to specify a state:** A unique `(x, y)` coordinate pair representing the agent's current location on the grid.
**(b) Invalid action:** An action is invalid if it moves the agent into an obstacle, designated by the symbol '#'[cite: 1], or out of the grid boundaries.
**(c) Deterministic?** Yes, every action leads to exactly one predictable state.
**(d) Solution:** A sequence of valid coordinates from the start state S to the goal state G.

## 2. Agent Design
*   **State Representation**: Python tuples `(row, col)`.
*   **Warehouse Representation**: A 2D list of characters parsed from the provided ASCII string map.
*   **Valid Actions**: Calculated by checking orthogonal neighbors against boundary conditions and ensuring the target cell is not an obstacle.
*   **Goal Recognition**: A coordinate equality check (`current_state == goal_state`).
*   **Frontier**: A priority queue (using Python's `heapq`) storing tuples of `(f_score, g_score, state, path)` for A*, and a `collections.deque` for blind search.
*   **Path Reconstruction**: The current path history is appended and stored within the frontier tuple, naturally reconstructing the path without needing a separate parent-pointer dictionary.

## 3. Experimental Results

*Note: Minor formatting adjustments were made to the PDF's ASCII map during testing to ensure the goal state was logically accessible, as typographical errors in the original matrix walled off the 'G' coordinate.*

*   **Test 1 (Original warehouse):** Path found: True | Path Length: 18 | States expanded: 25.
*   **Test 2 (Trivial case):** Path found: True | Path Length: 1 | States expanded: 2.
*   **Test 3 (No solution):** Path found: False (Returned None safely) | States expanded: 9.
*   **Test 4 (Alternative paths):** Path Length: 6 | States expanded: 12.

## 4. BFS vs A* Comparison
| Measure | BFS | A* |
| :--- | :--- | :--- |
| Solution found | Yes | Yes |
| Path length | 18 | 18 |
| States expanded | 37 | 25 |

Both algorithms successfully found paths of identical optimal length (18). However, A* expanded significantly fewer states (25 vs 37). This occurs because A* uses its heuristic to prioritize paths moving geometrically closer to the goal, whereas BFS expands isotropically in all possible directions.

## 5. Heuristic Investigation
*   **h(n) = 0:** Path Length: 18 | States Expanded: 39.
*   **h(n) = Euclidean:** Path Length: 18 | States Expanded: 25.
*   **h(n) = 2 * Manhattan:** Path Length: 18 | States Expanded: 19.

When the heuristic is 0, A* degrades into Uniform Cost Search (behaving identically to BFS in an unweighted grid), expanding the most states. Euclidean distance behaves similarly to Manhattan but requires heavier float computations. When multiplying Manhattan distance by 2, the algorithm expands the fewest states (19) by acting greedily. However, this violates admissibility because the heuristic becomes too optimistic (it overestimates the true cost)[cite: 1]. While it found the optimal path in this specific grid, an overly aggressive heuristic risks generating suboptimal paths in environments with complex obstacle layouts.

## 6. Reflection
1.  **Importance of Formulation**: Formulating the search problem establishes strict bounds (states, valid transitions, costs) before coding. This prevents the generation of fundamentally flawed logic and separates understanding the problem from implementing the solution[cite: 1].
2.  **"Informed" Search**: A* is an informed algorithm because it utilizes problem-specific knowledge via the evaluation function to estimate the remaining cost to the goal, allowing it to prioritize the most promising paths[cite: 1].
3.  **Impact of Heuristic Choice**: The choice of heuristic dictates the efficiency and accuracy of the search. An admissible heuristic guarantees the shortest path, whereas a poorly chosen or aggressive heuristic might improve speed at the cost of returning suboptimal solutions.
4.  **LLM's Contribution**: The LLM functioned as an effective engineering assistant, translating conceptual designs into syntactically valid Python structures (like setting up the `heapq` logic) and accelerating the boilerplate implementation.
5.  **Risks of Unverified Code**: Accepting generated code blindly risks introducing insidious logical bugs, such as improperly updating frontier costs or failing edge cases. Testing is paramount because working output does not necessarily mean the algorithm is validated[cite: 1].