# packet_gen/mutation_library.py
from typing import List

def get_heuristic_mutations(field_name: str, field_type: str) -> List[str]:
    """
    Suggests a list of mutation strategies based on common field names and types.
    This corresponds to selecting mutation operators from set M in Algorithm 2.
    """
    mutations = []
    
    # Heuristics based on field name
    if "checksum" in field_name or "csum" in field_name:
        mutations.extend(["invalid_checksum", "zero_checksum", "random_checksum"])
    
    if "len" in field_name or "length" in field_name:
        mutations.extend(["zero_length", "small_length", "large_length", "mismatched_length"])

    if "flags" in field_name:
        mutations.extend(["zero_flags", "all_flags_set", "random_flags", "invalid_flag_combination"])
    
    if "port" in field_name:
        mutations.extend(["zero_port", "well_known_port", "ephemeral_port", "max_port"])
        
    if "seq" in field_name or "ack" in field_name:
        mutations.extend(["random_seq", "zero_seq", "max_seq"])

    # Heuristics based on field type
    if "int" in field_type:
        mutations.extend(["boundary_value_min", "boundary_value_max", "random_int"])

    return list(set(mutations)) # Return unique mutations