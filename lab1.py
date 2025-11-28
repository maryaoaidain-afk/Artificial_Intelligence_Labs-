
from collections import deque


# --- Agent 1: Utility-Based Agent (From User) ---
# This agent is good for its original problem (delivery)
# but is the WRONG tool for the river puzzle.

class UtilityBasedDeliveryAgent:
    def __init__(self):
        self.position = 0
        self.has_package = False
        self.package_delivered = False
        self.world = None

    def perceive(self, world_state):
        """Perceive the environment"""
        self.world = world_state

    def calculate_utility(self, action):
        """Calculate utility for each possible action"""
        utilities = {
            "move_left": self._utility_move(-1),
            "move_right": self._utility_move(1),
            "pickup_package": self._utility_pickup(),
            "package_delivered": self._utility_deliver(),
            "wait": -10  # Waiting is usually bad
        }
        return utilities.get(action, -100)  # Unknown actions have very low utility

    def _utility_move(self, direction):
        """Calculate utility for moving"""
        new_pos = self.position + direction

        # Check if move is valid
        if new_pos < 0 or new_pos > 10:  # Assuming world bounds
            return -100  # Invalid move

        utility = -1  # Base cost for moving

        if self.has_package:
            # Carrying package - utility based on distance to delivery
            distance_to_delivery = abs(new_pos - self.world.delivery_location)
            utility -= distance_to_delivery * 0.5
            # High reward for getting closer to delivery
            if distance_to_delivery < abs(self.position - self.world.delivery_location):
                utility += 2
        else:
            # Not carrying package - utility based on distance to package
            distance_to_package = abs(new_pos - self.world.package_location)
            utility -= distance_to_package * 0.5
            # High reward for getting closer to package
            if distance_to_package < abs(self.position - self.world.package_location):
                utility += 2

        return utility

    def _utility_pickup(self):
        """Calculate utility for picking up package"""
        if (not self.has_package and
                self.position == self.world.package_location):
            return 10  # High reward for successful pickup
        return -10  # Penalty for impossible pickup

    def _utility_deliver(self):
        """Calculate utility for delivering package"""
        if (self.has_package and
                self.position == self.world.delivery_location):
            return 25  # Very high reward for delivery
        return -20  # Penalty for impossible delivery

    def act(self):
        """Choose and execute best action based on utility"""
        possible_actions = ["move_left", "move_right"]

        # Add special actions if conditions are met
        if self.position == self.world.package_location and not self.has_package:
            possible_actions.append("pickup_package")
        if self.position == self.world.delivery_location and self.has_package:
            possible_actions.append("package_delivered")

        # Calculate utilities for all possible actions
        action_utilities = {action: self.calculate_utility(action) for action in possible_actions}

        # Choose action with higher utility
        best_action = max(action_utilities, key=action_utilities.get)
        best_utility = action_utilities[best_action]

        # Execute the action
        if best_action == "move_left":
            self.position -= 1
        elif best_action == "move_right":
            self.position += 1
        elif best_action == "pickup_package":
            self.has_package = True
        elif best_action == "package_delivered":
            self.has_package = False
            self.package_delivered = True

        return best_action, best_utility

    def run(self, world_state, max_steps=20):
        """Run the utility-based agent"""
        self.perceive(world_state)
        print("\nUtility-Based Agent Starting!")
        print(f"Package at: {self.world.package_location}, Deliver to: {self.world.delivery_location}")
        print("=" * 40)

        for step in range(max_steps):
            action, utility = self.act()
            print(
                f"Step {step + 1}: Pos={self.position}, Action={action}, Utility={utility:.1f}, HasPackage={self.has_package}")

            if self.package_delivered:
                print("Package delivered successfully!")
                return True

        print("Failed to deliver package")
        return False


class WorldState:
    def __init__(self, package_loc, delivery_loc):
        self.package_location = package_loc
        self.delivery_location = delivery_loc


# --- Agent 2: Problem-Solving Agent (Correct for the River Problem) ---
# This is the correct type of agent to solve the puzzle.
# It uses Breadth-First Search (BFS) to find the shortest
# sequence of VALID moves.

