# packet_gen/templates.py
import json
from typing import Dict, Any

def format_packet_model_json(model_data: Dict[str, Any]) -> str:
    """
    Formats the packet model data into a nicely indented JSON string.
    """
    return json.dumps(model_data, indent=2)