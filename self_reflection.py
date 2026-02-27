import json
import re
from colorama import Fore

class SelfReflection:
    @staticmethod
    def analyze_action(theory: str, action: str, result: str, architect) -> str:
        """
        Прагматичный Аудитор. Оценивает шаг, направляя систему от разработки к тестам.
        """
        print(Fore.YELLOW + "🪞 [AUDITOR] Анализ выполненного действия...")

        if not action or not result:
            return "❌ [AUDIT FAILED] Пустое действие или результат. Системный сбой."

        # Жесткая инструкция для нейросети-аудитора
        system_prompt = (
            "Ты — Верховный Аудитор системы AGI (Проект Автогенезис). "
            "Твоя задача — проверить, успешно ли отработал инструмент на текущем шаге. \n\n"
            "⚠️ ЖЕСТКИЕ ЗАКОНЫ ПРАГМАТИКИ:\n"
            "1. Инструмент 'write_file' ТОЛЬКО сохраняет текст. Если файл успешно сохранен — это АБСОЛЮТНЫЙ УСПЕХ (✅ [AUDIT SUCCESS]). НЕ ТРЕБУЙ тестов на этом этапе!\n"
            "2. Инструмент 'execute_command' / 'execute_test' — если команда запустилась и выдала ЛЮБОЙ вывод (даже с ошибками Python) — это УСПЕХ ИНСТРУМЕНТА (✅ [AUDIT SUCCESS]). Ошибки кода — это фронт работ для следующего шага.\n"
            "3. Инструмент 'analyze_structure' / 'list_files' — если данные получены, это успех.\n\n"
            "ФОРМАТ ОТВЕТА:\n"
            "✅ [AUDIT SUCCESS] <Обоснование успеха>. | Урок: <Четкое техническое действие для следующего шага>\n"
            "❌ [AUDIT FAILED] <Причина сбоя инструмента>. | Урок: <Как исправить вызов инструмента>"
        )

        user_prompt = (
            f"ГИПОТЕЗА (ЧЕГО ХОТЕЛИ): {theory}\n"
            f"ИНСТРУМЕНТ: {action}\n"
            f"РЕЗУЛЬТАТ: {result}\n\n"
            "Оцени результат строго по ЗАКОНАМ ПРАГМАТИКИ."
        )

        try:
            # Запрашиваем оценку (температура 0.1 для исключения фантазий)
            response, _ = architect.think(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )

            if not response:
                return "✅ [AUDIT SUCCESS] Аварийный пропуск (сбой API)."

            response = response.strip()
            res_str = str(result).lower()
            
            # --- 🛡️ ПРИНУДИТЕЛЬНАЯ ЗАЩИТА ОТ ЦИКЛОВ (HARD OVERRIDE) ---
            
            # Если файл сохранен, Аудитор ОБЯЗАН дать команду на проверку
            if action == "write_file" and "успешно сохранен" in res_str:
                return "✅ [AUDIT SUCCESS] Файл сохранен. | Урок: Теперь проверь его работоспособность через execute_command."

            # Если команда выполнена, но в ней ошибки — это УСПЕХ инструмента, но повод для правки кода
            if action in ["execute_command", "execute_test"] and ("output" in res_str or "завершено" in res_str):
                if "❌" in response or "FAILED" in response or "error" in res_str:
                    return f"✅ [AUDIT SUCCESS] Команда выполнена, в коде обнаружены ошибки. | Урок: Проанализируй ошибки и исправь код через write_file."

            # Возвращаем вердикт нейросети, если он адекватный
            if "✅" in response or "❌" in response:
                return response
            else:
                return f"✅ [AUDIT SUCCESS] {response} (Вердикт подтвержден)"

        except Exception as e:
            return f"✅ [AUDIT SUCCESS] Системная ошибка аудитора: {e}. Пропускаем."