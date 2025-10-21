# Pacaller: Packet-Syscall Coordinated Fuzzing for Linux Kernel Network Stack

Pacaller is a packet-syscall coordinated fuzzer designed for the Linux kernel network stack. It addresses the unique challenges of network stack testing by integrating three key techniques. First, Pacaller performs automated configuration analysis to enhance code reachability into network-specific modules. Second, it systematically extracts network resources from the kernel source code to generate protocol-aware syscall specifications and packet models. Finally, Pacaller employs an coordinated fuzzing methodology that coordinates syscall execution with packet injection to test their complex interplay. This integrated approach enables Pacaller to uncover deep vulnerabilities within the network stack that are inaccessible to conventional fuzzing approaches.

## Key Features

-   **Automated Configuration Analysis**
    Pacaller analyzes the kernel build system (`Kconfig` and `Makefile`) to resolve complex dependencies among thousands of configuration options. This process automatically generates an optimized kernel configuration that activates network-related code previously disabled in default builds, thereby maximizing code reachability for fuzzing.

-   **Resource-Driven Input Generation**
    The tool parses kernel C source code to automatically extract critical network entities such as data structures, type definitions, and constants. These extracted resources are then used to generate two core types of fuzzing inputs: accurate, protocol-aware syscall specifications in Syzlang format, and packet models for evaluating packet-handling logic.

-   **Packet-Syscall Coordinated Fuzzing**
    Pacaller employs an coordinated fuzzing methodology that coordinates syscall execution and packet injection through a feedback-driven loop. The mechanism uses runtime information from syscall execution to guide packet generation, and vice versa. A weighted scoring strategy steers the fuzzing process toward network-related code areas, enabling the efficient discovery of vulnerabilities that depend on complex interactions.

## Workflow

The workflow of Pacaller is organized into three main stages, which directly correspond to the process illustrated in Figure 3 of the paper:

1.  **Resource Identification**
    This is the preparatory stage. Pacaller performs two tasks in parallel:
    -   **Network Resource Extraction**: Scans kernel source code in the `net/`, `drivers/net/`, and `include/` directories to parse network-related data structures and constants.
    -   **Static Configuration Analysis**: Analyzes kernel build scripts to determine the minimal set of configurations required to enable target network features.

2.  **Fuzzing Input Generation**
    In this stage, the outputs from the first stage are transformed into artifacts for the fuzzer:
    -   Syscall specifications and packet models are generated from the extracted network resources.
    -   The target kernel is compiled using the generated optimized configuration to prepare a specialized kernel image for fuzzing.

3.  **Coordinated Fuzzing**
    This is the core execution stage. Pacaller operates in a tightly-coupled loop, creating syscall and packet payloads based on the generated specifications and models. These payloads are executed on a prepared VM instance, guided by coverage feedback to efficiently discover crashes.

## How to Use

The entire process is divided into four main steps, from environment setup to launching the fuzzer. Detailed execution commands for each step can be found within the respective working directories.

#### Step 1: Environment Setup and Tool Compilation

Before starting, you need to prepare a base environment for fuzzing. This includes setting up a guest image with a root file system and obtaining the Linux kernel source you wish to test. You can refer to the [official Syzkaller documentation](https://github.com/google/syzkaller/blob/master/docs/linux/setup_ubuntu-host_qemu-vm_x86-64-kernel.md) for this step. After the basic setup is complete, compile the Pacaller project itself.

#### Step 2: Resource Identification and Configuration Analysis

This step corresponds to the **Resource Identification** stage in the paper. You will run the tools within the `Resource-Identification` directory to analyze the kernel source code you prepared. This process will accomplish two key tasks:

1.  **Automated Static Configuration Analysis**: It generates an optimized kernel `.config` file that enables network-related features to enhance code coverage. You must use this configuration to recompile your kernel.
2.  **Network Resource Extraction**: It parses network-related data structures, constants, and type definitions from kernel headers and source files, saving them in a structured intermediate format.

#### Step 3: Fuzzing Input Generation

This step corresponds to the **Fuzzing Input Generation** stage. Once resource extraction is complete, you will run the tools in the `Input-Generation` directory. These tools use the intermediate files from the previous step to produce the final fuzzing inputs:
1.  **Syscall Specifications**: Generates `Syzlang` files that describe network-related syscalls and their complex data structure arguments.
2.  **Packet Models**: Creates grammar-based models of protocol packets, which serve as the foundation for packet injection.

#### Step 4: Launching the Coordinated Fuzzing


With all the preparatory work complete (including the specially compiled kernel, syscall specifications, and packet models), you can now launch the **coordinated fuzzing** engine from the main `pacaller` directory. This will start the core fuzzing loop, which coordinates syscalls and packet injections to begin hunting for vulnerabilities in the target VM.
