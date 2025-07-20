#!/usr/bin/env python3
"""
Create Premium Showcase Render
Generate a stunning, professionally framed gemstone render for GitHub showcase
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


class PremiumCrystalGenerator(BaseMeshGenerator):
    """Premium crystal generator for stunning showcase"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a premium showcase crystal"""
        # Create sophisticated multi-part crystal
        bm = bmesh.new()
        
        # Main crystal - elegant diamond-like shape
        self._create_main_crystal(bm, geometry_data)
        
        # Add smaller accent crystals
        self._add_accent_crystals(bm, geometry_data)
        
        # Subdivide for smoothness
        bmesh.ops.subdivide_edges(
            bm,
            edges=bm.edges[:],
            cuts=2,
            use_grid_fill=True
        )
        
        # Create mesh object
        mesh = bpy.data.meshes.new("PremiumShowcase")
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new("PremiumShowcase", mesh)
        bpy.context.collection.objects.link(obj)
        
        # Apply smooth shading
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        return obj
    
    def _create_main_crystal(self, bm, geometry_data):
        """Create the main premium crystal"""
        height = geometry_data.get('height', 3.0)
        base_size = geometry_data.get('base_size', 1.2)
        
        # Create diamond-like shape with bmesh
        # Bottom pyramid
        bottom_apex = bm.verts.new((0, 0, -height * 0.3))
        
        # Middle section - octagonal
        mid_verts = []
        for i in range(8):
            angle = (i * 2 * math.pi) / 8
            x = base_size * math.cos(angle)
            y = base_size * math.sin(angle)
            mid_verts.append(bm.verts.new((x, y, 0)))
        
        # Top section - smaller octagon
        top_verts = []
        for i in range(8):
            angle = (i * 2 * math.pi) / 8
            x = base_size * 0.6 * math.cos(angle)
            y = base_size * 0.6 * math.sin(angle)
            top_verts.append(bm.verts.new((x, y, height * 0.6)))
        
        # Top apex
        top_apex = bm.verts.new((0, 0, height))
        
        # Create faces
        # Bottom pyramid faces
        for i in range(8):
            v1 = mid_verts[i]
            v2 = mid_verts[(i + 1) % 8]
            bm.faces.new([bottom_apex, v1, v2])
        
        # Middle section faces
        for i in range(8):
            v1 = mid_verts[i]
            v2 = mid_verts[(i + 1) % 8]
            v3 = top_verts[(i + 1) % 8]
            v4 = top_verts[i]
            bm.faces.new([v1, v2, v3, v4])
        
        # Top pyramid faces
        for i in range(8):
            v1 = top_verts[i]
            v2 = top_verts[(i + 1) % 8]
            bm.faces.new([v1, v2, top_apex])
    
    def _add_accent_crystals(self, bm, geometry_data):
        """Add smaller accent crystals around the main one"""
        accent_count = geometry_data.get('accent_count', 3)
        main_size = geometry_data.get('base_size', 1.2)
        
        for i in range(accent_count):
            angle = (i * 2 * math.pi) / accent_count + random.uniform(-0.3, 0.3)
            distance = main_size * random.uniform(1.8, 2.5)
            height_offset = random.uniform(-0.5, 0.2)
            size = random.uniform(0.3, 0.6)
            
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            z = height_offset
            
            # Create small crystal
            apex_bottom = bm.verts.new((x, y, z - size * 0.5))
            apex_top = bm.verts.new((x, y, z + size * 1.5))
            
            # Create small octagon around it
            small_verts = []
            for j in range(6):
                small_angle = (j * 2 * math.pi) / 6
                sx = x + size * 0.3 * math.cos(small_angle)
                sy = y + size * 0.3 * math.sin(small_angle)
                small_verts.append(bm.verts.new((sx, sy, z)))
            
            # Create faces for small crystal
            for j in range(6):
                v1 = small_verts[j]
                v2 = small_verts[(j + 1) % 6]
                # Bottom face
                try:
                    bm.faces.new([apex_bottom, v1, v2])
                except:
                    pass
                # Top face
                try:
                    bm.faces.new([v1, v2, apex_top])
                except:
                    pass
    
    def get_default_params(self) -> dict:
        return {
            'height': 3.0,
            'base_size': 1.2,
            'accent_count': 3
        }


