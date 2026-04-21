"""
GrowthOS AI v2.0 — Build & Launch Script
=========================================
Usage:
    python build.py                  # install deps + syntax check
    python build.py --install        # install requirements only
    python build.py --check          # syntax check all .py files
    python build.py --backend        # start FastAPI backend (uvicorn)
    python build.py --desktop        # start desktop app (PyQt5)
    python build.py --bot            # start Telegram bot
    python build.py --all            # backend + desktop (two processes)
    python build.py --build          # full build: install + check + report
    python build.py --exe            # compile to dist/GrowthOS/GrowthOS.exe
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = sys.executable


# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> int:
    """Run a command, stream output, return exit code."""
    print(f"\n▶  {' '.join(cmd)}\n{'─' * 60}")
    result = subprocess.run(cmd, **kwargs)
    return result.returncode


def header(title: str):
    width = 60
    print(f"\n{'═' * width}")
    print(f"  {title}")
    print(f"{'═' * width}")


# ─── Tasks ────────────────────────────────────────────────────────────────────

def install_deps() -> bool:
    header("Installing dependencies")
    req = ROOT / "requirements.txt"
    if not req.exists():
        print("❌  requirements.txt not found")
        return False
    code = run([PYTHON, "-m", "pip", "install", "-r", str(req), "--quiet"])
    if code == 0:
        print("✅  All dependencies installed.")
    else:
        print("❌  pip install failed.")
    return code == 0


def syntax_check() -> bool:
    header("Syntax check")
    files = [
        ROOT / "config.py",
        ROOT / "backend_api.py",
        ROOT / "desktop_app.py",
        ROOT / "telegram_bot.py",
        *sorted((ROOT / "ai_core").glob("*.py")),
        *sorted((ROOT / "smm_panel").glob("*.py")),
    ]
    ok = True
    for f in files:
        if not f.exists():
            continue
        result = subprocess.run(
            [PYTHON, "-m", "py_compile", str(f)],
            capture_output=True, text=True
        )
        status = "✅" if result.returncode == 0 else "❌"
        rel = f.relative_to(ROOT)
        print(f"  {status}  {rel}")
        if result.returncode != 0:
            print(f"       {result.stderr.strip()}")
            ok = False
    if ok:
        print("\n✅  All files passed syntax check.")
    else:
        print("\n❌  Syntax errors found — fix before running.")
    return ok


def start_backend():
    header("Starting FastAPI backend")
    os.chdir(ROOT)
    run([PYTHON, "-m", "uvicorn", "backend_api:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"])


def start_desktop():
    header("Starting Desktop App")
    os.chdir(ROOT)
    run([PYTHON, str(ROOT / "desktop_app.py")])


def start_bot():
    header("Starting Telegram Bot")
    os.chdir(ROOT)
    run([PYTHON, str(ROOT / "telegram_bot.py")])


def start_all():
    """Launch backend in a subprocess, then foreground the desktop app."""
    header("Starting backend + desktop")
    os.chdir(ROOT)
    backend_proc = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend_api:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT,
    )
    print(f"✅  Backend started (PID {backend_proc.pid})")
    try:
        run([PYTHON, str(ROOT / "desktop_app.py")])
    finally:
        print("\n🛑  Desktop closed — stopping backend…")
        backend_proc.terminate()
        backend_proc.wait()


def build_exe() -> bool:
    header("Building GrowthOS.exe  (PyInstaller)")

    # Ensure PyInstaller is available
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found — installing…")
        code = run([PYTHON, "-m", "pip", "install", "pyinstaller", "--quiet"])
        if code != 0:
            print("❌  Could not install PyInstaller.")
            return False

    spec = ROOT / "GrowthOS.spec"
    if not spec.exists():
        print(f"❌  Spec file not found: {spec}")
        return False

    print("Building — this may take several minutes…")
    code = run(
        [PYTHON, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec)],
        cwd=ROOT,
    )

    if code == 0:
        exe_path = ROOT / "dist" / "GrowthOS" / "GrowthOS.exe"
        print(f"\n✅  Build complete!")
        print(f"   Executable: {exe_path}")
        print(f"   Folder:     {exe_path.parent}")
        print("\n   Copy the entire dist/GrowthOS/ folder to share the app.")
        print("   The .env file is bundled — update secrets before distributing.")
    else:
        print("\n❌  PyInstaller build failed — see output above.")
    return code == 0


def full_build() -> bool:
    header("GrowthOS AI — Full Build")
    ok = install_deps()
    ok = syntax_check() and ok
    header("Build Report")
    if ok:
        print("✅  Build PASSED — ready to run.")
        print("\nLaunch commands:")
        print(f"  python build.py --backend   # start API server")
        print(f"  python build.py --desktop   # start desktop GUI")
        print(f"  python build.py --all       # both together")
        print(f"  python build.py --exe       # compile to .exe")
    else:
        print("❌  Build FAILED — see errors above.")
    return ok


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GrowthOS AI build & launch utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--install",  action="store_true", help="Install requirements")
    parser.add_argument("--check",    action="store_true", help="Syntax check all files")
    parser.add_argument("--backend",  action="store_true", help="Start FastAPI backend")
    parser.add_argument("--desktop",  action="store_true", help="Start desktop app")
    parser.add_argument("--bot",      action="store_true", help="Start Telegram bot")
    parser.add_argument("--all",      action="store_true", help="Start backend + desktop")
    parser.add_argument("--build",    action="store_true", help="Full build (install + check)")
    parser.add_argument("--exe",      action="store_true", help="Compile desktop app to .exe via PyInstaller")

    args = parser.parse_args()

    # Default: full build when no flags given
    if not any(vars(args).values()):
        sys.exit(0 if full_build() else 1)

    if args.install:
        sys.exit(0 if install_deps() else 1)
    if args.check:
        sys.exit(0 if syntax_check() else 1)
    if args.build:
        sys.exit(0 if full_build() else 1)
    if args.exe:
        sys.exit(0 if build_exe() else 1)
    if args.backend:
        start_backend()
    if args.desktop:
        start_desktop()
    if args.bot:
        start_bot()
    if args.all:
        start_all()


if __name__ == "__main__":
    main()
