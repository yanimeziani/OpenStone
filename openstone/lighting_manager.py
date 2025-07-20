#!/usr/bin/env python3
"""
Lighting Manager Module
Extensible system for creating different lighting setups and world environments
"""

import bpy
import mathutils
from mathutils import Vector, Euler
import math
import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class BaseLightingSetup(ABC):
    """Abstract base class for lighting setups"""
    
    @abstractmethod
    def setup_lights(self, lighting_data: Dict[str, Any]):
        """Set up lights based on lighting data
        
        Args:
            lighting_data: Dictionary containing lighting parameters
        """
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this lighting setup
        
        Returns:
            Dictionary of default parameter values
        """
        pass


class BaseWorldEnvironment(ABC):
    """Abstract base class for world environments"""
    
    @abstractmethod
    def setup_world(self, world_data: Dict[str, Any]):
        """Set up world environment
        
        Args:
            world_data: Dictionary containing world parameters
        """
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this world environment
        
        Returns:
            Dictionary of default parameter values
        """
        pass


class StudioLightingSetup(BaseLightingSetup):
    """Professional studio lighting setup with key, fill, and rim lights"""
    
    def setup_lights(self, lighting_data: Dict[str, Any]):
        """Set up studio lighting"""
        # Clear existing lights
        self._clear_lights()
        
        # Key light (main light)
        key_energy = lighting_data.get('key_light_energy', 10)
        key_light = self._create_area_light(
            name="KeyLight",
            location=(3, -3, 4),
            rotation=(math.radians(37), 0, math.radians(25)),
            energy=key_energy,
            size=2.0
        )
        
        # Fill light (soften shadows)
        fill_energy = lighting_data.get('fill_light_energy', 4)
        fill_light = self._create_area_light(
            name="FillLight",
            location=(-2, -2, 3),
            rotation=(math.radians(45), 0, math.radians(-30)),
            energy=fill_energy,
            size=1.5
        )
        
        # Rim light (edge definition)
        rim_energy = lighting_data.get('rim_light_energy', 8)
        rim_light = self._create_area_light(
            name="RimLight",
            location=(0, 4, 2),
            rotation=(math.radians(-30), 0, 0),
            energy=rim_energy,
            size=1.0
        )
        
        print("✨ Studio lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def _create_area_light(self, name: str, location: tuple, rotation: tuple, energy: float, size: float):
        """Create an area light"""
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.active_object
        light.name = name
        light.rotation_euler = rotation
        light.data.energy = energy
        light.data.size = size
        return light
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'key_light_energy': 10,
            'fill_light_energy': 4,
            'rim_light_energy': 8
        }


class NaturalLightingSetup(BaseLightingSetup):
    """Natural outdoor lighting setup"""
    
    def setup_lights(self, lighting_data: Dict[str, Any]):
        """Set up natural lighting"""
        self._clear_lights()
        
        # Sun light (primary)
        sun_energy = lighting_data.get('sun_energy', 3)
        sun_angle = lighting_data.get('sun_angle', 45)
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
        sun = bpy.context.active_object
        sun.name = "SunLight"
        sun.rotation_euler = (math.radians(sun_angle), 0, math.radians(30))
        sun.data.energy = sun_energy
        
        # Sky light (ambient)
        sky_energy = lighting_data.get('sky_energy', 0.5)
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
        sky = bpy.context.active_object
        sky.name = "SkyLight"
        sky.rotation_euler = (0, 0, 0)
        sky.data.energy = sky_energy
        sky.data.color = (0.7, 0.8, 1.0)  # Slight blue tint
        
        print("🌞 Natural lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'sun_energy': 3,
            'sun_angle': 45,
            'sky_energy': 0.5
        }