class PremiumGemStyle(BaseMaterialStyle):
    """Premium material style for showcase"""
    
    def create_material(self, material_data: dict, name: str = "PremiumGem") -> bpy.types.Material:
        """Create premium showcase material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (600, 200)
        
        # Create stunning internal complexity
        self._create_premium_internals(nodes, links, principled, material_data)
        
        # Premium material properties
        base_color = material_data.get('base_color', [0.1, 0.4, 0.95])
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = 0.98
        principled.inputs['Roughness'].default_value = 0.005
        principled.inputs['IOR'].default_value = 2.1
        
        # Add premium glow
        principled.inputs['Emission Color'].default_value = (*base_color, 1.0)
        principled.inputs['Emission Strength'].default_value = 0.03
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (800, 200)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _create_premium_internals(self, nodes, links, principled, material_data):
        """Create premium internal effects"""
        # Multiple layered textures for depth
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-1000, 200)
        
        # Layer 1: Large crystal structure
        voronoi1 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi1.location = (-800, 400)
        voronoi1.feature = 'DISTANCE_TO_EDGE'
        voronoi1.inputs['Scale'].default_value = 15.0
        
        # Layer 2: Medium internal facets
        voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi2.location = (-800, 200)
        voronoi2.feature = 'F1'
        voronoi2.inputs['Scale'].default_value = 35.0
        
        # Layer 3: Fine crystalline detail
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-800, 0)
        noise.inputs['Scale'].default_value = 80.0
        noise.inputs['Detail'].default_value = 16.0
        noise.inputs['Roughness'].default_value = 0.4
        
        # Layer 4: Flowing energy patterns
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-800, -200)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 25.0
        wave.inputs['Distortion'].default_value = 3.0
        
        # Combine layers with math nodes
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-600, 300)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-600, 100)
        math2.inputs[1].default_value = 0.3
        
        math3 = nodes.new(type='ShaderNodeMath')
        math3.operation = 'MULTIPLY'
        math3.location = (-600, -100)
        math3.inputs[1].default_value = 0.7
        
        math4 = nodes.new(type='ShaderNodeMath')
        math4.operation = 'ADD'
        math4.location = (-400, 100)
        
        # Premium color gradients
        color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
        color_ramp1.location = (-200, 200)
        
        # Set sophisticated color palette
        base_color = material_data.get('base_color', [0.1, 0.4, 0.95])
        highlight_color = [min(1.0, base_color[0] + 0.3), min(1.0, base_color[1] + 0.4), 1.0]
        accent_color = [base_color[0] * 0.5, base_color[1] * 0.8, min(1.0, base_color[2] + 0.2)]
        
        color_ramp1.color_ramp.elements[0].color = (*accent_color, 1.0)
        color_ramp1.color_ramp.elements[1].color = (*highlight_color, 1.0)
        
        # Add intermediate colors
        color_ramp1.color_ramp.elements.new(0.3)
        color_ramp1.color_ramp.elements[1].color = (*base_color, 1.0)
        
        color_ramp1.color_ramp.elements.new(0.7)
        mid_color = [(base_color[i] + highlight_color[i]) * 0.5 for i in range(3)]
        color_ramp1.color_ramp.elements[3].color = (*mid_color, 1.0)
        
        # Final mix
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (200, 200)
        mix.inputs['Factor'].default_value = 0.8
        mix.inputs['B'].default_value = (*base_color, 1.0)
        
        # Link the complex structure
        links.new(tex_coord.outputs['Generated'], voronoi1.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], voronoi2.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], wave.inputs['Vector'])
        
        links.new(voronoi1.outputs['Distance'], math1.inputs[0])
        links.new(voronoi2.outputs['Distance'], math1.inputs[1])
        links.new(math1.outputs['Value'], math2.inputs[0])
        links.new(noise.outputs['Fac'], math3.inputs[0])
        links.new(math2.outputs['Value'], math4.inputs[0])
        links.new(math3.outputs['Value'], math4.inputs[1])
        links.new(wave.outputs['Fac'], math4.inputs[1])
        
        links.new(math4.outputs['Value'], color_ramp1.inputs['Fac'])
        links.new(color_ramp1.outputs['Color'], mix.inputs['A'])
        links.new(mix.outputs['Result'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> dict:
        return {
            'base_color': [0.1, 0.4, 0.95]
        }


class PremiumLightingSetup(BaseLightingSetup):
    """Premium lighting setup for showcase"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up premium showcase lighting"""
        self._clear_lights()
        
        # Key light - premium golden hour lighting
        bpy.ops.object.light_add(type='AREA', location=(6, -5, 8))
        key_light = bpy.context.active_object
        key_light.name = "PremiumKey"
        key_light.rotation_euler = (math.radians(25), 0, math.radians(40))
        key_light.data.energy = 35
        key_light.data.size = 4.0
        key_light.data.color = [1.0, 0.9, 0.7]  # Warm golden
        
        # Fill light - cool sophisticated fill
        bpy.ops.object.light_add(type='AREA', location=(-4, -3, 6))
        fill_light = bpy.context.active_object
        fill_light.name = "PremiumFill"
        fill_light.rotation_euler = (math.radians(35), 0, math.radians(-25))
        fill_light.data.energy = 12
        fill_light.data.size = 5.0
        fill_light.data.color = [0.8, 0.9, 1.0]  # Cool blue
        
        # Rim light - dramatic edge lighting
        bpy.ops.object.light_add(type='SPOT', location=(2, 8, 5))
        rim_light = bpy.context.active_object
        rim_light.name = "PremiumRim"
        rim_light.rotation_euler = (math.radians(-15), 0, math.radians(15))
        rim_light.data.energy = 40
        rim_light.data.spot_size = math.radians(35)
        rim_light.data.spot_blend = 0.1
        rim_light.data.color = [0.95, 0.98, 1.0]
        
        # Accent light - magical purple accent
        bpy.ops.object.light_add(type='SPOT', location=(-6, 4, 4))
        accent_light = bpy.context.active_object
        accent_light.name = "PremiumAccent"
        accent_light.rotation_euler = (math.radians(30), 0, math.radians(-45))
        accent_light.data.energy = 18
        accent_light.data.spot_size = math.radians(50)
        accent_light.data.color = [0.9, 0.6, 1.0]  # Magical purple
        
        # Under light - subtle base illumination
        bpy.ops.object.light_add(type='AREA', location=(0, 0, -3))
        under_light = bpy.context.active_object
        under_light.name = "PremiumUnder"
        under_light.data.energy = 8
        under_light.data.size = 6.0
        under_light.data.color = [0.7, 0.8, 0.95]
        
        print("✨ Premium showcase lighting complete")
    
    def _clear_lights(self):
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {}


