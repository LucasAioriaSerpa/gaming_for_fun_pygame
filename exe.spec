# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['exe.py'],
    pathex=[],
    binaries=[],
    # Aqui dizemos ao PyInstaller para copiar as tuas pastas de assets
    datas=[
        ('content', 'content'),
        ('data', 'data')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='TheFall',          # O nome do teu ficheiro .exe final
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # False = Oculta a janela preta do terminal do Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='content/icone.ico', # Podes descomentar esta linha e adicionar um ícone se quiseres!
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TheFall',          # O nome da pasta final dentro de "dist/" onde o jogo vai ficar
)