class DramaticLightingSetup(BaseLightingSetup):
    """Dramatic, moody lighting setup"""
    
    def setup_lights(self, lighting_data: Dict[str, Any]):
        """Set up dramatic lighting"""
        self._clear_lights()
        
        # Single strong key light
        key_energy = lighting_data.get('key_light_energy', 20)
        bpy.ops.object.light_add(type='SPOT', location=(4, -4, 6))
        key_light = bpy.context.active_object
        key_light.name = "DramaticKey"
        key_light.rotation_euler = (math.radians(30), 0, math.radians(45))
        key_light.data.energy = key_energy
        key_light.data.spot_size = math.radians(60)
        
        # Subtle fill
        fill_energy = lighting_data.get('fill_light_energy', 2)
        bpy.ops.object.light_add(type='AREA', location=(-3, 0, 2))
        fill_light = bpy.context.active_object
        fill_light.name = "SubtleFill"
        fill_light.data.energy = fill_energy
        fill_light.data.size = 3.0
        fill_light.data.color = (0.8, 0.9, 1.0)
        
        print("🎭 Dramatic lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'key_light_energy': 20,
            'fill_light_energy': 2
        }


class HDRIWorldEnvironment(BaseWorldEnvironment):
    """HDRI-based world environment"""
    
    def setup_world(self, world_data: Dict[str, Any]):
        """Set up HDRI world environment"""
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create HDRI setup
        env_texture = nodes.new(type='ShaderNodeTexEnvironment')
        env_texture.location = (-300, 300)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 300)
        
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (200, 300)
        
        # Set HDRI strength
        hdri_strength = world_data.get('hdri_strength', 1.0)
        background.inputs['Strength'].default_value = hdri_strength
        
        # Try to load HDRI if path provided
        hdri_path = world_data.get('hdri_path')
        if hdri_path and os.path.exists(hdri_path):
            env_texture.image = bpy.data.images.load(hdri_path)
        else:
            # Use procedural sky if no HDRI
            self._create_procedural_sky(nodes, links, background)
            return
        
        # Link nodes
        links.new(env_texture.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌍 HDRI world environment setup complete")
    
    def _create_procedural_sky(self, nodes, links, background):
        """Create procedural sky when no HDRI is available"""
        sky_texture = nodes.new(type='ShaderNodeTexSky')
        sky_texture.location = (-300, 300)
        sky_texture.sky_type = 'NISHITA'
        
        links.new(sky_texture.outputs['Color'], background.inputs['Color'])
        print("🌤️ Using procedural sky")
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'hdri_strength': 1.0,
            'hdri_path': None
        }


class GradientWorldEnvironment(BaseWorldEnvironment):
    """Gradient-based world environment"""
    
    def setup_world(self, world_data: Dict[str, Any]):
        """Set up gradient world environment"""
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Create gradient setup
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 300)
        
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-300, 300)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 300)
        
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (200, 300)
        
        # Set gradient colors
        top_color = world_data.get('top_color', [0.05, 0.1, 0.3])
        bottom_color = world_data.get('bottom_color', [0.8, 0.9, 1.0])
        
        color_ramp.color_ramp.elements[0].color = (*bottom_color, 1.0)
        color_ramp.color_ramp.elements[1].color = (*top_color, 1.0)
        
        # Set strength
        strength = world_data.get('strength', 0.8)
        background.inputs['Strength'].default_value = strength
        
        # Link nodes
        links.new(tex_coord.outputs['Generated'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌈 Gradient world environment setup complete")
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'top_color': [0.05, 0.1, 0.3],
            'bottom_color': [0.8, 0.9, 1.0],
            'strength': 0.8
        }


class SolidColorWorldEnvironment(BaseWorldEnvironment):
    """Simple solid color world environment"""
    
    def setup_world(self, world_data: Dict[str, Any]):
        """Set up solid color world environment"""
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 300)
        
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (200, 300)
        
        # Set color and strength
        color = world_data.get('color', [0.1, 0.1, 0.15])
        strength = world_data.get('strength', 0.5)
        
        background.inputs['Color'].default_value = (*color, 1.0)
        background.inputs['Strength'].default_value = strength
        
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🎨 Solid color world environment setup complete")
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'color': [0.1, 0.1, 0.15],
            'strength': 0.5
        }


