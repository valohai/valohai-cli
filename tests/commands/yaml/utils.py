from __future__ import annotations


def build_args(source_path: str, yaml_path: str | None = None) -> list:
    args = [source_path]
    if yaml_path:
        args.append(f"--yaml={yaml_path}")
    return args
