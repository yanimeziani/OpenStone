#!/usr/bin/env python3
"""
Material Manager Module
Extensible system for creating different material and shading styles
"""

import bpy
import mathutils
from mathutils import Vector
import random
from typing import Dict, Any, Callable, List, Optional
from abc import ABC, abstractmethod


class BaseMaterialStyle(ABC):
    """Abstract base class for material styles"""
    
    @abstractmethod
    def create_material(self, material_data: Dict[str, Any], name: str = "GemMaterial") -> bpy.types.Material:
        """Create a material based on material data
        
        Args:
            material_data: Dictionary containing material parameters
            name: Name for the material
            
        Returns:
            Blender material
        """
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this material style
        
        Returns:
            Dictionary of default parameter values
        """
        pass


class RealisticGemStyle(BaseMaterialStyle):
    """Realistic gemstone material style using Principled BSDF"""
    
    def create_material(self, material_data: Dict[str, Any], name: str = "RealisticGem") -> bpy.types.Material:
        """Create realistic gemstone material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create main nodes
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        # Set material properties
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.9)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.05)
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.6)
        
        # Add subsurface scattering if supported
        if 'subsurface_scattering' in material_data:
            principled.inputs['Subsurface Weight'].default_value = material_data['subsurface_scattering']
        
        # Add artistic internal effects
        self._add_internal_complexity(nodes, links, principled, material_data)
        
        # Link to output
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _add_internal_complexity(self, nodes, links, principled, material_data):
        """Add internal complexity with noise and patterns"""
        # Create noise texture for internal variations
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 25.0
        noise.inputs['Detail'].default_value = 16.0
        
        # Create color ramp for artistic control
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 0)
        
        # Mix with base color
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (-100, 0)
        mix.inputs['Fac'].default_value = 0.3
        
        # Link internal effects
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
        
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        mix.inputs['Color1'].default_value = (*base_color, 1.0)
        
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'base_color': [0.8, 0.9, 1.0],
            'transparency': 0.9,
            'roughness': 0.05,
            'ior': 1.6,
            'subsurface_scattering': 0.2
        }


class StylizedGemStyle(BaseMaterialStyle):
    """Stylized, artistic gemstone material style"""
    
    def create_material(self, material_data: Dict[str, Any], name: str = "StylizedGem") -> bpy.types.Material:
        """Create stylized gemstone material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Create emission-based stylized look
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 100)
        
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, -100)
        
        # Mix shader for interesting effects
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (200, 0)
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        # Set up stylized properties
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        emission.inputs['Color'].default_value = (*base_color, 1.0)
        emission.inputs['Strength'].default_value = material_data.get('emission_strength', 0.5)
        
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.7)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.1)
        
        # Mix the shaders
        mix_shader.inputs['Fac'].default_value = material_data.get('stylization_mix', 0.3)
        
        # Link everything
        links.new(emission.outputs['Emission'], mix_shader.inputs[1])
        links.new(principled.outputs['BSDF'], mix_shader.inputs[2])
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        return material
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'base_color': [0.8, 0.9, 1.0],
            'transparency': 0.7,
            'roughness': 0.1,
            'emission_strength': 0.5,
            'stylization_mix': 0.3
        }


class CrystallineStyle(BaseMaterialStyle):
    """Complex crystalline structure material with internal facets"""
    
    def create_material(self, material_data: Dict[str, Any], name: str = "CrystallineGem") -> bpy.types.Material:
        """Create crystalline structure material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 0)
        
        # Create complex internal structure
        self._create_crystalline_structure(nodes, links, principled, material_data)
        
        # Set basic properties
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.95)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.02)
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.8)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _create_crystalline_structure(self, nodes, links, principled, material_data):
        """Create complex internal crystalline patterns"""
        # Voronoi for crystal cell structure
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-600, 200)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 15.0
        
        # Wave texture for internal flow
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-600, 0)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 20.0
        
        # Noise for randomization
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, -200)
        noise.inputs['Scale'].default_value = 30.0
        
        # Combine textures
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-400, 100)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-400, -100)
        
        # Color ramp for control
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 0)
        
        # Mix with base color
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (-100, 0)
        mix.inputs['Fac'].default_value = 0.5
        
        # Link the crystalline structure
        links.new(voronoi.outputs['Distance'], math1.inputs[0])
        links.new(wave.outputs['Fac'], math1.inputs[1])
        links.new(math1.outputs['Value'], math2.inputs[0])
        links.new(noise.outputs['Fac'], math2.inputs[1])
        links.new(math2.outputs['Value'], color_ramp.inputs['Fac'])
        
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        mix.inputs['Color1'].default_value = (*base_color, 1.0)
        links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'base_color': [0.8, 0.9, 1.0],
            'transparency': 0.95,
            'roughness': 0.02,
            'ior': 1.8
        }


