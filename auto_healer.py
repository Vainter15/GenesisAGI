import ast
import json
import re
import traceback
from colorama import Fore

class AutoHealer:
    def __init__(self, architect):
        """
        Инициализация системы авто-исправления.
        :param architect: Экземпляр GenesisCore для генерации патчей и диагнозов.
        """
        self.architect = architect
        self.max_retries = 3

    def heal(self, tool: str, args: dict, error_log: str) -> str:
        """
        Динамическое лечение ошибок времени выполнения (Runtime Errors / Tracebacks).
        Вызывается из Ядра, если инструмент (например, execute_command) вернул сбой.
        Анализирует ошибку и подготавливает точный диагноз для Аудитора на следующий такт.
        """
        print(Fore.YELLOW + f"🔬 [AUTO-HEAL] Глубокий анализ сбоя в инструменте '{tool}'...")
        
        prompt = f"""
        КРИТИЧЕСКИЙ СБОЙ ИНСТРУМЕНТА!
        Инструмент: {tool}
        Аргументы вызова: {json.dumps(args, ensure_ascii=False)}
        
        ВЫВОД СИСТЕМЫ / ТРЕЙСБЕК:
        {error_log}
        
        ИНСТРУКЦИЯ ДЛЯ АВТОХИЛЕРА:
        Проанализируй этот сбой. Напиши КРАТКУЮ, технически точную инструкцию (1-3 предложения), 
        что именно система должна сделать на следующем шаге для исправления ошибки 
        (например: 'В файле X на строке Y не хватает импорта Z. Использовать write_file для добавления').
        БЕЗ ВОДЫ. ТОЛЬКО СУТЬ.
        """
        
        try:
            # Низкая температура для максимальной технической точности диагноза
            diagnosis, _ = self.architect.think([{"role": "user", "content": prompt}], max_tokens=300, temperature=0.2)
            return f"{error_log}\n\n🩹 [АВТО-ДИАГНОЗ ДЛЯ СЛЕДУЮЩЕГО ШАГА]:\n{diagnosis.strip()}"
        except Exception as e:
            return f"{error_log}\n⚠️ [AUTO-HEAL] Сбой генерации диагноза: {e}"

    def validate_and_heal(self, filepath: str, content: str) -> tuple[bool, str]:
        """
        Статическое лечение (SyntaxError).
        Проверяет синтаксис Python-кода перед сохранением файла на диск и автономно переписывает его.
        """
        if not str(filepath).endswith(".py"):
            return True, content

        current_code = content
        
        for attempt in range(self.max_retries):
            try:
                # Попытка построения абстрактного синтаксического дерева
                ast.parse(current_code)
                
                if attempt > 0:
                    print(Fore.GREEN + f"✨ [AUTO-HEAL] Модуль {filepath} успешно восстановлен на попытке {attempt + 1}!")
                return True, current_code

            except SyntaxError as e:
                error_msg = getattr(e, 'msg', str(e))
                lineno = getattr(e, 'lineno', 1) or 1
                
                print(Fore.RED + f"⚠️ [AUTO-HEAL] Синтаксическая ошибка в {filepath}: {error_msg} (строка {lineno})")
                
                error_context = self._get_error_context(current_code, lineno)
                
                heal_prompt = f"""
                КРИТИЧЕСКАЯ СИНТАКСИЧЕСКАЯ ОШИБКА В КОДЕ:
                Файл: {filepath}
                Строка: {lineno}
                Ошибка: {error_msg}
                
                Контекст ошибки:
                {error_context}

                Полный исходный код:
                ```python
                {current_code}
                ```

                ИНСТРУКЦИЯ:
                Исправь синтаксическую ошибку (отступы, скобки, двоеточия). 
                ВЕРНИ ТОЛЬКО ПОЛНЫЙ ИСПРАВЛЕННЫЙ КОД ВНУТРИ БЛОКА MARKDOWN. БЕЗ ПОЯСНЕНИЙ.
                """

                try:
                    resp, _ = self.architect.think([{"role": "user", "content": heal_prompt}], temperature=0.1)
                    fixed_code = self._extract_code_robust(resp)

                    if fixed_code:
                        current_code = fixed_code
                        print(Fore.YELLOW + f"🔧 [AUTO-HEAL] Синтаксический патч сгенерирован. Перепроверка...")
                    else:
                        print(Fore.RED + f"❌ [AUTO-HEAL] ИИ не вернул код в markdown-блоке. Попытка {attempt + 1} провалена.")
                except Exception as ex:
                    print(Fore.RED + f"❌ [AUTO-HEAL] Ошибка API при лечении синтаксиса: {ex}")

        print(Fore.RED + f"💀 [AUTO-HEAL] ФАТАЛЬНО: Не удалось вылечить {filepath} за {self.max_retries} попыток.")
        return False, content

    def _get_error_context(self, code: str, lineno: int) -> str:
        """Извлекает проблемную строку и её окружение."""
        lines = code.splitlines()
        if not lines: return ""
        
        start = max(0, lineno - 3)
        end = min(len(lines), lineno + 2)
        context = []
        for i in range(start, end):
            prefix = ">>> " if i + 1 == lineno else "    "
            context.append(f"{prefix}{i + 1}: {lines[i]}")
        return "\n".join(context)

    def _extract_code_robust(self, text: str) -> str:
        """Бронебойное извлечение Python-кода из ответов LLM."""
        if not text:
            return None
            
        pattern = re.compile(r'```(?:python)?\s*\n(.*?)\n```', re.DOTALL | re.IGNORECASE)
        match = pattern.search(text)
        
        if match:
            return match.group(1).strip()
            
        # Резервный механизм: очистка от текста, если ИИ забыл markdown-разметку
        lines = text.splitlines()
        code_lines = [line for line in lines if not line.strip().startswith(("Вот", "Исправ", "Я исправил", "```"))]
        clean_text = "\n".join(code_lines).strip()
        
        if any(kw in clean_text for kw in ["def ", "import ", "class ", "return ", "from "]):
            return clean_text
            
        return None