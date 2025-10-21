#include "ast_visitor.hpp"
#include "clang/AST/Decl.h"

bool PacallerASTVisitor::VisitRecordDecl(clang::RecordDecl *Declaration) {
    if (Declaration->isThisDeclarationADefinition() && Declaration->isStruct()) {
        std::string structName = Declaration->getNameAsString();
        if (structName.empty()) {
            return true; // Skip anonymous structs for now
        }

        StructInfo currentStruct;
        currentStruct.name = structName;

        for (const auto *Field : Declaration->fields()) {
            FieldInfo field;
            field.name = Field->getNameAsString();
            clang::QualType q_type = Field->getType();
            field.type = q_type.getAsString();
            currentStruct.fields.push_back(field);
        }
        structs.push_back(currentStruct);
    }
    return true;
}

bool PacallerASTVisitor::VisitTypedefNameDecl(clang::TypedefNameDecl *Declaration) {
    TypedefInfo currentTypedef;
    currentTypedef.name = Declaration->getNameAsString();
    
    clang::QualType underlyingType = Declaration->getUnderlyingType();
    currentTypedef.underlying_type = underlyingType.getAsString();

    typedefs.push_back(currentTypedef);
    return true;
}

void PacallerASTVisitor::printResults() {
    std::cout << "{\n";
    std::cout << "  \"structs\": [\n";
    for (size_t i = 0; i < structs.size(); ++i) {
        const auto& s = structs[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << s.name << "\",\n";
        std::cout << "      \"fields\": [\n";
        for (size_t j = 0; j < s.fields.size(); ++j) {
            const auto& f = s.fields[j];
            std::cout << "        {\n";
            std::cout << "          \"name\": \"" << f.name << "\",\n";
            std::cout << "          \"type\": \"" << f.type << "\"\n";
            std::cout << "        }" << (j == s.fields.size() - 1 ? "" : ",") << "\n";
        }
        std::cout << "      ]\n";
        std::cout << "    }" << (i == structs.size() - 1 ? "" : ",") << "\n";
    }
    std::cout << "  ],\n";
    
    std::cout << "  \"typedefs\": [\n";
    for (size_t i = 0; i < typedefs.size(); ++i) {
        const auto& t = typedefs[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << t.name << "\",\n";
        std::cout << "      \"base_type\": \"" << t.underlying_type << "\"\n";
        std::cout << "    }" << (i == typedefs.size() - 1 ? "" : ",") << "\n";
    }
    std::cout << "  ]\n";
    std::cout << "}\n";
}```

#### **文件 7: `resource-identification/config_analyzer/main_analyzer.py`**

```python
import argparse
import os
import sys
from makefile_parser import MakefileParser
from kconfig_parser.parser import KconfigParser
from kconfig_parser.solver import KconfigSolver

def main():
    parser = argparse.ArgumentParser(description="Pacaller Static Configuration Analyzer")
    parser.add_argument('--kernel-dir', required=True, help='Path to the Linux kernel source directory.')
    parser.add_argument('--target-dirs', required=True, nargs='+', help='Target directories to analyze (e.g., net drivers/net).')
    parser.add_argument('--output', required=True, help='Output path for the generated .config fragment.')

    args = parser.parse_args()

    if not os.path.isdir(args.kernel_dir):
        print(f"Error: Kernel directory not found at {args.kernel_dir}", file=sys.stderr)
        sys.exit(1)

    print("[+] Starting Makefile analysis...")
    mf_parser = MakefileParser(args.kernel_dir)
    target_configs = mf_parser.get_configs_from_dirs(args.target_dirs)
    print(f"[+] Found {len(target_configs)} initial CONFIG options from Makefiles.")

    print("[+] Starting Kconfig parsing...")
    kc_parser = KconfigParser(args.kernel_dir)
    kc_parser.parse()
    print(f"[+] Parsed {len(kc_parser.options)} Kconfig options.")

    print("[+] Resolving dependencies...")
    solver = KconfigSolver(kc_parser.options, kc_parser.graph)
    required_configs = solver.resolve_dependencies(target_configs)
    print(f"[+] Resolved to {len(required_configs)} total required CONFIG options.")

    print(f"[+] Writing final configuration to {args.output}...")
    with open(args.output, 'w') as f:
        f.write("# Pacaller generated kernel configuration\n")
        f.write("# This config fragment enables network-related features for fuzzing.\n\n")
        for config in sorted(required_configs):
            # We enable them as modules 'm' where possible, 'y' otherwise
            option = kc_parser.options.get(config)
            if option and option.type in ['tristate']:
                 f.write(f"{config}=m\n")
            else:
                 f.write(f"{config}=y\n")
    
    print("[+] Done.")

if __name__ == "__main__":
    main()