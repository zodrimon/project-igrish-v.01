import PyInstaller.__main__
import os

if __name__ == '__main__':
    # Build the standalone executable
    PyInstaller.__main__.run([
        'run_service.py',
        '--name=melissa-service',
        '--onedir', # one directory mode is often safer for complex deps
        '--noconfirm', # overwrite output directory
        
        # Include data files/directories
        '--add-data=migrations;migrations',
        '--add-data=alembic.ini;.',
        '--collect-data=pocketsphinx',
        '--collect-all=chromadb',
        '--collect-all=pydantic',
        '--collect-all=piper',
        
        # Hidden imports for FastAPI / Uvicorn / SQLAlchemy
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
        '--hidden-import=uvicorn.lifespan.off',
        '--hidden-import=alembic',
        '--hidden-import=aiosqlite',
        '--hidden-import=chromadb',
        '--hidden-import=sqlite3',
        
        # Dynamic plugins
        '--hidden-import=app.plugins.coding_companion',
        '--hidden-import=app.plugins.search_tool',
        
        # Optional: Exclude large unnecessary things
        '--exclude-module=tkinter',
        '--exclude-module=IPython',
        '--exclude-module=pytest',
    ])
