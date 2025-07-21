# syscall_gen/generator.py
from pathlib import Path
from typing import List
from collections import defaultdict

from common.ir import IntermediateRepresentation, Struct
from common.utils import write_file
from common.logger import setup_logger
from config import KERNEL_NET_DIRS, SYZ_FILE_EXTENSION

from .dependency_resolver import DependencyResolver
from .type_mapper import TypeMapper
from .templates import get_base_syz_template, get_struct_template, get_syscall_template

class SyscallSpecificationGenerator:
    """
    Generates Syzlang (.syz) files from the Intermediate Representation.
    It resolves dependencies, maps types, and uses templates to format
    the output for different network subsystems.
    """
    def __init__(self, ir: IntermediateRepresentation):
        self.ir = ir
        self.type_mapper = TypeMapper()
        self.logger = setup_logger()

    def _group_resources_by_subsystem(self):
        groups = defaultdict(list)
        for name, resource in self.ir.resources.items():
            found = False
            for dir_prefix in KERNEL_NET_DIRS:
                if resource.origin_file.startswith(dir_prefix):
                    groups[dir_prefix].append(name)
                    found = True
                    break
            if not found:
                groups["misc"].append(name)
        return groups

    def _generate_struct_definition(self, struct: Struct) -> str:
        fields_str = []
        for field in struct.fields:
            syz_type = self.type_mapper.to_syz_type(field.type)
            fields_str.append(f"\t{field.name}\t{syz_type}")
        
        return get_struct_template().format(
            struct_name=struct.name,
            fields="\n".join(fields_str)
        )

    def generate_specifications(self, output_dir: Path):
        """
        Main method to generate all specification files.
        """
        resource_groups = self._group_resources_by_subsystem()
        
        for group_name, resource_names in resource_groups.items():
            self.logger.info(f"Processing subsystem: {group_name}")
            
            group_structs = {name: self.ir.structs[name] for name in resource_names if name in self.ir.structs}
            group_other_res = {name: self.ir.resources[name] for name in resource_names if name not in self.ir.structs}

            if not group_structs:
                self.logger.debug(f"No structs to process for group {group_name}. Skipping.")
                continue

            resolver = DependencyResolver(group_structs, group_other_res)
            sorted_struct_names = resolver.resolve()
            
            syz_content = [get_base_syz_template()]
            
            for struct_name in sorted_struct_names:
                struct_def = self.ir.structs.get(struct_name)
                if struct_def:
                    syz_content.append(self._generate_struct_definition(struct_def))
            
            # Add some example syscalls using these structs
            # This part is highly heuristic in a real implementation
            if "sctp" in group_name:
                sctp_info = self.ir.structs.get("sctp_sndrcvinfo")
                if sctp_info:
                    syz_content.append(get_syscall_template().format(
                        syscall_name="setsockopt$sctp_info",
                        args=f"fd sock, level const[IPPROTO_SCTP], optname const[SCTP_SNDRCV], optval ptr[in, sctp_sndrcvinfo], optlen len[optval]"
                    ))

            file_name = group_name.replace('/', '_') + SYZ_FILE_EXTENSION
            output_path = output_dir / file_name
            
            write_file(output_path, "\n\n".join(syz_content))
            self.logger.info(f"Generated spec file: {output_path}")