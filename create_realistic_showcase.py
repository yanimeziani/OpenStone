#!/usr/bin/env python3
"""
Create Realistic Rock Showcase
Generate a proper realistic rock with displacement, detailed materials, and procedural textures
"""

import sys
from pathlib import Path
import math
import random

# Add openstone to path
sys.path.insert(0, str(Path(__file__).parent))

import bpy
import bmesh
from mathutils import Vector, Euler
from openstone import AIGemGenerator, MeshCreator, MaterialManager, LightingManager
from openstone.mesh_creator import BaseMeshGenerator
from openstone.material_manager import BaseMaterialStyle
from openstone.lighting_manager import BaseLightingSetup, BaseWorldEnvironment


class RealisticRockGenerator(BaseMeshGenerator):
    """Realistic rock generator with proper displacement and detail"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a realistic rock with high detail"""
        # Start with a base mesh
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, location=(0, 0, 0))
        rock = bpy.context.active_object
        rock.name = "RealisticRock"
        
        # Apply initial deformation
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Scale irregularly for natural rock shape
        scale_variation = geometry_data.get('scale_variation', [1.2, 0.8, 1.1])
        bpy.ops.transform.resize(value=scale_variation)
        
        # Add random deformation using vertex random
        bpy.ops.transform.vertex_random(offset=geometry_data.get('noise_factor', 0.3))
        
        # Add more subdivisions for detail
        subdivision_levels = geometry_data.get('subdivision_levels', 3)
        for i in range(subdivision_levels):
            bpy.ops.mesh.subdivide(number_cuts=1)
            if i < subdivision_levels - 1:
                # Add progressively smaller noise
                bpy.ops.transform.vertex_random(offset=0.1 / (i + 1))
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add displacement modifier for micro-detail
        self._add_displacement_modifiers(rock, geometry_data)
        
        # Add subdivision surface for smooth displacement
        subdiv_mod = rock.modifiers.new(name="Subdivision", type='SUBSURF')
        subdiv_mod.levels = 2
        subdiv_mod.render_levels = 3
        
        return rock
    
    def _add_displacement_modifiers(self, obj, geometry_data):
        """Add multiple displacement modifiers for realistic rock detail"""
        # Large scale displacement
        disp_large = obj.modifiers.new(name="DisplaceLarge", type='DISPLACE')
        disp_large.strength = geometry_data.get('large_displacement', 0.3)
        disp_large.mid_level = 0.5
        
        # Create noise texture for large displacement
        large_noise = bpy.data.textures.new(name="LargeNoise", type='NOISE')
        if hasattr(large_noise, 'noise_scale'):
            large_noise.noise_scale = 0.5
            large_noise.noise_depth = 4
        disp_large.texture = large_noise
        
        # Medium scale displacement
        disp_medium = obj.modifiers.new(name="DisplaceMedium", type='DISPLACE')
        disp_medium.strength = geometry_data.get('medium_displacement', 0.15)
        disp_medium.mid_level = 0.5
        
        # Create noise texture for medium displacement
        medium_noise = bpy.data.textures.new(name="MediumNoise", type='NOISE')
        if hasattr(medium_noise, 'noise_scale'):
            medium_noise.noise_scale = 2.0
            medium_noise.noise_depth = 6
        disp_medium.texture = medium_noise
        
        # Fine detail displacement
        disp_fine = obj.modifiers.new(name="DisplaceFine", type='DISPLACE')
        disp_fine.strength = geometry_data.get('fine_displacement', 0.05)
        disp_fine.mid_level = 0.5
        
        # Create noise texture for fine displacement
        fine_noise = bpy.data.textures.new(name="FineNoise", type='NOISE')
        if hasattr(fine_noise, 'noise_scale'):
            fine_noise.noise_scale = 8.0
            fine_noise.noise_depth = 8
        disp_fine.texture = fine_noise
    
    def get_default_params(self) -> dict:
        return {
            'scale_variation': [1.3, 0.9, 1.1],
            'noise_factor': 0.4,
            'subdivision_levels': 3,
            'large_displacement': 0.4,
            'medium_displacement': 0.2,
            'fine_displacement': 0.08
        }


