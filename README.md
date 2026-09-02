# Logical Reasoning for Planning — Warehouse Robot

Submission for the AI Lab: *Using an LLM to Construct and Test a Simple Planning Agent*.

## 1. Problem Specification

**Locations:** A, B, C
**Initial state:**
```
I = { At(Robot, A), At(Package, A) }
```
**Goal:**
```
G = { At(Package, C) }
```

**Actions**

| Action | Preconditions | Effects |
|---|---|---|
| `Move(X,Y)` (for connected X,Y) | `At(Robot,X)` | ¬`At(Robot,X)`, `At(Robot,Y)` |
| `PickUp(Package,X)` | `At(Robot,X)`, `At(Package,X)` | ¬`At(Package,X)`, `Holding(Package)` |
| `Drop(Package,X)` | `At(Robot,X)`, `Holding(Package)` | ¬`Holding(Package)`, `At(Package,X)` |

Connections: A–B, B–C (bidirectional).

**Initial applicability check**
- `PickUp(Package,A)`: preconditions `At(Robot,A)` and `At(Package,A)` both hold in I → **applicable**.
- `Drop(Package,C)`: precondition `Holding(Package)` does not hold in I (nothing is being held yet) → **not applicable**.

## 2. Manually Constructed Plan

| State | Facts |
|---|---|
| S0 | At(Robot,A), At(Package,A) |
| S1 | At(Robot,A), Holding(Package) |
| S2 | At(Robot,B), Holding(Package) |
| S3 | At(Robot,C), Holding(Package) |
| S4 | At(Robot,C), At(Package,C) |

Plan: `PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)`

Precondition check at each step (independently traced, not just asserted by the plan):

- **PickUp(Package,A)** in S0: needs `At(Robot,A)`, `At(Package,A)` — both in S0. ✓
- **Move(A,B)** in S1: needs `At(Robot,A)` — in S1. ✓
- **Move(B,C)** in S2: needs `At(Robot,B)` — in S2. ✓
- **Drop(Package,C)** in S3: needs `At(Robot,C)`, `Holding(Package)` — both in S3. ✓
- S4 contains `At(Package,C)` → goal satisfied.

## 3. LLM Prompt Used

```
I want to implement a simple planning agent in Python.
Represent a state as a set of logical propositions.
Each action should contain:
• a name;
• positive preconditions;
• negative preconditions;
• positive effects;
• negative effects.

An action is applicable if all of its preconditions are satisfied by the current state.
When an action is applied:
1. remove its negative effects from the state;
2. add its positive effects to the state.

Use breadth-first search to find a sequence of actions that achieves a specified goal.

The program should also:
• detect when no plan exists;
• print the resulting sequence of actions;
• print the states reached after each action.

Explain the implementation and identify any assumptions you make.
```

## 4. Generated Python Program

See [`planner.py`](./planner.py).

Key pieces, mapped back to the spec:
- **Preconditions → applicability**: `Action.is_applicable` checks `pos_preconditions ⊆ state` and `neg_preconditions ∩ state = ∅`, i.e. `S |= Preconditions(a)`.
- **Effects → state update**: `Action.apply` removes `neg_effects` then adds `pos_effects`.
- **Goal → termination**: `goal_satisfied` is checked every time a new state is generated during search.
- **BFS → exploring alternatives**: `bfs_plan` uses a FIFO queue and a `visited` set, expanding plans in order of increasing length, which guarantees the shortest plan is returned first.

## 5. Test Results

### Test A — Solvable Problem
- Initial: `{At(Robot,A), At(Package,A)}`, Goal: `{At(Package,C)}`
- Plan found: `PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)`
- Matches the hand-derived plan above. **Valid.**

### Test B — Impossible Problem (PickUp actions removed)
- Same initial/goal, but no `PickUp` actions available.
- Result: **No plan found** — correct, since the package can never be picked up, so it can never leave A.

### Test C — Irrelevant Actions Present
- Robot-only `Move` actions exist alongside the pickup/drop actions (i.e. the robot *can* wander without the package).
- Result: planner still returns `PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)` — it does not mistake the robot reaching C for the package reaching C, because the goal is defined purely over `At(Package,C)`.

## 6. "Think About It" Answers

**Search diagram completion:**
```
Current state
  ↓
Check action preconditions
  ↓
Is the action applicable?  (S |= Preconditions(a))
  ↓
Generate successor state   (Apply(S, a))
  ↓
Search over alternatives   (BFS frontier)
  ↓
Goal?
```

**How logic and search work together:** at each state, logic decides *which actions are even legal* (by checking preconditions against the current propositions); search decides *which of those legal actions to try next, and in what order*, exploring the resulting state graph until a state satisfying the goal is reached. Logic prunes the branching factor; search finds the path.

**LLM explanation vs. independently executed transitions (Task 5):** the independently executed state transitions (b) should be trusted more. An LLM's natural-language explanation of *why* a plan is valid is a separate generation process from the plan itself — it can sound coherent and still misdescribe a precondition or skip a step, because nothing forces the explanation to be checked against the actual code execution. The Python program's state trace is mechanically derived from the same rules used to build the plan, so it's a real independent check rather than a restated justification.

## 7. Reflection Questions

1. **Why specify preconditions/effects before asking an LLM to write the planner?**
   Because the specification is what makes the output verifiable. If you just ask an LLM to "write a planner," you have no fixed contract to check its output against — you can't tell whether an action was applied correctly or whether the search logic is even doing what you think. Writing the preconditions/effects first turns "does this code work" into a checkable question.

2. **Example error from not checking preconditions:**
   The planner could apply `Drop(Package,C)` even when the robot isn't holding the package, silently adding `At(Package,C)` to the state without the package ever having moved there — producing a "valid-looking" plan that's physically impossible.

3. **Why a plan that "looks reasonable" isn't necessarily valid:**
   A plan can have a sensible-looking sequence of action names while still violating a precondition at some step (e.g. dropping a package that was never picked up, or moving through a location that isn't actually connected). Surface plausibility isn't the same as satisfying `S |= Preconditions(a)` at every step — only an explicit check confirms that.

4. **What did the LLM contribute?**
   The boilerplate implementation: the `Action` class structure, the BFS loop, state representation as sets/frozensets, and the printing logic — translating the specification into working Python quickly.

5. **What did I have to verify independently?**
   That each action's preconditions were genuinely satisfied in the state where it was applied (done by hand in Section 2 and cross-checked against the program's printed states), and that the "No plan found" case (Test B) and the irrelevant-actions case (Test C) behaved correctly rather than just trusting the code's output at face value.

6. **Where is logical reasoning used in this lab?**
   In checking whether `S |= Preconditions(a)` — determining whether an action is applicable in a given state — and in defining how effects update the state (adding/removing propositions).

7. **How does this relate to search algorithms from the previous module?**
   Planning here is framed as search over a state graph, where each action is an edge to a successor state; BFS explores that graph level-by-level to find the shortest sequence of actions from the initial state to a goal state, exactly like uninformed search over any other state-space problem.

## 8. Reflection on LLM Use

The LLM was useful for quickly producing a working implementation once given a precise specification, but it did not remove the need to independently verify correctness. Testing with a solvable case, an impossible case, and a case with irrelevant/misleading actions caught the kinds of errors that a plausible-looking but wrong planner could otherwise hide. The main lesson: **generation and verification are separate steps**, and skipping the verification step means trusting code (or an explanation) that was never actually checked against the specification.
