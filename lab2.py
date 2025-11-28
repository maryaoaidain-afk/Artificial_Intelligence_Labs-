from collections import deque

# تعريف ثابت للحالة الكلية (لتسهيل القراءة)
TOTAL_M = 3
TOTAL_C = 3


class State:
    def __init__(self, missionaries, cannibals, boat):
        self.missionaries = missionaries  # M_Left
        self.cannibals = cannibals  # C_Left
        self.boat = boat  # 0 for Left bank (Start), 1 for Right bank (Goal)
        self.parent = None
        self.action_taken = ""  # لتخزين الحركة التي أدت لهذه الحالة

    def is_valid(self):
        # التحقق من الحدود (الأعداد بين 0 و 3)
        if not (0 <= self.missionaries <= TOTAL_M and 0 <= self.cannibals <= TOTAL_C):
            return False

        # 1. التحقق من قيد الضفة اليسرى (الضفة الحالية)
        # إذا كان M > 0 و C > M (آكلو لحوم البشر أكثر من المبشرين)
        if self.missionaries > 0 and self.missionaries < self.cannibals:
            return False

        # 2. التحقق من قيد الضفة اليمنى (الضفة المعاكسة)
        m_right = TOTAL_M - self.missionaries
        c_right = TOTAL_C - self.cannibals
        # إذا كان M_Right > 0 و C_Right > M_Right
        if m_right > 0 and m_right < c_right:
            return False

        return True

    def is_goal(self):
        # الهدف: 0 مبشر و 0 آكل لحوم بشر في اليسار، والقارب في اليمين (1)
        return self.missionaries == 0 and self.cannibals == 0 and self.boat == 1

    def __eq__(self, other):
        return (self.missionaries == other.missionaries and
                self.cannibals == other.cannibals and
                self.boat == other.boat)

    def __hash__(self):
        return hash((self.missionaries, self.cannibals, self.boat))

    def __str__(self):
        side = "Right (اليمين)" if self.boat == 1 else "Left (اليسار)"
        m_right = TOTAL_M - self.missionaries
        c_right = TOTAL_C - self.cannibals

        return f"Left Bank: ({self.missionaries}M, {self.cannibals}C) | Boat: {side} | Right Bank: ({m_right}M, {c_right}C)"


def get_successors(current_state):
    successors = []
    # الحركات الممكنة: (M_move, C_move)
    moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

    # إذا كان القارب في اليسار (0)، الاتجاه هو +1 (نقل لليمين)
    # إذا كان القارب في اليمين (1)، الاتجاه هو -1 (نقل لليسار)
    direction = 1 if current_state.boat == 0 else -1

    for m_move, c_move in moves:
        # يجب أن يكون عدد الركاب 1 أو 2
        if not (1 <= m_move + c_move <= 2):
            continue

        # 1. تحديد الحالة الجديدة (Boat moves from B to 1-B)
        new_m = current_state.missionaries - (direction * m_move)
        new_c = current_state.cannibals - (direction * c_move)
        new_boat = 1 - current_state.boat  # عكس موقع القارب

        new_state = State(new_m, new_c, new_boat)

        # 2. التحقق من صلاحية الحالة الجديدة
        if new_state.is_valid():
            # 3. توثيق الحركة والأصل (للتتبع)
            new_state.parent = current_state

            # توضيح الحركة التي أدت إلى هذه الحالة الجديدة
            action_name = f"نقل {m_move}M و {c_move}C"
            if direction == 1:
                action_name += " ← (لليسار)"
            else:
                action_name += " → (لليمين)"

            new_state.action_taken = action_name
            successors.append(new_state)

    return successors


def solve_bfs():
    # الحالة الأولية: (3, 3, 0) الجميع في اليسار (0)
    initial_state = State(TOTAL_M, TOTAL_C, 0)
    if initial_state.is_goal():
        return initial_state

    # قائمة الانتظار (Frontier) - BFS
    frontier = deque([initial_state])
    # مجموعة الاستكشاف (Explored Set) - لتجنب التكرار/الحلقات
    explored = {initial_state}

    while frontier:
        state = frontier.popleft()  # نختار الأقدم (لضمان أقصر مسار)

        if state.is_goal():
            return state

        # لا نحتاج لإضافة state إلى explored هنا، لأنها أضيفت عند إنشائها
        # ولكن للتأكد من عدم تكرار التوليد، نتركها كما في الكود السابق.

        for child in get_successors(state):
            # شرط الترشيح: لم يُستكشف سابقاً
            if child not in explored:  # هذا الشرط وحده كافٍ لأن child لا يمكن أن يكون في frontier لو كان في explored
                explored.add(child)
                frontier.append(child)
    return None


def print_solution(solution):
    path = []
    curr = solution

    # 1. تتبع المسار للخلف (باستخدام Parent)
    while curr:
        path.append(curr)
        curr = curr.parent

    path.reverse()  # عكس المسار لطباعته من البداية للنهاية

    print("Missionaries & Cannibals Solution (Goal-Based Agent/BFS):")
    print("-" * 75)

    # 2. طباعة كل خطوة مع الإجراء المتخذ
    for i, state in enumerate(path):
        action = state.action_taken if i > 0 else "--- Initial State ---"
        print(f"Step {i}: {state} | Action: {action}")

    print("-" * 75)
    print(f"Goal Reached in {len(path) - 1} steps!")


if __name__ == "__main__":
    solution = solve_bfs()
    if solution:
        print_solution(solution)
    else:
        print("No solution found.")