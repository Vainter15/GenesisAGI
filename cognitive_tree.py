import re
import time
from colorama import Fore
from symbolic_engine import NeuroSymbolicBridge

class CognitiveTree:
    def __init__(self, architect, critic):
        """
        Инициализация дерева размышлений.
        :param architect: Экземпляр GenesisCore для генерации идей.
        :param critic: Класс SelfReflection для аудита (используется в логике оценки).
        """
        self.architect = architect
        self.critic = critic

    def search_best_action(self, prompt: str, context: str) -> dict:
        """
        Генерирует несколько вариантов действий (веток), оценивает их и выбирает оптимальный.
        """
        print(Fore.CYAN + "🌳 [TREE OF THOUGHTS] Разворачиваем дерево размышлений...")
        
        branches = []
        
        # Инструкция для моделей, заставляющая их соблюдать формат и помнить про Терминал
        system_instruction = (
            "ОТВЕЧАЙ СТРОГО В ФОРМАТЕ JSON. БЕЗ ЛИШНЕГО ТЕКСТА.\n"
            "Если твоё действие — 'write_file', ты ОБЯЗАН включить аргумент 'content' с полным кодом.\n"
            "Если твоё действие — 'execute_command', ты ОБЯЗАН включить аргумент 'command' с текстом команды терминала.\n"
            "Пример 1: {\"theory\": \"...\", \"tool\": \"write_file\", \"args\": {\"filename\": \"test.py\", \"content\": \"print('hello')\"}}\n"
            "Пример 2: {\"theory\": \"...\", \"tool\": \"execute_command\", \"args\": {\"command\": \"pip install torch\"}}"
        )
        
        # Генерация 3 независимых веток (Tree of Thoughts)
        for i in range(3):
            # Формируем запрос: сначала контекст и задача, потом жесткое правило формата
            branch_prompt = (
                f"ЗАДАЧА:\n{prompt}\n\n"
                f"КОНТЕКСТ ПРОШЛЫХ ШАГОВ:\n{context}\n\n"
                f"[ВЕТКА {i+1}]: Предложи свой вариант действий.\n"
                f"{system_instruction}"
            )
            
            try:
                # Запрос к нейроузелу (температура 0.4 для креативности в рамках формата)
                resp, model_name = self.architect.think(
                    [{"role": "user", "content": branch_prompt}], 
                    temperature=0.4, 
                    max_tokens=2000 
                )
                
                if not resp:
                    print(Fore.RED + f"   ├─ Ветка {i+1} ({model_name}): ❌ Пустой ответ.")
                else:
                    # 🌉 ИСПОЛЬЗУЕМ МОСТ: Вытягиваем данные из любого мусора в ответе
                    action_data = NeuroSymbolicBridge.parse_action_data(resp)
                    
                    if action_data and "tool" in action_data:
                        # Оценка качества предложенного действия
                        score = self.evaluate_branch(action_data)
                        branches.append({
                            "action": action_data, 
                            "score": score, 
                            "id": i+1, 
                            "model": model_name
                        })
                        print(Fore.LIGHTBLACK_EX + f"   ├─ Ветка {i+1} ({model_name}): {score}/10 | {action_data['tool']}")
                    else:
                        print(Fore.RED + f"   ├─ Ветка {i+1} ({model_name}): ❌ Парсинг провален.")
                        # Вывод начала сырого ответа для диагностики, если ветка рухнула
                        raw_preview = resp.strip().replace('\n', ' ')[:100]
                        print(Fore.LIGHTYELLOW_EX + f"   │  [RAW]: {raw_preview}...")
                    
            except Exception as e:
                print(Fore.RED + f"   ├─ Ветка {i+1}: ❌ Критическая ошибка: {e}")
            
            # 🛑 СПАСИТЕЛЬНАЯ ПАУЗА: Ждем 6 секунд, чтобы бесплатный API остыл. 
            # Не ждем после 3-й ветки, так как цикл закончился.
            if i < 2:
                time.sleep(6)

        # План Б: Если все 3 модели выдали нечитаемую кашу
        if not branches:
            print(Fore.YELLOW + "⚠️ [TREE OF THOUGHTS] Все ветки рухнули. Аварийный режим...")
            return {
                "theory": "Сбой когнитивного дерева. Вынужденный сбор данных.",
                "tool": "analyze_structure",
                "args": {}
            }

        # Выбор ветки с максимальным баллом
        best = max(branches, key=lambda x: x['score'])
        print(Fore.GREEN + f"🌿 [TREE OF THOUGHTS] Выбрана ветка {best['id']} ({best['score']}/10) от {best['model']}")
        
        return best['action']

    def evaluate_branch(self, action: dict) -> int:
        """
        Эвристическая оценка ветки. 
        Приоритет отдается созидательным действиям и проверкам.
        """
        tool = action.get("tool", "unknown").lower()
        score = 5 # Базовый балл

        # 🚀 ВЫСОКИЙ ПРИОРИТЕТ: Реальное изменение системы или терминальные тесты
        if tool in ["write_file", "execute_test", "integrate_tool", "execute_command"]:
            score += 4
            # Если ИИ вызвал инструмент, но забыл передать ключевые аргументы — это жесточайший штраф
            args = action.get("args", {})
            if tool == "write_file" and not args.get("content"):
                score -= 6 
            if tool == "execute_command" and not args.get("command"):
                score -= 6
            
        # 🔍 СРЕДНИЙ ПРИОРИТЕТ: Сбор информации
        elif tool in ["read_file", "analyze_structure", "list_files"]:
            score += 2
            
        # 💤 НИЗКИЙ ПРИОРИТЕТ: Попытка завершить задачу
        elif tool == "finish_step":
            # Мы штрафуем за лень, чтобы ИИ не закрывал задачу вручную без реальных дел (теперь за него это делает Аудитор)
            score -= 2 
            
        # ❌ КРИТИЧЕСКИЙ ШТРАФ: Неизвестный инструмент
        if tool == "unknown" or (tool == "list_files" and not action.get("args")):
            score -= 4

        # Дополнительный штраф, если парсеру пришлось восстанавливать данные вручную
        if action.get("theory") == "Восстановлено парсером":
            score -= 2

        return min(max(score, 0), 10)