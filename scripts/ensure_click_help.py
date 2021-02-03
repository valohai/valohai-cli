import ast
import argparse
import sys


def stringify_name(name: ast.AST):
    if isinstance(name, ast.Attribute):
        return f"{stringify_name(name.value)}.{stringify_name(name.attr)}"
    if isinstance(name, ast.Name):
        return name.id
    if isinstance(name, str):
        return name
    raise NotImplementedError(f"unstringifiable name/node {name} ({type(name)})")


class EnsureClickHelpWalker(ast.NodeVisitor):
    def __init__(self, add_message):
        self.add_message = add_message

    def visit_FunctionDef(self, node):
        for deco in node.decorator_list:
            self.process_decorator(deco)

    def process_decorator(self, deco):
        if isinstance(deco, ast.Call):
            deco_name = stringify_name(deco.func)
            if deco_name in ("click.option",):
                kwargs = {stringify_name(kw.arg): kw.value for kw in deco.keywords}
                if "help" not in kwargs:
                    self.add_message(deco, f"missing `help=`")


def process_file(filename):
    with open(filename) as infp:
        tree = ast.parse(infp.read(), filename=filename)

    messages = []

    def add_message(node, message):
        messages.append(f"{filename}:{node.lineno}: {message}")

    EnsureClickHelpWalker(add_message=add_message).visit(tree)
    return messages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", metavar="FILE", nargs="*")
    args = ap.parse_args()
    n_messages = 0
    for file in args.files:
        for message in process_file(file):
            print(message)
            n_messages += 1
    sys.exit(n_messages)


if __name__ == "__main__":
    main()