class LightingManager:
    """Main lighting and world management system"""
    
    def __init__(self):
        """Initialize with built-in lighting setups and world environments"""
        self.lighting_setups = {
            'studio': StudioLightingSetup(),
            'natural': NaturalLightingSetup(),
            'dramatic': DramaticLightingSetup()
        }
        
        self.world_environments = {
            'hdri': HDRIWorldEnvironment(),
            'gradient': GradientWorldEnvironment(),
            'solid_color': SolidColorWorldEnvironment()
        }
    
    def register_lighting_setup(self, name: str, setup: BaseLightingSetup):
        """Register a new lighting setup
        
        Args:
            name: Unique name for the setup
            setup: Instance of BaseLightingSetup
        """
        self.lighting_setups[name] = setup
        print(f"✅ Registered lighting setup: {name}")
    
    def register_world_environment(self, name: str, environment: BaseWorldEnvironment):
        """Register a new world environment
        
        Args:
            name: Unique name for the environment
            environment: Instance of BaseWorldEnvironment
        """
        self.world_environments[name] = environment
        print(f"✅ Registered world environment: {name}")
    
    def list_lighting_setups(self) -> List[str]:
        """Get list of available lighting setup names"""
        return list(self.lighting_setups.keys())
    
    def list_world_environments(self) -> List[str]:
        """Get list of available world environment names"""
        return list(self.world_environments.keys())
    
    def setup_lighting(self, gem_data: Dict[str, Any], lighting_override: Optional[str] = None):
        """Set up lighting from gemstone specification
        
        Args:
            gem_data: Complete gemstone specification
            lighting_override: Optional lighting setup override
        """
        lighting_data = gem_data.get('lighting', {})
        setup_name = lighting_override or lighting_data.get('setup', 'studio')
        
        if setup_name not in self.lighting_setups:
            print(f"⚠️ Unknown lighting setup '{setup_name}', using 'studio'")
            setup_name = 'studio'
        
        print(f"💡 Setting up {setup_name} lighting...")
        
        # Merge default params with provided params
        default_params = self.lighting_setups[setup_name].get_default_params()
        merged_params = {}
        merged_params.update(default_params)
        merged_params.update(lighting_data)
        
        # Set up the lighting
        self.lighting_setups[setup_name].setup_lights(merged_params)
    
    def setup_world(self, gem_data: Dict[str, Any], world_override: Optional[str] = None):
        """Set up world environment from gemstone specification
        
        Args:
            gem_data: Complete gemstone specification
            world_override: Optional world environment override
        """
        world_data = gem_data.get('world', {})
        env_name = world_override or world_data.get('environment', 'gradient')
        
        if env_name not in self.world_environments:
            print(f"⚠️ Unknown world environment '{env_name}', using 'gradient'")
            env_name = 'gradient'
        
        print(f"🌍 Setting up {env_name} world environment...")
        
        # Merge default params with provided params
        default_params = self.world_environments[env_name].get_default_params()
        merged_params = {}
        merged_params.update(default_params)
        merged_params.update(world_data)
        
        # Set up the world
        self.world_environments[env_name].setup_world(merged_params)


# Example of how to create custom lighting and world setups
class CinematicLightingSetup(BaseLightingSetup):
    """Example custom cinematic lighting setup"""
    
    def setup_lights(self, lighting_data: Dict[str, Any]):
        """Set up cinematic lighting with colored lights"""
        self._clear_lights()
        
        # Warm key light
        bpy.ops.object.light_add(type='AREA', location=(4, -3, 5))
        key_light = bpy.context.active_object
        key_light.name = "CinematicKey"
        key_light.data.energy = lighting_data.get('key_energy', 15)
        key_light.data.color = lighting_data.get('key_color', [1.0, 0.8, 0.6])
        
        # Cool fill light
        bpy.ops.object.light_add(type='AREA', location=(-2, -1, 3))
        fill_light = bpy.context.active_object
        fill_light.name = "CinematicFill"
        fill_light.data.energy = lighting_data.get('fill_energy', 8)
        fill_light.data.color = lighting_data.get('fill_color', [0.6, 0.8, 1.0])
        
        print("🎬 Cinematic lighting setup complete")
    
    def _clear_lights(self):
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'key_energy': 15,
            'key_color': [1.0, 0.8, 0.6],
            'fill_energy': 8,
            'fill_color': [0.6, 0.8, 1.0]
        }