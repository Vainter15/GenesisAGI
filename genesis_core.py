import requests
import config
import random
import time
from colorama import Fore

class GenesisCore:
    # Общий словарь штрафов для всех экземпляров
    _penalty_box = {}

    def __init__(self, primary_model=None, is_architect=False):
        # Загружаем пул из конфига
        if hasattr(config, 'MODELS_FREE') and isinstance(config.MODELS_FREE, list):
            self.model_pool = config.MODELS_FREE
        else:
            self.model_pool = [config.MODEL_ARCHITECT] 
            
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.proxies = {
            'http': f'socks5h://127.0.0.1:{config.PROXY_PORT}',
            'https': f'socks5h://127.0.0.1:{config.PROXY_PORT}'
        }

    def _get_healthy_models(self):
        """Отсеивает модели в бане."""
        current_time = time.time()
        healthy = []
        for model in self.model_pool:
            if model not in self._penalty_box or current_time > self._penalty_box[model]:
                healthy.append(model)
        
        if not healthy:
            self._penalty_box.clear()
            return self.model_pool
        return healthy

    def think(self, messages, max_tokens=4000, temperature=0.3, **kwargs):
        """
        Метод с тройной защитой от платных моделей.
        """
        active_pool = self._get_healthy_models()
        
        # 1. 🛡️ ПРЯМОЙ ЧЕРНЫЙ СПИСОК (Абсолютный запрет на списание денег)
        # Если модель содержит эти слова, она блокируется ДО запроса.
        money_drainers = [
            "gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-1.5-pro", 
            "pro", "ultra", "large", "premium", "paid", "nano-4.1"
        ]
        
        # Фильтруем пул, оставляя только гарантированно бесплатные/малые модели
        safe_pool = [
            m for m in active_pool 
            if not any(drainer in m.lower() for drainer in money_drainers)
        ]

        if not safe_pool:
            print(Fore.RED + "❌ [SECURITY] Безопасный пул пуст. Платные модели заблокированы.")
            return None, "NO_FREE_MODELS"

        # 2. Берем до 15 моделей для перебора
        attempts = random.sample(safe_pool, min(15, len(safe_pool)))

        for model in attempts:
            headers = {
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/Vainter15/GenesisAGI",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "provider": {
                    "allow_fallbacks": False # 🛑 Запрет на переключение на платные аналоги
                }
            }
            
            try:
                resp = requests.post(
                    self.url, 
                    headers=headers,
                    json=payload,
                    proxies=self.proxies, 
                    timeout=30
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    print(Fore.CYAN + f"📡 [NETWORK] {model} " + Fore.GREEN + "✅ (FREE)")
                    return content.strip(), model
                    
                elif resp.status_code == 402:
                    # Если каким-то чудом прорвалась платная модель
                    print(Fore.RED + f"🛑 [MONEY PROTECT] Заблокирована попытка списания за {model}")
                    self._penalty_box[model] = time.time() + 86400 # Бан на сутки
                    continue
                    
                else:
                    self._penalty_box[model] = time.time() + 300
                    continue
                    
            except Exception:
                self._penalty_box[model] = time.time() + 60
                continue 

        return None, "ALL_FAILED"