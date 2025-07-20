#!/usr/bin/env python3
"""
Blender Gemstone Creator
Blender script that reads JSON files and creates gemstones with materials and rendering
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Euler
import math
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
import colorsys

class BlenderGemCreator:
    """Blender gemstone creation from JSON specifications"""
    
    def __init__(self):
        self.output_dir = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        

        
        self.engraving_patterns = {
            "infinity": self._create_infinity_texture,
            "mystical": self._create_generic_engraving_texture,
            "geometric": self._create_generic_engraving_texture,
            "organic": self._create_generic_engraving_texture,
            "spiral": self._create_generic_engraving_texture,
            "star": self._create_generic_engraving_texture,
            "floral": self._create_generic_engraving_texture,
            "dragon": self._create_dragon_texture,
            "phoenix": self._create_phoenix_texture,
            "celtic": self._create_generic_engraving_texture,
            "mandala": self._create_generic_engraving_texture,
            "runes": self._create_generic_engraving_texture
        }
    
    def clear_scene(self):
        """Clear the current scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Clear materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    
    def load_gem_json(self, json_file: str) -> Dict[str, Any]:
        """Load gemstone specification from JSON file"""
        print(f"📁 Loading gemstone from: {json_file}")
        
        try:
            with open(json_file, 'r') as f:
                gem_data = json.load(f)
            
            print(f"✅ Loaded gemstone: {gem_data.get('name', 'Unknown')}")
            return gem_data
            
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            raise
    
    def create_gem_geometry(self, gem_data: Dict[str, Any]) -> bpy.types.Object:
        """Create organic gemstone geometry with natural variations"""
        print("🔷 Creating gemstone geometry...")
        
        # Get geometry parameters
        base_shape = gem_data.get('base_shape', 'organic')
        geometry = gem_data.get('geometry', {})
        
        # Create base mesh based on shape type
        if base_shape == 'organic':
            gem_obj = self._create_organic_shape(geometry)
        elif base_shape == 'crystal':
            gem_obj = self._create_crystal_shape(geometry)
        elif base_shape == 'pebble':
            gem_obj = self._create_pebble_shape(geometry)
        elif base_shape == 'loop':
            gem_obj = self._create_loop_shape(geometry)
        else:
            gem_obj = self._create_organic_shape(geometry)  # Default to organic
        
        # Add organic modifiers
        self._add_organic_modifiers(gem_obj, geometry)
        
        # Name the object
        gem_name = gem_data.get('name', 'Gemstone')
        gem_obj.name = f"Gem_{gem_name}"
        
        return gem_obj
    
    def _create_organic_shape(self, geometry: Dict[str, Any]) -> bpy.types.Object:
        """Create organic, blob-like gemstone shape with randomness"""
        # Create base mesh (UV sphere for organic shape)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=geometry.get('radius', 1.0),
            location=(0, 0, 0),
            segments=geometry.get('segments', 32),  # More segments for smoother base
            ring_count=geometry.get('ring_count', 16)  # More rings for smoother base
        )
        gem_obj = bpy.context.active_object
        
        # Add organic deformation with randomness
        for i in range(2):
            modifier = gem_obj.modifiers.new(name=f"Organic_Displace_{i}", type='DISPLACE')
            texture = bpy.data.textures.new(name=f"Organic_Texture_{i}", type='CLOUDS')
            texture.noise_scale = 2.0 + i * 1.5 + (hash(str(gem_obj.name)) % 50) / 100.0  # Random scale
            texture.noise_depth = 6 + i * 2
            modifier.texture = texture
            modifier.strength = 0.3 + i * 0.1 + (hash(str(gem_obj.name) + str(i)) % 30) / 1000.0  # Random strength
        
        # Add subdivision for smoothness
        subsurf = gem_obj.modifiers.new(name="Organic_Subsurf", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 3
        
        return gem_obj
    
    def _create_crystal_shape(self, geometry: Dict[str, Any]) -> bpy.types.Object:
        """Create crystal-like gemstone shape with randomness"""
        # Create base mesh (cube for crystal shape)
        bpy.ops.mesh.primitive_cube_add(
            size=geometry.get('size', 2.0),
            location=(0, 0, 0)
        )
        gem_obj = bpy.context.active_object
        
        # Add random scale variation for crystal
        crystal_scale = geometry.get('crystal_scale', True)
        if crystal_scale:
            gem_obj.scale = (
                0.8 + (hash(str(gem_obj.name)) % 40) / 1000.0,
                0.9 + (hash(str(gem_obj.name) + "Y") % 40) / 1000.0,
                1.1 + (hash(str(gem_obj.name) + "Z") % 40) / 1000.0
            )
        
        # Add bevel for crystal facets with randomness
        bevel = gem_obj.modifiers.new(name="Crystal_Bevel", type='BEVEL')
        bevel.width = 0.1 + (hash(str(gem_obj.name)) % 20) / 1000.0  # Random width
        bevel.segments = 3 + (hash(str(gem_obj.name)) % 3)  # Random segments
        
        # Add displacement for crystal surface variation
        crystal_displace = gem_obj.modifiers.new(name="Crystal_Displace", type='DISPLACE')
        crystal_texture = bpy.data.textures.new(name="Crystal_Texture", type='VORONOI')
        crystal_texture.noise_scale = 5.0 + (hash(str(gem_obj.name)) % 30) / 10.0  # Random scale
        crystal_displace.texture = crystal_texture
        crystal_displace.strength = 0.05 + (hash(str(gem_obj.name)) % 20) / 1000.0  # Random strength
        
        # Add subdivision for smoothness
        subsurf = gem_obj.modifiers.new(name="Crystal_Subsurf", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 3
        
        return gem_obj
    
    def _create_pebble_shape(self, geometry: Dict[str, Any]) -> bpy.types.Object:
        """Create pebble-like gemstone shape with randomness"""
        # Create base mesh (UV sphere for pebble shape)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=geometry.get('radius', 0.8),
            location=(0, 0, 0),
            segments=geometry.get('segments', 24),  # Fewer segments for more organic look
            ring_count=geometry.get('ring_count', 12)
        )
        gem_obj = bpy.context.active_object
        
        # Add pebble deformation with randomness
        for i in range(2):
            modifier = gem_obj.modifiers.new(name=f"Pebble_Displace_{i}", type='DISPLACE')
            texture = bpy.data.textures.new(name=f"Pebble_Texture_{i}", type='VORONOI')
            texture.noise_scale = 1.5 + i * 0.5 + (hash(str(gem_obj.name) + str(i)) % 20) / 100.0  # Random scale
            modifier.texture = texture
            modifier.strength = 0.2 + i * 0.05 + (hash(str(gem_obj.name) + str(i)) % 15) / 1000.0  # Random strength
        
        # Add wave displacement for pebble flow
        wave_mod = gem_obj.modifiers.new(name="Pebble_Wave", type='DISPLACE')
        wave_texture = bpy.data.textures.new(name="Pebble_Wave_Texture", type='MUSGRAVE')
        wave_texture.noise_scale = 3.0 + (hash(str(gem_obj.name)) % 20) / 10.0  # Random scale
        wave_texture.lacunarity = 2.0
        wave_mod.texture = wave_texture
        wave_mod.strength = 0.08 + (hash(str(gem_obj.name)) % 10) / 1000.0  # Random strength
        
        # Add subdivision for smoothness
        subsurf = gem_obj.modifiers.new(name="Pebble_Subsurf", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 3
        
        return gem_obj
    
    def _create_loop_shape(self, geometry: Dict[str, Any]) -> bpy.types.Object:
        """Create loop/torus-like gemstone shape with organic variations"""
        # Create base mesh (torus for loop shape)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=geometry.get('major_radius', 1.2),
            minor_radius=geometry.get('minor_radius', 0.4),
            major_segments=geometry.get('major_segments', 48),
            minor_segments=geometry.get('minor_segments', 24),
            location=(0, 0, 0)
        )
        gem_obj = bpy.context.active_object
        
        # Add organic deformation to the loop
        for i in range(2):
            modifier = gem_obj.modifiers.new(name=f"Loop_Displace_{i}", type='DISPLACE')
            texture = bpy.data.textures.new(name=f"Loop_Texture_{i}", type='CLOUDS')
            texture.noise_scale = 3.0 + i * 2.0 + (hash(str(gem_obj.name)) % 50) / 100.0  # Random scale
            texture.noise_depth = 6 + i * 2
            modifier.texture = texture
            modifier.strength = 0.2 + i * 0.1 + (hash(str(gem_obj.name) + str(i)) % 30) / 1000.0  # Random strength
        
        # Add wave displacement for organic flow
        wave_mod = gem_obj.modifiers.new(name="Loop_Wave", type='DISPLACE')
        wave_texture = bpy.data.textures.new(name="Loop_Wave_Texture", type='MUSGRAVE')
        wave_texture.noise_scale = 4.0 + (hash(str(gem_obj.name)) % 30) / 10.0  # Random scale
        wave_texture.lacunarity = 2.0
        wave_mod.texture = wave_texture
        wave_mod.strength = 0.15 + (hash(str(gem_obj.name)) % 20) / 1000.0  # Random strength
        
        # Add voronoi displacement for organic zones
        voronoi_mod = gem_obj.modifiers.new(name="Loop_Voronoi", type='DISPLACE')
        voronoi_texture = bpy.data.textures.new(name="Loop_Voronoi_Texture", type='VORONOI')
        voronoi_texture.noise_scale = 2.5 + (hash(str(gem_obj.name)) % 20) / 10.0  # Random scale
        voronoi_mod.texture = voronoi_texture
        voronoi_mod.strength = 0.1 + (hash(str(gem_obj.name)) % 15) / 1000.0  # Random strength
        
        # Add subdivision for smoothness
        subsurf = gem_obj.modifiers.new(name="Loop_Subsurf", type='SUBSURF')
        subsurf.levels = 3
        subsurf.render_levels = 4
        
        # Add smooth modifier for organic flow
        smooth_mod = gem_obj.modifiers.new(name="Loop_Smooth", type='SMOOTH')
        smooth_mod.factor = 0.5
        smooth_mod.iterations = 3
        
        # Add random scale variation for natural look
        random_scale = geometry.get('random_scale', True)
        if random_scale:
            gem_obj.scale = (
                0.9 + (hash(str(gem_obj.name)) % 100) / 1000.0,  # Random scale X
                0.85 + (hash(str(gem_obj.name) + "Y") % 100) / 1000.0,  # Random scale Y
                1.1 + (hash(str(gem_obj.name) + "Z") % 100) / 1000.0   # Random scale Z (taller)
            )
        
        # Add random rotation for natural orientation
        random_rotation = geometry.get('random_rotation', True)
        if random_rotation:
            gem_obj.rotation_euler = (
                geometry.get('rotation_x', 0.2) + (hash(str(gem_obj.name)) % 50) / 1000.0,
                geometry.get('rotation_y', 0.1) + (hash(str(gem_obj.name) + "Y") % 50) / 1000.0,
                geometry.get('rotation_z', 0.3) + (hash(str(gem_obj.name) + "Z") % 50) / 1000.0
            )
        
        return gem_obj
    
    def _add_organic_modifiers(self, gem_obj: bpy.types.Object, geometry: Dict[str, Any]):
        """Add organic modifiers for natural appearance with randomness"""
        # Add multiple displacement modifiers for organic randomness
        for i in range(3):
            noise_mod = gem_obj.modifiers.new(name=f"Organic_Noise_{i}", type='DISPLACE')
            noise_texture = bpy.data.textures.new(name=f"Organic_Texture_{i}", type='CLOUDS')
            noise_texture.noise_scale = 2.0 + i * 1.5  # Varying scales
            noise_texture.noise_depth = 4 + i * 2
            noise_mod.texture = noise_texture
            noise_mod.strength = 0.1 + i * 0.05  # Varying strengths
        
        # Add voronoi displacement for organic zones
        voronoi_mod = gem_obj.modifiers.new(name="Organic_Voronoi", type='DISPLACE')
        voronoi_texture = bpy.data.textures.new(name="Organic_Voronoi_Texture", type='VORONOI')
        voronoi_texture.noise_scale = 3.0
        voronoi_mod.texture = voronoi_texture
        voronoi_mod.strength = 0.08
        
        # Add wave displacement for organic flow
        wave_mod = gem_obj.modifiers.new(name="Organic_Wave", type='DISPLACE')
        wave_texture = bpy.data.textures.new(name="Organic_Wave_Texture", type='MUSGRAVE')
        wave_texture.noise_scale = 4.0
        wave_texture.lacunarity = 2.0
        wave_mod.texture = wave_texture
        wave_mod.strength = 0.06
        
        # Add subdivision for smoothness
        subsurf = gem_obj.modifiers.new(name="Organic_Subsurf", type='SUBSURF')
        subsurf.levels = 3
        subsurf.render_levels = 4
        
        # Add smooth modifier for organic flow
        smooth_mod = gem_obj.modifiers.new(name="Organic_Smooth", type='SMOOTH')
        smooth_mod.factor = 0.4
        smooth_mod.iterations = 3
        
        # Add random scale variation
        random_scale = geometry.get('random_scale', True)
        if random_scale:
            gem_obj.scale = (
                0.9 + (hash(str(gem_obj.name)) % 100) / 1000.0,  # Random scale X
                0.85 + (hash(str(gem_obj.name) + "Y") % 100) / 1000.0,  # Random scale Y
                0.95 + (hash(str(gem_obj.name) + "Z") % 100) / 1000.0   # Random scale Z
            )
        
        # Add random rotation for natural orientation
        random_rotation = geometry.get('random_rotation', True)
        if random_rotation:
            gem_obj.rotation_euler = (
                geometry.get('rotation_x', 0.1) + (hash(str(gem_obj.name)) % 50) / 1000.0,
                geometry.get('rotation_y', 0.05) + (hash(str(gem_obj.name) + "Y") % 50) / 1000.0,
                geometry.get('rotation_z', 0.2) + (hash(str(gem_obj.name) + "Z") % 50) / 1000.0
            )
        
        # Add slight random position offset
        random_position = geometry.get('random_position', True)
        if random_position:
            gem_obj.location = (
                (hash(str(gem_obj.name)) % 20) / 1000.0,  # Small X offset
                (hash(str(gem_obj.name) + "Y") % 20) / 1000.0,  # Small Y offset
                (hash(str(gem_obj.name) + "Z") % 20) / 1000.0   # Small Z offset
            )
    
    def create_advanced_material(self, material_data: Dict[str, Any]) -> bpy.types.Material:
        """Create simplified but intricate material for GLB export: mesh gradients, simple bump, and roughness variation"""
        material = bpy.data.materials.new(name=f"Gem_{material_data.get('name', 'Material')}")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        # Principled BSDF
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        # Material Output
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        material_output.location = (300, 0)
        links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])
        # Base properties
        base_color = material_data.get('base_color', [0.1, 0.3, 0.8, 1.0])
        principled.inputs['Base Color'].default_value = base_color
        principled.inputs['Metallic'].default_value = 0.0
        principled.inputs['Roughness'].default_value = 0.02
        principled.inputs['Transmission Weight'].default_value = 0.7
        principled.inputs['IOR'].default_value = 1.6
        principled.inputs['Alpha'].default_value = 0.95
        # Mesh gradients
        self._add_mesh_gradients(nodes, links, principled, material_data)
        # Simple bump/normal map
        noise_bump = nodes.new(type='ShaderNodeTexNoise')
        noise_bump.location = (-400, -200)
        noise_bump.inputs['Scale'].default_value = 30.0
        noise_bump.inputs['Detail'].default_value = 8.0
        bump_node = nodes.new(type='ShaderNodeBump')
        bump_node.location = (-200, -200)
        bump_node.inputs['Strength'].default_value = 0.25
        links.new(noise_bump.outputs['Fac'], bump_node.inputs['Height'])
        links.new(bump_node.outputs['Normal'], principled.inputs['Normal'])
        # Simple roughness variation
        noise_rough = nodes.new(type='ShaderNodeTexNoise')
        noise_rough.location = (-400, -400)
        noise_rough.inputs['Scale'].default_value = 12.0
        noise_rough.inputs['Detail'].default_value = 4.0
        rough_ramp = nodes.new(type='ShaderNodeValToRGB')
        rough_ramp.location = (-200, -400)
        rough_ramp.color_ramp.elements[0].position = 0.2
        rough_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)
        rough_ramp.color_ramp.elements[1].position = 0.8
        rough_ramp.color_ramp.elements[1].color = (0.25, 0.25, 0.25, 1.0)
        links.new(noise_rough.outputs['Fac'], rough_ramp.inputs['Fac'])
        links.new(rough_ramp.outputs['Color'], principled.inputs['Roughness'])
        return material
    
    def _add_mesh_gradients(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                           principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add sophisticated mesh gradients with medium-sized details"""
        # Get base color from JSON data
        base_color = material_data.get('base_color', [0.1, 0.3, 0.8, 1.0])
        
        # Create primary mesh gradient texture (medium scale)
        mesh_gradient1 = nodes.new(type='ShaderNodeTexNoise')
        mesh_gradient1.location = (-800, 200)
        mesh_gradient1.inputs['Scale'].default_value = 15.0  # Medium scale for mesh gradients
        mesh_gradient1.inputs['Detail'].default_value = 8.0
        mesh_gradient1.inputs['Roughness'].default_value = 0.6
        
        # Create secondary mesh gradient texture (larger scale)
        mesh_gradient2 = nodes.new(type='ShaderNodeTexNoise')
        mesh_gradient2.location = (-800, 400)
        mesh_gradient2.inputs['Scale'].default_value = 25.0  # Larger scale for broader gradients
        mesh_gradient2.inputs['Detail'].default_value = 6.0
        mesh_gradient2.inputs['Roughness'].default_value = 0.8
        
        # Create voronoi texture for mesh zones
        voronoi_mesh = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi_mesh.location = (-800, 600)
        voronoi_mesh.feature = 'DISTANCE_TO_EDGE'
        voronoi_mesh.inputs['Scale'].default_value = 20.0  # Medium scale for mesh zones
        
        # Create wave texture for mesh flow
        wave_mesh = nodes.new(type='ShaderNodeTexWave')
        wave_mesh.location = (-800, 800)
        wave_mesh.wave_type = 'RINGS'
        wave_mesh.inputs['Scale'].default_value = 18.0  # Medium scale for mesh flow
        wave_mesh.inputs['Distortion'].default_value = 1.5
        wave_mesh.inputs['Detail'].default_value = 4.0
        
        # Calculate color variations using color wheel theory
        complementary_color = [1.0 - base_color[0], 1.0 - base_color[1], 1.0 - base_color[2], base_color[3]]
        analogous_color1 = self._shift_hue(base_color, 30)
        analogous_color2 = self._shift_hue(base_color, -30)
        triadic_color1 = self._shift_hue(base_color, 120)
        triadic_color2 = self._shift_hue(base_color, -120)
        
        # Create primary mesh gradient color ramp
        mesh_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        mesh_ramp1.location = (-600, 200)
        mesh_ramp1.color_ramp.elements[0].position = 0.2
        mesh_ramp1.color_ramp.elements[0].color = [c * 0.4 for c in base_color[:3]] + [1.0]  # Dark base
        mesh_ramp1.color_ramp.elements[1].position = 0.8
        mesh_ramp1.color_ramp.elements[1].color = base_color  # Bright base
        
        # Create secondary mesh gradient color ramp
        mesh_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        mesh_ramp2.location = (-600, 400)
        mesh_ramp2.color_ramp.elements[0].position = 0.15
        mesh_ramp2.color_ramp.elements[0].color = [c * 0.5 for c in complementary_color[:3]] + [1.0]  # Dark complementary
        mesh_ramp2.color_ramp.elements[1].position = 0.85
        mesh_ramp2.color_ramp.elements[1].color = complementary_color  # Bright complementary
        
        # Create voronoi mesh color ramp
        mesh_ramp3 = nodes.new(type='ShaderNodeValToRGB')
        mesh_ramp3.location = (-600, 600)
        mesh_ramp3.color_ramp.elements[0].position = 0.25
        mesh_ramp3.color_ramp.elements[0].color = [c * 0.6 for c in analogous_color1[:3]] + [1.0]  # Dark analogous
        mesh_ramp3.color_ramp.elements[1].position = 0.75
        mesh_ramp3.color_ramp.elements[1].color = analogous_color1  # Bright analogous
        
        # Create wave mesh color ramp
        mesh_ramp4 = nodes.new(type='ShaderNodeValToRGB')
        mesh_ramp4.location = (-600, 800)
        mesh_ramp4.color_ramp.elements[0].position = 0.3
        mesh_ramp4.color_ramp.elements[0].color = [c * 0.7 for c in triadic_color1[:3]] + [1.0]  # Dark triadic
        mesh_ramp4.color_ramp.elements[1].position = 0.7
        mesh_ramp4.color_ramp.elements[1].color = triadic_color1  # Bright triadic
        
        # Mix primary and secondary mesh gradients
        mix_mesh1 = nodes.new(type='ShaderNodeMixRGB')
        mix_mesh1.location = (-400, 300)
        mix_mesh1.blend_type = 'OVERLAY'
        mix_mesh1.inputs['Fac'].default_value = 0.7
        
        # Mix voronoi and wave mesh gradients
        mix_mesh2 = nodes.new(type='ShaderNodeMixRGB')
        mix_mesh2.location = (-400, 700)
        mix_mesh2.blend_type = 'SOFT_LIGHT'
        mix_mesh2.inputs['Fac'].default_value = 0.6
        
        # Final mesh gradient mix
        final_mesh_mix = nodes.new(type='ShaderNodeMixRGB')
        final_mesh_mix.location = (-200, 500)
        final_mesh_mix.blend_type = 'MULTIPLY'
        final_mesh_mix.inputs['Fac'].default_value = 0.8
        
        # Link mesh gradient system
        links.new(mesh_gradient1.outputs['Fac'], mesh_ramp1.inputs['Fac'])
        links.new(mesh_gradient2.outputs['Fac'], mesh_ramp2.inputs['Fac'])
        links.new(voronoi_mesh.outputs['Distance'], mesh_ramp3.inputs['Fac'])
        links.new(wave_mesh.outputs['Fac'], mesh_ramp4.inputs['Fac'])
        
        links.new(mesh_ramp1.outputs['Color'], mix_mesh1.inputs['Color1'])
        links.new(mesh_ramp2.outputs['Color'], mix_mesh1.inputs['Color2'])
        
        links.new(mesh_ramp3.outputs['Color'], mix_mesh2.inputs['Color1'])
        links.new(mesh_ramp4.outputs['Color'], mix_mesh2.inputs['Color2'])
        
        links.new(mix_mesh1.outputs['Color'], final_mesh_mix.inputs['Color1'])
        links.new(mix_mesh2.outputs['Color'], final_mesh_mix.inputs['Color2'])
        
        # Apply mesh gradients to base color
        links.new(final_mesh_mix.outputs['Color'], principled.inputs['Base Color'])
    
    def setup_gem_scene(self, gem_data: Dict[str, Any], output_name: str) -> bool:
        """Setup complete gemstone scene with enhanced mesh gradients and Cycles rendering"""
        try:
            # Clear existing scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            
            # Set render engine to Cycles
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.cycles.samples = 128  # Good quality for preview
            bpy.context.scene.cycles.use_denoising = True
            
            # Create gemstone geometry
            gem_obj = self.create_gem_geometry(gem_data)
            if not gem_obj:
                print("❌ Failed to create gemstone geometry")
                return False
            
            # Create advanced material with mesh gradients
            material_data = gem_data.get('material', {})
            material = self.create_advanced_material(material_data)
            gem_obj.data.materials.append(material)
            
            # Setup professional lighting with enhanced world background
            lighting_data = gem_data.get('lighting', {})
            lighting_data['material'] = material_data  # Pass material data for world colors
            self.setup_professional_lighting(lighting_data)
            
            # Setup camera
            self.setup_camera(gem_data.get('camera', {}))
            
            # Save blend file
            output_path = Path(f"rendered_crystals/{output_name}.blend")
            output_path.parent.mkdir(exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
            
            print(f"✅ Blender scene created successfully")
            print(f"📁 Blend file: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating scene: {e}")
            return False
    

    
    def create_gem_material_with_engravings(self, gem_data: Dict[str, Any]) -> bpy.types.Material:
        """Create artistic gemstone material with integrated engravings"""
        print("🎨 Creating artistic gemstone material...")
        
        material = bpy.data.materials.new(name="Gem_Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create principled BSDF
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        # Create material output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        # Set artistic properties for realistic gemstone
        material_data = gem_data.get('material', {})
        base_color = material_data.get('base_color', [0.7, 0.4, 1.0, 1.0])
        
        # Handle base color input
        try:
            principled.inputs['Base Color'].default_value = base_color
        except:
            try:
                principled.inputs['Color'].default_value = base_color
            except:
                print("❌ Could not set base color")
        
        # Set IOR for realistic refraction (gemstone values)
        ior = material_data.get('ior', 1.6)
        try:
            principled.inputs['IOR'].default_value = ior
        except:
            print("❌ Could not set IOR value")
        
        # Set transmission for transparency (artistic gemstone look)
        transmission = material_data.get('transmission', 0.6)  # Much reduced from 0.85 to prevent overexposure
        try:
            principled.inputs['Transmission Weight'].default_value = transmission
        except:
            try:
                principled.inputs['Transmission'].default_value = transmission
            except:
                print("❌ Could not set transmission value")
        
        # Set roughness for smooth surface
        roughness = material_data.get('roughness', 0.05)  # Slightly higher for more realistic
        try:
            principled.inputs['Roughness'].default_value = roughness
        except:
            print("❌ Could not set roughness value")
        
        # Set metallic to 0 (gemstones are not metallic)
        try:
            principled.inputs['Metallic'].default_value = 0.0
        except:
            print("❌ Could not set metallic value")
        
        # Reduced subsurface scattering for less overexposure
        subsurface = material_data.get('subsurface', 0.1)  # Much reduced from 0.2
        subsurface_radius = material_data.get('subsurface_radius', [1.0, 0.6, 0.4])  # Much reduced
        try:
            principled.inputs['Subsurface Weight'].default_value = subsurface
            principled.inputs['Subsurface Radius'].default_value = subsurface_radius
        except:
            try:
                principled.inputs['Subsurface'].default_value = subsurface
                principled.inputs['Subsurface Radius'].default_value = subsurface_radius
            except:
                print("❌ Could not set subsurface scattering values")
        
        # Add artistic internal effects
        self._add_artistic_internal_effects(nodes, links, principled, material_data)
        
        # Add engraving texture if enabled
        engraving_data = gem_data.get('engraving', {})
        if engraving_data.get('enabled', False):
            self._add_engraving_texture(nodes, links, principled, engraving_data)
        
        # Remove emission entirely to prevent overexposure
        # Link principled to output directly
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _add_artistic_internal_effects(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                                     principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add detailed artistic internal effects for gemstone realism"""
        # Create multiple noise textures for complex internal structure
        noise1 = nodes.new(type='ShaderNodeTexNoise')
        noise1.location = (-800, -300)
        noise1.inputs['Scale'].default_value = 50.0
        noise1.inputs['Detail'].default_value = 16.0
        noise1.inputs['Roughness'].default_value = 0.8
        
        noise2 = nodes.new(type='ShaderNodeTexNoise')
        noise2.location = (-800, -100)
        noise2.inputs['Scale'].default_value = 25.0
        noise2.inputs['Detail'].default_value = 12.0
        noise2.inputs['Roughness'].default_value = 0.6
        
        # Create voronoi for crystal growth patterns
        voronoi1 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi1.location = (-800, 100)
        voronoi1.feature = 'DISTANCE_TO_EDGE'
        voronoi1.inputs['Scale'].default_value = 20.0
        
        voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi2.location = (-800, 300)
        voronoi2.feature = 'DISTANCE_TO_EDGE'
        voronoi2.inputs['Scale'].default_value = 35.0
        
        # Create wave texture for internal flow patterns
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-800, 500)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 30.0
        wave.inputs['Distortion'].default_value = 3.0
        wave.inputs['Detail'].default_value = 10.0
        
        # Mix multiple noise textures for complex internal structure
        mix_noise = nodes.new(type='ShaderNodeMixRGB')
        mix_noise.location = (-600, -200)
        mix_noise.blend_type = 'MULTIPLY'
        mix_noise.inputs['Fac'].default_value = 0.7
        
        # Mix voronoi patterns
        mix_voronoi = nodes.new(type='ShaderNodeMixRGB')
        mix_voronoi.location = (-600, 200)
        mix_voronoi.blend_type = 'ADD'
        mix_voronoi.inputs['Fac'].default_value = 0.5
        
        # Create color ramp for detailed internal structure
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 0)
        color_ramp.color_ramp.elements[0].position = 0.2
        color_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.1, 1.0)  # Very dark internal areas
        color_ramp.color_ramp.elements[1].position = 0.8
        color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # Bright areas
        
        # Mix internal effects with transmission
        mix_internal = nodes.new(type='ShaderNodeMixRGB')
        mix_internal.location = (-200, 0)
        mix_internal.blend_type = 'MULTIPLY'
        mix_internal.inputs['Fac'].default_value = 0.25  # Stronger effect
        
        # Link noise textures
        links.new(noise1.outputs['Fac'], mix_noise.inputs['Color1'])
        links.new(noise2.outputs['Fac'], mix_noise.inputs['Color2'])
        
        # Link voronoi patterns
        links.new(voronoi1.outputs['Distance'], mix_voronoi.inputs['Color1'])
        links.new(voronoi2.outputs['Distance'], mix_voronoi.inputs['Color2'])
        
        # Link wave texture
        links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
        
        # Mix all internal effects
        mix_final = nodes.new(type='ShaderNodeMixRGB')
        mix_final.location = (-400, 200)
        mix_final.blend_type = 'ADD'
        mix_final.inputs['Fac'].default_value = 0.6
        
        links.new(mix_noise.outputs['Color'], mix_final.inputs['Color1'])
        links.new(mix_voronoi.outputs['Color'], mix_final.inputs['Color2'])
        links.new(mix_final.outputs['Color'], color_ramp.inputs['Fac'])
        
        # Apply internal effects to transmission
        current_transmission = principled.inputs['Transmission Weight'].default_value
        mixed_transmission = current_transmission * 0.9  # Reduce transmission for internal structure
        principled.inputs['Transmission Weight'].default_value = mixed_transmission
        
        # Add complex bump mapping for internal structure
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (-200, 200)
        bump.inputs['Strength'].default_value = 0.3  # Stronger bump
        
        # Create bump mix
        bump_mix = nodes.new(type='ShaderNodeMixRGB')
        bump_mix.location = (-400, 200)
        bump_mix.blend_type = 'ADD'
        bump_mix.inputs['Fac'].default_value = 0.8
        
        links.new(voronoi1.outputs['Distance'], bump_mix.inputs['Color1'])
        links.new(noise1.outputs['Fac'], bump_mix.inputs['Color2'])
        links.new(bump_mix.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        
        # Add surface imperfections
        self._add_surface_imperfections(nodes, links, principled, material_data)
    
    def _add_engraving_texture(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                              principled: bpy.types.Node, engraving_data: Dict[str, Any]):
        """Add engraving texture to the material"""
        pattern_type = engraving_data.get('pattern', 'infinity')
        
        # Create engraving texture based on pattern
        if pattern_type == 'dragon':
            self._create_dragon_texture(nodes, links, principled, engraving_data)
        elif pattern_type == 'phoenix':
            self._create_phoenix_texture(nodes, links, principled, engraving_data)
        elif pattern_type == 'infinity':
            self._create_infinity_texture(nodes, links, principled, engraving_data)
        else:
            self._create_generic_engraving_texture(nodes, links, principled, engraving_data)
    
    def _create_dragon_texture(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                             principled: bpy.types.Node, engraving_data: Dict[str, Any]):
        """Create dragon engraving texture with enhanced visibility"""
        # Create voronoi texture for dragon scales
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-400, -200)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 12.0  # Larger scale for visibility
        
        # Create noise texture for dragon detail
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 20.0
        noise.inputs['Detail'].default_value = 10.0
        noise.inputs['Roughness'].default_value = 0.7
        
        # Create color ramp for dragon pattern with stronger contrast
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, -200)
        color_ramp.color_ramp.elements[0].position = 0.3  # More contrast
        color_ramp.color_ramp.elements[0].color = (1.0, 0.7, 0.2, 1.0)  # Bright golden dragon
        color_ramp.color_ramp.elements[1].position = 0.7
        color_ramp.color_ramp.elements[1].color = (0.1, 0.05, 0.0, 1.0)  # Dark background
        
        # Create second color ramp for additional detail
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-200, 0)
        color_ramp2.color_ramp.elements[0].position = 0.35
        color_ramp2.color_ramp.elements[0].color = (1.0, 0.8, 0.3, 1.0)  # Bright golden
        color_ramp2.color_ramp.elements[1].position = 0.65
        color_ramp2.color_ramp.elements[1].color = (0.2, 0.1, 0.0, 1.0)  # Dark background
        
        # Mix patterns
        mix_patterns = nodes.new(type='ShaderNodeMixRGB')
        mix_patterns.location = (0, -100)
        mix_patterns.blend_type = 'ADD'
        mix_patterns.inputs['Fac'].default_value = 0.6
        
        # Get current base color
        current_base_color = principled.inputs['Base Color'].default_value
        
        # Link nodes
        links.new(voronoi.outputs['Distance'], color_ramp.inputs['Fac'])
        links.new(noise.outputs['Fac'], color_ramp2.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_patterns.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix_patterns.inputs['Color2'])
        
        # Calculate mixed color with stronger effect
        mixed_color = [
            current_base_color[0] * (1 - 0.5) + (1.0 * 0.5),  # Stronger golden effect
            current_base_color[1] * (1 - 0.5) + (0.7 * 0.5),
            current_base_color[2] * (1 - 0.5) + (0.2 * 0.5),
            current_base_color[3]
        ]
        principled.inputs['Base Color'].default_value = mixed_color
        
        # Add bump mapping for engraving depth
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (0, 100)
        bump.inputs['Strength'].default_value = 0.6  # Stronger bump for visibility
        
        # Create bump mix
        bump_mix = nodes.new(type='ShaderNodeMixRGB')
        bump_mix.location = (-200, 100)
        bump_mix.blend_type = 'ADD'
        bump_mix.inputs['Fac'].default_value = 0.8
        
        links.new(voronoi.outputs['Distance'], bump_mix.inputs['Color1'])
        links.new(noise.outputs['Fac'], bump_mix.inputs['Color2'])
        links.new(bump_mix.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        
        print("✅ Dragon texture applied successfully with enhanced visibility")
    
    def _create_phoenix_texture(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                               principled: bpy.types.Node, engraving_data: Dict[str, Any]):
        """Create phoenix engraving texture with enhanced visibility"""
        # Create wave texture for phoenix flames
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-400, -200)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 15.0  # Larger scale for visibility
        wave.inputs['Distortion'].default_value = 3.0
        wave.inputs['Detail'].default_value = 12.0
        
        # Create noise texture for phoenix detail
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 25.0
        noise.inputs['Detail'].default_value = 8.0
        noise.inputs['Roughness'].default_value = 0.6
        
        # Create color ramp for phoenix pattern with stronger contrast
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, -200)
        color_ramp.color_ramp.elements[0].position = 0.25  # More contrast
        color_ramp.color_ramp.elements[0].color = (1.0, 0.9, 0.2, 1.0)  # Bright golden phoenix
        color_ramp.color_ramp.elements[1].position = 0.75
        color_ramp.color_ramp.elements[1].color = (0.8, 0.3, 0.0, 1.0)  # Orange-red
        
        # Create second color ramp for additional detail
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-200, 0)
        color_ramp2.color_ramp.elements[0].position = 0.3
        color_ramp2.color_ramp.elements[0].color = (1.0, 0.8, 0.3, 1.0)  # Bright golden
        color_ramp2.color_ramp.elements[1].position = 0.7
        color_ramp2.color_ramp.elements[1].color = (0.9, 0.4, 0.1, 1.0)  # Orange
        
        # Mix patterns
        mix_patterns = nodes.new(type='ShaderNodeMixRGB')
        mix_patterns.location = (0, -100)
        mix_patterns.blend_type = 'ADD'
        mix_patterns.inputs['Fac'].default_value = 0.7
        
        # Get current base color
        current_base_color = principled.inputs['Base Color'].default_value
        
        # Link nodes
        links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(noise.outputs['Fac'], color_ramp2.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_patterns.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix_patterns.inputs['Color2'])
        
        # Calculate mixed color with stronger effect
        mixed_color = [
            current_base_color[0] * (1 - 0.45) + (1.0 * 0.45),  # Stronger golden effect
            current_base_color[1] * (1 - 0.45) + (0.9 * 0.45),
            current_base_color[2] * (1 - 0.45) + (0.2 * 0.45),
            current_base_color[3]
        ]
        principled.inputs['Base Color'].default_value = mixed_color
        
        # Add bump mapping for engraving depth
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (0, 100)
        bump.inputs['Strength'].default_value = 0.5  # Stronger bump for visibility
        
        # Create bump mix
        bump_mix = nodes.new(type='ShaderNodeMixRGB')
        bump_mix.location = (-200, 100)
        bump_mix.blend_type = 'ADD'
        bump_mix.inputs['Fac'].default_value = 0.8
        
        links.new(wave.outputs['Fac'], bump_mix.inputs['Color1'])
        links.new(noise.outputs['Fac'], bump_mix.inputs['Color2'])
        links.new(bump_mix.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        
        print("✅ Phoenix texture applied successfully with enhanced visibility")
    
    def _create_infinity_texture(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                                principled: bpy.types.Node, engraving_data: Dict[str, Any]):
        """Create infinity symbol engraving texture with enhanced visibility"""
        # Create noise texture for infinity pattern
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, -200)
        noise.inputs['Scale'].default_value = 15.0  # Larger scale for more visible pattern
        noise.inputs['Detail'].default_value = 12.0
        noise.inputs['Roughness'].default_value = 0.8
        
        # Create voronoi texture for additional pattern detail
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-400, 0)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 20.0
        
        # Create color ramp for infinity pattern with stronger contrast
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, -200)
        color_ramp.color_ramp.elements[0].position = 0.35  # More contrast
        color_ramp.color_ramp.elements[0].color = (1.0, 0.8, 0.2, 1.0)  # Bright golden
        color_ramp.color_ramp.elements[1].position = 0.65
        color_ramp.color_ramp.elements[1].color = (0.1, 0.05, 0.0, 1.0)  # Dark background
        
        # Create second color ramp for pattern variation
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-200, 0)
        color_ramp2.color_ramp.elements[0].position = 0.4
        color_ramp2.color_ramp.elements[0].color = (1.0, 0.9, 0.3, 1.0)  # Bright golden
        color_ramp2.color_ramp.elements[1].position = 0.6
        color_ramp2.color_ramp.elements[1].color = (0.2, 0.1, 0.0, 1.0)  # Dark background
        
        # Mix the patterns
        mix_patterns = nodes.new(type='ShaderNodeMixRGB')
        mix_patterns.location = (0, -100)
        mix_patterns.blend_type = 'ADD'
        mix_patterns.inputs['Fac'].default_value = 0.7
        
        # Get current base color
        current_base_color = principled.inputs['Base Color'].default_value
        
        # Link nodes
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(voronoi.outputs['Distance'], color_ramp2.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_patterns.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix_patterns.inputs['Color2'])
        
        # Calculate mixed color with stronger effect
        mixed_color = [
            current_base_color[0] * (1 - 0.4) + (1.0 * 0.4),  # Stronger golden effect
            current_base_color[1] * (1 - 0.4) + (0.8 * 0.4),
            current_base_color[2] * (1 - 0.4) + (0.2 * 0.4),
            current_base_color[3]
        ]
        principled.inputs['Base Color'].default_value = mixed_color
        
        # Add bump mapping for engraving depth
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (0, 100)
        bump.inputs['Strength'].default_value = 0.5  # Stronger bump for visibility
        
        # Create bump mix
        bump_mix = nodes.new(type='ShaderNodeMixRGB')
        bump_mix.location = (-200, 100)
        bump_mix.blend_type = 'ADD'
        bump_mix.inputs['Fac'].default_value = 0.8
        
        links.new(noise.outputs['Fac'], bump_mix.inputs['Color1'])
        links.new(voronoi.outputs['Distance'], bump_mix.inputs['Color2'])
        links.new(bump_mix.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        
        print("✅ Infinity texture applied successfully with enhanced visibility")
    
    def _create_generic_engraving_texture(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                                        principled: bpy.types.Node, engraving_data: Dict[str, Any]):
        """Create generic engraving texture with enhanced visibility"""
        # Create voronoi texture for generic pattern
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-400, -200)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 10.0  # Larger scale for visibility
        
        # Create noise texture for additional detail
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 18.0
        noise.inputs['Detail'].default_value = 10.0
        noise.inputs['Roughness'].default_value = 0.7
        
        # Create color ramp for generic pattern with stronger contrast
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, -200)
        color_ramp.color_ramp.elements[0].position = 0.35  # More contrast
        color_ramp.color_ramp.elements[0].color = (1.0, 0.8, 0.2, 1.0)  # Bright golden engraving
        color_ramp.color_ramp.elements[1].position = 0.65
        color_ramp.color_ramp.elements[1].color = (0.1, 0.05, 0.0, 1.0)  # Dark background
        
        # Create second color ramp for additional detail
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-200, 0)
        color_ramp2.color_ramp.elements[0].position = 0.4
        color_ramp2.color_ramp.elements[0].color = (1.0, 0.9, 0.3, 1.0)  # Bright golden
        color_ramp2.color_ramp.elements[1].position = 0.6
        color_ramp2.color_ramp.elements[1].color = (0.2, 0.1, 0.0, 1.0)  # Dark background
        
        # Mix patterns
        mix_patterns = nodes.new(type='ShaderNodeMixRGB')
        mix_patterns.location = (0, -100)
        mix_patterns.blend_type = 'ADD'
        mix_patterns.inputs['Fac'].default_value = 0.6
        
        # Get current base color
        current_base_color = principled.inputs['Base Color'].default_value
        
        # Link nodes
        links.new(voronoi.outputs['Distance'], color_ramp.inputs['Fac'])
        links.new(noise.outputs['Fac'], color_ramp2.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_patterns.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix_patterns.inputs['Color2'])
        
        # Calculate mixed color with stronger effect
        mixed_color = [
            current_base_color[0] * (1 - 0.35) + (1.0 * 0.35),  # Stronger golden effect
            current_base_color[1] * (1 - 0.35) + (0.8 * 0.35),
            current_base_color[2] * (1 - 0.35) + (0.2 * 0.35),
            current_base_color[3]
        ]
        principled.inputs['Base Color'].default_value = mixed_color
        
        # Add bump mapping for engraving depth
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (0, 100)
        bump.inputs['Strength'].default_value = 0.4  # Stronger bump for visibility
        
        # Create bump mix
        bump_mix = nodes.new(type='ShaderNodeMixRGB')
        bump_mix.location = (-200, 100)
        bump_mix.blend_type = 'ADD'
        bump_mix.inputs['Fac'].default_value = 0.8
        
        links.new(voronoi.outputs['Distance'], bump_mix.inputs['Color1'])
        links.new(noise.outputs['Fac'], bump_mix.inputs['Color2'])
        links.new(bump_mix.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        
        print("✅ Generic engraving texture applied successfully with enhanced visibility")
    
    def _add_surface_imperfections(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                                 principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add sophisticated rock surface imperfections and geological features"""
        # Get surface imperfection settings
        surface_data = material_data.get('surface_imperfections', {})
        
        # Create primary surface noise (large scale geological features)
        surface_noise1 = nodes.new(type='ShaderNodeTexNoise')
        surface_noise1.location = (-1000, -800)
        surface_noise1.inputs['Scale'].default_value = surface_data.get('noise_scale', 25.0)
        surface_noise1.inputs['Detail'].default_value = 12.0
        surface_noise1.inputs['Roughness'].default_value = 0.8
        
        # Create secondary surface noise (medium scale weathering)
        surface_noise2 = nodes.new(type='ShaderNodeTexNoise')
        surface_noise2.location = (-1000, -600)
        surface_noise2.inputs['Scale'].default_value = surface_data.get('noise_scale', 25.0) * 0.6
        surface_noise2.inputs['Detail'].default_value = 16.0
        surface_noise2.inputs['Roughness'].default_value = 0.9
        
        # Create tertiary surface noise (fine scale erosion)
        surface_noise3 = nodes.new(type='ShaderNodeTexNoise')
        surface_noise3.location = (-1000, -400)
        surface_noise3.inputs['Scale'].default_value = surface_data.get('noise_scale', 25.0) * 0.3
        surface_noise3.inputs['Detail'].default_value = 20.0
        surface_noise3.inputs['Roughness'].default_value = 0.95
        
        # Create voronoi texture for fracture patterns
        fracture_voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        fracture_voronoi.location = (-1000, -200)
        fracture_voronoi.feature = 'DISTANCE_TO_EDGE'
        fracture_voronoi.inputs['Scale'].default_value = 35.0
        fracture_voronoi.inputs['Detail'].default_value = 8.0
        fracture_voronoi.inputs['Roughness'].default_value = 0.7
        
        # Create musgrave texture for geological strata
        strata_musgrave = nodes.new(type='ShaderNodeTexNoise')
        strata_musgrave.location = (-1000, 0)
        strata_musgrave.noise_type = 'MULTIFRACTAL'
        strata_musgrave.inputs['Scale'].default_value = 20.0
        strata_musgrave.inputs['Detail'].default_value = 10.0
        strata_musgrave.inputs['Lacunarity'].default_value = 2.5
        strata_musgrave.inputs['Roughness'].default_value = 0.8
        
        # Create wave texture for water erosion patterns
        erosion_wave = nodes.new(type='ShaderNodeTexWave')
        erosion_wave.location = (-1000, 200)
        erosion_wave.wave_type = 'RINGS'
        erosion_wave.inputs['Scale'].default_value = 15.0
        erosion_wave.inputs['Distortion'].default_value = 2.5
        erosion_wave.inputs['Detail'].default_value = 6.0
        
        # Create color ramp for primary surface features
        surface_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        surface_ramp1.location = (-800, -800)
        surface_ramp1.color_ramp.elements[0].position = 0.3
        surface_ramp1.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1.0)  # Deep crevices
        surface_ramp1.color_ramp.elements[1].position = 0.7
        surface_ramp1.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1.0)  # Elevated areas
        
        # Create color ramp for secondary weathering
        surface_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        surface_ramp2.location = (-800, -600)
        surface_ramp2.color_ramp.elements[0].position = 0.4
        surface_ramp2.color_ramp.elements[0].color = (0.2, 0.2, 0.2, 1.0)  # Weathered areas
        surface_ramp2.color_ramp.elements[1].position = 0.6
        surface_ramp2.color_ramp.elements[1].color = (0.5, 0.5, 0.5, 1.0)  # Less weathered
        
        # Create color ramp for fine erosion
        surface_ramp3 = nodes.new(type='ShaderNodeValToRGB')
        surface_ramp3.location = (-800, -400)
        surface_ramp3.color_ramp.elements[0].position = 0.45
        surface_ramp3.color_ramp.elements[0].color = (0.15, 0.15, 0.15, 1.0)  # Eroded areas
        surface_ramp3.color_ramp.elements[1].position = 0.55
        surface_ramp3.color_ramp.elements[1].color = (0.45, 0.45, 0.45, 1.0)  # Protected areas
        
        # Create color ramp for fracture patterns
        fracture_ramp = nodes.new(type='ShaderNodeValToRGB')
        fracture_ramp.location = (-800, -200)
        fracture_ramp.color_ramp.elements[0].position = 0.2
        fracture_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)  # Deep fractures
        fracture_ramp.color_ramp.elements[1].position = 0.8
        fracture_ramp.color_ramp.elements[1].color = (0.3, 0.3, 0.3, 1.0)  # Surface areas
        
        # Create color ramp for geological strata
        strata_ramp = nodes.new(type='ShaderNodeValToRGB')
        strata_ramp.location = (-800, 0)
        strata_ramp.color_ramp.elements[0].position = 0.35
        strata_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1.0)  # Lower strata
        strata_ramp.color_ramp.elements[1].position = 0.65
        strata_ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.35, 1.0)  # Upper strata
        
        # Create color ramp for erosion patterns
        erosion_ramp = nodes.new(type='ShaderNodeValToRGB')
        erosion_ramp.location = (-800, 200)
        erosion_ramp.color_ramp.elements[0].position = 0.25
        erosion_ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.08, 1.0)  # Eroded channels
        erosion_ramp.color_ramp.elements[1].position = 0.75
        erosion_ramp.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1.0)  # Elevated ridges
        
        # Mix primary and secondary surface features
        mix_surface1 = nodes.new(type='ShaderNodeMixRGB')
        mix_surface1.location = (-600, -700)
        mix_surface1.blend_type = 'MULTIPLY'
        mix_surface1.inputs['Fac'].default_value = 0.8
        
        # Mix tertiary and fracture features
        mix_surface2 = nodes.new(type='ShaderNodeMixRGB')
        mix_surface2.location = (-600, -300)
        mix_surface2.blend_type = 'OVERLAY'
        mix_surface2.inputs['Fac'].default_value = 0.7
        
        # Mix strata and erosion features
        mix_surface3 = nodes.new(type='ShaderNodeMixRGB')
        mix_surface3.location = (-600, 100)
        mix_surface3.blend_type = 'SOFT_LIGHT'
        mix_surface3.inputs['Fac'].default_value = 0.6
        
        # Final surface mix
        final_surface_mix = nodes.new(type='ShaderNodeMixRGB')
        final_surface_mix.location = (-400, -300)
        final_surface_mix.blend_type = 'MULTIPLY'
        final_surface_mix.inputs['Fac'].default_value = 0.9
        
        # Create bump mapping for surface displacement
        bump_surface = nodes.new(type='ShaderNodeBump')
        bump_surface.location = (-200, -300)
        bump_surface.inputs['Strength'].default_value = surface_data.get('bumps', 0.05)
        bump_surface.inputs['Distance'].default_value = 0.001
        
        # Create second bump for fine detail
        bump_fine = nodes.new(type='ShaderNodeBump')
        bump_fine.location = (-200, -100)
        bump_fine.inputs['Strength'].default_value = surface_data.get('scratches', 0.02)
        bump_fine.inputs['Distance'].default_value = 0.0005
        
        # Link sophisticated surface system
        links.new(surface_noise1.outputs['Fac'], surface_ramp1.inputs['Fac'])
        links.new(surface_noise2.outputs['Fac'], surface_ramp2.inputs['Fac'])
        links.new(surface_noise3.outputs['Fac'], surface_ramp3.inputs['Fac'])
        links.new(fracture_voronoi.outputs['Distance'], fracture_ramp.inputs['Fac'])
        links.new(strata_musgrave.outputs['Fac'], strata_ramp.inputs['Fac'])
        links.new(erosion_wave.outputs['Fac'], erosion_ramp.inputs['Fac'])
        
        links.new(surface_ramp1.outputs['Color'], mix_surface1.inputs['Color1'])
        links.new(surface_ramp2.outputs['Color'], mix_surface1.inputs['Color2'])
        
        links.new(surface_ramp3.outputs['Color'], mix_surface2.inputs['Color1'])
        links.new(fracture_ramp.outputs['Color'], mix_surface2.inputs['Color2'])
        
        links.new(strata_ramp.outputs['Color'], mix_surface3.inputs['Color1'])
        links.new(erosion_ramp.outputs['Color'], mix_surface3.inputs['Color2'])
        
        links.new(mix_surface1.outputs['Color'], final_surface_mix.inputs['Color1'])
        links.new(mix_surface2.outputs['Color'], final_surface_mix.inputs['Color2'])
        
        # Apply surface displacement
        links.new(final_surface_mix.outputs['Color'], bump_surface.inputs['Height'])
        links.new(bump_surface.outputs['Normal'], bump_fine.inputs['Normal'])
        links.new(bump_fine.outputs['Normal'], principled.inputs['Normal'])
        
        # Adjust roughness based on surface features
        roughness_mix = nodes.new(type='ShaderNodeMixRGB')
        roughness_mix.location = (-200, 100)
        roughness_mix.blend_type = 'MULTIPLY'
        roughness_mix.inputs['Fac'].default_value = 0.5
        
        # Create roughness ramp
        roughness_ramp = nodes.new(type='ShaderNodeValToRGB')
        roughness_ramp.location = (-400, 100)
        roughness_ramp.color_ramp.elements[0].position = 0.3
        roughness_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)  # Smooth areas
        roughness_ramp.color_ramp.elements[1].position = 0.7
        roughness_ramp.color_ramp.elements[1].color = (0.15, 0.15, 0.15, 1.0)  # Rough areas
        
        links.new(final_surface_mix.outputs['Color'], roughness_ramp.inputs['Fac'])
        links.new(roughness_ramp.outputs['Color'], roughness_mix.inputs['Color1'])
        links.new(roughness_mix.outputs['Color'], principled.inputs['Roughness'])
    
    def _add_internal_structure(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks,
                              principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add internal structure effects"""
        internal = material_data.get('internal_structure', {})
        
        if not internal:
            return
        
        # Create voronoi texture for crystal growth
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-400, -200)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 10.0
        
        # Create color ramp for inclusions
        inclusion_ramp = nodes.new(type='ShaderNodeValToRGB')
        inclusion_ramp.location = (-200, -200)
        try:
            inclusion_ramp.color_ramp.elements[0].position = 0.3
            inclusion_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            inclusion_ramp.color_ramp.elements[1].position = 0.7
            inclusion_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        except:
            # Alternative way to set color ramp
            inclusion_ramp.color_ramp.elements.remove(inclusion_ramp.color_ramp.elements[0])
            inclusion_ramp.color_ramp.elements.new(0.3)
            inclusion_ramp.color_ramp.elements.new(0.7)
            inclusion_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            inclusion_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        
        # Mix inclusions with transmission
        mix_transmission = nodes.new(type='ShaderNodeMixRGB')
        mix_transmission.location = (-50, -200)
        mix_transmission.blend_type = 'MULTIPLY'
        mix_transmission.inputs['Fac'].default_value = internal.get('inclusions', 0.2)
        
        # Link nodes
        links.new(voronoi.outputs['Distance'], inclusion_ramp.inputs['Fac'])
        links.new(inclusion_ramp.outputs['Color'], mix_transmission.inputs['Color1'])
        
        # Handle transmission (different versions have different names)
        # Since transmission is an input, not an output, we'll use a different approach
        transmission_value = nodes.new(type='ShaderNodeValue')
        transmission_value.location = (-300, -200)
        transmission_value.outputs['Value'].default_value = principled.inputs['Transmission Weight'].default_value
        
        try:
            links.new(transmission_value.outputs['Value'], mix_transmission.inputs['Color2'])
            links.new(mix_transmission.outputs['Color'], principled.inputs['Transmission Weight'])
        except:
            print("Warning: Could not connect transmission value")
            return
    
    def _add_complex_internal_effects(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks,
                                    principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add complex internal effects like inclusions, fractures, and crystal growth"""
        internal = material_data.get('internal_structure', {})
        
        if not internal:
            return
        
        # Create noise texture for crystal growth patterns
        crystal_noise = nodes.new(type='ShaderNodeTexNoise')
        crystal_noise.location = (-600, -300)
        crystal_noise.inputs['Scale'].default_value = 15.0
        crystal_noise.inputs['Detail'].default_value = 12.0
        crystal_noise.inputs['Roughness'].default_value = 0.8
        
        # Create voronoi for inclusions
        inclusion_voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        inclusion_voronoi.location = (-600, -100)
        inclusion_voronoi.feature = 'DISTANCE_TO_EDGE'
        inclusion_voronoi.inputs['Scale'].default_value = 20.0
        
        # Create color ramp for inclusions
        inclusion_ramp = nodes.new(type='ShaderNodeValToRGB')
        inclusion_ramp.location = (-400, -100)
        try:
            inclusion_ramp.color_ramp.elements[0].position = 0.2
            inclusion_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            inclusion_ramp.color_ramp.elements[1].position = 0.8
            inclusion_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        except:
            pass
        
        # Mix inclusions with transmission
        mix_inclusions = nodes.new(type='ShaderNodeMixRGB')
        mix_inclusions.location = (-200, -100)
        mix_inclusions.blend_type = 'MULTIPLY'
        mix_inclusions.inputs['Fac'].default_value = internal.get('inclusions', 0.3)
        
        # Link nodes
        links.new(inclusion_voronoi.outputs['Distance'], inclusion_ramp.inputs['Fac'])
        links.new(inclusion_ramp.outputs['Color'], mix_inclusions.inputs['Color1'])
        
        # Handle transmission weight connection
        # Since transmission is an input, not an output, we'll use a different approach
        transmission_value = nodes.new(type='ShaderNodeValue')
        transmission_value.location = (-400, -100)
        transmission_value.outputs['Value'].default_value = principled.inputs['Transmission Weight'].default_value
        
        try:
            links.new(transmission_value.outputs['Value'], mix_inclusions.inputs['Color2'])
            links.new(mix_inclusions.outputs['Color'], principled.inputs['Transmission Weight'])
        except:
            print("Warning: Could not connect transmission for inclusions")
    
    def _add_caustics_effects(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks,
                             principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add caustics and light scattering effects"""
        caustics = material_data.get('caustics', {})
        
        if not caustics:
            return
        
        # Create wave texture for caustics
        wave_tex = nodes.new(type='ShaderNodeTexWave')
        wave_tex.location = (-600, -500)
        wave_tex.wave_type = 'RINGS'
        wave_tex.inputs['Scale'].default_value = 50.0
        wave_tex.inputs['Distortion'].default_value = 2.0
        wave_tex.inputs['Detail'].default_value = 8.0
        
        # Create color ramp for caustics
        caustics_ramp = nodes.new(type='ShaderNodeValToRGB')
        caustics_ramp.location = (-400, -500)
        try:
            caustics_ramp.color_ramp.elements[0].position = 0.4
            caustics_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            caustics_ramp.color_ramp.elements[1].position = 0.6
            caustics_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        except:
            pass
        
        # Mix caustics with emission
        mix_caustics = nodes.new(type='ShaderNodeMixRGB')
        mix_caustics.location = (-200, -500)
        mix_caustics.blend_type = 'ADD'
        mix_caustics.inputs['Fac'].default_value = caustics.get('strength', 0.2)
        
        # Link nodes
        links.new(wave_tex.outputs['Fac'], caustics_ramp.inputs['Fac'])
        links.new(caustics_ramp.outputs['Color'], mix_caustics.inputs['Color1'])
        
        # Handle base color connection
        base_color_output = None
        for output_name in ['Base Color', 'Color']:
            if output_name in principled.outputs:
                base_color_output = principled.outputs[output_name]
                break
        
        if base_color_output:
            try:
                links.new(base_color_output, mix_caustics.inputs['Color2'])
                links.new(mix_caustics.outputs['Color'], principled.inputs['Base Color'])
            except:
                print("Warning: Could not connect base color for caustics")
        else:
            print("Warning: Could not find base color output for caustics")
    
    def create_engraving_material(self, engraving_data: Dict[str, Any]) -> bpy.types.Material:
        """Create material for metallic engravings"""
        print("🏆 Creating engraving material...")
        
        material = bpy.data.materials.new(name="Engraving_Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create principled BSDF
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        # Create material output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # Link principled to output
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Set metal properties based on metal type
        metal_type = engraving_data.get('metal_type', 'gold')
        metal_props = {
            "gold": {"color": [1.0, 0.8, 0.0, 1.0], "metallic": 1.0, "roughness": 0.1},
            "silver": {"color": [0.9, 0.9, 0.9, 1.0], "metallic": 1.0, "roughness": 0.05},
            "platinum": {"color": [0.8, 0.8, 0.8, 1.0], "metallic": 1.0, "roughness": 0.08},
            "copper": {"color": [0.8, 0.5, 0.2, 1.0], "metallic": 1.0, "roughness": 0.15}
        }
        
        props = metal_props.get(metal_type, metal_props["gold"])
        principled.inputs['Base Color'].default_value = props["color"]
        principled.inputs['Metallic'].default_value = props["metallic"]
        principled.inputs['Roughness'].default_value = props["roughness"]
        
        return material
    
    def setup_professional_lighting(self, lighting_data: Dict[str, Any]):
        """Setup professional photo studio lighting with light planes and no world background"""
        print("💡 Setting up professional photo studio lighting...")
        
        # Remove world background entirely
        world = bpy.context.scene.world
        world.use_nodes = False
        world.color = (0, 0, 0)  # Pure black background
        
        # Get lighting settings from JSON or use defaults
        lighting_config = {
            'key_light': {
                'type': 'AREA',
                'energy': 800,
                'color': (1.0, 1.0, 1.0),  # Pure white key light
                'location': (2.5, -3.0, 4.0),
                'rotation': (45, 0, 45),
                'size': 3.0
            },
            'fill_light': {
                'type': 'AREA',
                'energy': 400,
                'color': (0.9, 0.95, 1.0),  # Slightly cool fill light
                'location': (-2.0, -2.0, 3.0),
                'rotation': (30, 0, -30),
                'size': 2.5
            },
            'back_light': {
                'type': 'AREA',
                'energy': 600,
                'color': (1.0, 0.98, 0.95),  # Slightly warm back light
                'location': (0, 4.0, 2.5),
                'rotation': (-60, 0, 0),
                'size': 2.0
            },
            'rim_light': {
                'type': 'AREA',
                'energy': 300,
                'color': (0.95, 0.9, 1.0),  # Slightly purple rim light
                'location': (3.0, 1.0, 1.5),
                'rotation': (0, 45, 0),
                'size': 1.5
            },
            'bottom_light': {
                'type': 'AREA',
                'energy': 200,
                'color': (1.0, 1.0, 1.0),  # White bottom light
                'location': (0, 0, -2.0),
                'rotation': (0, 0, 0),
                'size': 4.0
            },
            'back_plane': {
                'type': 'AREA',
                'energy': 150,
                'color': (0.95, 0.95, 1.0),  # Slightly cool back plane
                'location': (0, 6.0, 0),
                'rotation': (0, 0, 0),
                'size': 8.0
            }
        }
        
        # Override with JSON settings if provided
        if lighting_data:
            for light_name, light_config in lighting_config.items():
                if light_name in lighting_data:
                    json_light = lighting_data[light_name]
                    # Convert RGBA to RGB if needed
                    color = json_light.get('color', light_config['color'])
                    if len(color) == 4:
                        color = color[:3]  # Take only RGB values
                    
                    light_config.update({
                        'energy': json_light.get('strength', light_config['energy']),
                        'color': color,
                        'location': json_light.get('position', light_config['location'])
                    })
        
        # Create each light
        for light_name, light_config in lighting_config.items():
            self._create_photo_studio_light(light_name, light_config)
    
    def _create_photo_studio_light(self, name: str, light_config: Dict[str, Any]):
        """Create a photo studio light with professional settings"""
        # Create light object
        light_obj = bpy.data.objects.new(name, bpy.data.lights.new(name=name, type=light_config['type']))
        bpy.context.scene.collection.objects.link(light_obj)
        
        # Set light properties
        light = light_obj.data
        light.energy = light_config['energy']
        light.color = light_config['color']
        light.size = light_config['size']
        
        # Set object properties
        light_obj.location = light_config['location']
        light_obj.rotation_euler = [math.radians(angle) for angle in light_config['rotation']]
        
        # Configure area light for photo studio quality
        if light_config['type'] == 'AREA':
            light.shape = 'RECTANGLE'
            light.size_y = light_config['size'] * 0.7
            
            # Add subtle shadow settings for professional look
            if hasattr(light, 'shadow_soft_size'):
                light.shadow_soft_size = 0.3
            
            # Enable contact shadows for better realism
            if hasattr(light, 'use_contact_shadow'):
                light.use_contact_shadow = True
    
    def setup_camera(self, camera_data: Dict[str, Any]):
        """Setup camera for optimal gemstone viewing with proper framing and headroom"""
        print("📷 Setting up camera...")
        
        # Get camera settings from JSON or use defaults
        position = camera_data.get('position', [0.0, -20.0, 10.0])  # Much further back and higher for generous headroom
        rotation = camera_data.get('rotation', [12.0, 0.0, 0.0])  # Gentler downward angle
        lens = camera_data.get('lens', 50.0)  # Wider lens for better framing
        f_stop = camera_data.get('f_stop', 8.0)  # Higher f-stop for more depth of field
        focus_distance = camera_data.get('focus_distance', 20.0)  # Focus on stone distance
        
        # Create camera if it doesn't exist
        if 'Camera' not in bpy.data.objects:
            bpy.ops.object.camera_add(location=position)
            camera = bpy.context.active_object
            camera.name = 'Camera'
        else:
            camera = bpy.data.objects['Camera']
            camera.location = position
        
        # Set camera rotation
        camera.rotation_euler = [math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2])]
        
        # Make this the active camera
        bpy.context.scene.camera = camera
        
        # Configure camera settings
        camera.data.lens = lens
        camera.data.dof.use_dof = True
        camera.data.dof.aperture_fstop = f_stop
        camera.data.dof.focus_distance = focus_distance
        
        # Set camera to look at the gemstone
        gem_obj = None
        for obj in bpy.data.objects:
            if 'Gem_' in obj.name:
                gem_obj = obj
                break
        
        if gem_obj:
            # Calculate optimal camera position for full stone visibility with generous headroom
            stone_size = max(gem_obj.dimensions.x, gem_obj.dimensions.y, gem_obj.dimensions.z)
            distance = stone_size * 12.0  # Much larger margin for generous headroom
            height_factor = 0.6  # Lower height for better framing
            
            camera = bpy.context.scene.camera
            camera.location = (0.0, -distance, distance * height_factor)
            camera.data.dof.focus_distance = distance
            
            # Ensure camera looks at the gemstone
            constraint = camera.constraints.new(type='TRACK_TO')
            constraint.target = gem_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
        
        print("✅ Camera setup completed")
    
    def setup_render_settings(self, render_data: Dict[str, Any]):
        """Setup render settings for transparent PNG output"""
        print("🎬 Setting up render settings...")
        
        # Get render settings from JSON or use defaults
        resolution_x = render_data.get('resolution_x', 1920)
        resolution_y = render_data.get('resolution_y', 1080)
        samples = render_data.get('samples', 512)  # Reduced for faster preview
        max_bounces = render_data.get('max_bounces', 12)
        use_denoising = render_data.get('use_denoising', True)
        file_format = render_data.get('file_format', 'PNG')
        color_depth = render_data.get('color_depth', '16')
        
        # Set render engine to Cycles
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.samples = samples
        bpy.context.scene.cycles.max_bounces = max_bounces
        bpy.context.scene.cycles.use_denoising = use_denoising
        
        # Set resolution
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.render.resolution_percentage = 100
        
        # Set file format for transparent PNG
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        bpy.context.scene.render.image_settings.color_depth = color_depth
        
        # Enable transparency
        bpy.context.scene.render.film_transparent = True
        
        # Set output path
        output_path = Path("rendered_crystals")
        output_path.mkdir(exist_ok=True)
        
        print("✅ Render settings configured")
    
    def render_gem(self, gem_data: Dict[str, Any], output_name: str) -> bool:
        """Render the gemstone with transparent background"""
        try:
            print("🎬 Rendering gemstone...")
            
            # Setup render settings
            render_data = gem_data.get('render_settings', {})
            self.setup_render_settings(render_data)
            
            # Setup camera for optimal viewing
            camera_data = gem_data.get('camera', {})
            self.setup_camera(camera_data)
            
            # Ensure gemstone is visible and properly framed
            gem_obj = None
            for obj in bpy.data.objects:
                if 'Gem_' in obj.name:
                    gem_obj = obj
                    break
            
            if gem_obj:
                # Calculate optimal camera position for full stone visibility with generous headroom
                stone_size = max(gem_obj.dimensions.x, gem_obj.dimensions.y, gem_obj.dimensions.z)
                distance = stone_size * 12.0  # Much larger margin for generous headroom
                height_factor = 0.6  # Lower height for better framing
                
                camera = bpy.context.scene.camera
                camera.location = (0.0, -distance, distance * height_factor)
                camera.data.dof.focus_distance = distance
                
                # Ensure camera looks at the gemstone
                constraint = camera.constraints.new(type='TRACK_TO')
                constraint.target = gem_obj
                constraint.track_axis = 'TRACK_NEGATIVE_Z'
                constraint.up_axis = 'UP_Y'
            
            # Set output file path
            output_path = Path(f"rendered_crystals/{output_name}.png")
            bpy.context.scene.render.filepath = str(output_path)
            
            # Render the image
            bpy.ops.render.render(write_still=True)
            
            print(f"✅ Render completed successfully")
            print(f"📁 PNG file: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Render failed: {e}")
            return False
    
    def create_gem_from_json(self, json_file: str) -> bool:
        """Create complete gemstone from JSON file"""
        print("🚀 Starting gemstone creation from JSON...")
        print("=" * 50)
        
        try:
            # Clear scene
            self.clear_scene()
            
            # Load gemstone specification
            gem_data = self.load_gem_json(json_file)
            
            # Create geometry
            gem_obj = self.create_gem_geometry(gem_data)
            
            # Create materials and setup scene
            output_name = gem_data.get('name', 'GeneratedGem')
            success = self.setup_gem_scene(gem_data, output_name)
            
            if success:
                print("=" * 50)
                print("🎉 Gemstone creation completed successfully!")
                print(f"Created: {gem_data['name']}")
                print(f"Gem type: {gem_data.get('gem_type', 'unknown')}")
                print(f"Base shape: {gem_data.get('base_shape', 'unknown')}")
                print(f"📁 Blend file saved for debugging")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Gemstone creation failed: {e}")
            return False
    
    def _add_organic_color_gradients(self, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, 
                                   principled: bpy.types.Node, material_data: Dict[str, Any]):
        """Add complex organic color gradients using color wheel theory from JSON data"""
        # Create multiple noise textures for color variation
        noise_color1 = nodes.new(type='ShaderNodeTexNoise')
        noise_color1.location = (-800, -600)
        noise_color1.inputs['Scale'].default_value = 8.0  # Larger scale for broader color zones
        noise_color1.inputs['Detail'].default_value = 12.0
        noise_color1.inputs['Roughness'].default_value = 0.7
        
        noise_color2 = nodes.new(type='ShaderNodeTexNoise')
        noise_color2.location = (-800, -400)
        noise_color2.inputs['Scale'].default_value = 4.0  # Smaller scale for fine detail
        noise_color2.inputs['Detail'].default_value = 16.0
        noise_color2.inputs['Roughness'].default_value = 0.9
        
        # Create voronoi for color zones
        voronoi_color = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi_color.location = (-800, -200)
        voronoi_color.feature = 'DISTANCE_TO_EDGE'
        voronoi_color.inputs['Scale'].default_value = 6.0
        
        # Create wave texture for color flow
        wave_color = nodes.new(type='ShaderNodeTexWave')
        wave_color.location = (-800, 0)
        wave_color.wave_type = 'RINGS'
        wave_color.inputs['Scale'].default_value = 10.0
        wave_color.inputs['Distortion'].default_value = 2.0
        wave_color.inputs['Detail'].default_value = 8.0
        
        # Get base color from JSON data
        base_color = material_data.get('base_color', [0.1, 0.3, 0.8, 1.0])
        
        # Create sophisticated color variations using color wheel theory
        # Calculate complementary color (opposite on color wheel)
        complementary_color = [1.0 - base_color[0], 1.0 - base_color[1], 1.0 - base_color[2], base_color[3]]
        
        # Calculate analogous colors (adjacent on color wheel)
        # Shift hue by 30 degrees for analogous colors
        analogous_color1 = self._shift_hue(base_color, 30)
        analogous_color2 = self._shift_hue(base_color, -30)
        
        # Calculate triadic colors (120 degrees apart on color wheel)
        triadic_color1 = self._shift_hue(base_color, 120)
        triadic_color2 = self._shift_hue(base_color, -120)
        
        # Create primary color ramp with sophisticated gradient
        color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp1.location = (-600, -400)
        color_ramp1.color_ramp.elements[0].position = 0.1
        color_ramp1.color_ramp.elements[0].color = [c * 0.3 for c in base_color[:3]] + [1.0]  # Dark primary
        color_ramp1.color_ramp.elements[1].position = 0.9
        color_ramp1.color_ramp.elements[1].color = base_color  # Bright primary
        
        # Create complementary color ramp
        color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp2.location = (-600, -200)
        color_ramp2.color_ramp.elements[0].position = 0.2
        color_ramp2.color_ramp.elements[0].color = [c * 0.4 for c in complementary_color[:3]] + [1.0]  # Dark complementary
        color_ramp2.color_ramp.elements[1].position = 0.8
        color_ramp2.color_ramp.elements[1].color = complementary_color  # Bright complementary
        
        # Create analogous color ramp
        color_ramp3 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp3.location = (-600, 0)
        color_ramp3.color_ramp.elements[0].position = 0.15
        color_ramp3.color_ramp.elements[0].color = [c * 0.5 for c in analogous_color1[:3]] + [1.0]  # Dark analogous
        color_ramp3.color_ramp.elements[1].position = 0.85
        color_ramp3.color_ramp.elements[1].color = analogous_color1  # Bright analogous
        
        # Create triadic color ramp
        color_ramp4 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp4.location = (-600, 200)
        color_ramp4.color_ramp.elements[0].position = 0.25
        color_ramp4.color_ramp.elements[0].color = [c * 0.6 for c in triadic_color1[:3]] + [1.0]  # Dark triadic
        color_ramp4.color_ramp.elements[1].position = 0.75
        color_ramp4.color_ramp.elements[1].color = triadic_color1  # Bright triadic
        
        # Mix primary and complementary colors
        mix_primary_comp = nodes.new(type='ShaderNodeMixRGB')
        mix_primary_comp.location = (-400, -300)
        mix_primary_comp.blend_type = 'OVERLAY'
        mix_primary_comp.inputs['Fac'].default_value = 0.6
        
        # Mix analogous and triadic colors
        mix_analogous_triadic = nodes.new(type='ShaderNodeMixRGB')
        mix_analogous_triadic.location = (-400, 100)
        mix_analogous_triadic.blend_type = 'SOFT_LIGHT'
        mix_analogous_triadic.inputs['Fac'].default_value = 0.5
        
        # Final sophisticated color mix
        final_color_mix = nodes.new(type='ShaderNodeMixRGB')
        final_color_mix.location = (-200, -100)
        final_color_mix.blend_type = 'MULTIPLY'
        final_color_mix.inputs['Fac'].default_value = 0.7
        
        # Link sophisticated color system
        links.new(noise_color1.outputs['Fac'], color_ramp1.inputs['Fac'])
        links.new(noise_color2.outputs['Fac'], color_ramp2.inputs['Fac'])
        links.new(voronoi_color.outputs['Distance'], color_ramp3.inputs['Fac'])
        links.new(wave_color.outputs['Fac'], color_ramp4.inputs['Fac'])
        
        links.new(color_ramp1.outputs['Color'], mix_primary_comp.inputs['Color1'])
        links.new(color_ramp2.outputs['Color'], mix_primary_comp.inputs['Color2'])
        
        links.new(color_ramp3.outputs['Color'], mix_analogous_triadic.inputs['Color1'])
        links.new(color_ramp4.outputs['Color'], mix_analogous_triadic.inputs['Color2'])
        
        links.new(mix_primary_comp.outputs['Color'], final_color_mix.inputs['Color1'])
        links.new(mix_analogous_triadic.outputs['Color'], final_color_mix.inputs['Color2'])
        
        # Apply sophisticated color to base color
        links.new(final_color_mix.outputs['Color'], principled.inputs['Base Color'])
    
    def _shift_hue(self, color: List[float], degrees: float) -> List[float]:
        """Shift the hue of a color by the specified degrees"""
        # Convert RGB to HSV
        r, g, b = color[:3]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Shift hue by degrees (convert to 0-1 range)
        h_shifted = (h + degrees / 360.0) % 1.0
        
        # Convert back to RGB
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_shifted, s, v)
        
        return [r_new, g_new, b_new, color[3]]

    def setup_eevee_render_settings(self, render_data: Dict[str, Any]):
        """Setup Eevee render settings for GLTF/GLB export (Blender 4.5+)"""
        print("🎬 Setting up Eevee render settings for GLB export...")
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'  # Blender 4.5+ engine name
        # SSR and refraction settings are not available in Eevee Next (Blender 4.5+)
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.eevee.taa_render_samples = render_data.get('samples', 128)
        bpy.context.scene.render.resolution_x = render_data.get('resolution_x', 1920)
        bpy.context.scene.render.resolution_y = render_data.get('resolution_y', 1080)
        bpy.context.scene.render.resolution_percentage = 100
        print("✅ Eevee render settings configured")

    def bake_material_to_textures(self, obj, output_dir, bake_types=["Base Color", "Roughness", "Normal"]):
        """Bake procedural material channels to image textures and assign them to Principled BSDF (must use Cycles for baking)"""
        print("🔥 Baking material to textures for GLTF export...")
        bpy.context.scene.render.engine = 'CYCLES'
        mat = obj.active_material
        if not mat or not mat.use_nodes:
            print("❌ No node material found for baking.")
            return
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not principled:
            print("❌ No Principled BSDF found for baking.")
            return
        if not obj.data.uv_layers or len(obj.data.uv_layers) == 0:
            print("🟡 No UV map found. Creating one with Smart UV Project...")
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')
        uv_layer = obj.data.uv_layers.active
        if len(obj.material_slots) > 1:
            obj.active_material_index = 0
            for i in range(len(obj.material_slots) - 1, 0, -1):
                obj.active_material_index = i
                bpy.ops.object.material_slot_remove()
        baked_images = {}
        for bake_type in bake_types:
            print(f"🟠 Baking {bake_type} from procedural material...")
            img = bpy.data.images.new(f"{obj.name}_{bake_type}_Baked", width=1024, height=1024)
            baked_images[bake_type] = img
            img_node = nodes.new(type='ShaderNodeTexImage')
            img_node.image = img
            for n in nodes:
                n.select = False
            img_node.select = True
            nodes.active = img_node
            bpy.context.view_layer.objects.active = obj
            if bake_type == "Base Color":
                bpy.ops.object.bake(type='DIFFUSE', use_clear=True, margin=2, pass_filter={'COLOR'})
            elif bake_type == "Roughness":
                bpy.ops.object.bake(type='ROUGHNESS', use_clear=True, margin=2)
            elif bake_type == "Normal":
                bpy.ops.object.bake(type='NORMAL', use_clear=True, margin=2)
            img.filepath_raw = str(output_dir / f"{obj.name}_{bake_type}_Baked.png")
            img.file_format = 'PNG'
            img.save()
            nodes.remove(img_node)
            print(f"🟢 Finished baking {bake_type}.")
        print("🎨 Assigning baked textures to new Principled BSDF for export...")
        export_mat = bpy.data.materials.new(name="GLB_Export_Material")
        export_mat.use_nodes = True
        export_nodes = export_mat.node_tree.nodes
        export_links = export_mat.node_tree.links
        export_nodes.clear()
        export_principled = export_nodes.new(type='ShaderNodeBsdfPrincipled')
        export_output = export_nodes.new(type='ShaderNodeOutputMaterial')
        export_links.new(export_principled.outputs['BSDF'], export_output.inputs['Surface'])
        for bake_type, img in baked_images.items():
            img_node = export_nodes.new(type='ShaderNodeTexImage')
            img_node.image = img
            if bake_type == "Base Color":
                export_links.new(img_node.outputs['Color'], export_principled.inputs['Base Color'])
            elif bake_type == "Roughness":
                export_links.new(img_node.outputs['Color'], export_principled.inputs['Roughness'])
            elif bake_type == "Normal":
                normal_map = export_nodes.new(type='ShaderNodeNormalMap')
                export_links.new(img_node.outputs['Color'], normal_map.inputs['Color'])
                export_links.new(normal_map.outputs['Normal'], export_principled.inputs['Normal'])
        obj.data.materials.clear()
        obj.data.materials.append(export_mat)
        print("✅ Baking and material assignment for GLB export complete.")
        # After baking, you can switch back to Eevee Next for GLB export if desired

    def export_gem_to_glb(self, obj, output_path):
        """Export the gemstone object as a GLB file"""
        print(f"🌐 Exporting {obj.name} to GLB: {output_path}")
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB', use_selection=True)
        print(f"✅ Exported GLB: {output_path}")

