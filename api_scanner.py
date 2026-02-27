import os
import requests
import json
import time
from dotenv import load_dotenv
from colorama import Fore, init
import logging

init(autoreset=True)

# Настройка логирования в файл
logging.basicConfig(
    filename='api_diagnostic.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Загружаем переменные окружения
load_dotenv(".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Настройки из твоего config.py
PROXY_URL = "socks5://vpn:vpn@91.211.15.93:1080"  # Формат requests (если есть логин/пароль, они должны быть тут)
# Если прокси без пароля, раскомментируй строку ниже:
PROXY_URL = "socks5h://91.211.15.93:1080" 

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

TEST_MODEL = "stepfun/step-3.5-flash:free"

def log_and_print(msg, color=Fore.WHITE, level="info"):
    print(color + msg)
    if level == "info": logging.info(msg)
    elif level == "error": logging.error(msg)
    elif level == "warning": logging.warning(msg)

def test_api_key():
    log_and_print("\n--- 1. ПРОВЕРКА API КЛЮЧА ---", Fore.CYAN)
    if not API_KEY:
        log_and_print("❌ Ключ OPENROUTER_API_KEY не найден в файле .env!", Fore.RED, "error")
        return False
    
    masked_key = f"{API_KEY[:10]}...{API_KEY[-4:]}" if len(API_KEY) > 15 else "***"
    log_and_print(f"✅ Ключ найден: {masked_key}", Fore.GREEN)
    return True

def test_connection(use_proxy=False):
    mode = "ЧЕРЕЗ ПРОКСИ" if use_proxy else "НАПРЯМУЮ"
    log_and_print(f"\n--- 2. ПРОВЕРКА СВЯЗИ ({mode}) ---", Fore.CYAN)
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    proxies = PROXIES if use_proxy else None
    
    try:
        start_time = time.time()
        # Проверяем эндпоинт аутентификации OpenRouter
        resp = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, proxies=proxies, timeout=10)
        ping = round((time.time() - start_time) * 1000)
        
        if resp.status_code == 200:
            data = resp.json()
            log_and_print(f"✅ Успешное подключение! Пинг: {ping}мс", Fore.GREEN)
            log_and_print(f"ℹ️ Данные ключа: Лимит: {data.get('data', {}).get('limit')}, Использовано: {data.get('data', {}).get('usage')}", Fore.YELLOW)
            return True
        elif resp.status_code == 401:
            log_and_print(f"❌ Ошибка 401: Ваш API ключ недействителен или забанен.", Fore.RED, "error")
            return False
        else:
            log_and_print(f"⚠️ Странный ответ сервера: {resp.status_code} - {resp.text}", Fore.YELLOW, "warning")
            return False
            
    except requests.exceptions.ProxyError:
        log_and_print(f"❌ Ошибка Прокси! Туннель {PROXY_URL} недоступен или мертв.", Fore.RED, "error")
        return False
    except requests.exceptions.ConnectionError:
        log_and_print(f"❌ Ошибка Сети! Нет связи с openrouter.ai.", Fore.RED, "error")
        return False
    except Exception as e:
        log_and_print(f"❌ Неизвестная ошибка: {e}", Fore.RED, "error")
        return False

def test_model_generation(use_proxy=False):
    log_and_print(f"\n--- 3. ТЕСТ ГЕНЕРАЦИИ МОДЕЛИ '{TEST_MODEL}' ---", Fore.CYAN)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": "Say 'OK' if you hear me."}],
        "max_tokens": 10
    }
    proxies = PROXIES if use_proxy else None
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, proxies=proxies, timeout=15)
        
        if resp.status_code == 200:
            result = resp.json()
            answer = result['choices'][0]['message']['content'].strip()
            log_and_print(f"✅ Модель работает! Ответ: {answer}", Fore.GREEN)
            return True
        else:
            log_and_print(f"❌ Ошибка модели {resp.status_code}: {resp.text}", Fore.RED, "error")
            return False
            
    except Exception as e:
        log_and_print(f"❌ Ошибка запроса к модели: {e}", Fore.RED, "error")
        return False

if __name__ == "__main__":
    log_and_print("🚀 ЗАПУСК ДИАГНОСТИКИ API...", Fore.MAGENTA)
    
    if test_api_key():
        # Сначала пробуем напрямую
        direct_ok = test_connection(use_proxy=False)
        if direct_ok:
            test_model_generation(use_proxy=False)
        
        # Потом пробуем через твой прокси из конфига
        proxy_ok = test_connection(use_proxy=True)
        if proxy_ok:
            test_model_generation(use_proxy=True)
            
    log_and_print("\n📁 Полный отчет сохранен в api_diagnostic.log", Fore.MAGENTA)