import uvicorn
import sys
import os
import multiprocessing

# Set POCKETSPHINX_PATH to avoid importlib crash in PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.environ["POCKETSPHINX_PATH"] = os.path.join(sys._MEIPASS, "pocketsphinx", "model")

# Explicitly import the app module so PyInstaller can trace all its dependencies
import app.main

if __name__ == "__main__":
    # Needed for PyInstaller multiprocessing on Windows
    multiprocessing.freeze_support()
    
    # Run Alembic migrations programmatically
    import alembic.config
    import alembic.command
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        ini_path = os.path.join(sys._MEIPASS, "alembic.ini")
        alembic_cfg = alembic.config.Config(ini_path)
        alembic_cfg.set_main_option("script_location", os.path.join(sys._MEIPASS, "migrations"))
    else:
        ini_path = "alembic.ini"
        alembic_cfg = alembic.config.Config(ini_path)
        alembic_cfg.set_main_option("script_location", "migrations")
        
    alembic.command.upgrade(alembic_cfg, "head")
    
    # Run the uvicorn server directly using the imported module instead of string
    uvicorn.run(app.main.app, host="127.0.0.1", port=8000, reload=False)
