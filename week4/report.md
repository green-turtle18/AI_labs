# Laboratory Submission: Logical Planning

## 1. Specification of the Planning Problem
*   **Initial State (I):** `I = {At(Robot, A), At(Package, A)}`[cite: 3].
*   **Goal (G):** `G = {At(Package, C)}`[cite: 3].
*   **Available Actions:** `Move(A,B)`, `Move(B,A)`, `Move(B,C)`, `Move(C,B)`, `PickUp(Package, A)`, `PickUp(Package, B)`, `PickUp(Package, C)`, `Drop(Package, A)`, `Drop(Package, B)`, `Drop(Package, C)`[cite: 3].
*   **Preconditions and Effects:**
    *   **Move(X, Y)** - Preconditions: `At(Robot, X)`. Effects: `-At(Robot, X)`, `At(Robot, Y)`[cite: 3].
    *   **PickUp(Package, X)** - Preconditions: `At(Robot, X)`, `At(Package, X)`. Effects: `-At(Package, X)`, `Holding(Package)`[cite: 3].
    *   **Drop(Package, X)** - Preconditions: `At(Robot, X)`, `Holding(Package)`. Effects: `-Holding(Package)`, `At(Package, X)`[cite: 3].

## 2. Manually Constructed Plan
*   **$S_{0}$:** `At(Robot, A)`, `At(Package, A)`
*   **Action:** `PickUp(Package, A)`
*   **$S_{1}$:** `At(Robot, A)`, `Holding(Package)`
*   **Action:** `Move(A, B)`
*   **$S_{2}$:** `At(Robot, B)`, `Holding(Package)`
*   **Action:** `Move(B, C)`
*   **$S_{3}$:** `At(Robot, C)`, `Holding(Package)`
*   **Action:** `Drop(Package, C)`
*   **$S_{4}$:** `At(Robot, C)`, `At(Package, C)`

## 3. Prompt Used with the LLM
> "I want to implement a simple planning agent in Python. Represent a state as a set of logical propositions. Each action should contain: a name; positive preconditions; negative preconditions; positive effects; negative effects. An action is applicable if all of its preconditions are satisfied by the current state. When an action is applied: 1. remove its negative effects from the state; 2. add its positive effects to the state. Use breadth-first search to find a sequence of actions that achieves a specified goal. The program should also: detect when no plan exists; print the resulting sequence of actions; print the states reached after each action. Explain the implementation and identify any assumptions you make. Include the actions and initial state required to solve the warehouse problem where the robot and package start at A and must move to C."

## 4. Generated Python Program
*The generated Python program has been provided in the accompanying `planner.py` file.*

## 5. Results of Tests
*   **Test A (Solvable Problem):**
    *   **Initial state:** `{'At(Robot,A)', 'At(Package,A)'}`
    *   **Goal:** `{'At(Package,C)'}`
    *   **Plan found:** Yes.
    *   **Resulting plan:** `PickUp(Package,A)`, `Move(A,B)`, `Move(B,C)`, `Drop(Package,C)`.
    *   **Validity:** Valid. The sequence of logical state changes matches the manual plan.
*   **Test B (Impossible Problem):**
    *   **Initial state:** `{'At(Robot,A)', 'At(Package,A)'}`
    *   **Goal:** `{'At(Package,C)'}`
    *   **Plan found:** No plan found. (The `PickUp` actions were removed).
    *   **Validity:** Valid. The agent correctly deduced that the goal is logically unreachable.
*   **Test C (Irrelevant Actions):**
    *   **Initial state:** `{'At(Robot,A)', 'At(Package,A)'}`
    *   **Goal:** `{'At(Robot,C)'}`
    *   **Plan found:** Yes.
    *   **Resulting plan:** `Move(A,B)`, `Move(B,C)`.
    *   **Validity:** Valid. The agent did not waste steps interacting with the package.

## 6. Answers to "Think About It" Questions
*   **Task 0:** Starting from `I={At(Robot, A), At(Package, A)}`, the action `PickUp(Package, A)` is applicable because both preconditions (`At(Robot, A)` and `At(Package, A)`) are satisfied[cite: 3]. `Drop(Package, C)` is not applicable because its preconditions (`At(Robot, C)` and `Holding(Package)`) are false[cite: 3].
*   **Task 2:** 
    *   *Preconditions/Effects:* Evaluated in `Action.is_applicable()` and updated in `Action.apply()`[cite: 3].
    *   *Goal Termination:* Evaluated inside the `while` loop by checking if all goal propositions exist in the current state[cite: 3].
    *   *BFS Exploration:* Handled using a `collections.deque` and a `visited` set to safely track alternative state paths[cite: 3].
*   **Task 4:** Logical reasoning validates if an action can occur (`S ⊨ Preconditions(a)`) and computes the resulting state[cite: 3]. Search dictates the traversal strategy (BFS) to efficiently explore valid states until reaching the goal[cite: 3].
*   **Task 5:** I trust the independently executed state transitions. An LLM's explanation is a probabilistic text generation that mimics reasoning, whereas the Python implementation performs true deterministic logic based on strict state changes[cite: 3].

## 7. Reflection Questions
1.  **Why specify beforehand?** It forces human comprehension of the underlying logic and prevents the LLM from hallucinating rules or relying on unstated assumptions.
2.  **Error example:** If preconditions were ignored, the planner might select `Drop(Package, C)` immediately, erroneously teleporting the package to the goal without intermediate movement.
3.  **"Looks reasonable" vs Valid:** A plan might conceptually make sense to a human (e.g., "move to B, grab package"), but fail in a formal system if a strict intermediate logical state is missing.
4.  **LLM Contribution:** The LLM contributed the boilerplate object-oriented structure, the BFS queue implementation, and the syntax for set operations.
5.  **Independent Verification:** I had to independently verify that the graph search correctly avoided infinite loops (using the `visited` set) and that negative effects were properly clearing obsolete propositions from the state.
6.  **Where is logic used?** Logic acts as the edge-generator in the search graph, strictly defining which state transitions are possible.
7.  **Relation to previous module:** Planning builds directly upon search algorithms (like BFS). However, instead of navigating a static, hard-coded map, the graph's nodes (states) and edges (actions) are generated dynamically via logical rules.