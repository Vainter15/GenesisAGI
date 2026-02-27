import os
import sys
import importlib
import inspect
from colorama import Fore
from toolbox import Toolbox

class EvolutionEngine:
    def __init__(self):
        """
        Инициализация движка эволюции.
        Управляет созданием, хранением и горячей загрузкой новых навыков.
        """
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        if self.root_dir not in sys.path:
            sys.path.append(self.root_dir)

        self.plugins_dir = os.path.join(self.root_dir, "plugins")
        self.tools = {}  # Реестр динамически созданных функций
        
        self._ensure_environment()
        self._load_existing_tools()

    def _ensure_environment(self):
        """Создает структуру папок и __init__ файлы."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        init_file = os.path.join(self.plugins_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Genesis Dynamic Plugins Module\n")

    def _load_existing_tools(self):
        """Подгружает ранее созданные инструменты из папки plugins при старте."""
        try:
            loaded_count = 0
            for filename in os.listdir(self.plugins_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = f"plugins.{filename[:-3]}"
                    tool_name = filename[:-3]
                    
                    if self._import_and_bind_tool(module_name, tool_name):
                        loaded_count += 1
                        
            if loaded_count > 0:
                print(Fore.GREEN + f"📜 [EVOLUTION] Загружено навыков из памяти: {loaded_count}")
        except Exception as e:
            print(Fore.RED + f"⚠️ [EVOLUTION] Ошибка загрузки навыков: {e}")

    def _import_and_bind_tool(self, module_name, tool_name):
        """Импортирует модуль и привязывает функцию к Toolbox."""
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            # Ищем функцию с именем tool_name внутри модуля
            if hasattr(module, tool_name):
                func = getattr(module, tool_name)
                if callable(func):
                    # Привязываем к экземпляру Toolbox
                    setattr(Toolbox, tool_name, func)
                    self.tools[tool_name] = func
                    return True
            return False
        except Exception as e:
            print(Fore.RED + f"⚠️ Ошибка импорта {tool_name}: {e}")
            return False

    def inject_new_tool(self, tool_name: str, tool_code: str) -> str:
        """Интегрирует новый код в систему 'на лету', создавая отдельный файл."""
        print(Fore.MAGENTA + f"🧬 [EVOLUTION] Интеграция нового навыка: {tool_name}...")
        
        # Защита от кривых имен файлов
        safe_name = tool_name.replace(" ", "_").lower()
        file_path = os.path.join(self.plugins_dir, f"{safe_name}.py")
        module_name = f"plugins.{safe_name}"

        try:
            # 1. Записываем чистый код ИИ в отдельный файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Auto-generated skill: {safe_name}\n\n")
                f.write(tool_code)

            # 2. Пытаемся импортировать и привязать
            success = self._import_and_bind_tool(module_name, safe_name)
            
            if success:
                print(Fore.GREEN + f"✅ [EVOLUTION] Навык '{safe_name}' успешно усвоен и готов к работе.")
                return f"✅ УСПЕХ: Инструмент '{safe_name}' добавлен в Toolbox."
            else:
                # Если файл создался, но функция не найдена (ИИ назвал функцию иначе)
                return f"❌ ОШИБКА: Код сохранен, но функция def {safe_name}(...) не найдена внутри кода."

        except Exception as e:
            return f"❌ [EVOLUTION] Критическая ошибка при интеграции: {e}"

    def get_evolved_inventory(self):
        """Возвращает список имен всех созданных инструментов."""
        return list(self.tools.keys())