import requests
import config

proxies = {
    'http': f'socks5h://127.0.0.1:{config.PROXY_PORT}',
    'https': f'socks5h://127.0.0.1:{config.PROXY_PORT}'
}

print("🌐 Запуск диагностического зонда для SSH-туннеля...")
try:
    # Проверка связи через прокси
    resp = requests.get("https://openrouter.ai/api/v1/models", proxies=proxies, timeout=10)
    if resp.status_code == 200:
        print("✅ СВЯЗЬ ЕСТЬ! Туннель и OpenRouter работают.")
    else:
        print(f"❌ ОШИБКА API: Код {resp.status_code}. Проверь ключ или баланс.")
except Exception as e:
    print(f"❌ [ОБРЫВ] Ошибка соединения.\nПричина: {e}")