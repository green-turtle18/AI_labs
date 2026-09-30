"""
Simple STRIPS-style planning agent.

A state is represented as a frozenset of propositions (strings), e.g.
    {"At(Robot,A)", "At(Package,A)"}

Each Action has:
    name                - a label, e.g. "Move(A,B)"
    pos_preconditions   - propositions that must be present in the state
    neg_preconditions   - propositions that must be absent from the state
    pos_effects         - propositions added to the state after the action
    neg_effects         - propositions removed from the state after the action

Planning is done with breadth-first search (BFS) over states, which
guarantees the shortest plan (in number of actions) is found, since BFS
explores plans in increasing order of length.
"""

from collections import deque


class Action:
    def __init__(self, name, pos_preconditions=None, neg_preconditions=None,
                 pos_effects=None, neg_effects=None):
        self.name = name
        self.pos_preconditions = set(pos_preconditions or [])
        self.neg_preconditions = set(neg_preconditions or [])
        self.pos_effects = set(pos_effects or [])
        self.neg_effects = set(neg_effects or [])

    def is_applicable(self, state):
        """An action is applicable iff all positive preconditions are
        present in the state AND all negative preconditions are absent."""
        return self.pos_preconditions.issubset(state) and \
               self.neg_preconditions.isdisjoint(state)

    def apply(self, state):
        """Apply the action: remove negative effects, then add positive
        effects. Order matters only if a proposition appears in both
        effect sets; here we remove first, then add, so positive effects
        win in that (unusual) case."""
        new_state = (set(state) - self.neg_effects) | self.pos_effects
        return frozenset(new_state)

    def __repr__(self):
        return self.name


def goal_satisfied(state, goal):
    """Goal is a set of propositions that must all hold in the state."""
    return set(goal).issubset(state)


def bfs_plan(initial_state, actions, goal):
    """
    Breadth-first search over the state space.

    Returns (plan, states) where:
        plan   - list of Action objects, in order, or None if no plan exists
        states - list of states S0, S1, ..., Sn visited along that plan
    """
    initial_state = frozenset(initial_state)

    if goal_satisfied(initial_state, goal):
        return [], [initial_state]

    # Each queue entry: (state, plan_so_far, states_so_far)
    frontier = deque([(initial_state, [], [initial_state])])
    visited = {initial_state}

    while frontier:
        state, plan, states = frontier.popleft()

        for action in actions:
            if not action.is_applicable(state):
                continue

            next_state = action.apply(state)

            if next_state in visited:
                continue

            new_plan = plan + [action]
            new_states = states + [next_state]

            if goal_satisfied(next_state, goal):
                return new_plan, new_states

            visited.add(next_state)
            frontier.append((next_state, new_plan, new_states))

    return None, None  # no plan found


def run_planner(initial_state, actions, goal, label=""):
    print(f"=== {label} ===")
    print("Initial state:", set(initial_state))
    print("Goal:", set(goal))

    plan, states = bfs_plan(initial_state, actions, goal)

    if plan is None:
        print("No plan found")
        print()
        return

    print("Plan found:")
    for i, action in enumerate(plan):
        print(f"  Step {i+1}: {action}")

    print("\nStates reached after each action:")
    print(f"  S0 = {set(states[0])}")
    for i, (action, state) in enumerate(zip(plan, states[1:]), start=1):
        print(f"  S{i} = {set(state)}   (after {action})")
    print()


# ---------------------------------------------------------------------------
# Warehouse problem setup
# ---------------------------------------------------------------------------

def make_warehouse_actions():
    actions = []

    # Move actions between connected locations
    connections = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]
    for (x, y) in connections:
        actions.append(Action(
            name=f"Move({x},{y})",
            pos_preconditions={f"At(Robot,{x})"},
            neg_preconditions=set(),
            pos_effects={f"At(Robot,{y})"},
            neg_effects={f"At(Robot,{x})"},
        ))

    # PickUp actions at each location
    
    for loc in ["A", "B", "C"]:
        actions.append(Action(
            name=f"PickUp(Package,{loc})",
            pos_preconditions={f"At(Robot,{loc})", f"At(Package,{loc})"},
            neg_preconditions=set(),
            pos_effects={"Holding(Package)"},
            neg_effects={f"At(Package,{loc})"},
        ))
    

    # Drop actions at each location
    for loc in ["A", "B", "C"]:
        actions.append(Action(
            name=f"Drop(Package,{loc})",
            pos_preconditions={f"At(Robot,{loc})", "Holding(Package)"},
            neg_preconditions=set(),
            pos_effects={f"At(Package,{loc})"},
            neg_effects={"Holding(Package)"},
        ))

    return actions


if __name__ == "__main__":
    # ---- Test A: Solvable problem (original warehouse) ----
    initial_state = {"At(Robot,A)", "At(Package,A)"}
    goal = {"At(Package,C)"}
    actions = make_warehouse_actions()
    run_planner(initial_state, actions, goal, label="Test A: Solvable Problem")

    # ---- Test B: Impossible problem (no PickUp actions) ----
    actions_no_pickup = [a for a in actions if not a.name.startswith("PickUp")]
    run_planner(initial_state, actions_no_pickup, goal,
                label="Test B: Impossible Problem (PickUp removed)")

    # ---- Test C: Irrelevant actions (robot moves, package doesn't) ----
    # Same action set as Test A; goal only in terms of the package, so
    # actions that only move the robot must not be mistaken for progress.
    run_planner(initial_state, actions, goal,
                label="Test C: Irrelevant Actions (robot-only moves present)")