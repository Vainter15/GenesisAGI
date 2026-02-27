import json
import os
from colorama import Fore

class GoalPlanner:
    def __init__(self, plan_file="current_plan.json"):
        """Инициализация планировщика. Загружает план или создает чистый лист."""
        self.plan_file = plan_file
        self.plan = self._load_plan()

    @property
    def current_idx(self) -> int:
        """Позволяет читать индекс как атрибут."""
        return self.plan.get("current_idx", 0)

    @current_idx.setter
    def current_idx(self, value: int):
        """Позволяет записывать индекс как атрибут."""
        self.plan["current_idx"] = value

    def _load_plan(self) -> dict:
        """Бронебойная загрузка плана. При любых сбоях возвращает чистый старт."""
        if os.path.exists(self.plan_file):
            try:
                with open(self.plan_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict) and "tasks" in data:
                        # Защита от потери индекса
                        if "current_idx" not in data:
                            data["current_idx"] = 0
                        return data
                    else:
                        print(Fore.YELLOW + f"⚠️ [PLANNER] Неверная структура {self.plan_file}. Сброс.")
            except json.JSONDecodeError:
                print(Fore.RED + f"⚠️ [PLANNER] Файл {self.plan_file} поврежден. Начинаем с чистого листа.")
            except Exception as e:
                print(Fore.RED + f"⚠️ [PLANNER] Ошибка чтения: {e}")

        # Идеально чистый старт
        return {
            "global_goal": "Ожидание генерации автономной миссии",
            "tasks": [],
            "current_idx": 0
        }

    def save_plan(self):
        """Надежное сохранение текущего состояния."""
        try:
            with open(self.plan_file, "w", encoding="utf-8") as f:
                json.dump(self.plan, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(Fore.RED + f"❌ [PLANNER] Ошибка записи плана: {e}")

    def get_current_step_text(self) -> str:
        """Возвращает текст текущей задачи или сигнал к генерации нового плана."""
        tasks = self.plan.get("tasks", [])
        idx = self.current_idx
        
        if not tasks or idx >= len(tasks):
            return "Все задачи выполнены"
            
        return tasks[idx].get("task", "Неизвестная задача")

    def mark_done(self) -> str:
        """Закрывает текущую задачу и сдвигает указатель."""
        tasks = self.plan.get("tasks", [])
        idx = self.current_idx
        
        if idx < len(tasks):
            tasks[idx]["done"] = True
            self.current_idx = idx + 1
            self.save_plan()
            
            task_name = tasks[idx].get('task', 'Без названия')
            print(Fore.GREEN + f"✅ [PLANNER] Задача выполнена: {task_name}")
            return f"Задача '{task_name}' успешно закрыта."
            
        return "❌ Ошибка: нет активных задач для завершения."

    def add_step(self, task_description: str, immediate: bool = False) -> str:
        """
        Позволяет ИИ добавлять новые шаги на лету.
        Если immediate=True, вставляет задачу следующей в очередь, иначе в конец.
        """
        if "tasks" not in self.plan:
            self.plan["tasks"] = []
            
        new_task = {"task": task_description, "done": False}
        
        if immediate and self.current_idx < len(self.plan["tasks"]):
            # Экстренная подзадача: вставляем прямо за текущей
            self.plan["tasks"].insert(self.current_idx + 1, new_task)
        else:
            self.plan["tasks"].append(new_task)
            
        self.save_plan()
        return f"✅ Шаг добавлен в план: {task_description[:50]}..."