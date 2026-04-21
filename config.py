import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv(".env")

# --- 📂 ПУТИ ПРОЕКТА ---
# Используем Path для кроссплатформенности (Windows/Linux)
PROJECT_ROOT = Path(__file__).parent
DIR_HISTORY = PROJECT_ROOT / "History"
DIR_RESEARCH = PROJECT_ROOT / "Research"
DIR_SANDBOX = PROJECT_ROOT / "Sandbox"
DIR_LOGS = PROJECT_ROOT / "research" # Для journal.md

# Автоматическое создание структуры при запуске
for d in [DIR_HISTORY, DIR_RESEARCH, DIR_SANDBOX, DIR_LOGS]:
    d.mkdir(parents=True, exist_ok=True)

# --- 🔐 СЕТЬ И БЕЗОПАСНОСТЬ ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PROXY_PORT = 1080 # Должен совпадать с портом в genesis_core.py

# Данные для SSH-туннеля (для справки)
VPS_USER = "vpn"
VPS_IP = "91.211.15.93"

# --- 🧠 МОЗГОВОЙ ЦЕНТР (АРХИТЕКТУРА) ---
# Основная модель для принятия решений (должна быть в списке FREE)
MODEL_ARCHITECT = "nvidia/nemotron-3-super-120b-a12b:free"
MODEL_MONITOR = "liquid/lfm-2.5-1.2b-thinking:free"

# --- 🛡️ ГАРАНТИРОВАННО БЕСПЛАТНЫЙ ПУЛ (MODELS_FREE) ---
# Я удалил подозрительные модели, чтобы исключить списания
MODELS_FREE = [
    # Самые стабильные и быстрые
    "arcee-ai/trinity-large-preview:free",
    
    
    
    # Модели с глубоким рассуждением (Thinking)
    "liquid/lfm-2.5-1.2b-thinking:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    
    # Надежные Llama и Mistral
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "mistralai/pixtral-12b:free",
    
    # Кодеры (для написания micro_brain.py)
    "qwen/qwen3-coder:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    
    # Дополнительные проверенные узлы
    "nvidia/nemotron-nano-9b-v2:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free"
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free"




]


# --- ⚠️ ВНИМАНИЕ ---
# Все модели выше проверяются в genesis_core.py через 'money_drainers'.
# Даже если OpenRouter сделает их платными, ядро заблокирует запрос.