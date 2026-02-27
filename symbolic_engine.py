import re
import json
from colorama import Fore

class NeuroSymbolicBridge:
    # 🗺️ РАСШИРЕННАЯ КАРТА СИНОНИМОВ
    # Теперь ИИ может называть инструменты как угодно — мост поймет его
    TOOL_ALIASES = {
        "анализ": "analyze_structure", "структур": "analyze_structure", "ast": "analyze_structure",
        "чтение": "read_file", "прочитать": "read_file", "открой": "read_file",
        "запись": "write_file", "сохранить": "write_file", "записать": "write_file",
        "план": "update_plan", "шаг": "update_plan",
        "завершить": "finish_step", "готово": "finish_step", "стоп": "finish_step",
        "список": "list_files", "файлы": "list_files",
        "интеграция": "integrate_tool", "внедрить": "integrate_tool", 
        "тест": "execute_test", "проверка": "execute_test",
        "терминал": "execute_command", "команда": "execute_command", "cmd": "execute_command", "консоль": "execute_command"
    }

    @staticmethod
    def parse_action_data(text: str) -> dict:
        """Извлекает JSON из текста любой степени замусоренности с глубокой очисткой."""
        if not text: return None
        
        # 1. Поиск блока JSON через улучшенную регулярку
        try:
            # Ищем самый широкий блок между фигурными скобками
            match = re.search(r'(\{[\s\S]*\})', text)
            if match:
                json_str = match.group(1)
                # Чистим комментарии (// и #)
                json_str = re.sub(r'//.*', '', json_str)
                json_str = re.sub(r'#.*', '', json_str)
                # Удаляем висячие запятые
                json_str = re.sub(r',\s*\}', '}', json_str)
                json_str = re.sub(r',\s*\]', ']', json_str)
                # Убираем лишние переносы строк внутри строк JSON
                json_str = json_str.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
                
                return json.loads(json_str)
        except:
            pass

        # 2. ПЛАН Б: Ручной сбор данных (если JSON совсем развалился)
        try:
            # Ищем поле tool
            tool_match = re.search(r'["\']tool["\']\s*:\s*["\']([^"\']+)["\']', text)
            if tool_match:
                tool = tool_match.group(1)
                args = {}
                # Ищем filename
                f_match = re.search(r'["\'](?:filename|file|path)["\']\s*:\s*["\']([^"\']+)["\']', text)
                if f_match: args["filename"] = f_match.group(1)
                # Ищем command (для терминала)
                cmd_match = re.search(r'["\'](?:command|cmd|text)["\']\s*:\s*["\']([^"\']+)["\']', text)
                if cmd_match: args["command"] = cmd_match.group(1)
                # Ищем content (для записи файлов)
                c_match = re.search(r'["\'](?:content|code|body)["\']\s*:\s*["\']([\s\S]*?)["\']\s*[,}]', text)
                if c_match: args["content"] = c_match.group(1)
                
                return {"theory": "Восстановлено парсером", "tool": tool, "args": args}
        except:
            pass
        return None

    @staticmethod
    def fix_tool_name(tool_name: str, raw_text: str = "") -> str:
        """Нормализует имя инструмента, используя карту алиасов."""
        name_clean = str(tool_name).strip().lower()
        for alias, real_name in NeuroSymbolicBridge.TOOL_ALIASES.items():
            if alias in name_clean: return real_name
        return name_clean

    @staticmethod
    def bridge_arguments(tool_name: str, args: dict) -> dict:
        """Унифицирует аргументы для всех инструментов, исправляя ошибки ИИ."""
        if not isinstance(args, dict): args = {}
        
        # 📂 Унификация путей к файлам
        if tool_name in ["read_file", "write_file", "execute_test"]:
            for key in ["file", "path", "filename", "filepath", "target"]:
                if key in args and key != "filename":
                    args["filename"] = args.pop(key)
                    break
        
        # 📝 Унификация контента (для записи)
        if tool_name == "write_file":
            for key in ["code", "text", "content", "body", "data"]:
                if key in args and key != "content":
                    args["content"] = args.pop(key)
                    break

        # ⚡ Унификация команд (для ТЕРМИНАЛА)
        if tool_name == "execute_command":
            for key in ["cmd", "text", "command", "run", "script"]:
                if key in args and key != "command":
                    args["command"] = args.pop(key)
                    break
                    
        return args