class RealisticRockMaterial(BaseMaterialStyle):
    """Realistic rock material with procedural textures and displacement"""
    
    def create_material(self, material_data: dict, name: str = "RealisticRock") -> bpy.types.Material:
        """Create realistic rock material with complex procedural textures"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (800, 0)
        
        # Create complex rock texture system
        self._create_rock_texture_system(nodes, links, principled, material_data)
        
        # Set realistic rock properties
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.9)
        principled.inputs['Specular IOR Level'].default_value = material_data.get('specular', 0.1)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (1000, 0)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _create_rock_texture_system(self, nodes, links, principled, material_data):
        """Create complex procedural rock texture system"""
        # Texture coordinate
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-1200, 0)
        
        # Mapping for texture control
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-1000, 0)
        mapping.inputs['Scale'].default_value = material_data.get('texture_scale', [4.0, 4.0, 4.0])
        
        # Base rock color using multiple noise textures
        # Large scale color variation
        noise_large = nodes.new(type='ShaderNodeTexNoise')
        noise_large.location = (-800, 400)
        noise_large.inputs['Scale'].default_value = 3.0
        noise_large.inputs['Detail'].default_value = 8.0
        noise_large.inputs['Roughness'].default_value = 0.6
        
        # Medium scale detail
        noise_medium = nodes.new(type='ShaderNodeTexNoise')
        noise_medium.location = (-800, 200)
        noise_medium.inputs['Scale'].default_value = 12.0
        noise_medium.inputs['Detail'].default_value = 12.0
        noise_medium.inputs['Roughness'].default_value = 0.5
        
        # Fine detail
        noise_fine = nodes.new(type='ShaderNodeTexNoise')
        noise_fine.location = (-800, 0)
        noise_fine.inputs['Scale'].default_value = 40.0
        noise_fine.inputs['Detail'].default_value = 16.0
        noise_fine.inputs['Roughness'].default_value = 0.4
        
        # Voronoi for rock structure
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-800, -200)
        voronoi.feature = 'F1'
        voronoi.inputs['Scale'].default_value = 6.0
        
        # Color ramps for different rock layers
        color_ramp_base = nodes.new(type='ShaderNodeValToRGB')
        color_ramp_base.location = (-600, 400)
        
        # Set realistic rock colors
        base_colors = material_data.get('base_colors', [
            [0.3, 0.25, 0.2],   # Dark brown
            [0.4, 0.35, 0.3],   # Medium brown
            [0.5, 0.45, 0.4]    # Light brown
        ])
        
        color_ramp_base.color_ramp.elements[0].color = (*base_colors[0], 1.0)
        color_ramp_base.color_ramp.elements[1].color = (*base_colors[1], 1.0)
        
        # Add more color variation
        color_ramp_base.color_ramp.elements.new(0.5)
        color_ramp_base.color_ramp.elements[1].color = (*base_colors[2], 1.0)
        
        # Color ramp for detail
        color_ramp_detail = nodes.new(type='ShaderNodeValToRGB')
        color_ramp_detail.location = (-600, 200)
        color_ramp_detail.color_ramp.elements[0].color = (0.2, 0.15, 0.1, 1.0)  # Dark cracks
        color_ramp_detail.color_ramp.elements[1].color = (0.6, 0.55, 0.5, 1.0)  # Highlighted edges
        
        # Mix the color layers
        mix1 = nodes.new(type='ShaderNodeMix')
        mix1.data_type = 'RGBA'
        mix1.location = (-400, 300)
        mix1.inputs['Factor'].default_value = 0.3
        
        mix2 = nodes.new(type='ShaderNodeMix')
        mix2.data_type = 'RGBA'
        mix2.location = (-400, 100)
        mix2.inputs['Factor'].default_value = 0.4
        
        # Create roughness variation
        color_ramp_roughness = nodes.new(type='ShaderNodeValToRGB')
        color_ramp_roughness.location = (-600, -200)
        color_ramp_roughness.color_ramp.elements[0].color = (0.7, 0.7, 0.7, 1.0)  # Smoother areas
        color_ramp_roughness.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # Rougher areas
        
        # Math nodes for combining textures
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-600, 0)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-400, -100)
        
        # Final color mix
        final_mix = nodes.new(type='ShaderNodeMix')
        final_mix.data_type = 'RGBA'
        final_mix.location = (-200, 0)
        final_mix.inputs['Factor'].default_value = 0.6
        
        # Link the texture system
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise_large.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise_medium.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])
        links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
        
        # Link color generation
        links.new(noise_large.outputs['Fac'], color_ramp_base.inputs['Fac'])
        links.new(noise_medium.outputs['Fac'], color_ramp_detail.inputs['Fac'])
        links.new(noise_fine.outputs['Fac'], math1.inputs[0])
        links.new(voronoi.outputs['Distance'], math1.inputs[1])
        links.new(math1.outputs['Value'], math2.inputs[0])
        links.new(noise_medium.outputs['Fac'], math2.inputs[1])
        
        # Mix colors
        links.new(color_ramp_base.outputs['Color'], mix1.inputs['A'])
        links.new(color_ramp_detail.outputs['Color'], mix1.inputs['B'])
        links.new(mix1.outputs['Result'], final_mix.inputs['A'])
        
        # Create secondary color layer
        mix3 = nodes.new(type='ShaderNodeMix')
        mix3.data_type = 'RGBA'
        mix3.location = (-200, -200)
        mix3.inputs['Factor'].default_value = 0.2
        mix3.inputs['A'].default_value = (0.35, 0.3, 0.25, 1.0)  # Base rock color
        links.new(math2.outputs['Value'], color_ramp_roughness.inputs['Fac'])
        links.new(color_ramp_roughness.outputs['Color'], mix3.inputs['B'])
        links.new(mix3.outputs['Result'], final_mix.inputs['B'])
        
        # Connect to principled shader
        links.new(final_mix.outputs['Result'], principled.inputs['Base Color'])
        links.new(color_ramp_roughness.outputs['Alpha'], principled.inputs['Roughness'])
        
        # Add normal map for surface detail
        self._add_normal_mapping(nodes, links, principled, mapping)
    
    def _add_normal_mapping(self, nodes, links, principled, mapping):
        """Add normal mapping for surface detail"""
        # Normal map noise
        noise_normal = nodes.new(type='ShaderNodeTexNoise')
        noise_normal.location = (-600, -400)
        noise_normal.inputs['Scale'].default_value = 25.0
        noise_normal.inputs['Detail'].default_value = 16.0
        
        # Normal map
        normal_map = nodes.new(type='ShaderNodeNormalMap')
        normal_map.location = (-400, -400)
        normal_map.inputs['Strength'].default_value = 1.5
        
        # Bump for additional detail
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (-200, -400)
        bump.inputs['Strength'].default_value = 0.3
        
        # Link normal mapping
        links.new(mapping.outputs['Vector'], noise_normal.inputs['Vector'])
        links.new(noise_normal.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], bump.inputs['Normal'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    
    def get_default_params(self) -> dict:
        return {
            'roughness': 0.85,
            'specular': 0.1,
            'texture_scale': [3.0, 3.0, 3.0],
            'base_colors': [
                [0.35, 0.28, 0.22],  # Dark granite
                [0.45, 0.38, 0.32],  # Medium granite  
                [0.55, 0.48, 0.42]   # Light granite
            ]
        }


class NaturalLightingSetup(BaseLightingSetup):
    """Natural outdoor lighting for realistic rock showcase"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up natural lighting for rock showcase"""
        self._clear_lights()
        
        # Strong sun light for dramatic shadows
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
        sun = bpy.context.active_object
        sun.name = "NaturalSun"
        sun.rotation_euler = (math.radians(35), 0, math.radians(25))
        sun.data.energy = lighting_data.get('sun_energy', 4.5)
        sun.data.color = [1.0, 0.95, 0.8]  # Warm sunlight
        
        # Sky light for ambient illumination
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 8))
        sky = bpy.context.active_object
        sky.name = "SkyLight"
        sky.rotation_euler = (0, 0, 0)
        sky.data.energy = lighting_data.get('sky_energy', 1.2)
        sky.data.color = [0.6, 0.7, 1.0]  # Cool sky color
        
        # Fill light to soften shadows
        bpy.ops.object.light_add(type='AREA', location=(-5, -5, 6))
        fill = bpy.context.active_object
        fill.name = "FillLight"
        fill.rotation_euler = (math.radians(45), 0, math.radians(45))
        fill.data.energy = lighting_data.get('fill_energy', 8)
        fill.data.size = 4.0
        fill.data.color = [0.8, 0.85, 0.9]
        
        print("🌞 Natural lighting setup complete")
    
    def _clear_lights(self):
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'sun_energy': 4.5,
            'sky_energy': 1.2,
            'fill_energy': 8
        }


