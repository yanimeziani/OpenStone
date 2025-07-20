"""
OpenStone: Crystal Gemstone Generation & Rendering Pipeline

A comprehensive system for generating organic gemstones with metallic engravings
and rendering them with professional quality materials and lighting.
"""

__version__ = "1.0.0"
__author__ = "Yani Meziani"
__email__ = "mezianiyani0@gmail.com"

from .ai_generator import AIGemGenerator
from .mesh_creator import MeshCreator  
from .material_manager import MaterialManager
from .lighting_manager import LightingManager

__all__ = [
    "AIGemGenerator",
    "MeshCreator", 
    "MaterialManager",
    "LightingManager"
]