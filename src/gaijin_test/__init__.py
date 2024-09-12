from dataclasses import dataclass
import importlib.util
import os
from pathlib import Path
from types import ModuleType

import click


@dataclass
class ModuleData:
    path: Path
    module: ModuleType
    commands: list[str]


@dataclass
class ModuleLoadError:
    path: Path
    message: str
    exception: Exception | None = None


def load_data_from_module(module_path: Path) -> ModuleData | ModuleLoadError:
    module_name = module_path.stem
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            return ModuleLoadError(module_path, "Error creating module spec.")
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            return ModuleLoadError(module_path, "Mudule spec loader is None.")
        spec.loader.exec_module(module)
    except Exception as exception:
        return ModuleLoadError(module_path, "Error loading module", exception)
    commands = getattr(module, "CMDS", None)
    if commands is None:
        return ModuleLoadError(module_path, "Module doesn't have a `CMDS` attribute.")
    return ModuleData(
        path=module_path,
        module=module,
        commands=commands,
    )


def simple_alphabetical_order_sort_key_funtion(path: Path) -> str:
    """
    Doesn't consider case, special characters, numbers, and / separation.
    """
    return str(path.absolute()).lower()


@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True),
)
@click.command()
def main(directory: str) -> None:
    target_files = list(Path(directory).rglob("*.py"))
    target_files.sort(key=simple_alphabetical_order_sort_key_funtion)

    modules_data = [load_data_from_module(file) for file in target_files]

    executed_commands: set[str] = set()
    for module_data in modules_data:
        match module_data:
            case ModuleData(path=path, commands=commands):
                for command in commands:
                    if command in executed_commands:
                        print(f"Command `{command}` already executed.")
                    else:
                        try:
                            os.system(command)
                        except Exception as exception:
                            # I don't really remembeer if it raises anything but better safe than sorry
                            print(f"Error executing command `{command}`: {exception}")
                        executed_commands.add(command)
            case ModuleLoadError(path=path, message=message, exception=None):
                print(f"{path}: {message}")
            case ModuleLoadError(path=path, message=message, exception=exception):
                print(f"{path}: {message}; {exception}")


if __name__ == "__main__":
    main()
