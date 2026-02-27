import ast
import inspect
import os
import networkx as nx
from typing import Dict, List, Tuple, Any

class CodeAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.ast_cache = {}
        self.dependency_graph = nx.DiGraph()
        self.modification_points = {}
    
    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def analyze_structure(self) -> Dict[str, Any]:
        self._build_ast_cache()
        self._build_dependency_graph()
        self._identify_modification_points()
        return {
            'dependency_graph': self.dependency_graph,
            'modification_points': self.modification_points
        }
    
    def _build_ast_cache(self):
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        content = self.read_file(file_path)
                        self.ast_cache[file_path] = ast.parse(content)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    
    def _build_dependency_graph(self):
        for file_path, tree in self.ast_cache.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependency_graph.add_edge(file_path, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    self.dependency_graph.add_edge(file_path, node.module)
    
    def _identify_modification_points(self):
        for file_path, tree in self.ast_cache.items():
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    metrics = self._calculate_metrics(node, file_path)
                    self.modification_points[node.name] = {
                        'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                        'file': file_path,
                        'metrics': metrics
                    }
    
    def _calculate_metrics(self, node: ast.AST, file_path: str) -> Dict[str, Any]:
        return {
            'lines_of_code': len(ast.get_source_segment(self.read_file(file_path), node).split('\n')),
            'dependencies': self._get_dependencies(node),
            'complexity': self._calculate_complexity(node)
        }
    
    def _get_dependencies(self, node: ast.AST) -> List[str]:
        dependencies = []
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Name):
                dependencies.append(sub_node.id)
        return list(set(dependencies))
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for sub_node in ast.walk(node):
            if isinstance(sub_node, (ast.If, ast.For, ast.While, ast.With, ast.ExceptHandler)):
                complexity += 1
        return complexity

def main():
    analyzer = CodeAnalyzer('.')
    result = analyzer.analyze_structure()
    print("Dependency Graph:", result['dependency_graph'].edges)
    print("Modification Points:", result['modification_points'])

if __name__ == "__main__":
    main()