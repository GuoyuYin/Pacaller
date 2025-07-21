import os
import re

class KconfigOption:
    def __init__(self, name, option_type, file_path):
        self.name = name
        self.type = option_type # bool, tristate, string, etc.
        self.file_path = file_path
        self.dependencies = []
        self.selections = []

class KconfigParser:
    def __init__(self, kernel_dir):
        self.kernel_dir = kernel_dir
        self.options = {} # name -> KconfigOption
        self.graph = {} # name -> { 'deps': set(), 'selects': set() }
        self.arch = "x86" # Assume x86 for simplicity in artifact

        self.re_config = re.compile(r'^\s*(menu)?config\s+([A-Z0-9_]+)\s*$')
        self.re_type = re.compile(r'^\s*(bool|tristate|string|hex|int)\s*.*$')
        self.re_depends = re.compile(r'^\s*depends\s+on\s+(.*)$')
        self.re_select = re.compile(r'^\s*select\s+([A-Z0-9_]+)\s*')
        self.re_source = re.compile(r'^\s*source\s+"?([^"]+)"?\s*')

    def _clean_dep_string(self, dep_str):
        # Simplistic cleaning of a dependency string
        # This is a hard problem in general, we simplify for the artifact
        return [item.strip() for item in re.split(r'\s*&&\s*|\s*\|\|\s*', dep_str) if item.strip().isupper()]

    def parse(self):
        main_kconfig = os.path.join(self.kernel_dir, 'arch', self.arch, 'Kconfig')
        if not os.path.exists(main_kconfig):
            main_kconfig = os.path.join(self.kernel_dir, 'Kconfig') # Fallback for top-level
        
        self._parse_file(main_kconfig, os.path.dirname(main_kconfig))

    def _parse_file(self, file_path, base_dir):
        if not os.path.exists(file_path):
            return

        current_option = None
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Match config definition
                    match_config = self.re_config.match(line)
                    if match_config:
                        name = match_config.group(2)
                        current_option = KconfigOption(name, None, file_path)
                        self.options[name] = current_option
                        self.graph[name] = {'deps': set(), 'selects': set()}
                        continue
                    
                    if not current_option:
                        # Handle sourcing outside of a config block
                        match_source = self.re_source.match(line)
                        if match_source:
                            source_path = os.path.join(base_dir, match_source.group(1))
                            self._parse_file(source_path, os.path.dirname(source_path))
                        continue

                    # Match type
                    match_type = self.re_type.match(line)
                    if match_type and not current_option.type:
                        current_option.type = match_type.group(1)
                    
                    # Match depends on
                    match_depends = self.re_depends.match(line)
                    if match_depends:
                        deps = self._clean_dep_string(match_depends.group(1))
                        current_option.dependencies.extend(deps)
                        self.graph[current_option.name]['deps'].update(deps)

                    # Match select
                    match_select = self.re_select.match(line)
                    if match_select:
                        selection = match_select.group(1)
                        current_option.selections.append(selection)
                        self.graph[current_option.name]['selects'].add(selection)

        except Exception:
            pass