# import os
import shutil
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).parent
    release_dir = root_dir / "release"
    backend_dir = root_dir / "backend"
    release_backend_dir = release_dir / "backend"
    version = get_version(root_dir / "pyproject.toml")
    archive_name = f"release-{version}.7z"
    archive_path = release_dir / archive_name

    # Удаляем старые .7z архивы
    for file in release_dir.glob("*.7z"):
        print(f"Удаляю {file.name}")
        file.unlink()

    # Копируем backend -> release/backend (поверх, без удаления чужих файлов)
    print("Копирую backend → release/backend (перезапись файлов, без удаления остальных)")
    copy_dir_overwrite(src=backend_dir, dst=release_backend_dir)

    # Создаём архив
    print(f"Создаю архив {archive_name}")
    subprocess.run(["7z", "a", "-t7z", "-mx=2", str(archive_path), "."], cwd=release_dir, check=True)

def get_version(toml_path):
    import tomllib  # Python 3.11+
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]

def copy_dir_overwrite(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = src / item.name
        d = dst / item.name
        if s.is_dir():
            copy_dir_overwrite(s, d)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    main()
