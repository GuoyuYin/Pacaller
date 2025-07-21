# Pacaller: Packet-Syscall Ensemble Fuzzing for Linux Kernel Network Stack

Pacaller is a packet-syscall ensemble fuzzer designed for the Linux kernel network stack. It addresses the unique challenges of network stack testing by integrating three key techniques. First, Pacaller performs automated configuration analysis to enhance code reachability into network-specific modules. Second, it systematically extracts network resources from the kernel source code to generate protocol-aware syscall specifications and packet models. Finally, Pacaller employs an ensemble fuzzing methodology that coordinates syscall execution with packet injection to test their complex interplay. This integrated approach enables Pacaller to uncover deep vulnerabilities within the network stack that are inaccessible to conventional fuzzing approaches.

## How to Use Pacaller

To build Pacaller, run the following command in the root directory:

```bash
# First, execute the syz-env script to install all required dependencies,
# such as the Go toolchain and C cross-compilers for the fuzzing target.
./tools/syz-env

# Next, configure Git to trust the source directory. This step resolves potential
# Git failures caused by file ownership mismatches, which can occur
# in environments like Docker containers.
git config --global --add safe.directory /syzkaller/gopath/src/github.com/google/syzkaller

# Then, set the Go proxy. For users in certain regions, using a proxy can
# significantly accelerate the download of Go modules and prevent

# build interruptions due to network connectivity issues.
export GOPROXY=https://goproxy.cn

# Finally, run make to compile the entire project in parallel,
# generating the necessary executable files.
make -j
```

To start the fuzzing process, run:

```bash
./bin/syz-manager -config my_config.json
```

Here, `my_config.json` is the configuration file for the fuzzer. It must specify critical paths and settings for the target kernel, guest VM, and fuzzing instance. An example configuration is shown below:

```json
{
    "target": "linux/amd64",
    "http": "127.0.0.1:56724",
    "workdir": "/path/to/workdir",
    "kernel_obj": "/path/to/linux",
    "image": "/path/to/bullseye.img",
    "sshkey": "/path/to/bullseye.id_rsa",
    "syzkaller": "/path/to/Pacaller",
    "procs": 8,
    "type": "qemu",
    "cover": true,
    "vm": {
            "count": 8,
            "kernel": "/path/to/bzImage",
            "cpu": 4,
            "mem": 4096,
            "cmdline": "net.ifnames=0"
    }
}
```