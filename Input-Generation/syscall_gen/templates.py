# syscall_gen/templates.py

def get_base_syz_template() -> str:
    """Returns the basic includes for a Syzlang file."""
    return "include <net/socket.h>"

def get_struct_template() -> str:
    """Template for a Syzlang struct definition."""
    return """\
{struct_name} {{
{fields}
}}"""

def get_syscall_template() -> str:
    """Template for a Syzlang syscall definition."""
    return "{syscall_name}({args})"