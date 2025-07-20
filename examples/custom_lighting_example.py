#!/usr/bin/env python3
"""
Example: Creating Custom Lighting and World Setups

This example shows how to create your own lighting setups
and world environments for unique atmospheres.
"""

import sys
from pathlib import Path

# Add openstone to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import bpy
import math
from mathutils import Vector
from openstone.lighting_manager import BaseLightingSetup, BaseWorldEnvironment, LightingManager


class NeonClubLightingSetup(BaseLightingSetup):
    """Custom lighting setup that simulates neon club atmosphere"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up neon club lighting with colored strobes"""
        self._clear_lights()
        
        # Multiple colored lights for neon effect
        colors = [
            [1.0, 0.0, 1.0],  # Magenta
            [0.0, 1.0, 1.0],  # Cyan
            [1.0, 1.0, 0.0],  # Yellow
            [1.0, 0.0, 0.0],  # Red
            [0.0, 0.0, 1.0]   # Blue
        ]
        
        energy = lighting_data.get('neon_energy', 15)
        radius = lighting_data.get('light_radius', 5)
        
        for i, color in enumerate(colors):
            angle = (i * 2 * math.pi) / len(colors)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 3
            
            bpy.ops.object.light_add(type='SPOT', location=(x, y, z))
            light = bpy.context.active_object
            light.name = f"NeonLight_{i}"
            
            # Point toward center
            light.rotation_euler = (math.radians(45), 0, angle + math.pi)
            
            light.data.energy = energy
            light.data.color = color
            light.data.spot_size = math.radians(lighting_data.get('spot_angle', 45))
            light.data.spot_blend = 0.2
        
        # Add dim fill light
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 8))
        fill = bpy.context.active_object
        fill.name = "ClubFill"
        fill.data.energy = lighting_data.get('fill_energy', 2)
        fill.data.size = 8
        fill.data.color = [0.2, 0.2, 0.4]  # Cool blue fill
        
        print("🕺 Neon club lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'neon_energy': 15,
            'light_radius': 5,
            'spot_angle': 45,
            'fill_energy': 2
        }


class UnderwaterLightingSetup(BaseLightingSetup):
    """Custom lighting setup that simulates underwater caustics"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up underwater lighting with caustic patterns"""
        self._clear_lights()
        
        # Main sun light filtering through water
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
        sun = bpy.context.active_object
        sun.name = "UnderwaterSun"
        sun.rotation_euler = (math.radians(30), 0, 0)
        sun.data.energy = lighting_data.get('sun_energy', 3)
        sun.data.color = [0.6, 0.8, 1.0]  # Blue-green tint
        
        # Animated caustic lights (in practice, you'd animate these)
        num_caustics = lighting_data.get('caustic_lights', 8)
        caustic_energy = lighting_data.get('caustic_energy', 5)
        
        for i in range(num_caustics):
            angle = (i * 2 * math.pi) / num_caustics
            x = 3 * math.cos(angle) + (i % 2 - 0.5) * 2  # Add some randomness
            y = 3 * math.sin(angle) + ((i + 1) % 3 - 1) * 1.5
            z = 6 + (i % 3) * 0.5
            
            bpy.ops.object.light_add(type='SPOT', location=(x, y, z))
            caustic = bpy.context.active_object
            caustic.name = f"Caustic_{i}"
            caustic.rotation_euler = (math.radians(60 + i * 5), 0, angle)
            
            caustic.data.energy = caustic_energy
            caustic.data.color = [0.7, 0.9, 1.0]  # Bright blue-white
            caustic.data.spot_size = math.radians(30)
            caustic.data.spot_blend = 0.8  # Soft edges
        
        print("🌊 Underwater lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'sun_energy': 3,
            'caustic_lights': 8,
            'caustic_energy': 5
        }


