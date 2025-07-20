#!/usr/bin/env python3
"""
Create GitHub Example Render
Generate a stunning gemstone render with transparent background for GitHub README
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
from openstone.lighting_manager import BaseLightingSetup


class GitHubShowcaseGenerator(BaseMeshGenerator):
    """Showcase crystal generator optimized for GitHub display"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a showcase crystal perfect for GitHub"""
        height = geometry_data.get('height', 2.5)
        base_size = geometry_data.get('base_size', 1.0)
        facets = geometry_data.get('facets', 12)
        
        # Create sophisticated crystal using bmesh
        bm = bmesh.new()
        
        # Create main crystal body - elongated hexagonal prism
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=facets,
            radius1=base_size,
            radius2=base_size * 0.9,  # Slight taper
            depth=height
        )
        
        # Add crystal termination (pointed top)
        top_verts = [v for v in bm.verts if v.co.z > height/3]
        if top_verts:
            # Get center point
            center = sum((v.co for v in top_verts), Vector()) / len(top_verts)
            center.z = height * 0.7
            
            # Create apex point
            apex = bm.verts.new((center.x, center.y, height * 0.9))
            
            # Connect top faces to apex
            top_faces = [f for f in bm.faces if all(v.co.z > height/3 for v in f.verts)]
            for face in top_faces[:]:
                bm.faces.remove(face)
            
            # Create pyramid faces
            top_edges = [e for e in bm.edges if all(v.co.z > height/3 for v in e.verts)]
            edge_loops = []
            
            # Find boundary loop
            boundary_verts = list(set(v for e in top_edges for v in e.verts))
            boundary_verts.sort(key=lambda v: math.atan2(v.co.y - center.y, v.co.x - center.x))
            
            # Create triangular faces to apex
            for i in range(len(boundary_verts)):
                v1 = boundary_verts[i]
                v2 = boundary_verts[(i + 1) % len(boundary_verts)]
                try:
                    bm.faces.new([v1, v2, apex])
                except:
                    pass
        
        # Add crystal growth features
        self._add_crystal_features(bm, geometry_data)
        
        # Subdivide for smoothness
        bmesh.ops.subdivide_edges(
            bm,
            edges=bm.edges[:],
            cuts=1,
            use_grid_fill=True
        )
        
        # Create mesh object
        mesh = bpy.data.meshes.new("GitHubShowcase")
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new("GitHubShowcase", mesh)
        bpy.context.collection.objects.link(obj)
        
        # Apply smooth shading
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        return obj
    
    def _add_crystal_features(self, bm, geometry_data):
        """Add natural crystal growth features"""
        detail_level = geometry_data.get('detail_level', 0.7)
        
        if detail_level > 0.5:
            # Add subtle surface variation
            for vert in bm.verts:
                if abs(vert.co.z) < geometry_data.get('height', 2.5) * 0.3:
                    # Add small random displacement to middle section
                    noise_factor = detail_level * 0.05
                    vert.co += Vector((
                        random.uniform(-noise_factor, noise_factor),
                        random.uniform(-noise_factor, noise_factor),
                        0
                    ))
    
    def get_default_params(self) -> dict:
        return {
            'height': 2.5,
            'base_size': 1.0,
            'facets': 12,
            'detail_level': 0.7
        }