class PremiumWorldEnvironment(BaseWorldEnvironment):
    """Premium world environment for showcase"""
    
    def setup_world(self, world_data: dict):
        """Set up premium world environment"""
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("PremiumWorld")
            bpy.context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Create sophisticated gradient with subtle complexity
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 300)
        
        # Main gradient
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 300)
        
        # Premium color scheme
        color_ramp.color_ramp.elements[0].color = (0.02, 0.03, 0.08, 1.0)  # Deep blue-black
        color_ramp.color_ramp.elements[1].color = (0.08, 0.12, 0.25, 1.0)  # Sophisticated blue
        
        # Add subtle atmospheric noise
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, 100)
        noise.inputs['Scale'].default_value = 8.0
        noise.inputs['Detail'].default_value = 4.0
        
        # Mix atmospheric effect
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (-200, 200)
        mix.inputs['Factor'].default_value = 0.1
        
        # Background shader
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 200)
        background.inputs['Strength'].default_value = 0.15
        
        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (200, 200)
        
        # Link everything
        links.new(tex_coord.outputs['Generated'], color_ramp.inputs['Fac'])
        links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
        
        links.new(color_ramp.outputs['Color'], mix.inputs['A'])
        links.new(noise.outputs['Color'], mix.inputs['B'])
        
        links.new(mix.outputs['Result'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌌 Premium world environment complete")
    
    def get_default_params(self) -> dict:
        return {}


def create_premium_showcase():
    """Create a premium showcase render for GitHub"""
    print("💎 Creating Premium Showcase Render")
    print("=" * 50)
    
    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Register premium components
    mesh_creator.register_generator('premium_showcase', PremiumCrystalGenerator())
    material_manager.register_style('premium', PremiumGemStyle())
    lighting_manager.register_lighting_setup('premium', PremiumLightingSetup())
    lighting_manager.register_world_environment('premium', PremiumWorldEnvironment())
    
    # Create premium gem specification
    gem_data = {
        'name': 'PremiumShowcase',
        'description': 'A premium crystal showcase for GitHub',
        'base_shape': 'premium_showcase',
        'geometry': {
            'height': 3.2,
            'base_size': 1.3,
            'accent_count': 4
        },
        'material': {
            'style': 'premium',
            'base_color': [0.08, 0.35, 0.92]  # Premium sapphire blue
        },
        'lighting': {
            'setup': 'premium'
        },
        'world': {
            'environment': 'premium'
        },
        'render_settings': {
            'samples': 512,
            'resolution': [1200, 800]  # 3:2 aspect ratio for better framing
        }
    }
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Create the premium showcase
    print("💎 Creating premium crystal geometry...")
    gem_obj = mesh_creator.create_gem_geometry(gem_data)
    
    print("🎨 Applying premium material...")
    material = material_manager.create_material(gem_data)
    gem_obj.data.materials.append(material)
    
    print("💡 Setting up premium lighting...")
    lighting_manager.setup_lighting(gem_data)
    
    print("🌍 Creating premium atmosphere...")
    lighting_manager.setup_world(gem_data)
    
    # Setup perfect showcase camera
    print("📷 Positioning premium camera...")
    setup_premium_camera()
    
    # Setup premium render settings
    print("🎬 Configuring premium render...")
    setup_premium_render(gem_data['render_settings'])
    
    # Save scene
    output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
    output_path.mkdir(parents=True, exist_ok=True)
    
    scene_file = output_path / "PremiumShowcase.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    
    # Render the masterpiece
    render_path = Path(__file__).parent / "examples" / "premium_showcase.png"
    bpy.context.scene.render.filepath = str(render_path)
    
    print("📸 Rendering premium showcase...")
    bpy.ops.render.render(write_still=True)
    
    print("=" * 50)
    print("🏆 PREMIUM SHOWCASE COMPLETE!")
    print(f"📁 Scene: {scene_file}")
    print(f"🖼️ Render: {render_path}")
    print("✨ Premium Features:")
    print("   - Multi-crystal composition with accent gems")
    print("   - Complex internal crystalline structure")
    print("   - Premium lighting with golden hour warmth")
    print("   - Sophisticated atmospheric background")
    print("   - Perfect 1200x800 framing for GitHub")
    print("   - 512 samples for maximum quality")
    
    return gem_obj


def setup_premium_camera():
    """Set up camera for premium showcase framing"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)
    
    # Create premium showcase camera - perfect composition
    bpy.ops.object.camera_add(location=(4.5, -7.2, 4.8))
    camera = bpy.context.active_object
    camera.name = "PremiumCamera"
    
    # Premium showcase angle - rule of thirds composition
    camera.rotation_euler = (math.radians(58), 0, math.radians(28))
    
    # Premium camera settings
    camera.data.lens = 75  # Portrait lens for elegant compression
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 8.5
    camera.data.dof.aperture_fstop = 4.0  # Moderate depth of field
    
    bpy.context.scene.camera = camera


def setup_premium_render(render_settings: dict):
    """Set up premium render settings"""
    scene = bpy.context.scene
    
    # Use Cycles for maximum quality
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 512)
    
    # Premium resolution with proper aspect ratio
    resolution = render_settings.get('resolution', [1200, 800])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Premium color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.3
    scene.view_settings.gamma = 0.95
    
    # Premium quality settings
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.01
    
    # Premium motion blur and effects
    scene.render.motion_blur_shutter = 0.8
    
    # Output settings
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 90
    scene.render.image_settings.color_depth = '16'


if __name__ == "__main__":
    create_premium_showcase()