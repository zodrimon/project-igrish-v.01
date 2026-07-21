import pytest
import os
from app.core.plugin_loader import PluginRegistry
from app.plugins.base import PluginBase

def test_plugin_loader():
    plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "app", "plugins")
    dummy_file = os.path.join(plugins_dir, "dummy_for_test.py")
    
    with open(dummy_file, "w") as f:
        f.write('''
from app.plugins.base import PluginBase

class DummyTestPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "DummyTestPlugin"
''')
        
    try:
        registry = PluginRegistry()
        registry.load_plugins("app.plugins")
        
        plugins = registry.get_all_plugins()
        assert len(plugins) >= 1
        
        names = [p.name for p in plugins]
        assert "DummyTestPlugin" in names
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
