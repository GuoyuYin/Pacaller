# config.py

# Global configurations and constants for the generation process.

# Defines the kernel directories that are parsed in the resource identification stage.
# This is used to logically group resources.
KERNEL_NET_DIRS = [
    "net/ipv4",
    "net/ipv6",
    "net/sctp",
    "net/dccp",
    "net/netfilter",
    "drivers/net",
]

# Default syscalls to be considered for attaching generated network structures.
# The generator will look for these syscalls to create specialized versions.
TARGET_SYSCALLS = {
    "setsockopt",
    "getsockopt",
    "sendmsg",
    "recvmsg",
    "sendto",
    "recvfrom",
}

# The extension for generated syscall specification files.
SYZ_FILE_EXTENSION = ".syz"

# The extension for generated packet model files.
PKT_MODEL_FILE_EXTENSION = ".json"

# Logging level for the application. Can be "INFO", "DEBUG", "WARNING", "ERROR".
LOG_LEVEL = "INFO"