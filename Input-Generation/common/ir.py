# common/ir.py
from typing import List, Dict, Any, Optional

class Resource:
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name")
        self.resource_type = data.get("type")
        self.origin_file = data.get("origin_file", "unknown")

class TypeDef(Resource):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.base_type = data.get("base_type")

    def __repr__(self):
        return f"TypeDef(name='{self.name}', base_type='{self.base_type}')"

class Field:
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name")
        self.type = data.get("type")
        self.is_pointer = "*" in self.type
        self.is_array = "[]" in self.type
    
    def __repr__(self):
        return f"Field(name='{self.name}', type='{self.type}')"

class Struct(Resource):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.fields = [Field(f) for f in data.get("fields", [])]
        self.dependencies = self._find_dependencies()

    def _find_dependencies(self):
        deps = set()
        for field in self.fields:
            clean_type = field.type.replace('*', '').replace('[]', '').strip()
            # We assume custom types are structs or typedefs
            # This is a simplification; a real system might need more checks.
            if ' ' not in clean_type and clean_type != self.name:
                deps.add(clean_type)
        return list(deps)

    def __repr__(self):
        return f"Struct(name='{self.name}', fields={len(self.fields)})"

class Constant(Resource):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.value = data.get("value")

    def __repr__(self) -> str:
        return f"Constant(name='{self.name}', value='{self.value}')"

class IntermediateRepresentation:
    def __init__(self, raw_data: List[Dict[str, Any]]):
        self.raw_data = raw_data
        self.resources: Dict[str, Resource] = {}
        self.structs: Dict[str, Struct] = {}
        self.typedefs: Dict[str, TypeDef] = {}
        self.constants: Dict[str, Constant] = {}
        self._parse()

    def _parse(self):
        for item in self.raw_data:
            res_type = item.get("type")
            name = item.get("name")
            if not name:
                continue

            if res_type == "struct":
                resource = Struct(item)
                self.structs[name] = resource
            elif res_type == "typedef":
                resource = TypeDef(item)
                self.typedefs[name] = resource
            elif res_type == "const":
                resource = Constant(item)
                self.constants[name] = resource
            else:
                continue
            
            self.resources[name] = resource
    
    def get_resource(self, name: str) -> Optional[Resource]:
        return self.resources.get(name)