class NebulaWorldEnvironment(BaseWorldEnvironment):
    """Custom world environment that creates a space nebula background"""
    
    def setup_world(self, world_data: dict):
        """Set up nebula world environment"""
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Create complex nebula texture
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 300)
        
        # Multiple noise textures for complexity
        noise1 = nodes.new(type='ShaderNodeTexNoise')
        noise1.location = (-600, 400)
        noise1.inputs['Scale'].default_value = world_data.get('nebula_scale', 2.0)
        noise1.inputs['Detail'].default_value = 16.0
        
        noise2 = nodes.new(type='ShaderNodeTexNoise')
        noise2.location = (-600, 200)
        noise2.inputs['Scale'].default_value = world_data.get('detail_scale', 5.0)
        noise2.inputs['Detail'].default_value = 8.0
        
        # Voronoi for star field
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-600, 0)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = world_data.get('star_density', 50.0)
        
        # Math nodes to combine
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-400, 300)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-400, 100)
        
        # ColorRamp for nebula colors
        color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp1.location = (-200, 300)
        
        # Set nebula colors
        nebula_colors = world_data.get('nebula_colors', [
            [0.1, 0.0, 0.3],  # Deep purple
            [0.8, 0.2, 0.5],  # Pink
            [0.2, 0.5, 1.0]   # Blue
        ])
        
        color_ramp1.color_ramp.elements[0].color = (*nebula_colors[0], 1.0)
        color_ramp1.color_ramp.elements[1].color = (*nebula_colors[1], 1.0)
        
        if len(nebula_colors) > 2:
            color_ramp1.color_ramp.elements.new(0.5)
            color_ramp1.color_ramp.elements[1].color = (*nebula_colors[2], 1.0)
        
        # ColorRamp for stars
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-200, 0)
        color_ramp2.color_ramp.elements[0].position = 0.95
        color_ramp2.color_ramp.elements[0].color = (0, 0, 0, 1)
        color_ramp2.color_ramp.elements[1].color = (1, 1, 1, 1)
        
        # Mix nebula and stars
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (0, 200)
        mix.blend_type = 'ADD'
        mix.inputs['Fac'].default_value = 1.0
        
        # Background shader
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (200, 200)
        background.inputs['Strength'].default_value = world_data.get('nebula_strength', 0.8)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (400, 200)
        
        # Link everything
        links.new(tex_coord.outputs['Generated'], noise1.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], noise2.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], voronoi.inputs['Vector'])
        
        links.new(noise1.outputs['Fac'], math1.inputs[0])
        links.new(noise2.outputs['Fac'], math1.inputs[1])
        links.new(math1.outputs['Value'], color_ramp1.inputs['Fac'])
        
        links.new(voronoi.outputs['Distance'], color_ramp2.inputs['Fac'])
        
        links.new(color_ramp1.outputs['Color'], mix.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix.inputs['Color2'])
        
        links.new(mix.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌌 Nebula world environment setup complete")
    
    def get_default_params(self) -> dict:
        return {
            'nebula_scale': 2.0,
            'detail_scale': 5.0,
            'star_density': 50.0,
            'nebula_strength': 0.8,
            'nebula_colors': [
                [0.1, 0.0, 0.3],  # Deep purple
                [0.8, 0.2, 0.5],  # Pink
                [0.2, 0.5, 1.0]   # Blue
            ]
        }


def demo_custom_lighting():
    """Demonstrate custom lighting and world setups"""
    print("💡 Custom Lighting & World Demo")
    print("=" * 40)
    
    # Create lighting manager and register custom setups
    lighting_manager = LightingManager()
    lighting_manager.register_lighting_setup('neon_club', NeonClubLightingSetup())
    lighting_manager.register_lighting_setup('underwater', UnderwaterLightingSetup())
    lighting_manager.register_world_environment('nebula', NebulaWorldEnvironment())
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create test object
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2)
    gem = bpy.context.active_object
    gem.name = "TestGem"
    
    # Test different setups
    print("\n🕺 Setting up neon club lighting...")
    gem_data_neon = {
        'lighting': {
            'setup': 'neon_club',
            'neon_energy': 20,
            'light_radius': 6
        },
        'world': {
            'environment': 'solid_color',
            'color': [0.0, 0.0, 0.1],
            'strength': 0.3
        }
    }
    
    lighting_manager.setup_lighting(gem_data_neon)
    lighting_manager.setup_world(gem_data_neon)
    
    print("✅ Custom lighting demo complete!")
    print("💡 Try switching between setups:")
    print("   - neon_club: Colorful strobing lights")
    print("   - underwater: Caustic water effects")
    print("   - nebula world: Space nebula background")


if __name__ == "__main__":
    demo_custom_lighting()