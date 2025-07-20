#!/usr/bin/env python3
"""
Example: Creating a Custom Material Style

This example shows how to create your own material style
for unique gemstone appearances.
"""

import sys
from pathlib import Path

# Add openstone to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import bpy
from openstone.material_manager import BaseMaterialStyle, MaterialManager


class HolographicStyle(BaseMaterialStyle):
    """Custom material style that creates holographic effects"""
    
    def create_material(self, material_data: dict, name: str = "HolographicGem") -> bpy.types.Material:
        """Create holographic material with color shifting effects"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create coordinate and mapping nodes for control
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        
        # Create noise for holographic variations
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 200)
        noise.inputs['Scale'].default_value = material_data.get('hologram_scale', 50.0)
        
        # Create wave texture for interference patterns
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-400, 0)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = material_data.get('wave_scale', 30.0)
        
        # Create ColorRamp for color control
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 100)
        
        # Set up rainbow colors
        color_ramp.color_ramp.elements[0].color = (1.0, 0.0, 0.5, 1.0)  # Magenta
        color_ramp.color_ramp.elements[1].color = (0.0, 1.0, 1.0, 1.0)  # Cyan
        
        # Add more color stops for rainbow effect
        color_ramp.color_ramp.elements.new(0.33)
        color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 0.0, 1.0)  # Yellow
        
        color_ramp.color_ramp.elements.new(0.66)
        color_ramp.color_ramp.elements[2].color = (0.0, 1.0, 0.0, 1.0)  # Green
        
        # Math node to combine noise and wave
        math_add = nodes.new(type='ShaderNodeMath')
        math_add.operation = 'ADD'
        math_add.location = (-300, 0)
        
        # Principled BSDF for base
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (100, 0)
        
        # Set holographic properties
        principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.9)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.01)
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.4)
        
        # Add emission for glow
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (100, 200)
        emission.inputs['Strength'].default_value = material_data.get('glow_strength', 0.5)
        
        # Mix shaders
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (300, 100)
        mix_shader.inputs['Fac'].default_value = material_data.get('glow_mix', 0.3)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (500, 100)
        
        # Link everything
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        
        links.new(noise.outputs['Fac'], math_add.inputs[0])
        links.new(wave.outputs['Fac'], math_add.inputs[1])
        links.new(math_add.outputs['Value'], color_ramp.inputs['Fac'])
        
        links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
        links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
        
        links.new(principled.outputs['BSDF'], mix_shader.inputs[1])
        links.new(emission.outputs['Emission'], mix_shader.inputs[2])
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        return material
    
    def get_default_params(self) -> dict:
        return {
            'transparency': 0.9,
            'roughness': 0.01,
            'ior': 1.4,
            'hologram_scale': 50.0,
            'wave_scale': 30.0,
            'glow_strength': 0.5,
            'glow_mix': 0.3
        }


class LavaStyle(BaseMaterialStyle):
    """Custom material style that simulates molten lava crystals"""
    
    def create_material(self, material_data: dict, name: str = "LavaGem") -> bpy.types.Material:
        """Create lava-like material with heat effects"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Create noise for lava texture
        noise1 = nodes.new(type='ShaderNodeTexNoise')
        noise1.location = (-600, 200)
        noise1.inputs['Scale'].default_value = material_data.get('lava_scale', 15.0)
        noise1.inputs['Detail'].default_value = 16.0
        
        # Second noise for complexity
        noise2 = nodes.new(type='ShaderNodeTexNoise')
        noise2.location = (-600, 0)
        noise2.inputs['Scale'].default_value = material_data.get('detail_scale', 8.0)
        
        # ColorRamp for lava colors
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-300, 100)
        
        # Set lava colors: black to red to orange to yellow
        color_ramp.color_ramp.elements[0].color = (0.1, 0.0, 0.0, 1.0)  # Dark red
        color_ramp.color_ramp.elements[1].color = (1.0, 0.3, 0.0, 1.0)  # Bright orange
        
        # Add intermediate colors
        color_ramp.color_ramp.elements.new(0.3)
        color_ramp.color_ramp.elements[1].color = (0.5, 0.0, 0.0, 1.0)  # Medium red
        
        color_ramp.color_ramp.elements.new(0.8)
        color_ramp.color_ramp.elements[3].color = (1.0, 1.0, 0.5, 1.0)  # Hot yellow
        
        # Math to combine noises
        math_mult = nodes.new(type='ShaderNodeMath')
        math_mult.operation = 'MULTIPLY'
        math_mult.location = (-400, 100)
        
        # Principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.3)
        
        # Strong emission for heat glow
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 200)
        emission.inputs['Strength'].default_value = material_data.get('heat_glow', 2.0)
        
        # Mix for heat effect
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (200, 100)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 100)
        
        # Link nodes
        links.new(noise1.outputs['Fac'], math_mult.inputs[0])
        links.new(noise2.outputs['Fac'], math_mult.inputs[1])
        links.new(math_mult.outputs['Value'], color_ramp.inputs['Fac'])
        
        links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
        links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
        
        links.new(principled.outputs['BSDF'], mix_shader.inputs[1])
        links.new(emission.outputs['Emission'], mix_shader.inputs[2])
        links.new(color_ramp.outputs['Fac'], mix_shader.inputs['Fac'])
        
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        return material
    
    def get_default_params(self) -> dict:
        return {
            'lava_scale': 15.0,
            'detail_scale': 8.0,
            'roughness': 0.3,
            'heat_glow': 2.0
        }


def demo_custom_materials():
    """Demonstrate custom material styles"""
    print("🎨 Custom Material Styles Demo")
    print("=" * 40)
    
    # Create material manager and register custom styles
    material_manager = MaterialManager()
    material_manager.register_style('holographic', HolographicStyle())
    material_manager.register_style('lava', LavaStyle())
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create test objects
    bpy.ops.mesh.primitive_ico_sphere_add(location=(-2, 0, 0))
    sphere1 = bpy.context.active_object
    sphere1.name = "HolographicGem"
    
    bpy.ops.mesh.primitive_ico_sphere_add(location=(2, 0, 0))
    sphere2 = bpy.context.active_object
    sphere2.name = "LavaGem"
    
    # Create materials
    gem_data_holo = {
        'name': 'HolographicDemo',
        'material': {
            'style': 'holographic',
            'hologram_scale': 60.0,
            'glow_strength': 0.8
        }
    }
    
    gem_data_lava = {
        'name': 'LavaDemo',
        'material': {
            'style': 'lava',
            'heat_glow': 3.0,
            'lava_scale': 20.0
        }
    }
    
    # Apply materials
    holo_material = material_manager.create_material(gem_data_holo)
    lava_material = material_manager.create_material(gem_data_lava)
    
    sphere1.data.materials.append(holo_material)
    sphere2.data.materials.append(lava_material)
    
    print("✅ Custom materials created!")
    print("💡 Left sphere: Holographic style")
    print("💡 Right sphere: Lava style")
    
    return sphere1, sphere2


if __name__ == "__main__":
    demo_custom_materials()