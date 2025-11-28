"""
هذا الملف يوضح نوعين مختلفين من وكلاء الذكاء الاصطناعي (AI Agents).

1. UtilityBasedDeliveryAgent (وكيل التوصيل القائم على المنفعة):
    - النوع: وكيل قائم على المنفعة (Utility-Based).
    - المشكلة: يجد المسار الأكثر "كفاءة" بناءً على حساب النقاط (مكافأة - تكلفة).
    - مناسب لـ: البيئات المتغيرة، اتخاذ القرارات التي فيها مفاضلة (Trade-offs).

2. RiverProblemSolvingAgent (وكيل حل مشكلة النهر):
    - النوع: وكيل حل المشكلات (Problem-Solving) باستخدام البحث في فضاء الحالات.
    - المشكلة: يحل لغز المزارع والذئب والبطة والذرة.
    - مناسب لـ: الألغاز المنطقية، إيجاد المسارات، والمشاكل ذات القواعد الصارمة.

الدرس المستفاد: الوكيل القائم على المنفعة لا يمكنه حل مشكلة النهر، لأن اللغز يعتمد على
حالات "صحيحة/خاطئة" (Valid/Invalid) وليس "جيدة/سيئة" (Good/Bad).
"""

from collections import deque  # استيراد هيكل بيانات "الطابور" لاستخدامه في خوارزمية البحث (BFS)


# --- الوكيل الأول: وكيل التوصيل القائم على المنفعة (من الكود الأصلي) ---
# هذا الوكيل جيد لمشكلة التوصيل ولكنه أداة خاطئة لحل لغز النهر.

class UtilityBasedDeliveryAgent:
    def __init__(self):
        # دالة البناء (Constructor) لتهيئة الوكيل
        self.position = 0  # الموقع الحالي للوكيل (يبدأ عند 0)
        self.has_package = False  # هل يحمل الطرد؟ (في البداية لا)
        self.package_delivered = False  # هل تم توصيل الطرد؟ (في البداية لا)
        self.world = None  # متغير لتخزين حالة العالم المحيط

    def perceive(self, world_state):
        """إدراك البيئة المحيطة وتخزينها"""
        self.world = world_state  # حفظ نسخة من حالة العالم

    def calculate_utility(self, action):
        """حساب المنفعة (Utility) لكل إجراء ممكن"""
        # قاموس يربط كل إجراء بقيمة المنفعة الخاصة به
        utilities = {
            "move_left": self._utility_move(-1),  # منفعة التحرك لليسار
            "move_right": self._utility_move(1),  # منفعة التحرك لليمين
            "pickup_package": self._utility_pickup(),  # منفعة التقاط الطرد
            "package_delivered": self._utility_deliver(),  # منفعة تسليم الطرد
            "wait": -10  # الانتظار عادة ما يكون سيئًا (تكلفة)
        }
        # إرجاع منفعة الإجراء، أو -100 إذا كان الإجراء غير معروف
        return utilities.get(action, -100)

    def _utility_move(self, direction):
        """حساب المنفعة لعملية التحرك"""
        new_pos = self.position + direction  # الموقع الجديد المتوقع

        # التحقق مما إذا كانت الحركة صالحة (داخل حدود العالم)
        if new_pos < 0 or new_pos > 10:  # نفترض أن حدود العالم من 0 إلى 10
            return -100  # حركة غير صالحة (عقوبة كبيرة)

        utility = -1  # التكلفة الأساسية لأي حركة (استهلاك طاقة/وقت)

        if self.has_package:
            # إذا كان يحمل الطرد - المنفعة تعتمد على المسافة إلى موقع التسليم
            distance_to_delivery = abs(new_pos - self.world.delivery_location)
            utility -= distance_to_delivery * 0.5  # تقليل المنفعة كلما زادت المسافة

            # مكافأة عالية إذا اقتربنا من الهدف
            if distance_to_delivery < abs(self.position - self.world.delivery_location):
                utility += 2
        else:
            # إذا لم يحمل الطرد - المنفعة تعتمد على المسافة إلى موقع الطرد
            distance_to_package = abs(new_pos - self.world.package_location)
            utility -= distance_to_package * 0.5  # تقليل المنفعة كلما زادت المسافة

            # مكافأة عالية إذا اقتربنا من الطرد
            if distance_to_package < abs(self.position - self.world.package_location):
                utility += 2

        return utility  # إرجاع القيمة النهائية للمنفعة

    def _utility_pickup(self):
        """حساب المنفعة لالتقاط الطرد"""
        # إذا لم يكن يحمل الطرد، وكان في نفس موقع الطرد
        if (not self.has_package and
                self.position == self.world.package_location):
            return 10  # مكافأة عالية لالتقاط الطرد بنجاح
        return -10  # عقوبة لمحاولة التقاط مستحيلة

    def _utility_deliver(self):
        """حساب المنفعة لتسليم الطرد"""
        # إذا كان يحمل الطرد، وكان في موقع التسليم
        if (self.has_package and
                self.position == self.world.delivery_location):
            return 25  # مكافأة عالية جداً لإنجاز المهمة
        return -20  # عقوبة لمحاولة تسليم مستحيلة

    def act(self):
        """اختيار وتنفيذ أفضل إجراء بناءً على المنفعة"""
        possible_actions = ["move_left", "move_right"]  # الإجراءات المتاحة دائماً

        # إضافة إجراءات خاصة إذا تحققت الشروط
        if self.position == self.world.package_location and not self.has_package:
            possible_actions.append("pickup_package")  # إضافة خيار الالتقاط
        if self.position == self.world.delivery_location and self.has_package:
            possible_actions.append("package_delivered")  # إضافة خيار التسليم

        # حساب المنفعة لجميع الإجراءات الممكنة
        action_utilities = {action: self.calculate_utility(action) for action in possible_actions}

        # اختيار الإجراء صاحب أعلى قيمة منفعة
        best_action = max(action_utilities, key=action_utilities.get)
        best_utility = action_utilities[best_action]

        # تنفيذ الإجراء المختار (تحديث حالة الوكيل)
        if best_action == "move_left":
            self.position -= 1
        elif best_action == "move_right":
            self.position += 1
        elif best_action == "pickup_package":
            self.has_package = True
        elif best_action == "package_delivered":
            self.has_package = False
            self.package_delivered = True

        return best_action, best_utility  # إرجاع الإجراء وقيمته للطباعة

    def run(self, world_state, max_steps=20):
        """تشغيل دورة حياة الوكيل"""
        self.perceive(world_state)  # إدراك العالم أولاً
        print("\nUtility-Based Agent Starting! (بدأ الوكيل القائم على المنفعة)")
        print(f"Package at: {self.world.package_location}, Deliver to: {self.world.delivery_location}")
        print("=" * 40)

        for step in range(max_steps):  # حلقة تكرار لعدد محدد من الخطوات
            action, utility = self.act()  # اتخاذ قرار
            # طباعة تفاصيل الخطوة
            print(
                f"Step {step + 1}: Pos={self.position}, Action={action}, Utility={utility:.1f}, HasPackage={self.has_package}")

            if self.package_delivered:  # إذا تم التسليم، انتهت المهمة
                print("Package delivered successfully! (تم التسليم بنجاح)")
                return True

        print("Failed to deliver package (فشل التسليم)")
        return False


