import sys
import json
import os
import time
import inspect
import re
from datetime import datetime
from colorama import Fore, init
from unittest.mock import MagicMock

# 💉 УЛЬТРА-ВАКЦИНА: Заглушки для специфических окружений (если проект запускается в симуляции)
mock_modules = [
    'rospy', 'intera_interface', 'intera_interface.cfg', 'gazebo_msgs', 
    'gazebo_msgs.srv', 'gazebo_msgs.msg', 'sensor_msgs', 'sensor_msgs.msg', 
    'std_msgs', 'std_msgs.msg', 'geometry_msgs', 'geometry_msgs.msg', 
    'moveit_commander', 'moveit_msgs'
]
for mod in mock_modules:
    if mod not in sys.modules:
        mock_obj = MagicMock()
        mock_obj.__path__ = [] 
        sys.modules[mod] = mock_obj

# 🔧 ГАРАНТИЯ ИМПОРТОВ: Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорт всех твоих модулей
import config
from genesis_core import GenesisCore
from planner import GoalPlanner
from self_reflection import SelfReflection
from toolbox import Toolbox
from evolution_engine import EvolutionEngine
from meta_learner import MetaLearner
from cognitive_tree import CognitiveTree
from long_term_memory import GenesisLongTerm
from graph_manager import EntityGraph
from auto_healer import AutoHealer
from symbolic_engine import NeuroSymbolicBridge

init(autoreset=True)

