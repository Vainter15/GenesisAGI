import os
import json
import logging
from colorama import Fore

# Пытаемся импортировать torch. Если его нет, гомункул должен будет установить его через терминал.
try:
    import torch
except ImportError:
    torch = None

class MLToolbox:
    def __init__(self):
        """Инициализация инструментов машинного обучения для Seed AI."""
        self.root = os.getcwd()
        self.device = "cuda" if torch and torch.cuda.is_available() else "cpu"

    def check_hardware(self) -> str:
        """
        Техническая диагностика доступных вычислительных ресурсов.
        Критически важно для предотвращения CUDA Out Of Memory (OOM) ошибок.
        """
        if not torch:
            return "❌ Пакет 'torch' не установлен. Выполните 'pip install torch' через терминал."
            
        report = f"✅ [ML_TOOLBOX] Вычислительное устройство: {self.device.upper()}\n"
        
        if self.device == "cuda":
            vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            vram_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            report += f"GPU: {torch.cuda.get_device_name(0)}\n"
            report += f"VRAM Всего: {vram_total:.2f} GB\n"
            report += f"VRAM Занято: {vram_allocated:.2f} GB\n"
            
            # Строгий технический лимит под 4 ГБ VRAM
            if vram_total <= 4.1:
                report += "\n⚠️ ВНИМАНИЕ: Доступно около 4 ГБ видеопамяти. " \
                          "Архитектура модели должна быть <= 50 млн параметров. " \
                          "Используйте batch_size <= 4 и gradient_accumulation."
        return report

    def prepare_text_dataset(self, text_filepath: str, seq_length: int = 128) -> str:
        """
        Преобразует сырой текстовый файл в тензоры для обучения.
        Пока реализована простая символьная токенизация для старта.
        """
        if not torch:
            return "❌ Пакет 'torch' не установлен."
            
        try:
            full_path = os.path.abspath(os.path.join(self.root, text_filepath))
            if not os.path.exists(full_path):
                return f"❌ Ошибка: Датасет '{text_filepath}' не найден."
                
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            chars = sorted(list(set(text)))
            vocab_size = len(chars)
            stoi = {ch: i for i, ch in enumerate(chars)}
            
            # Сохраняем словарь, чтобы ИИ мог потом декодировать мысли
            vocab_path = os.path.join(os.path.dirname(full_path), "vocab.json")
            with open(vocab_path, 'w', encoding='utf-8') as f:
                json.dump({'stoi': stoi, 'chars': chars}, f, ensure_ascii=False, indent=2)
                
            data = torch.tensor([stoi[c] for c in text], dtype=torch.long)
            
            report = f"✅ [SUCCESS] Датасет загружен: {len(text)} символов.\n"
            report += f"Размер словаря (vocab_size): {vocab_size}\n"
            report += f"Словарь сохранен в: {vocab_path}\n"
            report += "Для обучения используйте генератор батчей, нарезая 'data' тензор."
            return report
            
        except Exception as e:
            return f"❌ Ошибка подготовки датасета: {e}"

    def save_checkpoint(self, state_dict: dict, filename: str = "checkpoint.pt") -> str:
        """Безопасное сохранение весов модели (чекпоинт)."""
        if not torch: return "❌ Ошибка: torch не установлен."
        try:
            full_path = os.path.abspath(os.path.join(self.root, filename))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            torch.save(state_dict, full_path)
            return f"✅ [SUCCESS] Чекпоинт сохранен: {filename}"
        except Exception as e:
            return f"❌ Ошибка сохранения чекпоинта: {e}"