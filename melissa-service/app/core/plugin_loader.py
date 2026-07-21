import os
import pkgutil
import importlib
import inspect
from typing import List, Type
import logging
from app.plugins.base import PluginBase

logger = logging.getLogger(__name__)

class PluginRegistry:
    def __init__(self):
        self.plugins: List[PluginBase] = []
        
    def load_plugins(self, package_name: str = "app.plugins"):
        """
        Dynamically discovers and loads all PluginBase implementations in the given package.
        """
        try:
            package = importlib.import_module(package_name)
        except ImportError as e:
            logger.error(f"Failed to import plugin package {package_name}: {e}")
            return
            
        package_path = package.__path__
        
        for _, module_name, is_pkg in pkgutil.walk_packages(package_path, package_name + "."):
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        # Instantiate the plugin
                        plugin_instance = obj()
                        self.plugins.append(plugin_instance)
                        logger.info(f"Loaded plugin: {plugin_instance.name}")
            except Exception as e:
                logger.error(f"Failed to load plugin from {module_name}: {e}")
                
    def get_all_plugins(self) -> List[PluginBase]:
        return self.plugins

global_plugin_registry = PluginRegistry()