class MetallicAccentStyle(BaseMaterialStyle):
    """Material style with metallic engravings and accents"""
    
    def create_material(self, material_data: Dict[str, Any], name: str = "MetallicAccentGem") -> bpy.types.Material:
        """Create material with metallic accents"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main gem shader
        gem_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        gem_principled.location = (0, 100)
        
        # Metallic accent shader
        metal_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        metal_principled.location = (0, -100)
        
        # Mix shader
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (300, 0)
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (500, 0)
        
        # Set up gem properties
        base_color = material_data.get('base_color', [0.8, 0.9, 1.0])
        gem_principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        gem_principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.9)
        gem_principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.05)
        
        # Set up metallic properties
        engraving_data = material_data.get('engraving', {})
        metal_color = self._get_metal_color(engraving_data.get('metal_type', 'silver'))
        metal_principled.inputs['Base Color'].default_value = (*metal_color, 1.0)
        metal_principled.inputs['Metallic'].default_value = engraving_data.get('metallic', 1.0)
        metal_principled.inputs['Roughness'].default_value = engraving_data.get('roughness', 0.2)
        
        # Create mask for engravings
        self._create_engraving_mask(nodes, links, mix_shader, engraving_data)
        
        # Link shaders
        links.new(gem_principled.outputs['BSDF'], mix_shader.inputs[1])
        links.new(metal_principled.outputs['BSDF'], mix_shader.inputs[2])
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        return material
    
    def _get_metal_color(self, metal_type: str) -> List[float]:
        """Get color for different metal types"""
        metal_colors = {
            'gold': [1.0, 0.766, 0.336],
            'silver': [0.972, 0.960, 0.915],
            'copper': [0.955, 0.637, 0.538],
            'platinum': [0.672, 0.672, 0.672],
            'bronze': [0.804, 0.498, 0.196]
        }
        return metal_colors.get(metal_type, metal_colors['silver'])
    
    def _create_engraving_mask(self, nodes, links, mix_shader, engraving_data):
        """Create procedural mask for engravings"""
        pattern = engraving_data.get('pattern', 'mystical')
        
        if pattern == 'infinity':
            # Create infinity symbol pattern
            coord = nodes.new(type='ShaderNodeTexCoord')
            coord.location = (-800, 0)
            
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-600, 0)
            
            # Use wave texture to create infinity-like pattern
            wave = nodes.new(type='ShaderNodeTexWave')
            wave.location = (-400, 0)
            wave.wave_type = 'RINGS'
            wave.inputs['Scale'].default_value = 8.0
            
            color_ramp = nodes.new(type='ShaderNodeValToRGB')
            color_ramp.location = (-200, 0)
            
            links.new(coord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
            links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(color_ramp.outputs['Fac'], mix_shader.inputs['Fac'])
        else:
            # Generic procedural pattern
            noise = nodes.new(type='ShaderNodeTexNoise')
            noise.location = (-400, 0)
            noise.inputs['Scale'].default_value = 12.0
            
            color_ramp = nodes.new(type='ShaderNodeValToRGB')
            color_ramp.location = (-200, 0)
            color_ramp.color_ramp.elements[0].position = 0.6
            
            links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(color_ramp.outputs['Fac'], mix_shader.inputs['Fac'])
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'base_color': [0.8, 0.9, 1.0],
            'transparency': 0.9,
            'roughness': 0.05,
            'engraving': {
                'metal_type': 'silver',
                'metallic': 1.0,
                'roughness': 0.2,
                'pattern': 'mystical'
            }
        }


class MaterialManager:
    """Main material management system with extensible styles"""
    
    def __init__(self):
        """Initialize with built-in material styles"""
        self.styles = {
            'realistic': RealisticGemStyle(),
            'stylized': StylizedGemStyle(),
            'crystalline': CrystallineStyle(),
            'metallic_accent': MetallicAccentStyle()
        }
    
    def register_style(self, name: str, style: BaseMaterialStyle):
        """Register a new material style
        
        Args:
            name: Unique name for the style
            style: Instance of BaseMaterialStyle
        """
        self.styles[name] = style
        print(f"✅ Registered material style: {name}")
    
    def list_styles(self) -> List[str]:
        """Get list of available style names"""
        return list(self.styles.keys())
    
    def get_default_params(self, style_name: str) -> Dict[str, Any]:
        """Get default parameters for a style
        
        Args:
            style_name: Name of the style
            
        Returns:
            Dictionary of default parameters
        """
        if style_name not in self.styles:
            raise ValueError(f"Unknown material style: {style_name}")
        return self.styles[style_name].get_default_params()
    
    def create_material(self, gem_data: Dict[str, Any], style_override: Optional[str] = None) -> bpy.types.Material:
        """Create material from gemstone specification
        
        Args:
            gem_data: Complete gemstone specification
            style_override: Optional style override
            
        Returns:
            Blender material
        """
        material_data = gem_data.get('material', {})
        style_name = style_override or material_data.get('style', 'realistic')
        
        if style_name not in self.styles:
            print(f"⚠️ Unknown material style '{style_name}', using 'realistic'")
            style_name = 'realistic'
        
        print(f"🎨 Creating {style_name} material...")
        
        # Merge default params with provided params
        default_params = self.styles[style_name].get_default_params()
        
        # Create a deep copy and update
        merged_params = {}
        merged_params.update(default_params)
        merged_params.update(material_data)
        
        # Generate the material
        gem_name = gem_data.get('name', 'UnknownGem')
        material = self.styles[style_name].create_material(merged_params, f"{gem_name}_{style_name}")
        
        return material


# Example of how to create a custom material style
class NeonGemStyle(BaseMaterialStyle):
    """Example custom material style for neon-like gems"""
    
    def create_material(self, material_data: Dict[str, Any], name: str = "NeonGem") -> bpy.types.Material:
        """Create neon-style material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Strong emission for neon effect
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Set neon properties
        base_color = material_data.get('base_color', [0.0, 1.0, 0.5])
        emission.inputs['Color'].default_value = (*base_color, 1.0)
        emission.inputs['Strength'].default_value = material_data.get('neon_strength', 5.0)
        
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        return material
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'base_color': [0.0, 1.0, 0.5],
            'neon_strength': 5.0
        }