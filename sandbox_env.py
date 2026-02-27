import subprocess
import sys
import os
import time
from colorama import Fore

class PrometheusSandbox:
    def __init__(self, timeout=10):
        self.timeout = timeout

    def run_simulation(self, code_content, filename="simulation_test.py"):
        """
        Запуск Фазы 2: Симуляция в изолированном пространстве.
        """
        temp_path = os.path.join("Sandbox", filename)
        os.makedirs("Sandbox", exist_ok=True)
        
        # Сохраняем код для теста
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        print(Fore.MAGENTA + f"🧪 [SANDBOX] Запуск симуляции '{filename}'...")
        
        try:
            start_time = time.time()
            # Запускаем в отдельном процессе
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            elapsed = time.time() - start_time
            
            # Анализ результатов симуляции (Phase 2 Evaluation)
            is_stable = result.returncode == 0
            stats = {
                "success": is_stable,
                "duration": round(elapsed, 4),
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500]
            }
            
            if is_stable:
                print(Fore.GREEN + f"✅ [SANDBOX] Симуляция успешна ({stats['duration']} сек).")
            else:
                print(Fore.RED + f"❌ [SANDBOX] Сбой стабильности: {result.stderr[:200]}")
                
            return stats

        except subprocess.TimeoutExpired:
            print(Fore.RED + "❌ [SANDBOX] Ошибка: Превышен лимит ресурсов (зацикливание).")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}