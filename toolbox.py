import os
import ast
import sys
import subprocess
from colorama import Fore

class Toolbox:
    def __init__(self):
        """Инициализация инструментов взаимодействия с файловой системой и ОС."""
        # Корень проекта — там, где запущен скрипт
        self.root = os.getcwd()
        
    def __init__(self):
        """Инициализация инструментов взаимодействия с файловой системой и ОС."""
        self.root = os.getcwd()
        self.clipboard = {} # 🆕 Оперативная память для фрагментов кода
        
    def save_to_clipboard(self, key: str, content: str) -> str:
        """Сохраняет кусок кода или текст в оперативную память ИИ."""
        self.clipboard[key] = content
        return f"✅ [SUCCESS] Данные сохранены в буфер под ключом '{key}'. Объем: {len(content)} символов."

    def view_clipboard(self) -> str:
        """Показывает все сохраненные фрагменты."""
        if not self.clipboard:
            return "Буфер обмена пуст."
        
        report = "📋 [CLIPBOARD] СОДЕРЖИМОЕ ВАШЕГО БУФЕРА:\n"
        for k, v in self.clipboard.items():
            report += f"\n--- КЛЮЧ: [{k}] ---\n{v}\n"
        return report
    
    def search_in_file(self, filename: str, search_query: str) -> str:
        """Ищет конкретный текст в файле и выводит его вместе с контекстом (соседними строками)."""
        try:
            full_path = os.path.abspath(os.path.join(self.root, filename))
            if not os.path.exists(full_path):
                return f"❌ Ошибка: Файл '{filename}' не найден."

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            results = []
            context_radius = 5 # Захватываем 5 строк до и 5 после совпадения

            for i, line in enumerate(lines):
                if search_query.lower() in line.lower():
                    start = max(0, i - context_radius)
                    end = min(len(lines), i + context_radius + 1)
                    
                    snippet = f"--- Совпадение на строке {i+1} ---\n"
                    for j in range(start, end):
                        prefix = ">> " if j == i else "   "
                        snippet += f"{prefix}{j+1}: {lines[j]}"
                    results.append(snippet)

            if not results:
                return f"🔍 Запрос '{search_query}' в файле {filename} не найден."
            
            return f"✅ [SUCCESS] Найдены совпадения:\n\n" + "\n".join(results[:3]) # Отдаем максимум 3 куска, чтобы не перегрузить ИИ
            
        except Exception as e:
            return f"❌ Ошибка поиска: {e}"

    def list_files(self, directory="."):
        """Возвращает список файлов, игнорируя служебные папки."""
        try:
            target_dir = os.path.abspath(os.path.join(self.root, directory))
            if not target_dir.startswith(self.root):
                return "❌ Ошибка безопасности: Попытка выхода за пределы проекта."

            if not os.path.exists(target_dir):
                return f"❌ Ошибка: Директория '{directory}' не найдена."

            files = os.listdir(target_dir)
            # Список папок, которые ИИ не нужно 'видеть', чтобы не забивать контекст
            ignored = [".git", "__pycache__", "mem0_db", "research", ".env", "venv", "AGI_V2_Sandbox"]
            filtered = [f for f in files if f not in ignored]
            
            return f"✅ [SUCCESS] 📂 КАРТА СИСТЕМЫ в '{directory}':\n{filtered}"
        except Exception as e:
            return f"❌ Ошибка листинга: {e}"

    def read_file(self, filename, start_line=1, end_line=None):
        """Инструмент 'Полного зрения': считывает файл или его часть."""
        try:
            full_path = os.path.abspath(os.path.join(self.root, filename))
            # ... проверки безопасности ...
            
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            end = end_line if end_line else min(start_line + 300, total_lines) # Читаем максимум 300 строк за раз
            
            content = "".join(lines[start_line-1:end])
            
            report = f"✅ [SUCCESS] 📖 ФАЙЛ {filename} (Строки {start_line}-{end} из {total_lines}):\n\n{content}"
            if end < total_lines:
                report += f"\n\n⚠️ Файл слишком большой. Чтобы прочитать дальше, вызови read_file с start_line={end+1}"
            return report
        except Exception as e:
            return f"❌ Ошибка чтения {filename}: {e}"

    def write_file(self, filename, content):
        """Записывает данные в файл, надежно очищая от Markdown-разметки ИИ."""
        try:
            full_path = os.path.abspath(os.path.join(self.root, filename))
            if not full_path.startswith(self.root):
                return "❌ Ошибка безопасности: Запись файлов вне проекта запрещена."

            # Бронебойная очистка от маркдауна (```python ... ```)
            content = content.strip()
            if content.startswith("```"):
                # Ищем конец первой строки с тегами (например, ```python\n)
                first_newline = content.find('\n')
                if first_newline != -1:
                    content = content[first_newline+1:]
                if content.endswith("```"):
                    content = content[:-3].strip()

            # Автоматически создаем папки, если файл вложенный
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ [SUCCESS] Файл {filename} успешно сохранен. Объем: {len(content)} байт."
        except Exception as e:
            return f"❌ Ошибка записи {filename}: {e}"

    def execute_test(self, filename):
        """Запуск python-кода в изолированном процессе с жестким таймаутом."""
        try:
            full_path = os.path.abspath(os.path.join(self.root, filename))
            if not os.path.exists(full_path):
                return f"❌ Ошибка: Скрипт '{filename}' не найден."

            print(Fore.YELLOW + f"⚙️ [TOOLBOX] Тестовый прогон: {filename}...")
            
            result = subprocess.run(
                [sys.executable, full_path], 
                capture_output=True, 
                text=True, 
                timeout=20 # Увеличил до 20 сек для ML-скриптов
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            status = "✅ [SUCCESS]" if result.returncode == 0 else "❌ [FAILED]"
            
            if len(output) > 2000:
                output = output[:2000] + "\n\n...[ВЫВОД ОБРЕЗАН ДЛЯ ЭКОНОМИИ КОНТЕКСТА]..."
                
            return f"{status} Исполнение '{filename}' завершено.\n\nВЫВОД:\n{output}"
            
        except subprocess.TimeoutExpired:
            return f"❌ [FAILED] Ошибка: Превышен лимит времени (20 сек)."
        except Exception as e:
            return f"❌ [FAILED] Критическая ошибка исполнения: {e}"

    def execute_command(self, command: str) -> str:
        """
        ⚡ ВЫСШИЙ УРОВЕНЬ ДОСТУПА (С ЗАЩИТОЙ ОТ СУДНОГО ДНЯ) ⚡
        Выполняет команду в терминале, предварительно пропуская ее через фильтр безопасности.
        """
        # --- 🛡️ БЛОК БЕЗОПАСНОСТИ ---
        command_lower = command.lower()
        forbidden_keywords = [
            "del ", "rm ", "rmdir", "rd ", "format ", "diskpart", 
            "mklink", "icacls", "takeown", "attrib", "reg ", "regedit",
            "shutdown", "restart", "wipe", "vssadmin", "bcdedit", 
            "powercfg", "schtasks", "net user", "net localgroup"
        ]
        
        for keyword in forbidden_keywords:
            if keyword in command_lower:
                warning_msg = f"❌ [SECURITY BLOCK] Действие заблокировано! Команда содержит опасный паттерн '{keyword}'."
                print(Fore.RED + f"🛑 [SECURITY ALERT] ИИ попытался выполнить опасную команду: {command}")
                return warning_msg
        # ----------------------------

        try:
            print(Fore.MAGENTA + f"\n[TERMINAL] Выполняю команду: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120 
            )
            
            output = result.stdout.strip()
            if result.stderr:
                output += f"\n[СИСТЕМНЫЕ СООБЩЕНИЯ/ОШИБКИ]:\n{result.stderr.strip()}"
                
            if not output:
                return f"✅ [SUCCESS] Команда '{command}' выполнена успешно."
            
            if len(output) > 3000:
                output = output[:3000] + "\n\n...[ВЫВОД ОБРЕЗАН]..."
                
            return f"✅ [TERMINAL OUTPUT]:\n{output}"
            
        except subprocess.TimeoutExpired:
            return "❌ [FAILED] Ошибка: Превышено время ожидания терминала (120 секунд)."
        except Exception as e:
            return f"❌ [FAILED] Системная ошибка терминала: {e}"

    def analyze_structure(self):
        """Глубокий анализ архитектуры: дерево файлов + граф связей (импортов)."""
        print(Fore.YELLOW + "🔍 [TOOLBOX] Анализ структуры проекта...")
        
        report = "✅ [SUCCESS] 🔍 ТЕХНИЧЕСКИЙ АНАЛИЗ АРХИТЕКТУРЫ:\n\n"
        
        tree = []
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "mem0_db", "research", "plugins", "venv"]]
            level = root.replace(self.root, '').count(os.sep)
            indent = ' ' * 4 * level
            tree.append(f"{indent}📁 {os.path.basename(root) or 'ROOT'}/")
            for f in files:
                tree.append(f"{' ' * 4 * (level + 1)}📄 {f}")
        
        report += "🌲 ИЕРАРХИЯ ПРОЕКТА:\n" + "\n".join(tree) + "\n\n"

        report += "🔗 ГРАФ ИМПОРТОВ (СВЯЗИ):\n"
        py_files = [f for f in os.listdir(self.root) if f.endswith('.py')]
        
        for pf in py_files:
            try:
                with open(pf, 'r', encoding='utf-8') as f:
                    tree_node = ast.parse(f.read())
                    imports = []
                    for node in ast.walk(tree_node):
                        if isinstance(node, ast.Import):
                            for n in node.names: imports.append(n.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module: imports.append(node.module)
                    
                    if imports:
                        report += f"- {pf} -> {', '.join(sorted(set(imports)))}\n"
            except: continue

        return report