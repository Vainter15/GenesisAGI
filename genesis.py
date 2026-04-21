import sys
import json
import os
import time
import inspect
import re
import logging
import traceback
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
from sandbox_env import PrometheusSandbox
from ml_toolbox import MLToolbox


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("genesis_system.log", encoding='utf-8'),
        logging.StreamHandler() # Дублирует критические ошибки в консоль
    ]
)

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
        
        # Системы памяти и обучения
        self.short_term = []           
        self.long_term = GenesisLongTerm() 
        self.graph = EntityGraph()     
        self.meta = MetaLearner()
        self.healer = AutoHealer(self.architect)
        
        # 🆕 ДОБАВЛЕНО: Песочница и ML-инструменты
        self.sandbox = PrometheusSandbox(timeout=15)
        self.ml = MLToolbox()
        
        
        self.global_intent = "Проект Инкубатор: Создание локального Seed AI"
        
        self.stuck_counter = 0
        self.last_task = ""

    def _get_inventory(self):
        base = ["read_file", "write_file", "list_files", "analyze_structure", 
                "update_plan", "integrate_tool", "finish_step", "execute_test", "execute_command",
                "check_hardware", "prepare_text_dataset", "save_checkpoint",
                # 🆕 ДОБАВЛЕНО: Инструменты памяти и поиска
                "save_to_clipboard", "view_clipboard", "search_in_file"]
        return base + self.evolution.get_evolved_inventory()

    def _exec(self, tool: str, args: dict):
        """Диспетчер выполнения инструментов: связь ИИ с реальностью."""
        try:
            # 1. Специальные инструменты планирования
            if tool == "update_plan":
                return self.planner.add_step(args.get("task", "Новая задача"), immediate=args.get("immediate", False))
            
            # 2. Инструменты эволюции кода
            if tool == "integrate_tool" and "filename" in args and "content" in args:
                # 🛡️ Защита: Проверяем код нового инструмента на ошибки ДО интеграции
                is_valid, fixed_content = self.healer.validate_and_heal(f"plugins/{args['filename']}.py", args["content"])
                
                if not is_valid:
                    return f"❌ ОШИБКА ИНТЕГРАЦИИ: В твоем коде критические ошибки синтаксиса. Исправь их перед внедрением инструмента."
                
                # Если все ок, внедряем вылеченный код
                return self.evolution.inject_new_tool(args["filename"], fixed_content)

            # 🛑 3. ПРОВЕРКА СИНТАКСИСА ПЕРЕД ЗАПИСЬЮ (Auto-Healer)
            if tool == "write_file" and "filename" in args and "content" in args:
                # Пытаемся вылечить синтаксические ошибки до сохранения на диск
                is_valid, fixed_content = self.healer.validate_and_heal(args["filename"], args["content"])
                if not is_valid:
                    return f"❌ ОШИБКА СИНТАКСИСА: В коде критические ошибки. Файл НЕ сохранен. Исправь логику."
                
                args["content"] = fixed_content # Подменяем на вылеченный код
                self.graph.update_node(args["filename"], status="modified_by_ai")

            # 🧪 4. БЕЗОПАСНЫЙ ЗАПУСК В ПЕСОЧНИЦЕ (PrometheusSandbox)
            if tool == "execute_test" and "filename" in args:
                try:
                    # Читаем исходный файл напрямую
                    with open(args["filename"], 'r', encoding='utf-8') as f:
                        raw_code = f.read()
                    
                    # Запускаем в изоляции Sandbox/
                    stats = self.sandbox.run_simulation(raw_code, args["filename"])
                    if stats.get("success"):
                        return f"✅ [SANDBOX] Успех ({stats.get('duration')}с).\nВывод: {stats.get('stdout')}"
                    else:
                        return f"❌ [SANDBOX] Сбой.\nВывод: {stats.get('stderr') or stats.get('error')}"
                except Exception as e:
                    return f"❌ Ошибка загрузки файла в песочницу: {e}"
                
                
            if tool == "check_impact_zone" and "filename" in args:
                impacted = self.graph.get_impact_zone(args["filename"])
                if impacted:
                    return f"⚠️ ВНИМАНИЕ: Если ты изменишь {args['filename']}, это может сломать работу следующих модулей: {', '.join(impacted)}. Убедись, что они не пострадают."
                return f"✅ Файл {args['filename']} ни на кого не влияет (изолирован). Можно безопасно менять."

            # 🧠 5. ИНСТРУМЕНТЫ МАШИННОГО ОБУЧЕНИЯ (ML Toolbox)
            if hasattr(self.ml, tool):
                method = getattr(self.ml, tool)
                sig = inspect.signature(method)
                valid_args = {k: v for k, v in args.items() if k in sig.parameters}
                return method(**valid_args)

            # 🛠️ 6. БАЗОВЫЕ ИНСТРУМЕНТЫ (Toolbox)
            if hasattr(self.tools, tool):
                method = getattr(self.tools, tool)
                sig = inspect.signature(method)
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

        # --- 1. ДЕТЕКТОР ЗАЦИКЛИВАНИЯ ---
        if current_step == self.last_task and "ЭКСТРЕННО" in current_step:
            self.stuck_counter += 1
            if self.stuck_counter > 3:
                print(Fore.RED + "💀 [ANTI-LOOP] Система зациклилась на одной ошибке! Сброс контекста и принудительный откат.")
                self.meta.reset_logic() # Стираем старые правила, они могут мешать
                self.short_term.clear() # Очищаем мысли
                self.planner.mark_done() # Принудительно закрываем сломанную задачу, чтобы идти дальше
                self.stuck_counter = 0
                return True
        else:
            self.last_task = current_step
            self.stuck_counter = 0

        # --- 2. ПРОВЕРКА НАЛИЧИЯ ЗАДАЧ ---
        if not current_step or current_step == "Все задачи выполнены":
            self._generate_autonomous_mission() # Вызываем генерацию миссии
            return True # 👈 Принудительно говорим циклу: "Продолжай работу, не останавливайся!"

        print(Fore.WHITE + f"\n--- 🌀 ЦИКЛ: {current_step} ---")

        # --- 3. СБОР КОНТЕКСТА И ПАМЯТИ ---
        inventory = self._get_inventory()
        directives = self.meta.get_system_directives()

        past_experience = self.long_term.get_relevant_facts(current_step)
        memories_text = "\n- " + "\n- ".join(past_experience) if past_experience else "Нет релевантных воспоминаний."

        prompt = (
            f"ГЛОБАЛЬНАЯ ЦЕЛЬ: {self.global_intent}\n"
            f"ТЕКУЩАЯ ЗАДАЧА: {current_step}\n"
            f"ИНВЕНТАРЬ: {', '.join(inventory)}\n"
            f"ДИРЕКТИВЫ: {directives}\n\n"
            f"📚 БАЗА ЗНАНИЙ (Твой прошлый опыт):\n{memories_text}"
        )

        # --- 4. ДЕРЕВО РАЗМЫШЛЕНИЙ ---
        action_data = self.tree.search_best_action(prompt, "\n".join(self.short_term[-3:]))
        if not action_data: return True

        tool = self.bridge.fix_tool_name(action_data.get('tool', 'unknown'))
        args = self.bridge.bridge_arguments(tool, action_data.get('args', {}))

        # --- 5. ВЫПОЛНЕНИЕ И АВТО-ЛЕЧЕНИЕ ---
        result = self._exec(tool, args)
        
        # Строгая проверка на провал: ищем крестик или слово Error, 
        # но только если нет зеленой галочки Успеха!
        is_failed = isinstance(result, str) and ("❌" in result or "Error" in result) and "✅" not in result

        if is_failed:
            print(Fore.RED + "🩹 [HEALER] Зафиксирован сбой. Попытка авто-исправления...")
            heal_result = self.healer.heal(tool, args, result)
            
            # Если Хилер вернул свой жесткий маркер сбоя
            if "❌" in heal_result or "[CRITICAL]" in heal_result:
                self.planner.add_step(f"ЭКСТРЕННО: Исправить критический сбой после инструмента {tool}. Лог: {heal_result[:100]}", immediate=True)
            
            # Подменяем результат результатом работы хилера для дальнейшего аудита
            result = heal_result
        
        # --- 6. РЕФЛЕКСИЯ И МЕТА-ОБУЧЕНИЕ ---
        refl = SelfReflection.analyze_action(action_data.get('theory', ''), tool, str(result), self.architect)
        print(Fore.YELLOW + f"🪞 Рефлексия: {refl}")

        if "❌ [AUDIT FAILED]" in refl or "КРИТИЧЕСКИЙ СБОЙ" in str(result):
            history_str = "\n".join(self.short_term)
            self.meta.extract_new_rule(self.architect, history_str, str(result))

        # --- 7. ЗАВЕРШЕНИЕ ШАГА ---
        if "✅ [AUDIT SUCCESS]" in refl or tool == "finish_step":
            self.planner.mark_done()
            self.long_term.save_experience(current_step, str(result), "success")

        theory = action_data.get('theory', 'Без гипотезы')
        clean_result = str(result).replace('\n', ' ')[:150]
        self.short_term.append(f"Шаг: {theory} -> Инструмент: {tool} -> Итог: {clean_result}")
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
        
        # 🚨 ДИАГНОСТИКА: Выводим в консоль всё, что ответила нейросеть
        print(Fore.CYAN + f"🤖 СЫРОЙ ОТВЕТ МОДЕЛИ:\n{resp}")
        
        new_plan = self.bridge.parse_action_data(resp)
        
        if new_plan and "tasks" in new_plan:
            new_plan["current_idx"] = 0
            for t in new_plan["tasks"]: t["done"] = False
            with open("current_plan.json", "w", encoding="utf-8") as f:
                json.dump(new_plan, f, indent=4, ensure_ascii=False)
            self.planner = GoalPlanner() # Перезагрузка
            print(Fore.GREEN + "✅ [PLANNER] Новая миссия принята.")
            return True
            
        # 🚨 ЛОГИРОВАНИЕ ПРОВАЛА
        print(Fore.RED + "❌ [PLANNER] Ошибка: Нейросеть вернула невалидный JSON или ошибку API.")
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
    logging.info("=========================================")
    logging.info("🚀 ЗАПУСК СИСТЕМЫ GENESIS AGI")
    logging.info("=========================================")
    init(autoreset=True)
    
    try:
        agi = GenesisAGI()
        print(Fore.GREEN + "🤖 GENESIS AGI Инициализирован. Ожидание цели...")
        
        while True:
            try:
                # Запускаем цикл. Если он вернет False - логируем причину остановки
                cycle_status = agi.run_cycle()
                if not cycle_status:
                    logging.warning("⚠️ Метод run_cycle() вернул False или None. Цикл остановлен.")
                    print(Fore.YELLOW + "Остановка: Система не смогла сгенерировать новую задачу.")
                    break
                
                time.sleep(2)
                
            except Exception as e:
                # 🛑 ПЕРЕХВАТ ЛЮБОЙ ОШИБКИ ВНУТРИ ЦИКЛА
                error_trace = traceback.format_exc()
                logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА В РАБОТЕ:\n{error_trace}")
                print(Fore.RED + "Критический сбой! Полная ошибка записана в genesis_system.log")
                
                # Даем системе 10 секунд на "остывание" и пытаемся перезапустить цикл, 
                # вместо того чтобы полностью умирать!
                print(Fore.CYAN + "Перезапуск цикла через 10 секунд...")
                time.sleep(10)
                continue 

    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 [SYSTEM] Получен сигнал прерывания (Ctrl+C).")
        logging.info("Система остановлена пользователем (Ctrl+C).")
        # agi.graph.save_graph() # раскомментируй, если настроил граф
        print(Fore.GREEN + "✅ Система безопасно остановлена.")
        exit(0)
        
    except Exception as e:
        # 🛑 ПЕРЕХВАТ ФАТАЛЬНЫХ ОШИБОК ИНИЦИАЛИЗАЦИИ
        error_trace = traceback.format_exc()
        logging.critical(f"💀 ФАТАЛЬНЫЙ СБОЙ ПРИ ЗАПУСКЕ:\n{error_trace}")
        print(Fore.RED + "Система не смогла запуститься. Смотри genesis_system.log")