def main():
    """Main function to create gemstone from JSON and export as GLB with baked textures (Eevee only)"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: blender --background --python blender_gem_creator.py -- <json_file>")
        sys.exit(1)
    json_file = sys.argv[-1]  # Last argument is the JSON file
    print("🚀 Starting gemstone creation from JSON for GLB export...")
    print("=" * 50)
    creator = BlenderGemCreator()
    try:
        # Clear scene
        creator.clear_scene()
        # Load gemstone specification
        gem_data = creator.load_gem_json(json_file)
        gem_name = gem_data.get('name', 'UnknownGem')
        # Create geometry
        gem_obj = creator.create_gem_geometry(gem_data)
        # Create material and assign
        material_data = gem_data.get('material', {})
        material = creator.create_advanced_material(material_data)
        gem_obj.data.materials.append(material)
        # Setup Eevee for GLB
        render_data = gem_data.get('render_settings', {})
        creator.setup_eevee_render_settings(render_data)
        # Bake all relevant channels to textures and assign
        creator.bake_material_to_textures(gem_obj, creator.output_dir)
        # Export as GLB
        glb_path = creator.output_dir / f"{gem_name}.glb"
        creator.export_gem_to_glb(gem_obj, glb_path)
        print("=" * 50)
        print(f"🎉 Gemstone GLB export completed successfully!\nCreated: {gem_name}\nGLB file: {glb_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 