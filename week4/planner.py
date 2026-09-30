from collections import deque

class Action:
    def __init__(self, name, pos_pre, neg_pre, pos_eff, neg_eff):
        self.name = name
        self.pos_pre = set(pos_pre)
        self.neg_pre = set(neg_pre)
        self.pos_eff = set(pos_eff)
        self.neg_eff = set(neg_eff)

    def is_applicable(self, state):
        for p in self.pos_pre:
            if p not in state:
                return False
        for p in self.neg_pre:
            if p in state:
                return False
        return True

    def apply(self, state):
        new_state = set(state)
        new_state.difference_update(self.neg_eff)
        new_state.update(self.pos_eff)
        return frozenset(new_state)

def plan(initial_state, goal_state, actions):
    initial_state = frozenset(initial_state)
    queue = deque([(initial_state, [])])
    visited = set([initial_state])

    while queue:
        current_state, path = queue.popleft()

        # Check if goal is met
        goal_met = True
        for g in goal_state:
            if g not in current_state:
                goal_met = False
                break
        
        if goal_met:
            return path

        # Explore alternatives
        for action in actions:
            if action.is_applicable(current_state):
                next_state = action.apply(current_state)
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [action]))

    return None

if __name__ == "__main__":
    # Problem Definition
    initial = {"At(Robot,A)", "At(Package,A)"}
    goal = {"At(Package,C)"}

    actions = [
        Action("Move(A,B)", ["At(Robot,A)"], [], ["At(Robot,B)"], ["At(Robot,A)"]),
        Action("Move(B,A)", ["At(Robot,B)"], [], ["At(Robot,A)"], ["At(Robot,B)"]),
        Action("Move(B,C)", ["At(Robot,B)"], [], ["At(Robot,C)"], ["At(Robot,B)"]),
        Action("Move(C,B)", ["At(Robot,C)"], [], ["At(Robot,B)"], ["At(Robot,C)"]),
        Action("PickUp(Package,A)", ["At(Robot,A)", "At(Package,A)"], [], ["Holding(Package)"], ["At(Package,A)"]),
        Action("PickUp(Package,B)", ["At(Robot,B)", "At(Package,B)"], [], ["Holding(Package)"], ["At(Package,B)"]),
        Action("PickUp(Package,C)", ["At(Robot,C)", "At(Package,C)"], [], ["Holding(Package)"], ["At(Package,C)"]),
        Action("Drop(Package,A)", ["At(Robot,A)", "Holding(Package)"], [], ["At(Package,A)"], ["Holding(Package)"]),
        Action("Drop(Package,B)", ["At(Robot,B)", "Holding(Package)"], [], ["At(Package,B)"], ["Holding(Package)"]),
        Action("Drop(Package,C)", ["At(Robot,C)", "Holding(Package)"], [], ["At(Package,C)"], ["Holding(Package)"])
    ]

    print("--- Test A: Solvable Problem ---")
    result_a = plan(initial, goal, actions)
    if result_a:
        print("Plan found:")
        current = frozenset(initial)
        print(f"Initial State: {set(current)}")
        for a in result_a:
            print(f"Action: {a.name}")
            current = a.apply(current)
            print(f"State after action: {set(current)}")
    else:
        print("No plan found.")

    print("\n--- Test B: Impossible Problem ---")
    impossible_actions = [a for a in actions if not a.name.startswith("PickUp")]
    result_b = plan(initial, goal, impossible_actions)
    if result_b:
        print("Plan found:", [a.name for a in result_b])
    else:
        print("No plan found.")

    print("\n--- Test C: Irrelevant Actions ---")
    irrelevant_goal = {"At(Robot,C)"} 
    result_c = plan(initial, irrelevant_goal, actions)
    if result_c:
        print("Plan found for irrelevant action test:")
        current = frozenset(initial)
        print(f"Initial State: {set(current)}")
        for a in result_c:
            print(f"Action: {a.name}")
            current = a.apply(current)
            print(f"State after action: {set(current)}")
    else:
        print("No plan found.")