class GitHubGemStyle(BaseMaterialStyle):
    """Material style optimized for GitHub showcase"""
    
    def create_material(self, material_data: dict, name: str = "GitHubGem") -> bpy.types.Material:
        """Create stunning material for GitHub display"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (400, 200)
        
        # Create stunning internal effects
        self._create_showcase_internals(nodes, links, principled, material_data)
        
        # Set showcase properties for maximum visual impact
        base_color = material_data.get('base_color', [0.2, 0.6, 1.0])  # Brilliant blue
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = 0.95
        principled.inputs['Roughness'].default_value = 0.01
        principled.inputs['IOR'].default_value = 1.8
        
        # Add subtle emission for inner glow
        principled.inputs['Emission Color'].default_value = (*base_color, 1.0)
        principled.inputs['Emission Strength'].default_value = material_data.get('inner_glow', 0.1)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 200)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return material
    
    def _create_showcase_internals(self, nodes, links, principled, material_data):
        """Create internal complexity optimized for visual appeal"""
        # Coordinate system
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 200)
        
        # Voronoi for crystalline structure
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-600, 300)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 25.0
        
        # Wave for elegant flow
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-600, 100)
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = 20.0
        wave.inputs['Distortion'].default_value = 1.5
        
        # Noise for organic variation
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, -100)
        noise.inputs['Scale'].default_value = 40.0
        noise.inputs['Detail'].default_value = 12.0
        
        # Combine patterns
        math1 = nodes.new(type='ShaderNodeMath')
        math1.operation = 'MULTIPLY'
        math1.location = (-400, 200)
        
        math2 = nodes.new(type='ShaderNodeMath')
        math2.operation = 'ADD'
        math2.location = (-400, 0)
        
        # Color ramp for beautiful gradients
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 100)
        
        # Set gradient colors for maximum appeal
        base_color = material_data.get('base_color', [0.2, 0.6, 1.0])
        highlight_color = material_data.get('highlight_color', [0.9, 0.95, 1.0])
        
        color_ramp.color_ramp.elements[0].color = (*base_color, 1.0)
        color_ramp.color_ramp.elements[1].color = (*highlight_color, 1.0)
        
        # Add intermediate color for richness
        color_ramp.color_ramp.elements.new(0.6)
        mid_color = [
            (base_color[0] + highlight_color[0]) * 0.6,
            (base_color[1] + highlight_color[1]) * 0.6,
            (base_color[2] + highlight_color[2]) * 0.6
        ]
        color_ramp.color_ramp.elements[1].color = (*mid_color, 1.0)
        
        # Mix with base color
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (0, 200)
        mix.inputs['Factor'].default_value = 0.4
        mix.inputs['B'].default_value = (*base_color, 1.0)
        
        # Link everything
        links.new(tex_coord.outputs['Generated'], voronoi.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], wave.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
        
        links.new(voronoi.outputs['Distance'], math1.inputs[0])
        links.new(wave.outputs['Fac'], math1.inputs[1])
        links.new(math1.outputs['Value'], math2.inputs[0])
        links.new(noise.outputs['Fac'], math2.inputs[1])
        
        links.new(math2.outputs['Value'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix.inputs['A'])
        links.new(mix.outputs['Result'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> dict:
        return {
            'base_color': [0.2, 0.6, 1.0],
            'highlight_color': [0.9, 0.95, 1.0],
            'inner_glow': 0.1
        }


class GitHubLightingSetup(BaseLightingSetup):
    """Lighting setup optimized for GitHub showcase"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up lighting for maximum visual appeal"""
        self._clear_lights()
        
        # Primary key light - strong, slightly warm
        bpy.ops.object.light_add(type='AREA', location=(4, -3, 5))
        key_light = bpy.context.active_object
        key_light.name = "GitHubKey"
        key_light.rotation_euler = (math.radians(30), 0, math.radians(35))
        key_light.data.energy = lighting_data.get('key_energy', 20)
        key_light.data.size = 2.5
        key_light.data.color = [1.0, 0.95, 0.9]  # Slightly warm
        
        # Fill light - cooler, softer
        bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
        fill_light = bpy.context.active_object
        fill_light.name = "GitHubFill"
        fill_light.rotation_euler = (math.radians(40), 0, math.radians(-25))
        fill_light.data.energy = lighting_data.get('fill_energy', 8)
        fill_light.data.size = 3.0
        fill_light.data.color = [0.9, 0.95, 1.0]  # Cool blue
        
        # Rim light for dramatic edge definition
        bpy.ops.object.light_add(type='SPOT', location=(1, 5, 4))
        rim_light = bpy.context.active_object
        rim_light.name = "GitHubRim"
        rim_light.rotation_euler = (math.radians(-25), 0, math.radians(15))
        rim_light.data.energy = lighting_data.get('rim_energy', 25)
        rim_light.data.spot_size = math.radians(45)
        rim_light.data.spot_blend = 0.2
        rim_light.data.color = [0.95, 0.98, 1.0]
        
        # Subtle under light for base glow
        bpy.ops.object.light_add(type='AREA', location=(0, 0, -1.5))
        under_light = bpy.context.active_object
        under_light.name = "GitHubUnder"
        under_light.rotation_euler = (0, 0, 0)
        under_light.data.energy = lighting_data.get('under_energy', 3)
        under_light.data.size = 2.0
        under_light.data.color = [0.8, 0.9, 1.0]
        
        print("✨ GitHub showcase lighting setup complete")
    
    def _clear_lights(self):
        """Remove existing lights"""
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'key_energy': 20,
            'fill_energy': 8,
            'rim_energy': 25,
            'under_energy': 3
        }


