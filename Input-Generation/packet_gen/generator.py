# packet_gen/generator.py
import json
from pathlib import Path
from collections import defaultdict

from common.ir import IntermediateRepresentation, Struct
from common.utils import write_file
from common.logger import setup_logger
from config import PKT_MODEL_FILE_EXTENSION

from .mutation_library import get_heuristic_mutations
from .templates import format_packet_model_json

class PacketModelGenerator:
    """
    Generates abstract packet models from struct definitions in the IR.
    Each model includes a base structure and a list of potential mutation targets.
    """
    def __init__(self, ir: IntermediateRepresentation):
        self.ir = ir
        self.logger = setup_logger()

    def _create_base_model(self, struct_def: Struct) -> dict:
        """Creates a hierarchical dictionary representing the base packet structure."""
        model = {"name": struct_def.name, "fields": []}
        for field in struct_def.fields:
            # In a real model, we might resolve field types to sizes
            model["fields"].append({"name": field.name, "type": field.type})
        return model

    def _identify_mutation_targets(self, struct_def: Struct) -> list:
        """Identifies potential mutation targets based on field names and types."""
        targets = []
        for field in struct_def.fields:
            mutations = get_heuristic_mutations(field.name, field.type)
            if mutations:
                targets.append({
                    "field_name": field.name,
                    "mutations": mutations
                })
        return targets

    def generate_models(self, output_dir: Path):
        """
        Main method to generate all packet model files.
        """
        # We focus on structs that are likely to be packet headers.
        # This is a heuristic; a real system might use naming conventions
        # like `_hdr` or `_header`.
        
        packet_header_candidates = [s for s in self.ir.structs.values() if 'hdr' in s.name or 'header' in s.name]
        
        if not packet_header_candidates:
            self.logger.warning("No potential packet headers found based on naming conventions. Generating for all structs.")
            packet_header_candidates = list(self.ir.structs.values())

        for struct_def in packet_header_candidates:
            self.logger.info(f"Generating packet model for: {struct_def.name}")
            
            base_model = self._create_base_model(struct_def)
            mutation_targets = self._identify_mutation_targets(struct_def)
            
            full_model = {
                "base_model": base_model,
                "mutation_targets": mutation_targets
            }
            
            file_name = struct_def.name + PKT_MODEL_FILE_EXTENSION
            output_path = output_dir / file_name
            
            json_content = format_packet_model_json(full_model)
            write_file(output_path, json_content)
            self.logger.info(f"Generated packet model file: {output_path}")