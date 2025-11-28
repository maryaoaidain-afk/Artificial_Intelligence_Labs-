from collections import deque


class State:
    def __init__(self, missionaries, cannibals, boat):
        self.missionaries = missionaries
        self.cannibals = cannibals
        self.boat = boat  # 1 for Left bank, 0 for Right bank
        self.parent = None  # To trace the path back

    def is_valid(self):
        # Check bounds
        if self.missionaries < 0 or self.cannibals < 0 or self.missionaries > 3 or self.cannibals > 3:
            return False

        # Check Left bank constraints
        if self.missionaries > 0 and self.missionaries < self.cannibals:
            return False

        # Check Right bank constraints
        m_right = 3 - self.missionaries
        c_right = 3 - self.cannibals
        if m_right > 0 and m_right < c_right:
            return False

        return True

    def is_goal(self):
        return self.missionaries == 0 and self.cannibals == 0 and self.boat == 0

    def __eq__(self, other):
        return (self.missionaries == other.missionaries and
                self.cannibals == other.cannibals and
                self.boat == other.boat)

    def __hash__(self):
        return hash((self.missionaries, self.cannibals, self.boat))

    def __str__(self):
        side = "Left" if self.boat == 1 else "Right"
        return f"Left Bank: ({self.missionaries}M, {self.cannibals}C) | Boat: {side} | Right Bank: ({3 - self.missionaries}M, {3 - self.cannibals}C)"


def get_successors(current_state):
    successors = []
    # Possible moves: (Missionaries, Cannibals) to move
    moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

    # If boat is on Left (1), we subtract; if on Right (0), we add to Left bank
    direction = -1 if current_state.boat == 1 else 1

    for m, c in moves:
        new_m = current_state.missionaries + (direction * m)
        new_c = current_state.cannibals + (direction * c)
        new_boat = 1 - current_state.boat

        new_state = State(new_m, new_c, new_boat)
        if new_state.is_valid():
            new_state.parent = current_state
            successors.append(new_state)

    return successors


def solve_bfs():
    initial_state = State(3, 3, 1)
    if initial_state.is_goal():
        return initial_state

    frontier = deque([initial_state])
    explored = set()

    while frontier:
        state = frontier.popleft()

        if state.is_goal():
            return state

        explored.add(state)

        for child in get_successors(state):
            if child not in explored and child not in frontier:
                frontier.append(child)
    return None


def print_solution(solution):
    path = []
    curr = solution
    while curr:
        path.append(curr)
        curr = curr.parent
    path.reverse()

    print("Missionaries & Cannibals Solution (BFS):")
    print("-" * 50)
    for i, state in enumerate(path):
        print(f"Step {i}: {state}")
    print("-" * 50)
    print("Goal Reached!")


if __name__ == "__main__":
    solution = solve_bfs()
    if solution:
        print_solution(solution)
    else:
        print("No solution found.")