#ifndef AST_VISITOR_HPP
#define AST_VISITOR_HPP

#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/Tooling.h"

#include <iostream>
#include <vector>
#include <string>

struct FieldInfo {
    std::string name;
    std::string type;
};

struct StructInfo {
    std::string name;
    std::vector<FieldInfo> fields;
};

struct TypedefInfo {
    std::string name;
    std::string underlying_type;
};

class PacallerASTVisitor : public clang::RecursiveASTVisitor<PacallerASTVisitor> {
public:
    explicit PacallerASTVisitor(clang::ASTContext *Context) : Context(Context) {}

    bool VisitRecordDecl(clang::RecordDecl *Declaration);
    bool VisitTypedefNameDecl(clang::TypedefNameDecl *Declaration);

    void printResults();

private:
    clang::ASTContext *Context;
    std::vector<StructInfo> structs;
    std::vector<TypedefInfo> typedefs;
};

class PacallerASTConsumer : public clang::ASTConsumer {
public:
    explicit PacallerASTConsumer(clang::ASTContext *Context) : Visitor(Context) {}

    void HandleTranslationUnit(clang::ASTContext &Context) override {
        Visitor.TraverseDecl(Context.getTranslationUnitDecl());
        Visitor.printResults();
    }

private:
    PacallerASTVisitor Visitor;
};

class PacallerFrontendAction : public clang::ASTFrontendAction {
public:
    std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(clang::CompilerInstance &CI,
                                                          llvm::StringRef InFile) override {
        return std::make_unique<PacallerASTConsumer>(&CI.getASTContext());
    }
};

class PacallerASTConsumerFactory : public clang::tooling::FrontendActionFactory {
public:
    std::unique_ptr<clang::FrontendAction> create() override {
        return std::make_unique<PacallerFrontendAction>();
    }
};

#endif // AST_VISITOR_HPP