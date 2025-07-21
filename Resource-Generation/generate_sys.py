import os

# 模拟 headerparser.py 的输出，包含更多不常见协议类型
header_output = {
    "udphdr": "udphdr {\n  source be16 #(__be16)\n  dest be16 #(__be16)\n  len be16 #(__be16)\n  check sum16 #(__sum16)\n}",
    "tcphdr": "tcphdr {\n  source be16 #(__be16)\n  dest be16 #(__be16)\n  seq be32 #(__be32)\n  ack_seq be32 #(__be32)\n  doff int8 #(__u8)\n  flags int8 #(__u8)\n  window be16 #(__be16)\n  check sum16 #(__sum16)\n  urg_ptr be16 #(__be16)\n}",
    "icmphdr": "icmphdr {\n  type int8 #(__u8)\n  code int8 #(__u8)\n  checksum sum16 #(__sum16)\n  id be16 #(__be16)\n  sequence be16 #(__be16)\n}",
    "dccp_hdr": "dccp_hdr {\n  dccph_type int8 #(__u8)\n  dccph_ccval int8 #(__u8)\n  dccph_cscov int8 #(__u8)\n  dccph_seq be16 #(__u16)\n  dccph_sport be16 #(__u16)\n  dccph_dport be16 #(__u16)\n  dccph_x be32 #(__u32)\n}",
    "sctphdr": "sctphdr {\n  source be16 #(__u16)\n  dest be16 #(__u16)\n  vtag be32 #(__u32)\n  checksum be32 #(__u32)\n}",
    "igmphdr": "igmphdr {\n  type int8 #(__u8)\n  code int8 #(__u8)\n  csum sum16 #(__sum16)\n  group be32 #(__be32)\n}"
}

# 已知协议的系统调用模板
protocol_templates = {
    "udp": {
        "resources": "resource sock_{protocol}[sock]",
        "socket": "socket${protocol}(domain const[AF_INET], type const[SOCK_DGRAM], proto const[IPPROTO_UDP]) sock_{protocol}",
        "send": "sendto${protocol}(fd sock_{protocol}, buf ptr[in, array[int8]], len len[buf], flags int32, addr ptr[in, sockaddr_in], addrlen const[16]) int32",
        "recv": "recvfrom${protocol}(fd sock_{protocol}, buf ptr[out, array[int8]], len len[buf], flags int32, addr ptr[out, sockaddr_in], addrlen ptr[inout, int32]) int32"
    },
    "tcp": {
        "resources": "resource sock_{protocol}[sock]",
        "socket": "socket${protocol}(domain const[AF_INET], type const[SOCK_STREAM], proto const[IPPROTO_TCP]) sock_{protocol}",
        "connect": "connect${protocol}(fd sock_{protocol}, addr ptr[in, sockaddr_in], addrlen const[16]) int32",
        "accept": "accept${protocol}(fd sock_{protocol}, addr ptr[out, sockaddr_in], addrlen ptr[inout, int32]) sock_{protocol}",
        "send": "send${protocol}(fd sock_{protocol}, buf ptr[in, array[int8]], len len[buf], flags int32) int32",
        "recv": "recv${protocol}(fd sock_{protocol}, buf ptr[out, array[int8]], len len[buf], flags int32) int32"
    }
}

# 通用协议的系统调用模板（动态使用协议名）
generic_template = {
    "resources": "resource sock_{protocol}[sock]",
    "socket": "socket${protocol}(domain const[AF_INET], type const[SOCK_RAW], proto int32) sock_{protocol}",
    "send": "sendto${protocol}(fd sock_{protocol}, buf ptr[in, array[int8]], len len[buf], flags int32, addr ptr[in, sockaddr_in], addrlen const[16]) int32",
    "recv": "recvfrom${protocol}(fd sock_{protocol}, buf ptr[out, array[int8]], len len[buf], flags int32, addr ptr[out, sockaddr_in], addrlen ptr[inout, int32]) int32"
}

# 预定义类型和资源
predefined_types = """
resource fd[int32]
resource sock[fd]
type sockaddr_in {
  family    int16
  port      be16
  addr      int32
  pad       array[int8, 8]
}
type sock_type[int32] {
  SOCK_STREAM   1
  SOCK_DGRAM    2
}
"""

def extract_protocol_name(struct_name):
    """
    从结构体名称中提取协议名称。
    参数：
    - struct_name: 结构体名称（如 'udphdr'）
    返回：
    - 提取出的协议名（如 'udp' 或 'icmp'）
    """
    struct_name = struct_name.lower()
    if "udp" in struct_name:
        return "udp"
    elif "tcp" in struct_name:
        return "tcp"
    else:
        return struct_name.replace("hdr", "")  # 对于未知协议，去掉 'hdr' 后缀

def generate_syzlang_file(struct_name, struct_def):
    """
    为指定协议生成 Syzlang 描述文件。
    参数：
    - struct_name: 结构体名称（如 'udphdr'）
    - struct_def: 结构体定义（来自 headerparser.py 的输出）
    """
    output = []

    # 添加预定义类型和资源
    output.append(predefined_types)

    # 添加结构体定义
    output.append(struct_def)

    # 提取协议名称
    protocol = extract_protocol_name(struct_name)

    # 选择系统调用模板
    if protocol in protocol_templates:
        template = protocol_templates[protocol]
    else:
        template = generic_template

    # 使用协议名生成资源和系统调用
    resources = template["resources"].format(protocol=protocol)
    output.append(resources)

    if "socket" in template:
        socket_call = template["socket"].format(protocol=protocol)
        output.append(socket_call)
    if "connect" in template:
        connect_call = template["connect"].format(protocol=protocol)
        output.append(connect_call)
    if "accept" in template:
        accept_call = template["accept"].format(protocol=protocol)
        output.append(accept_call)
    if "send" in template:
        send_call = template["send"].format(protocol=protocol)
        output.append(send_call)
    if "recv" in template:
        recv_call = template["recv"].format(protocol=protocol)
        output.append(recv_call)

    # 写入文件
    filename = f"{struct_name}_syscalls.txt"
    with open(filename, "w") as f:
        f.write("\n".join(output) + "\n")
    print(f"已生成系统调用描述文件：{filename}")

# 主逻辑：为每个协议生成描述文件
for struct_name, struct_def in header_output.items():
    generate_syzlang_file(struct_name, struct_def)