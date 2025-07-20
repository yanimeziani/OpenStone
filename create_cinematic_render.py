#!/usr/bin/env python3
"""
Create Cinematic Gemstone Render
Combines custom mesh, material, and lighting for a dramatic cinematic result
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


class CinematicCrystalGenerator(BaseMeshGenerator):
    """Cinematic crystal with dramatic angular cuts"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a dramatic crystal with cinematic proportions"""
        height = geometry_data.get('height', 3.0)
        base_radius = geometry_data.get('base_radius', 1.2)
        top_radius = geometry_data.get('top_radius', 0.3)
        cuts = geometry_data.get('dramatic_cuts', 8)
        twist = geometry_data.get('twist_angle', 15)
        
        # Create mesh using bmesh
        bm = bmesh.new()
        
        # Create dramatic tapered crystal
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=cuts,
            radius1=base_radius,
            radius2=top_radius,
            depth=height
        )
        
        # Add twist for cinematic effect
        bmesh.ops.rotate(
            bm,
            verts=bm.verts[:],
            cent=(0, 0, 0),
            matrix=Euler((0, 0, math.radians(twist))).to_matrix()
        )
        
        # Add dramatic cuts
        for i in range(cuts // 2):
            angle = (i * 2 * math.pi) / (cuts // 2)
            cut_location = (
                base_radius * 0.8 * math.cos(angle),
                base_radius * 0.8 * math.sin(angle),
                height * 0.3
            )
            bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                dist=0.01,
                plane_co=cut_location,
                plane_no=Vector((math.cos(angle + math.pi/4), math.sin(angle + math.pi/4), 0.5))
            )
        
        # Subdivide for smooth surfaces
        bmesh.ops.subdivide_edges(
            bm,
            edges=bm.edges[:],
            cuts=1,
            use_grid_fill=True
        )
        
        # Create mesh object
        mesh = bpy.data.meshes.new("CinematicCrystal")
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new("CinematicCrystal", mesh)
        bpy.context.collection.objects.link(obj)
        
        # Apply smooth shading
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        return obj
    
    def get_default_params(self) -> dict:
        return {
            'height': 3.0,
            'base_radius': 1.2,
            'top_radius': 0.3,
            'dramatic_cuts': 8,
            'twist_angle': 15
        }


class CinematicGemStyle(BaseMaterialStyle):
    """Cinematic material with dramatic internal lighting and depth"""
    
    def create_material(self, material_data: dict, name: str = "CinematicGem") -> bpy.types.Material:
        """Create cinematic gem material with complex internal structure"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (400, 200)
        
        # Create complex internal structure
        self._create_cinematic_internals(nodes, links, principled, material_data)
        
        # Set cinematic properties
        base_color = material_data.get('base_color', [0.1, 0.3, 0.8])
        principled.inputs['Transmission Weight'].default_value = material_data.get('transparency', 0.95)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.02)
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.8)
        
        # Add volume shader for internal glow
        volume_scatter = nodes.new(type='ShaderNodeVolumeScatter')
        volume_scatter.location = (400, -100)
        volume_scatter.inputs['Color'].default_value = (*base_color, 1.0)
        volume_scatter.inputs['Density'].default_value = material_data.get('volume_density', 0.1)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 100)
        
        # Link everything
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        links.new(volume_scatter.outputs['Volume'], output.inputs['Volume'])
        
        return material
    
    def _create_cinematic_internals(self, nodes, links, principled, material_data):
        """Create complex internal structure for cinematic effect"""
        # Coordinate system
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 200)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 200)
        
        # Multiple layers of complexity
        # Layer 1: Large scale crystalline structure
        voronoi1 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi1.location = (-400, 400)
        voronoi1.feature = 'DISTANCE_TO_EDGE'
        voronoi1.inputs['Scale'].default_value = 8.0
        
        # Layer 2: Medium scale internal facets
        voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi2.location = (-400, 200)
        voronoi2.feature = 'F1'
        voronoi2.inputs['Scale'].default_value = 20.0
        
        # Layer 3: Fine detail with noise
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 50.0
        noise.inputs['Detail'].default_value = 16.0
        
        # Layer 4: Dramatic wave patterns
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-400, -200)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 15.0
        wave.inputs['Distortion'].default_value = 2.0
        
        # Combine all layers
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-200, 300)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-200, 100)
        
        math3 = nodes.new(type='ShaderNodeMath')
        math3.operation = 'MULTIPLY'
        math3.location = (-200, -100)
        
        # Final color mixing
        color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp1.location = (0, 200)
        
        # Set dramatic color gradient
        base_color = material_data.get('base_color', [0.1, 0.3, 0.8])
        highlight_color = material_data.get('highlight_color', [0.8, 0.9, 1.0])
        
        color_ramp1.color_ramp.elements[0].color = (*base_color, 1.0)
        color_ramp1.color_ramp.elements[1].color = (*highlight_color, 1.0)
        
        # Add intermediate colors for complexity
        color_ramp1.color_ramp.elements.new(0.3)
        color_ramp1.color_ramp.elements[1].color = (
            (base_color[0] + highlight_color[0]) / 2,
            (base_color[1] + highlight_color[1]) / 2,
            (base_color[2] + highlight_color[2]) / 2,
            1.0
        )
        
        color_ramp1.color_ramp.elements.new(0.7)
        color_ramp1.color_ramp.elements[3].color = (*highlight_color, 1.0)
        
        # Mix with base color
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (200, 200)
        mix.inputs['Fac'].default_value = 0.6
        mix.inputs['Color2'].default_value = (*base_color, 1.0)
        
        # Link the complex internal structure
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], voronoi1.inputs['Vector'])
        links.new(mapping.outputs['Vector'], voronoi2.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        
        links.new(voronoi1.outputs['Distance'], math1.inputs[0])
        links.new(voronoi2.outputs['F1'], math1.inputs[1])
        links.new(math1.outputs['Value'], math2.inputs[0])
        links.new(noise.outputs['Fac'], math2.inputs[1])
        links.new(math2.outputs['Value'], math3.inputs[0])
        links.new(wave.outputs['Fac'], math3.inputs[1])
        
        links.new(math3.outputs['Value'], color_ramp1.inputs['Fac'])
        links.new(color_ramp1.outputs['Color'], mix.inputs['Color1'])
        links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> dict:
        return {
            'base_color': [0.1, 0.3, 0.8],
            'highlight_color': [0.8, 0.9, 1.0],
            'transparency': 0.95,
            'roughness': 0.02,
            'ior': 1.8,
            'volume_density': 0.1
        }


class CinematicLightingSetup(BaseLightingSetup):
    """Dramatic cinematic lighting with film-style setup"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up cinematic lighting"""
        self._clear_lights()
        
        # Key light - strong, warm, dramatic angle
        bpy.ops.object.light_add(type='AREA', location=(5, -4, 6))
        key_light = bpy.context.active_object
        key_light.name = "CinematicKey"
        key_light.rotation_euler = (math.radians(25), 0, math.radians(40))
        key_light.data.energy = lighting_data.get('key_energy', 25)
        key_light.data.size = 3.0
        key_light.data.color = lighting_data.get('key_color', [1.0, 0.9, 0.7])  # Warm
        
        # Fill light - cool, soft, from opposite side
        bpy.ops.object.light_add(type='AREA', location=(-3, -2, 4))
        fill_light = bpy.context.active_object
        fill_light.name = "CinematicFill"
        fill_light.rotation_euler = (math.radians(35), 0, math.radians(-30))
        fill_light.data.energy = lighting_data.get('fill_energy', 8)
        fill_light.data.size = 4.0
        fill_light.data.color = lighting_data.get('fill_color', [0.7, 0.8, 1.0])  # Cool
        
        # Rim light - strong backlight for dramatic silhouette
        bpy.ops.object.light_add(type='SPOT', location=(0, 6, 3))
        rim_light = bpy.context.active_object
        rim_light.name = "CinematicRim"
        rim_light.rotation_euler = (math.radians(-20), 0, 0)
        rim_light.data.energy = lighting_data.get('rim_energy', 30)
        rim_light.data.spot_size = math.radians(60)
        rim_light.data.spot_blend = 0.3
        rim_light.data.color = lighting_data.get('rim_color', [0.9, 0.95, 1.0])
        
        # Accent light - colored light for drama
        bpy.ops.object.light_add(type='SPOT', location=(-4, 3, 2))
        accent_light = bpy.context.active_object
        accent_light.name = "CinematicAccent"
        accent_light.rotation_euler = (math.radians(45), 0, math.radians(-60))
        accent_light.data.energy = lighting_data.get('accent_energy', 12)
        accent_light.data.spot_size = math.radians(45)
        accent_light.data.color = lighting_data.get('accent_color', [0.8, 0.3, 1.0])  # Purple
        
        # Under light - subtle uplighting for base glow
        bpy.ops.object.light_add(type='AREA', location=(0, 0, -2))
        under_light = bpy.context.active_object
        under_light.name = "CinematicUnder"
        under_light.rotation_euler = (0, 0, 0)
        under_light.data.energy = lighting_data.get('under_energy', 5)
        under_light.data.size = 2.0
        under_light.data.color = [0.4, 0.6, 0.9]
        
        print("🎬 Cinematic lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'key_energy': 25,
            'key_color': [1.0, 0.9, 0.7],
            'fill_energy': 8,
            'fill_color': [0.7, 0.8, 1.0],
            'rim_energy': 30,
            'rim_color': [0.9, 0.95, 1.0],
            'accent_energy': 12,
            'accent_color': [0.8, 0.3, 1.0],
            'under_energy': 5
        }


class CinematicWorldEnvironment(BaseWorldEnvironment):
    """Dramatic world environment with film-style atmosphere"""
    
    def setup_world(self, world_data: dict):
        """Set up cinematic world environment"""
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Create dramatic atmosphere
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 300)
        
        # Gradient for dramatic sky
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-300, 300)
        
        # Set cinematic colors
        bottom_color = world_data.get('bottom_color', [0.05, 0.02, 0.1])  # Deep purple
        top_color = world_data.get('top_color', [0.2, 0.15, 0.3])  # Lighter purple
        
        color_ramp.color_ramp.elements[0].color = (*bottom_color, 1.0)
        color_ramp.color_ramp.elements[1].color = (*top_color, 1.0)
        
        # Add atmospheric particles effect
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, 100)
        noise.inputs['Scale'].default_value = world_data.get('atmosphere_scale', 20.0)
        noise.inputs['Detail'].default_value = 8.0
        
        # Mix atmospheric effect
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (-100, 200)
        mix.inputs['Fac'].default_value = world_data.get('atmosphere_strength', 0.2)
        
        # Background shader
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (100, 200)
        background.inputs['Strength'].default_value = world_data.get('world_strength', 0.4)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (300, 200)
        
        # Link everything
        links.new(tex_coord.outputs['Generated'], color_ramp.inputs['Fac'])
        links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
        
        links.new(color_ramp.outputs['Color'], mix.inputs['Color1'])
        links.new(noise.outputs['Color'], mix.inputs['Color2'])
        
        links.new(mix.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🎭 Cinematic world environment setup complete")
    
    def get_default_params(self) -> dict:
        return {
            'bottom_color': [0.05, 0.02, 0.1],
            'top_color': [0.2, 0.15, 0.3],
            'atmosphere_scale': 20.0,
            'atmosphere_strength': 0.2,
            'world_strength': 0.4
        }


def create_cinematic_gemstone():
    """Create a complete cinematic gemstone render"""
    print("🎬 Creating Cinematic Gemstone Render")
    print("=" * 50)
    
    # Initialize all managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Register custom components
    mesh_creator.register_generator('cinematic_crystal', CinematicCrystalGenerator())
    material_manager.register_style('cinematic', CinematicGemStyle())
    lighting_manager.register_lighting_setup('cinematic', CinematicLightingSetup())
    lighting_manager.register_world_environment('cinematic', CinematicWorldEnvironment())
    
    # Create cinematic gem specification
    gem_data = {
        'name': 'CinematicMasterpiece',
        'description': 'A dramatic crystal with cinematic lighting and complex internal structure',
        'base_shape': 'cinematic_crystal',
        'geometry': {
            'height': 3.5,
            'base_radius': 1.4,
            'top_radius': 0.2,
            'dramatic_cuts': 10,
            'twist_angle': 20
        },
        'material': {
            'style': 'cinematic',
            'base_color': [0.15, 0.25, 0.9],  # Deep blue
            'highlight_color': [0.9, 0.95, 1.0],  # Bright white
            'transparency': 0.98,
            'roughness': 0.01,
            'ior': 1.9,
            'volume_density': 0.05
        },
        'lighting': {
            'setup': 'cinematic',
            'key_energy': 30,
            'key_color': [1.0, 0.85, 0.6],  # Warm gold
            'fill_energy': 10,
            'fill_color': [0.6, 0.8, 1.0],  # Cool blue
            'rim_energy': 35,
            'accent_energy': 15,
            'accent_color': [0.9, 0.2, 0.8]  # Magenta
        },
        'world': {
            'environment': 'cinematic',
            'bottom_color': [0.03, 0.01, 0.08],  # Deep purple-black
            'top_color': [0.15, 0.1, 0.25],     # Lighter purple
            'atmosphere_strength': 0.3,
            'world_strength': 0.3
        },
        'render_settings': {
            'samples': 512,
            'resolution': [1920, 1080]
        }
    }
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Create the cinematic gemstone
    print("🔷 Creating dramatic crystal geometry...")
    gem_obj = mesh_creator.create_gem_geometry(gem_data)
    
    print("🎨 Applying cinematic material...")
    material = material_manager.create_material(gem_data)
    gem_obj.data.materials.append(material)
    
    print("💡 Setting up cinematic lighting...")
    lighting_manager.setup_lighting(gem_data)
    
    print("🌍 Creating dramatic atmosphere...")
    lighting_manager.setup_world(gem_data)
    
    # Setup camera for cinematic angle
    print("📷 Positioning cinematic camera...")
    setup_cinematic_camera()
    
    # Setup render settings
    print("🎬 Configuring render settings...")
    setup_cinematic_render(gem_data['render_settings'])
    
    # Save scene
    output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
    output_path.mkdir(parents=True, exist_ok=True)
    
    scene_file = output_path / "CinematicMasterpiece.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    
    # Render the masterpiece
    render_path = output_path / "CinematicMasterpiece.png"
    bpy.context.scene.render.filepath = str(render_path)
    
    print("🎬 Rendering cinematic masterpiece...")
    bpy.ops.render.render(write_still=True)
    
    print("=" * 50)
    print("🎉 CINEMATIC MASTERPIECE COMPLETE!")
    print(f"📁 Scene: {scene_file}")
    print(f"🖼️ Render: {render_path}")
    print("✨ Features:")
    print("   - Dramatic angular crystal geometry")
    print("   - Complex internal light refraction")
    print("   - Film-style multi-light setup")
    print("   - Atmospheric world environment")
    print("   - High-quality 512 samples")
    
    return gem_obj


def setup_cinematic_camera():
    """Set up camera for dramatic cinematic angle"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)
    
    # Create dramatic low-angle camera
    bpy.ops.object.camera_add(location=(3.5, -5, 1.5))
    camera = bpy.context.active_object
    camera.name = "CinematicCamera"
    
    # Dramatic angle pointing slightly up at the crystal
    camera.rotation_euler = (math.radians(70), 0, math.radians(35))
    
    # Set camera properties for cinematic look
    camera.data.lens = 50  # Standard cinematic focal length
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 6.0
    camera.data.dof.aperture_fstop = 2.8  # Shallow depth of field
    
    bpy.context.scene.camera = camera


def setup_cinematic_render(render_settings: dict):
    """Set up render settings for cinematic quality"""
    scene = bpy.context.scene
    
    # Use Cycles for photorealistic rendering
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 512)
    
    # High resolution
    resolution = render_settings.get('resolution', [1920, 1080])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Cinematic aspect ratio and settings
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    
    # Enable motion blur for cinematic feel
    scene.render.motion_blur_shutter = 0.5
    
    # Color management for cinematic look
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.5
    scene.view_settings.gamma = 1.0
    
    # High quality settings
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'  # Use GPU denoising if available
    
    # Output settings
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15


if __name__ == "__main__":
    create_cinematic_gemstone()