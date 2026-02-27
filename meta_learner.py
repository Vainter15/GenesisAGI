import json
import os
import re
from colorama import Fore

class MetaLearner:
    def __init__(self, rules_file="system_rules.json"):
        """
        Инициализация модуля самообучения архитектуры.
        :param rules_file: Файл, где хранятся выученные правила.
        """
        self.rules_file = rules_file
        self.rules = self._load_rules()
        self.max_rules = 15 # Лимит, чтобы не перегружать контекст модели

    def _load_rules(self):
        """Загружает существующие динамические правила из JSON."""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def get_system_directives(self) -> str:
        """Склеивает неизменяемые инстинкты и выученные правила."""
        
        # 🛡️ ИММУТАБЕЛЬНЫЕ БАЗОВЫЕ ПРАВИЛА (Зашиты намертво)
        core_directives = """
[БАЗОВЫЕ ЗАКОНЫ СИСТЕМЫ - НЕ НАРУШАТЬ]:
1. ТЕРМИНАЛ: После создания или изменения .py файла через 'write_file', СЛЕДУЮЩИМ шагом ОБЯЗАТЕЛЬНО запускай его через 'execute_command' (например, 'python script.py') для проверки.
2. ИСПРАВЛЕНИЕ ОШИБОК: Если 'execute_command' вернул ошибку, НЕ завершай шаг. Прочитай ошибку, исправь код через 'write_file' и проверь снова.
3. АППАРАТНЫЕ ОГРАНИЧЕНИЯ: Ты работаешь на локальном железе с 4 ГБ VRAM. Любые ML-модели должны быть микроскопическими, batch_size минимальным.
4. ЗАВИСИМОСТИ: При ошибке 'ModuleNotFoundError' используй 'execute_command' для установки (например, 'pip install torch').
"""
        # Добавляем динамически выученный опыт
        if not self.rules:
            return core_directives + "\n[ДИНАМИЧЕСКИЕ ПРАВИЛА]: Пока не сформированы."
        
        dyn_text = "\n[ВЫУЧЕННЫЙ ОПЫТ (ДИНАМИЧЕСКИЕ ПРАВИЛА)]:\n" + "\n".join([f"- {rule}" for rule in self.rules])
        return core_directives + dyn_text

    def extract_new_rule(self, architect, action_history: str, failure_log: str):
        """
        Анализирует провал и заставляет LLM сформулировать новое правило,
        чтобы избежать повторения этой ошибки в будущем.
        """
        print(Fore.MAGENTA + "🧠 [META-LEARNER] Анализ ошибки и извлечение опыта...")

        prompt = f"""
        ТЫ — СИСТЕМА МЕТА-ОБУЧЕНИЯ AGI.
        
        ИСТОРИЯ ДЕЙСТВИЙ:
        {action_history}
        
        ЛОГ КРИТИЧЕСКОЙ ОШИБКИ:
        {failure_log}

        ЗАДАЧА:
        Выведи ОДНО предельно краткое и жесткое техническое правило (директиву), 
        которое предотвратит эту ошибку в будущем. 
        Правило должно касаться архитектуры кода или логики вызова инструментов.

        ВЕРНИ JSON:
        {{
            "new_rule": "текст правила",
            "reasoning": "почему это важно"
        }}
        """

        try:
            resp, _ = architect.think([{"role": "user", "content": prompt}])
            
            match = re.search(r'\{[\s\S]*\}', resp)
            if match:
                data = json.loads(match.group(0).replace("```json", "").replace("```", ""))
                new_rule = data.get("new_rule")
                
                if new_rule and new_rule not in self.rules:
                    self.rules.append(new_rule)
                    if len(self.rules) > self.max_rules:
                        self.rules.pop(0)
                    
                    self._save_rules()
                    print(Fore.GREEN + f"🆕 [META-LEARNER] Усвоено новое правило: {new_rule}")
                else:
                    print(Fore.YELLOW + "🔍 [META-LEARNER] Новых уникальных правил не обнаружено.")
        
        except Exception as e:
            print(Fore.RED + f"❌ [META-LEARNER] Сбой при извлечении правила: {e}")

    def _save_rules(self):
        """Сохраняет правила в файл."""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(Fore.RED + f"❌ [META-LEARNER] Не удалось сохранить правила: {e}")

    def reset_logic(self):
        """Полная очистка правил (если система зашла в тупик)."""
        self.rules = []
        if os.path.exists(self.rules_file):
            os.remove(self.rules_file)
        print(Fore.RED + "🧹 [META-LEARNER] Все системные правила стерты.")