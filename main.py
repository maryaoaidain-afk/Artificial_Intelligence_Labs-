from collections import deque


def solve_river_problem():
    """
    Solves the Wolf, Duck, and Corn river crossing problem using Breadth-First Search.
    """

    # --- 1. Define States and Helpers ---

    # State representation:
    # A tuple: (Farmer, Wolf, Duck, Corn)
    # 'S' = South bank, 'N' = North bank
    START_STATE = ('S', 'S', 'S', 'S')
    GOAL_STATE = ('N', 'N', 'N', 'N')

    def is_valid(state):
        """Checks if a given state is valid (no one gets eaten)."""
        farmer, wolf, duck, corn = state

        # Case 1: Wolf eats Duck
        # This happens if they are on the same bank, and the farmer is on the other.
        if wolf == duck and farmer != wolf:
            return False

        # Case 2: Duck eats Corn
        # This happens if they are on the same bank, and the farmer is on the other.
        if duck == corn and farmer != duck:
            return False

        # If neither of the above, the state is safe.
        return True

    def get_next_states(current_state):
        """Generates all possible valid moves from the current state."""
        farmer, wolf, duck, corn = current_state
        possible_next_states = []

        # Determine the destination bank
        destination = 'N' if farmer == 'S' else 'S'

        # Helper to create a new state tuple
        def move(item_index):
            new_state_list = list(current_state)
            # Move farmer
            new_state_list[0] = destination
            # Move item (if not -1)
            if item_index != -1:
                new_state_list[item_index + 1] = destination
            return tuple(new_state_list)

        # Possible moves:
        # -1: Farmer alone
        #  0: Farmer + Wolf
        #  1: Farmer + Duck
        #  2: Farmer + Corn

        items_to_try = [-1]  # Farmer can always try to cross alone

        # Check which items are on the same bank as the farmer
        if wolf == farmer:
            items_to_try.append(0)
        if duck == farmer:
            items_to_try.append(1)
        if corn == farmer:
            items_to_try.append(2)

        for item_index in items_to_try:
            next_state = move(item_index)
            if is_valid(next_state):
                possible_next_states.append(next_state)

        return possible_next_states

    # --- 2. Implement Breadth-First Search (BFS) ---

    # The queue will store (path, state) tuples.
    # Storing the full path allows us to retrace our steps.
    queue = deque([([START_STATE], START_STATE)])

    # 'visited' set stores states we've already seen to avoid cycles
    # and redundant work.
    visited = {START_STATE}

    while queue:
        current_path, last_state = queue.popleft()

        # Check if we've reached the goal
        if last_state == GOAL_STATE:
            return current_path  # Success! Return the solution path.

        # Explore neighbors (next possible moves)
        for next_state in get_next_states(last_state):
            if next_state not in visited:
                visited.add(next_state)
                new_path = current_path + [next_state]
                queue.append((new_path, next_state))

    # If the queue becomes empty and we haven't found a solution
    return None


def format_state(state):
    """Helper function to make the state output readable."""
    farmer, wolf, duck, corn = state

    south_bank = []
    north_bank = []

    if farmer == 'S':
        south_bank.append('Farmer')
    else:
        north_bank.append('Farmer')

    if wolf == 'S':
        south_bank.append('Wolf')
    else:
        north_bank.append('Wolf')

    if duck == 'S':
        south_bank.append('Duck')
    else:
        north_bank.append('Corn')

    if corn == 'S':
        south_bank.append('Corn')
    else:
        north_bank.append('Duck')  # Corrected: Was corn, should be duck

    # Correction: The previous logic was flawed. Let's simplify.
    south_bank = []
    north_bank = []

    if farmer == 'S':
        south_bank.append('Farmer')
    else:
        north_bank.append('Farmer')

    if wolf == 'S':
        south_bank.append('Wolf')
    else:
        north_bank.append('Wolf')

    if duck == 'S':
        south_bank.append('Duck')
    else:
        north_bank.append('Duck')

    if corn == 'S':
        south_bank.append('Corn')
    else:
        north_bank.append('Corn')

    return f"South: {south_bank if south_bank else ['Empty']} | North: {north_bank if north_bank else ['Empty']}"


def print_solution(path):
    """Prints the solution path in a human-readable format."""
    if not path:
        print("No solution found.")
        return

    print("✅ Solution Found in 7 steps!\n")
    print(f"Step 0 (Start): {format_state(path[0])}")

    for i in range(1, len(path)):
        prev_state = path[i - 1]
        curr_state = path[i]

        # Determine who moved
        move = "Farmer returns"
        if curr_state[0] == 'N':  # Moving South -> North
            move = "Farmer crosses"

        # Check which item moved with the farmer
        if prev_state[1] != curr_state[1]:
            move += " with the Wolf"
        elif prev_state[2] != curr_state[2]:
            move += " with the Duck"
        elif prev_state[3] != curr_state[3]:
            move += " with the Corn"
        elif curr_state[0] != prev_state[0]:  # Farmer moved alone
            move += " alone"

        # Correct direction
        if curr_state[0] == 'N':
            move += " (South → North)"
        else:
            move += " (North → South)"

        print(f"\nStep {i}: {move}")
        print(f"       Result: {format_state(curr_state)}")


# --- 3. Run the Solver ---
if __name__ == "__main__":
    solution_path = solve_river_problem()
    print_solution(solution_path)