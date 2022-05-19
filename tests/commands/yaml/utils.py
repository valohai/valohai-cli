from typing import Optional


def build_args(source_path: str, yaml_path: Optional[str] = None) -> list:
    args = [source_path]
    if yaml_path:
        args.append(f'--yaml={yaml_path}')
    return args