class WorldState:
    def __init__(self, package_loc, delivery_loc):
        self.package_location = package_loc  # موقع الطرد
        self.delivery_location = delivery_loc  # موقع التسليم


# --- الوكيل الثاني: وكيل حل المشكلات (الصحيح لمشكلة النهر) ---
# هذا هو النوع الصحيح من الوكلاء لحل اللغز.
# يستخدم خوارزمية البحث بالعرض أولاً (BFS) لإيجاد أقصر سلسلة حركات صالحة.

class RiverProblemSolvingAgent:
    def __init__(self):
        """
        تمثيل الحالة (State) كـ Tuple: (مزارع، ذئب، بطة، ذرة)
        'S' = الضفة الجنوبية، 'N' = الضفة الشمالية
        """
        self.START_STATE = ('S', 'S', 'S', 'S')  # حالة البداية: الجميع في الجنوب
        self.GOAL_STATE = ('N', 'N', 'N', 'N')  # الهدف: الجميع في الشمال

    def _is_valid(self, state):
        """تتحقق مما إذا كانت الحالة صالحة (لا أحد يأكل الآخر)."""
        farmer, wolf, duck, corn = state  # تفكيك الـ Tuple إلى متغيرات

        # الحالة 1: الذئب يأكل البطة
        # (إذا كان الذئب مع البطة في نفس الضفة، والمزارع ليس معهما)
        if wolf == duck and farmer != wolf:
            return False  # حالة غير صالحة

        # الحالة 2: البطة تأكل الذرة
        # (إذا كانت البطة مع الذرة في نفس الضفة، والمزارع ليس معهما)
        if duck == corn and farmer != duck:
            return False  # حالة غير صالحة

        return True  # الحالة آمنة

    def _get_next_states(self, current_state):
        """تولد جميع الحركات الممكنة والصالحة من الحالة الحالية."""
        farmer, wolf, duck, corn = current_state
        possible_next_states = []  # قائمة لتخزين الحالات التالية الممكنة

        # تحديد الوجهة (عكس مكان المزارع الحالي)
        destination = 'N' if farmer == 'S' else 'S'

        # دالة مساعدة لإنشاء حالة جديدة
        def move(item_index):
            new_state_list = list(current_state)  # تحويل الـ Tuple إلى قائمة للتعديل
            new_state_list[0] = destination  # تحريك المزارع دائماً
            if item_index != -1:
                new_state_list[item_index + 1] = destination  # تحريك العنصر المختار معه
            return tuple(new_state_list)  # إرجاع كـ Tuple مرة أخرى

        # العناصر التي يمكن محاولة تحريكها (بالفهرس):
        # -1: المزارع وحده
        #  0: المزارع + الذئب
        #  1: المزارع + البطة
        #  2: المزارع + الذرة

        # القائمة تبدأ بـ -1 لأن المزارع يمكنه دائماً العبور وحده
        items_on_same_bank = [-1]

        # إضافة العناصر الموجودة في نفس ضفة المزارع فقط
        if wolf == farmer: items_on_same_bank.append(0)
        if duck == farmer: items_on_same_bank.append(1)
        if corn == farmer: items_on_same_bank.append(2)

        # تجربة تحريك كل عنصر متاح
        for item_index in items_on_same_bank:
            next_state = move(item_index)  # إنشاء الحالة الجديدة
            if self._is_valid(next_state):  # التحقق من القواعد (هل أكل أحد الآخر؟)
                possible_next_states.append(next_state)  # إضافة الحالة للقائمة إذا كانت آمنة

        return possible_next_states  # إرجاع جميع الحركات الممكنة

    def solve(self):
        """
        تحل اللغز باستخدام البحث بالعرض أولاً (BFS).
        BFS تضمن إيجاد أقصر حل ممكن.
        """

        # الطابور يخزن الـ (المسار الكامل، الحالة الحالية)
        # المسار عبارة عن قائمة من الحالات من البداية حتى الآن
        queue = deque([([self.START_STATE], self.START_STATE)])

        # مجموعة 'visited' لتخزين الحالات التي زرناها لتجنب التكرار والدوران في حلقات مفرغة
        visited = {self.START_STATE}

        while queue:  # طالما الطابور ليس فارغاً
            current_path, last_state = queue.popleft()  # سحب أقدم عنصر في الطابور

            # هل وصلنا للهدف؟
            if last_state == self.GOAL_STATE:
                return current_path  # نجاح! أرجع المسار الكامل للحل

            # استكشاف الحالات التالية الممكنة
            for next_state in self._get_next_states(last_state):
                if next_state not in visited:  # إذا لم نزر هذه الحالة من قبل
                    visited.add(next_state)  # وضع علامة "تمت الزيارة"
                    new_path = current_path + [next_state]  # إنشاء مسار جديد مضافاً إليه هذه الخطوة
                    queue.append((new_path, next_state))  # إضافة للمراجعة في الطابور

        return None  # لم يتم العثور على حل

    def _format_state(self, state):
        """دالة مساعدة لجعل شكل الحالة مقروءاً عند الطباعة."""
        farmer, wolf, duck, corn = state

        south_bank = []
        north_bank = []

        # توزيع العناصر على القوائم بناءً على مكانهم
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

        # تحويل القوائم لنصوص
        south_str = ", ".join(south_bank) if south_bank else "Empty"
        north_str = ", ".join(north_bank) if north_bank else "Empty"
        return f"South: [{south_str}] | North: [{north_str}]"

    def print_solution(self, path):
        """تطبع مسار الحل بتنسيق يسهل على البشر قراءته."""
        if not path:
            print("No solution found. (لم يتم العثور على حل)")
            return

        print(f"✅ Solution Found in {len(path) - 1} steps! (تم الحل في {len(path) - 1} خطوة)\n")
        print(f"Step 0 (Start): {self._format_state(path[0])}")

        for i in range(1, len(path)):
            prev_state = path[i - 1]  # الحالة السابقة
            curr_state = path[i]  # الحالة الحالية

            # تحديد من الذي تحرك
            move = "Farmer"
            direction = "(South → North)" if curr_state[0] == 'N' else "(North → South)"

            # مقارنة المواقع لمعرفة العنصر المرافق
            if prev_state[1] != curr_state[1]:
                move += " takes the Wolf (يأخذ الذئب)"
            elif prev_state[2] != curr_state[2]:
                move += " takes the Duck (يأخذ البطة)"
            elif prev_state[3] != curr_state[3]:
                move += " takes the Corn (يأخذ الذرة)"
            else:
                move += " returns alone (يعود وحده)"

            print(f"\nStep {i}: {move} {direction}")
            print(f"       Result: {self._format_state(curr_state)}")


# --- كتلة التنفيذ الرئيسية لتشغيل كلا الوكيلين ---

if __name__ == "__main__":
    # 1. تشغيل الوكيل القائم على المنفعة (لمشكلته الأصلية)
    print("=" * 50)
    print("UTILITY-BASED AGENT DEMONSTRATION (تجربة وكيل المنفعة)")
    world = WorldState(package_loc=3, delivery_loc=6)  # إعداد العالم
    utility_agent = UtilityBasedDeliveryAgent()  # إنشاء الوكيل
    utility_agent.run(world)  # تشغيل الوكيل

    # 2. تشغيل وكيل حل المشكلات (لحل مشكلة النهر)
    print("\n\n" + "=" * 50)
    print("RIVER PROBLEM-SOLVING AGENT DEMONSTRATION (تجربة وكيل مشكلة النهر)")
    river_agent = RiverProblemSolvingAgent()  # إنشاء الوكيل
    solution_path = river_agent.solve()  # البحث عن الحل
    river_agent.print_solution(solution_path)  # طباعة النتيجة