import os
import shutil
import zipfile
import subprocess

PACKAGE_DIR = "lambda-package"
ZIP_NAME = "lambda-deployment.zip"

APP_FILES = [
    "server.py",
    "lambda_handler.py",
]

OPTIONAL_FILES = [
    ".env",
]

OPTIONAL_DIRS = [
    "memory",
    "data",
]


def clean():
    print("🧹 Cleaning previous builds...")
    if os.path.exists(PACKAGE_DIR):
        shutil.rmtree(PACKAGE_DIR)
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)


def install_dependencies():
    print("📦 Installing dependencies (Lambda-compatible)...")

    os.makedirs(PACKAGE_DIR, exist_ok=True)

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{os.getcwd()}:/var/task",
            "--platform",
            "linux/amd64",
            "--entrypoint",
            "",
            "public.ecr.aws/lambda/python:3.12",
            "/bin/sh",
            "-c",
            (
                "pip install "
                "--target /var/task/lambda-package "
                "-r /var/task/requirements.txt "
                "--platform manylinux2014_x86_64 "
                "--only-binary=:all: "
                "--upgrade"
            ),
        ],
        check=True,
    )


def copy_files():
    print("📁 Copying application files...")

    for file in APP_FILES:
        if os.path.exists(file):
            shutil.copy2(file, PACKAGE_DIR)
        else:
            print(f"⚠️ Warning: {file} not found")

    for file in OPTIONAL_FILES:
        if os.path.exists(file):
            shutil.copy2(file, PACKAGE_DIR)

    for d in OPTIONAL_DIRS:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(PACKAGE_DIR, d))


def remove_unnecessary():
    """
    Reduce size → faster cold starts
    """
    print("✂️ Removing unnecessary files...")

    for root, dirs, files in os.walk(PACKAGE_DIR):
        for file in files:
            if file.endswith((".pyc", ".pyo")):
                os.remove(os.path.join(root, file))

        for d in dirs:
            if d in ("__pycache__", "tests", "test"):
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)


def create_zip():
    print("🗜️ Creating deployment zip...")

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(PACKAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PACKAGE_DIR)
                zipf.write(file_path, arcname)

    size_mb = os.path.getsize(ZIP_NAME) / (1024 * 1024)
    print(f"✅ Package ready: {ZIP_NAME} ({size_mb:.2f} MB)")

    if size_mb > 50:
        print("⚠️ Warning: Package >50MB (Lambda limit risk)")


def main():
    print("🚀 Building Lambda package for Academic Summarizer...\n")

    clean()
    install_dependencies()
    copy_files()
    remove_unnecessary()
    create_zip()

    print("\n🎯 Done. Ready to deploy.")


if __name__ == "__main__":
    main()