class GenesisAGI:
    def __init__(self):
        print(Fore.CYAN + "🧬 GENESIS AGI: РЕЖИМ АВТОНОМНОЙ ЭВОЛЮЦИИ ЗАПУЩЕН")
        
        # Основные компоненты системы
        self.planner = GoalPlanner()
        self.tools = Toolbox()
        self.evolution = EvolutionEngine()
        self.bridge = NeuroSymbolicBridge()
        
        # Мозговой центр (Архитектор)
        self.architect = GenesisCore(config.MODEL_ARCHITECT, is_architect=True)
        self.tree = CognitiveTree(self.architect, SelfReflection)
        
        # Системы памяти и обучения
        self.short_term = []           
        self.long_term = GenesisLongTerm() 
        self.graph = EntityGraph()     
        self.meta = MetaLearner()
        self.healer = AutoHealer(self.architect)
        
        self.global_intent = "Проект Инкубатор: Создание локального Seed AI"

    def _get_inventory(self):
        """Собирает список всех доступных инструментов (базовых и созданных)."""
        base = ["read_file", "write_file", "list_files", "analyze_structure", 
                "update_plan", "integrate_tool", "finish_step", "execute_test", "execute_command"]
        return base + self.evolution.get_evolved_inventory()

    def _exec(self, tool: str, args: dict):
        """Диспетчер выполнения инструментов: связь ИИ с реальностью."""
        try:
            # 1. Специальные инструменты планирования
            if tool == "update_plan":
                return self.planner.add_step(args.get("task", "Новая задача"), immediate=args.get("immediate", False))
            
            # 2. Инструменты эволюции кода
            if tool == "integrate_tool":
                return self.evolution.inject_new_tool(args.get("filename", "new_skill"), args.get("content", ""))

            # 3. Базовые инструменты из Toolbox
            if hasattr(self.tools, tool):
                method = getattr(self.tools, tool)
                sig = inspect.signature(method)
                # Передаем только те аргументы, которые ожидает метод
                valid_args = {k: v for k, v in args.items() if k in sig.parameters}
                return method(**valid_args)

            return f"❌ ОШИБКА: Инструмент '{tool}' не найден."
        except Exception as e:
            return f"❌ КРИТИЧЕСКИЙ СБОЙ ИНСТРУМЕНТА '{tool}': {e}"

    def _append_to_journal(self, task, theory, tool, result, reflection):
        """Запись опыта в журнал для последующего планирования."""
        log_dir = "research"
        os.makedirs(log_dir, exist_ok=True)
        journal_path = os.path.join(log_dir, "journal.md")
        
        entry = (
            f"### [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ШАГ: {task}\n"
            f"- **Гипотеза:** {theory}\n"
            f"- **Инструмент:** `{tool}`\n"
            f"- **Результат:** {str(result)[:500]}...\n"
            f"- **Вердикт:** {reflection}\n"
            f"---\n\n"
        )
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def run_cycle(self):
        """Один такт 'мысли-действия' GENESIS."""
        current_step = self.planner.get_current_step_text()
        
        # Если задач нет — генерируем новую миссию
        if not current_step or current_step == "Все задачи выполнены":
            return self._generate_autonomous_mission()

        print(Fore.WHITE + f"\n--- 🌀 ЦИКЛ: {current_step} ---")

        # 1. Сбор контекста
        inventory = self._get_inventory()
        directives = self.meta.get_system_directives()
        prompt = (
            f"ГЛОБАЛЬНАЯ ЦЕЛЬ: {self.global_intent}\n"
            f"ТЕКУЩАЯ ЗАДАЧА: {current_step}\n"
            f"ИНВЕНТАРЬ: {', '.join(inventory)}\n"
            f"ДИРЕКТИВЫ: {directives}"
        )

        # 2. Принятие решения через дерево размышлений
        action_data = self.tree.search_best_action(prompt, "\n".join(self.short_term[-3:]))
        if not action_data: return True

        tool = self.bridge.fix_tool_name(action_data.get('tool', 'unknown'))
        args = self.bridge.bridge_arguments(tool, action_data.get('args', {}))

        # 3. Выполнение и авто-лечение
        result = self._exec(tool, args)
        if isinstance(result, str) and ("❌" in result or "Error" in result):
            print(Fore.RED + "🩹 [HEALER] Попытка исправления...")
            result = self.healer.heal(tool, args, result)

        # 4. Рефлексия (Аудит)
        refl = SelfReflection.analyze_action(action_data.get('theory', ''), tool, str(result), self.architect)
        print(Fore.YELLOW + f"🪞 Рефлексия: {refl}")

        # 5. Сохранение опыта и завершение шага
        if "✅ [AUDIT SUCCESS]" in refl or tool == "finish_step":
            self.planner.mark_done()
            self.long_term.save_experience(current_step, str(result), "success")

        self.short_term.append(f"Инструмент: {tool} | Итог: {str(result)[:50]}")
        if len(self.short_term) > 5: self.short_term.pop(0)
        
        self._append_to_journal(current_step, action_data.get('theory', ''), tool, result, refl)
        return True

    def _generate_autonomous_mission(self):
        """Анализ проекта и постановка новых целей."""
        print(Fore.MAGENTA + "\n🧠 [PLANNER] Анализ состояния системы для новой миссии...")
        
        files = os.listdir('.')
        journal_path = os.path.join("research", "journal.md")
        journal_context = ""
        if os.path.exists(journal_path):
            with open(journal_path, 'r', encoding='utf-8') as f:
                journal_context = f.read()[-1500:]

        prompt = (
            f"Твоя ГЛОБАЛЬНАЯ ЦЕЛЬ: {self.global_intent}\n"
            f"ФАЙЛЫ: {', '.join(files)}\n"
            f"ИСТОРИЯ: {journal_context}\n"
            "Сформулируй 3 конкретные технические задачи для саморазвития.\n"
            "ОТВЕТЬ ТОЛЬКО JSON: {\"global_goal\": \"...\", \"tasks\": [{\"task\": \"...\"}]}"
        )
        
        resp, _ = self.architect.think([{"role": "user", "content": prompt}])
        new_plan = self.bridge.parse_action_data(resp)
        
        if new_plan and "tasks" in new_plan:
            new_plan["current_idx"] = 0
            for t in new_plan["tasks"]: t["done"] = False
            with open("current_plan.json", "w", encoding="utf-8") as f:
                json.dump(new_plan, f, indent=4, ensure_ascii=False)
            self.planner = GoalPlanner() # Перезагрузка
            print(Fore.GREEN + "✅ [PLANNER] Новая миссия принята.")
            return True
        return False

    def start(self):
        """Главный вход в бесконечный цикл жизни GENESIS."""
        print(Fore.GREEN + "🚀 GENESIS запущен в автономном режиме. Ctrl+C для остановки.")
        while True:
            try:
                self.run_cycle()
                time.sleep(5) 
            except KeyboardInterrupt:
                print(Fore.RED + "\n🛑 Остановка системы.")
                break
            except Exception as e:
                print(Fore.RED + f"🔥 Ошибка цикла: {e}")
                time.sleep(10)

if __name__ == "__main__":
    bot = GenesisAGI()
    bot.start()