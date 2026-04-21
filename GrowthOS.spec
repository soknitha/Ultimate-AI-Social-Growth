# -*- mode: python ; coding: utf-8 -*-
# GrowthOS AI v2.0 — PyInstaller spec
# Build with:  python build.py --exe
#          or: pyinstaller GrowthOS.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH)

block_cipher = None

a = Analysis(
    [str(ROOT / 'desktop_app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # .env  (loaded at runtime by python-dotenv)
        (str(ROOT / '.env'),          '.'),
        # ai_core package
        (str(ROOT / 'ai_core'),       'ai_core'),
        # smm_panel package
        (str(ROOT / 'smm_panel'),     'smm_panel'),
        # config + backend bundled so imports work
        (str(ROOT / 'config.py'),     '.'),
        (str(ROOT / 'backend_api.py'),'.'),
        # memory store directory (created at runtime if missing)
        (str(ROOT / 'memory_store'),  'memory_store'),
    ],
    hiddenimports=[
        # PyQt5
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.sip',
        # FastAPI / uvicorn (backend launched as subprocess from desktop)
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'pydantic',
        'pydantic.v1',
        'pydantic_core',
        # stdlib extras
        'zoneinfo',
        'zoneinfo._czoneinfo',
        'importlib.metadata',
        'importlib.resources',
        # project modules
        'config',
        'ai_core.strategy_agent',
        'ai_core.content_engine',
        'ai_core.analytics_ai',
        'ai_core.trend_radar',
        'ai_core.campaign_engine',
        'ai_core.risk_engine',
        'ai_core.multi_agent',
        'ai_core.memory_system',
        'ai_core.geo_engine',
        'smm_panel.panel_client',
        # networking
        'requests',
        'httpx',
        'aiohttp',
        'openai',
        'dotenv',
        'python_dateutil',
        'dateutil',
        'dateutil.parser',
        'aiogram',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GrowthOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # set to 'icon.ico' if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GrowthOS',        # output folder: dist/GrowthOS/
)
