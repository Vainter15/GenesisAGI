from mem0 import Memory
from colorama import Fore
import os

class GenesisLongTerm:
    def __init__(self):
        """
        Инициализация долговременной памяти на базе Mem0.
        Использует локальный Ollama для эмбеддингов и ChromaDB для хранения.
        """
        self.memory = None # Инициализируем заранее для защиты от AttributeError
        self.user_id = "Vainter15"
        
        print(Fore.MAGENTA + "🐘 [MEM0] Подключение к векторному хранилищу знаний...")
        try:
            config = {
                "vector_store": {
                    "provider": "chroma", 
                    "config": {
                        "path": "./mem0_db", 
                    }
                },
                "embedder": {
                    "provider": "ollama", 
                    "config": {
                        "model": "nomic-embed-text" 
                    }
                }
            }
            self.memory = Memory.from_config(config)
            print(Fore.GREEN + "✅ [MEM0] Векторная база данных успешно подключена.")
        except Exception as e:
            print(Fore.RED + f"❌ [MEM0] Ошибка инициализации (база будет отключена): {e}")

    def save_experience(self, step_name, result_data, status="success"):
        """
        Обертка для сохранения опыта выполнения шага.
        Вызывается ядром genesis.py при автоматическом успешном завершении задачи.
        """
        fact_text = f"ОПЫТ ({status.upper()}): Выполнен шаг '{step_name}'. Итог: {result_data}"
        return self.store_fact(fact_text)

    def store_fact(self, text):
        """
        Сохраняет новый факт или событие в память.
        """
        if not self.memory:
            return "⚠️ [MEM0] Сохранение невозможно: база данных не инициализирована."
            
        try:
            print(Fore.MAGENTA + f"📝 [MEM0] Запись нового инсайта: {text[:50]}...")
            self.memory.add(text, user_id=self.user_id)
            return "✅ Факт успешно сохранен в векторную базу."
        except Exception as e:
            err = f"⚠️ Не удалось сохранить факт: {e}"
            print(Fore.RED + err)
            return err

    def get_relevant_facts(self, query):
        """
        Семантический поиск релевантных знаний по запросу.
        """
        if not self.memory:
            return []
            
        try:
            results = self.memory.search(query, user_id=self.user_id)
            facts = []
            
            if isinstance(results, dict):
                results = results.get("results", []) or results.get("memories", [])
                
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        content = r.get('memory') or r.get('content') or r.get('text')
                        if content:
                            facts.append(content)
                    elif isinstance(r, str):
                        facts.append(r)
            
            return list(set(facts))
        except Exception as e:
            print(Fore.RED + f"⚠️ [MEM0] Ошибка поиска: {e}")
            return []

    def update_fact(self, memory_id, new_text):
        """
        Принудительное обновление конкретной записи.
        """
        if not self.memory:
            return False
            
        try:
            self.memory.update(memory_id=memory_id, data=new_text)
            print(Fore.GREEN + f"🔄 [MEM0] Запись {memory_id} обновлена.")
            return True
        except Exception as e:
            print(Fore.RED + f"❌ [MEM0] Ошибка обновления записи: {e}")
            return False

    def delete_fact_by_query(self, query):
        """
        Удаление фактов.
        """
        if not self.memory:
            return
            
        try:
            self.memory.delete_all(user_id=self.user_id) 
            print(Fore.YELLOW + f"🧹 [MEM0] Очистка памяти по запросу: {query}")
        except Exception as e:
            print(Fore.RED + f"❌ [MEM0] Ошибка удаления: {e}")

    def get_all_memories(self):
        """
        Возвращает абсолютно все записи.
        """
        if not self.memory:
            return []
            
        try:
            return self.memory.get_all(user_id=self.user_id)
        except Exception as e:
            print(Fore.RED + f"❌ [MEM0] Ошибка получения всей базы: {e}")
            return []

    def reset_entire_memory(self, force=False):
        """
        Полное уничтожение базы данных пользователя.
        Убрано ожидание ввода (input), так как это вешает автономного агента.
        """
        if not self.memory:
            print(Fore.RED + "❌ [MEM0] База данных не подключена.")
            return
            
        if force:
            try:
                self.memory.reset()
                print(Fore.GREEN + "🧹 [MEM0] База данных полностью очищена.")
            except Exception as e:
                print(Fore.RED + f"❌ [MEM0] Ошибка сброса: {e}")
        else:
            print(Fore.YELLOW + "⚠️ [MEM0] Для сброса памяти используйте параметр force=True.")