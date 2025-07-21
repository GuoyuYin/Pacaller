# generate_all.py
import argparse
import json
import os
from pathlib import Path

from common.logger import setup_logger
from common.ir import IntermediateRepresentation
from common.utils import ensure_dir, load_json

from syscall_gen.generator import SyscallSpecificationGenerator
from packet_gen.generator import PacketModelGenerator

def main():
    """
    Main orchestration script for the Fuzzing Input Generation stage.
    This script loads the extracted network resources (IR) and invokes
    the syscall specification generator and the packet model generator.
    """
    parser = argparse.ArgumentParser(
        description="Generate Syzlang specifications and Packet Models from Kernel IR."
    )
    parser.add_argument(
        "--ir-path",
        type=str,
        required=True,
        help="Path to the directory containing the structured IR JSON files."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="generated_inputs",
        help="Directory to save the generated Syzlang and Packet Model files."
    )
    args = parser.parse_args()

    logger = setup_logger()
    logger.info("Starting Fuzzing Input Generation stage for Pacaller.")
    
    ir_path = Path(args.ir_path)
    if not ir_path.is_dir():
        logger.error(f"IR path '{ir_path}' is not a valid directory.")
        return

    output_dir = Path(args.output_dir)
    syscall_output_dir = output_dir / "syscall_specs"
    packet_output_dir = output_dir / "packet_models"
    
    ensure_dir(syscall_output_dir)
    ensure_dir(packet_output_dir)

    logger.info(f"Loading all IR files from: {ir_path}")
    
    all_ir_data = []
    for json_file in sorted(ir_path.glob("*.json")):
        logger.debug(f"Loading IR file: {json_file.name}")
        data = load_json(json_file)
        if data:
            all_ir_data.extend(data)

    if not all_ir_data:
        logger.error("No valid IR data loaded. Aborting.")
        return

    ir = IntermediateRepresentation(all_ir_data)
    logger.info(f"Successfully loaded and parsed {len(ir.resources)} resource definitions.")
    
    # --- Syscall Specification Generation ---
    logger.info("Starting Syscall Specification Generation...")
    syscall_generator = SyscallSpecificationGenerator(ir)
    syscall_generator.generate_specifications(syscall_output_dir)
    logger.info(f"Syscall specifications generated in: {syscall_output_dir}")

    # --- Packet Model Generation ---
    logger.info("Starting Packet Model Generation...")
    packet_generator = PacketModelGenerator(ir)
    packet_generator.generate_models(packet_output_dir)
    logger.info(f"Packet models generated in: {packet_output_dir}")
    
    logger.info("Fuzzing Input Generation stage completed successfully.")


if __name__ == "__main__":
    main()