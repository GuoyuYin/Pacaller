# syscall_gen/type_mapper.py
from typing import Dict

class TypeMapper:
    """
    Maps C-like kernel types to their Syzlang equivalents.
    This is a simplified mapping.
    """
    def __init__(self):
        self.mapping: Dict[str, str] = {
            "__u8": "int8",
            "__s8": "int8",
            "u8": "int8",
            "s8": "int8",
            "char": "int8",
            
            "__u16": "int16",
            "__s16": "int16",
            "u16": "int16",
            "s16": "int16",
            "short": "int16",

            "__u32": "int32",
            "__s32": "int32",
            "u32": "int32",
            "s32": "int32",
            "int": "int32",
            "unsigned int": "int32",

            "__u64": "int64",
            "__s64": "int64",
            "u64": "int64",
            "s64": "int64",
            "long": "int64",
            "unsigned long": "int64",
            "size_t": "intptr",
            
            "void*": "ptr",
            "void *": "ptr",
            "char*": "string",
            "char *": "string",
            "const char*": "string",
            "const char *": "string",
            
            "sctp_assoc_t": "int32", # Example of a known typedef
        }

    def to_syz_type(self, c_type: str) -> str:
        """
        Converts a C type string into a Syzlang type string.
        Handles pointers and basic types.
        """
        c_type = c_type.strip()
        is_pointer = c_type.endswith('*')
        
        base_type = c_type.replace('*', '').strip()
        
        # Direct mapping
        if base_type in self.mapping:
            syz_base = self.mapping[base_type]
        else:
            # Assume it's a custom struct/resource type
            syz_base = base_type
            
        if is_pointer:
            # Simple heuristic: if not a known ptr type like string, assume ptr[in, type]
            if syz_base in ["ptr", "string"]:
                return syz_base
            return f"ptr[in, {syz_base}]"
        
        return syz_base