def create_github_showcase():
    """Create a stunning gemstone render for GitHub README"""
    print("✨ Creating GitHub Showcase Render")
    print("=" * 50)
    
    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Register showcase components
    mesh_creator.register_generator('github_showcase', GitHubShowcaseGenerator())
    material_manager.register_style('github', GitHubGemStyle())
    lighting_manager.register_lighting_setup('github', GitHubLightingSetup())
    
    # Create showcase gem specification
    gem_data = {
        'name': 'GitHubShowcase',
        'description': 'A stunning crystal showcase for GitHub README',
        'base_shape': 'github_showcase',
        'geometry': {
            'height': 2.8,
            'base_size': 1.1,
            'facets': 16,
            'detail_level': 0.8
        },
        'material': {
            'style': 'github',
            'base_color': [0.15, 0.55, 0.95],  # Brilliant blue
            'highlight_color': [0.95, 0.98, 1.0],  # Bright white highlights
            'inner_glow': 0.08
        },
        'lighting': {
            'setup': 'github',
            'key_energy': 22,
            'fill_energy': 9,
            'rim_energy': 28,
            'under_energy': 4
        },
        'render_settings': {
            'samples': 256,
            'resolution': [800, 800]
        }
    }
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Create the showcase gemstone
    print("💎 Creating showcase crystal geometry...")
    gem_obj = mesh_creator.create_gem_geometry(gem_data)
    
    print("🎨 Applying showcase material...")
    material = material_manager.create_material(gem_data)
    gem_obj.data.materials.append(material)
    
    print("💡 Setting up showcase lighting...")
    lighting_manager.setup_lighting(gem_data)
    
    # Setup transparent world
    print("🌍 Setting up transparent background...")
    setup_transparent_world()
    
    # Setup camera for optimal showcase angle
    print("📷 Positioning showcase camera...")
    setup_showcase_camera()
    
    # Setup render settings for GitHub
    print("🎬 Configuring GitHub render settings...")
    setup_github_render(gem_data['render_settings'])
    
    # Save scene
    output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
    output_path.mkdir(parents=True, exist_ok=True)
    
    scene_file = output_path / "GitHubShowcase.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    
    # Render the showcase
    render_path = Path(__file__).parent / "examples" / "github_showcase.png"
    bpy.context.scene.render.filepath = str(render_path)
    
    print("📸 Rendering GitHub showcase...")
    bpy.ops.render.render(write_still=True)
    
    print("=" * 50)
    print("🎉 GITHUB SHOWCASE COMPLETE!")
    print(f"📁 Scene: {scene_file}")
    print(f"🖼️ Render: {render_path}")
    print("✨ Features:")
    print("   - Transparent background for GitHub")
    print("   - Optimized 800x800 resolution")
    print("   - Stunning crystalline internal structure")
    print("   - Professional showcase lighting")
    print("   - Perfect for README display")
    
    return gem_obj


def setup_transparent_world():
    """Set up transparent world background"""
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("GitHubWorld")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Simple transparent background
    background = nodes.new(type='ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs['Color'].default_value = (0, 0, 0, 0)  # Transparent
    background.inputs['Strength'].default_value = 0.0
    
    output = nodes.new(type='ShaderNodeOutputWorld')
    output.location = (200, 0)
    
    links.new(background.outputs['Background'], output.inputs['Surface'])


def setup_showcase_camera():
    """Set up camera for perfect showcase angle"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)
    
    # Create showcase camera
    bpy.ops.object.camera_add(location=(3.2, -4.5, 2.8))
    camera = bpy.context.active_object
    camera.name = "GitHubCamera"
    
    # Perfect showcase angle
    camera.rotation_euler = (math.radians(65), 0, math.radians(32))
    
    # Camera settings for showcase
    camera.data.lens = 85  # Portrait lens for minimal distortion
    camera.data.dof.use_dof = False  # Keep everything sharp
    
    bpy.context.scene.camera = camera


def setup_github_render(render_settings: dict):
    """Set up render settings optimized for GitHub"""
    scene = bpy.context.scene
    
    # Use Cycles for quality
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 256)
    
    # Perfect square format for GitHub
    resolution = render_settings.get('resolution', [800, 800])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Enable transparency
    scene.render.film_transparent = True
    
    # Color management for web display
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.exposure = 0.2
    scene.view_settings.gamma = 1.0
    
    # High quality settings
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    
    # Output settings with transparency
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15


if __name__ == "__main__":
    create_github_showcase()