class RiverProblemSolvingAgent:
    def __init__(self):
        """
        A state is a tuple: (Farmer, Wolf, Duck, Corn)
        'S' = South bank, 'N' = North bank
        """
        self.START_STATE = ('S', 'S', 'S', 'S')
        self.GOAL_STATE = ('N', 'N', 'N', 'N')

    def _is_valid(self, state):
        """Checks if a given state is valid (no one gets eaten)."""
        farmer, wolf, duck, corn = state

        # Case 1: Wolf eats Duck
        if wolf == duck and farmer != wolf:
            return False

        # Case 2: Duck eats Corn
        if duck == corn and farmer != duck:
            return False

        return True

    def _get_next_states(self, current_state):
        """Generates all possible valid moves from the current state."""
        farmer, wolf, duck, corn = current_state
        possible_next_states = []

        destination = 'N' if farmer == 'S' else 'S'

        # Helper to create a new state tuple
        def move(item_index):
            new_state_list = list(current_state)
            new_state_list[0] = destination  # Move farmer
            if item_index != -1:
                new_state_list[item_index + 1] = destination  # Move item
            return tuple(new_state_list)

        # Items to try moving (by index):
        # -1: Farmer alone
        #  0: Farmer + Wolf
        #  1: Farmer + Duck
        #  2: Farmer + Corn
        items_on_same_bank = [-1]  # Farmer can always try to cross alone
        if wolf == farmer: items_on_same_bank.append(0)
        if duck == farmer: items_on_same_bank.append(1)
        if corn == farmer: items_on_same_bank.append(2)

        for item_index in items_on_same_bank:
            next_state = move(item_index)
            if self._is_valid(next_state):
                possible_next_states.append(next_state)

        return possible_next_states

    def solve(self):
        """
        Solves the puzzle using Breadth-First Search (BFS).
        BFS guarantees the shortest solution.
        """

        # The queue stores (path, state) tuples.
        queue = deque([([self.START_STATE], self.START_STATE)])

        # 'visited' stores states we've seen to avoid cycles.
        visited = {self.START_STATE}

        while queue:
            current_path, last_state = queue.popleft()

            if last_state == self.GOAL_STATE:
                return current_path  # Success!

            for next_state in self._get_next_states(last_state):
                if next_state not in visited:
                    visited.add(next_state)
                    new_path = current_path + [next_state]
                    queue.append((new_path, next_state))

        return None  # No solution found

    def _format_state(self, state):
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
            north_bank.append('Duck')

        if corn == 'S':
            south_bank.append('Corn')
        else:
            north_bank.append('Corn')

        south_str = ", ".join(south_bank) if south_bank else "Empty"
        north_str = ", ".join(north_bank) if north_bank else "Empty"
        return f"South: [{south_str}] | North: [{north_str}]"

    def print_solution(self, path):
        """Prints the solution path in a human-readable format."""
        if not path:
            print("No solution found.")
            return

        print(f"✅ Solution Found in {len(path) - 1} steps!\n")
        print(f"Step 0 (Start): {self._format_state(path[0])}")

        for i in range(1, len(path)):
            prev_state = path[i - 1]
            curr_state = path[i]

            # Determine who moved
            move = "Farmer"
            direction = "(South → North)" if curr_state[0] == 'N' else "(North → South)"

            if prev_state[1] != curr_state[1]:
                move += " takes the Wolf"
            elif prev_state[2] != curr_state[2]:
                move += " takes the Duck"
            elif prev_state[3] != curr_state[3]:
                move += " takes the Corn"
            else:
                move += " returns alone"

            print(f"\nStep {i}: {move} {direction}")
            print(f"       Result: {self._format_state(curr_state)}")


# --- Main execution block to run both agents ---

if __name__ == "__main__":
    # 1. Run the Utility-Based Agent (for its original problem)
    print("=" * 50)
    print("UTILITY-BASED AGENT DEMONSTRATION")
    world = WorldState(package_loc=3, delivery_loc=6)
    utility_agent = UtilityBasedDeliveryAgent()
    utility_agent.run(world)

    # 2. Run the Problem-Solving Agent (for the new problem)
    print("\n\n" + "=" * 50)
    print("RIVER PROBLEM-SOLVING AGENT DEMONSTRATION")
    river_agent = RiverProblemSolvingAgent()
    solution_path = river_agent.solve()
    river_agent.print_solution(solution_path)