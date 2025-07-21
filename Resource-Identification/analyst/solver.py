class KconfigSolver:
    def __init__(self, options, graph):
        self.options = options
        self.graph = graph

    def resolve_dependencies(self, initial_targets, max_iterations=5000):
        """
        Resolves the dependency graph to find all required configs.
        This is a simplified solver that handles direct dependencies and selections.
        """
        required = set(initial_targets)
        worklist = set(initial_targets)
        
        iterations = 0
        while worklist and iterations < max_iterations:
            iterations += 1
            current_config = worklist.pop()

            if current_config not in self.graph:
                continue

            # Add all dependencies to the worklist
            for dep in self.graph[current_config].get('deps', set()):
                if dep not in required:
                    required.add(dep)
                    worklist.add(dep)
            
            # If we enable a config, we must also enable what it selects
            for sel in self.graph[current_config].get('selects', set()):
                if sel not in required:
                    required.add(sel)
                    worklist.add(sel)

        if iterations >= max_iterations:
            print(f"Warning: Dependency resolution reached max iterations ({max_iterations}). Result may be incomplete.")
            
        return required