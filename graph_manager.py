import json
import os
import shutil
from datetime import datetime
from colorama import Fore

class EntityGraph:
    def __init__(self, storage="knowledge_graph.json"):
        """
        Инициализация графа знаний проекта.
        :param storage: Путь к файлу хранения данных.
        """
        self.storage = storage
        # Структура: {"nodes": {name: data}, "edges": [{"from": a, "to": b, "type": t}]}
        self.data = self._load()
        
        # Если загрузка вернула None (ошибка файла), инициализируем пустые структуры, но ставим флаг
        self.nodes = self.data.get("nodes", {}) if self.data else {}
        self.edges = self.data.get("edges", []) if self.data else []

    def _load(self):
        """Загружает граф из файла с защитой от повреждений."""
        if os.path.exists(self.storage):
            try:
                # Если файл пустой (0 байт), сразу возвращаем базовую структуру
                if os.path.getsize(self.storage) == 0:
                     return {"nodes": {}, "edges": []}
                     
                with open(self.storage, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if "nodes" in content and "edges" in content:
                        return content
            except json.JSONDecodeError as e:
                # ФАЙЛ ПОВРЕЖДЕН: Делаем бэкап перед тем, как вернуть пустой граф
                backup_name = f"{self.storage}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.storage, backup_name)
                print(Fore.RED + f"⚠️ [GRAPH] Файл графа поврежден! Сделан бэкап: {backup_name}")
                print(Fore.RED + f"⚠️ [GRAPH] Начинаем с чистого листа.")
                return {"nodes": {}, "edges": []}
            except Exception as e:
                print(Fore.RED + f"⚠️ [GRAPH] Системная ошибка чтения графа: {e}")
                return {"nodes": {}, "edges": []}
                
        # Если файла нет вообще
        return {"nodes": {}, "edges": []}

    def update_node(self, name, node_type="file", status="active", metadata=None):
        """
        Создает или обновляет узел в графе.
        :param name: Имя сущности (например, 'genesis.py').
        :param node_type: Тип (file, class, function, task).
        :param status: Текущее состояние (active, broken, deprecated).
        :param metadata: Дополнительные данные (автор, описание, hash).
        """
        # Если обновляем существующий, сливаем метаданные, а не затираем
        existing_meta = self.nodes.get(name, {}).get("metadata", {})
        if metadata:
            existing_meta.update(metadata)
            
        self.nodes[name] = {
            "type": node_type,
            "status": status,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": existing_meta
        }
        self._save()

    def add_relation(self, source, target, rel_type="depends_on"):
        """
        Создает направленную связь между узлами.
        """
        edge = {"from": source, "to": target, "type": rel_type}
        if edge not in self.edges:
            self.edges.append(edge)
            self._save()
            print(Fore.BLUE + f"🔗 [GRAPH] Связь установлена: {source} --({rel_type})--> {target}")

    def remove_node(self, name):
        """Удаляет узел и все связанные с ним ребра."""
        if name in self.nodes:
            del self.nodes[name]
            self.edges = [e for e in self.edges if e["from"] != name and e["to"] != name]
            self._save()
            return True
        return False

    def get_all_statuses(self):
        """Возвращает краткую сводку по всем узлам для промпта LLM."""
        if not self.nodes:
            return "Граф пуст."
        return ", ".join([f"{name}:[{data['status']}]" for name, data in self.nodes.items()])

    def get_dependencies(self, node_name):
        """Возвращает список того, от чего зависит данный узел."""
        deps = [e["to"] for e in self.edges if e["from"] == node_name]
        return deps

    def get_impact_zone(self, node_name):
        """
        Анализ влияния: что сломается, если изменить этот узел?
        """
        impacted = [e["from"] for e in self.edges if e["to"] == node_name]
        return impacted

    def find_isolated_nodes(self):
        """Находит модули, которые никем не используются и ни от чего не зависят."""
        connected = set()
        for e in self.edges:
            connected.add(e["from"])
            connected.add(e["to"])
        return [n for n in self.nodes if n not in connected]

    def get_project_map(self):
        """
        Формирует текстовую карту проекта для когнитивного анализа.
        """
        map_str = "🗺️ КАРТА СВЯЗЕЙ GENESIS:\n"
        for node, data in self.nodes.items():
            deps = self.get_dependencies(node)
            dep_str = f" -> зависит от: {', '.join(deps)}" if deps else " (изолирован)"
            map_str += f"- [{data['type'].upper()}] {node} [{data['status']}]{dep_str}\n"
        return map_str

    def _save(self):
        """Атомарная запись графа в JSON с защитой от обрыва записи."""
        try:
            temp_data = {"nodes": self.nodes, "edges": self.edges}
            
            # Пишем во временный файл
            temp_file = self.storage + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(temp_data, f, indent=4, ensure_ascii=False)
                
            # Атомарно переименовываем (заменяем старый)
            os.replace(temp_file, self.storage)
            
        except Exception as e:
            print(Fore.RED + f"❌ Ошибка сохранения графа: {e}")

    def clear(self):
        """Полная очистка данных."""
        self.nodes = {}
        self.edges = []
        self._save()