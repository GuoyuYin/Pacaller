# syscall_gen/dependency_resolver.py
from typing import List, Dict
from collections import defaultdict
from common.ir import Struct, Resource
from common.logger import setup_logger

class DependencyResolver:
    """
    Resolves declaration order for structs and other resources based on their
    field dependencies. Implements topological sort.
    """
    def __init__(self, structs: Dict[str, Struct], other_resources: Dict[str, Resource]):
        self.structs = structs
        self.all_resource_names = set(structs.keys()) | set(other_resources.keys())
        self.logger = setup_logger()
        self.graph = defaultdict(list)
        self.visiting = set()
        self.visited = set()
        self.sorted_order = []

    def _build_graph(self):
        for name, struct_def in self.structs.items():
            for dep in struct_def.dependencies:
                # A dependency only matters if it's another struct we are processing
                if dep in self.structs:
                    self.graph[name].append(dep)

    def _dfs(self, node_name: str):
        self.visiting.add(node_name)
        
        for neighbor in self.graph.get(node_name, []):
            if neighbor in self.visiting:
                # This indicates a cyclic dependency. For syscall specs, this
                # can often be broken with forward declarations (e.g., struct foo;).
                # For simplicity here, we log it and move on.
                self.logger.warning(f"Cyclic dependency detected: {node_name} -> {neighbor}")
                continue
            if neighbor not in self.visited:
                self._dfs(neighbor)
                
        self.visiting.remove(node_name)
        self.visited.add(node_name)
        self.sorted_order.append(node_name)

    def resolve(self) -> List[str]:
        """
        Performs a topological sort on the structs to determine the correct
        order of definition.
        
        Returns:
            A list of struct names in an order that respects dependencies.
        """
        self.logger.info("Building struct dependency graph...")
        self._build_graph()
        self.logger.debug(f"Dependency graph: {dict(self.graph)}")

        self.sorted_order = []
        self.visited = set()
        self.visiting = set()

        all_struct_names = sorted(list(self.structs.keys()))

        for name in all_struct_names:
            if name not in self.visited:
                self._dfs(name)
        
        self.logger.info(f"Resolved dependency order for {len(self.sorted_order)} structs.")
        
        # The result of DFS is in reverse topological order, so it's correct for definition.
        return self.sorted_order