class NaturalWorldEnvironment(BaseWorldEnvironment):
    """Natural world environment for realistic showcase"""
    
    def setup_world(self, world_data: dict):
        """Set up natural world environment"""
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("NaturalWorld")
            bpy.context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Use sky texture for realistic environment
        sky_texture = nodes.new(type='ShaderNodeTexSky')
        sky_texture.location = (-400, 300)
        sky_texture.sky_type = 'NISHITA'
        sky_texture.sun_elevation = math.radians(world_data.get('sun_elevation', 35))
        sky_texture.sun_rotation = math.radians(world_data.get('sun_rotation', 25))
        
        # Background shader
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (-200, 300)
        background.inputs['Strength'].default_value = world_data.get('sky_strength', 0.8)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (0, 300)
        
        # Link everything
        links.new(sky_texture.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌍 Natural world environment complete")
    
    def get_default_params(self) -> dict:
        return {
            'sun_elevation': 35,
            'sun_rotation': 25,
            'sky_strength': 0.8
        }


def create_realistic_showcase():
    """Create a realistic rock showcase"""
    print("🗿 Creating Realistic Rock Showcase")
    print("=" * 50)
    
    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Register realistic components
    mesh_creator.register_generator('realistic_rock', RealisticRockGenerator())
    material_manager.register_style('realistic_rock', RealisticRockMaterial())
    lighting_manager.register_lighting_setup('natural', NaturalLightingSetup())
    lighting_manager.register_world_environment('natural', NaturalWorldEnvironment())
    
    # Create realistic rock specification
    gem_data = {
        'name': 'RealisticRockShowcase',
        'description': 'A realistic rock with proper displacement and materials',
        'base_shape': 'realistic_rock',
        'geometry': {
            'scale_variation': [1.4, 0.8, 1.2],
            'noise_factor': 0.5,
            'subdivision_levels': 4,
            'large_displacement': 0.6,
            'medium_displacement': 0.3,
            'fine_displacement': 0.12
        },
        'material': {
            'style': 'realistic_rock',
            'roughness': 0.9,
            'specular': 0.05,
            'texture_scale': [2.5, 2.5, 2.5],
            'base_colors': [
                [0.3, 0.25, 0.2],   # Dark weathered rock
                [0.4, 0.35, 0.28],  # Medium rock
                [0.5, 0.45, 0.38]   # Light exposed rock
            ]
        },
        'lighting': {
            'setup': 'natural',
            'sun_energy': 5.0,
            'sky_energy': 1.5,
            'fill_energy': 10
        },
        'world': {
            'environment': 'natural',
            'sun_elevation': 40,
            'sun_rotation': 30,
            'sky_strength': 1.0
        },
        'render_settings': {
            'samples': 256,
            'resolution': [1200, 800]
        }
    }
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials and textures
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)
    
    # Create the realistic rock
    print("🗿 Creating realistic rock geometry...")
    rock_obj = mesh_creator.create_gem_geometry(gem_data)
    
    print("🎨 Applying realistic rock material...")
    material = material_manager.create_material(gem_data)
    rock_obj.data.materials.append(material)
    
    print("💡 Setting up natural lighting...")
    lighting_manager.setup_lighting(gem_data)
    
    print("🌍 Creating natural environment...")
    lighting_manager.setup_world(gem_data)
    
    # Setup camera for rock showcase
    print("📷 Positioning rock showcase camera...")
    setup_rock_camera()
    
    # Setup render settings
    print("🎬 Configuring realistic render...")
    setup_realistic_render(gem_data['render_settings'])
    
    # Save scene
    output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
    output_path.mkdir(parents=True, exist_ok=True)
    
    scene_file = output_path / "RealisticRockShowcase.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    
    # Render the realistic rock
    render_path = Path(__file__).parent / "examples" / "realistic_rock_showcase.png"
    bpy.context.scene.render.filepath = str(render_path)
    
    print("📸 Rendering realistic rock showcase...")
    bpy.ops.render.render(write_still=True)
    
    print("=" * 50)
    print("🏆 REALISTIC ROCK SHOWCASE COMPLETE!")
    print(f"📁 Scene: {scene_file}")
    print(f"🖼️ Render: {render_path}")
    print("✨ Realistic Features:")
    print("   - Multi-level displacement for surface detail")
    print("   - Complex procedural rock materials")
    print("   - Realistic granite-like coloring and textures")
    print("   - Natural outdoor lighting with sun and sky")
    print("   - High subdivision for smooth displacement")
    print("   - Normal mapping for fine surface detail")
    print("   - Proper roughness and specular variation")
    
    return rock_obj


def setup_rock_camera():
    """Set up camera for rock showcase"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)
    
    # Create camera positioned to show rock detail
    bpy.ops.object.camera_add(location=(3.5, -4.2, 2.8))
    camera = bpy.context.active_object
    camera.name = "RockCamera"
    
    # Angle to show surface detail and form
    camera.rotation_euler = (math.radians(65), 0, math.radians(35))
    
    # Camera settings for rock detail
    camera.data.lens = 50
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 5.5
    camera.data.dof.aperture_fstop = 5.6  # Good depth of field for detail
    
    bpy.context.scene.camera = camera


def setup_realistic_render(render_settings: dict):
    """Set up render settings for realistic rock"""
    scene = bpy.context.scene
    
    # Use Cycles for realistic rendering
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 256)
    
    # Good resolution for detail
    resolution = render_settings.get('resolution', [1200, 800])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Realistic color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    
    # Quality settings for displacement
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.feature_set = 'SUPPORTED'
    
    # Enable subdivision for displacement
    scene.cycles.dicing_rate = 1.0
    scene.cycles.max_subdivisions = 12
    
    # Output settings
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.compression = 90


if __name__ == "__main__":
    create_realistic_showcase()