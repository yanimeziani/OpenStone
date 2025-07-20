#!/usr/bin/env python3
"""
Create Cinematic Geode Showcase
Generate a beautiful translucent geode with internal crystal formations and dramatic lighting
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


class CinematicGeodeGenerator(BaseMeshGenerator):
    """Cinematic geode generator with hollow interior and crystal formations"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a cinematic geode with internal crystals"""
        # Create main geode shape
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, location=(0, 0, 0))
        geode = bpy.context.active_object
        geode.name = "CinematicGeode"
        
        # Scale to create geode proportions
        geode.scale = geometry_data.get('geode_scale', [1.2, 1.0, 1.4])
        
        # Apply initial deformation
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Add natural geode variation
        bpy.ops.transform.vertex_random(offset=geometry_data.get('surface_variation', 0.15))
        
        # Create hollow interior using bmesh
        bpy.ops.object.mode_set(mode='EDIT')
        me = geode.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        
        # Inset all faces to create wall thickness
        bmesh.ops.inset_region(bm, faces=bm.faces[:], thickness=geometry_data.get('wall_thickness', 0.15))
        
        # Select newly created inner faces
        inner_faces = [f for f in bm.faces if f.select]
        
        # Extrude inner faces inward
        ret = bmesh.ops.extrude_face_region(bm, geom=inner_faces)
        extruded_verts = [v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)]
        
        # Scale inner geometry to create hollow space
        bmesh.ops.scale(bm, vec=(0.6, 0.6, 0.6), verts=extruded_verts)
        
        # Delete top faces to create opening
        z_threshold = 0.5
        faces_to_delete = [f for f in bm.faces if f.calc_center_median().z > z_threshold]
        bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')
        
        # Update mesh (ensure object mode first)
        bpy.ops.object.mode_set(mode='OBJECT')
        bm.to_mesh(me)
        bm.free()
        
        # Add solidify modifier for geode walls
        solidify_mod = geode.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify_mod.thickness = geometry_data.get('wall_thickness', 0.05)
        solidify_mod.offset = 0
        
        # Add subdivision for smooth surfaces
        subdiv_mod = geode.modifiers.new(name="Subdivision", type='SUBSURF')
        subdiv_mod.levels = 2
        subdiv_mod.render_levels = 3
        
        # Create internal crystal formations
        self._create_internal_crystals(geode, geometry_data)
        
        return geode
    
    def _create_internal_crystals(self, geode_obj, geometry_data):
        """Create internal crystal formations"""
        crystal_count = geometry_data.get('crystal_count', 12)
        
        for i in range(crystal_count):
            # Create crystal
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2)
            crystal = bpy.context.active_object
            crystal.name = f"InternalCrystal_{i}"
            
            # Random position inside geode
            angle = (i / crystal_count) * 2 * math.pi + random.uniform(-0.5, 0.5)
            radius = random.uniform(0.2, 0.5)
            height = random.uniform(-0.3, 0.2)
            
            crystal.location = (
                radius * math.cos(angle),
                radius * math.sin(angle),
                height
            )
            
            # Random scale for variety
            scale = random.uniform(0.05, 0.15)
            crystal.scale = (scale, scale, scale * random.uniform(1.5, 3.0))
            
            # Random rotation
            crystal.rotation_euler = (
                random.uniform(0, math.pi),
                random.uniform(0, math.pi),
                random.uniform(0, 2 * math.pi)
            )
            
            # Parent to geode
            crystal.parent = geode_obj
    
    def get_default_params(self) -> dict:
        return {
            'geode_scale': [1.2, 1.0, 1.4],
            'surface_variation': 0.15,
            'wall_thickness': 0.05,
            'crystal_count': 12
        }


class CinematicGeodeMaterial(BaseMaterialStyle):
    """Cinematic geode material with translucency and internal reflections"""
    
    def create_material(self, material_data: dict, name: str = "CinematicGeode") -> bpy.types.Material:
        """Create cinematic geode material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (400, 0)
        
        # Set translucent properties
        base_color = material_data.get('base_color', [0.9, 0.7, 0.8])
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = material_data.get('transmission', 0.95)
        principled.inputs['Alpha'].default_value = material_data.get('alpha', 0.8)
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.45)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.1)
        
        # Add subsurface scattering for internal glow
        principled.inputs['Subsurface Weight'].default_value = material_data.get('subsurface', 0.3)
        subsurface_color = material_data.get('subsurface_color', [1.0, 0.4, 0.6])
        # Try different possible input names for subsurface color
        if 'Subsurface Color' in principled.inputs:
            principled.inputs['Subsurface Color'].default_value = (*subsurface_color, 1.0)
        elif 'Subsurface Radius' in principled.inputs:
            principled.inputs['Subsurface Radius'].default_value = subsurface_color
        
        # Create texture for surface variation
        self._create_surface_texture(nodes, links, principled, material_data)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 0)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Enable blend mode for transparency
        material.blend_method = 'BLEND'
        
        return material
    
    def _create_surface_texture(self, nodes, links, principled, material_data):
        """Create surface texture for geode"""
        # Texture coordinate
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)
        
        # Mapping
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        mapping.inputs['Scale'].default_value = material_data.get('texture_scale', [3.0, 3.0, 3.0])
        
        # Noise for surface variation
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 200)
        noise.inputs['Scale'].default_value = 8.0
        noise.inputs['Detail'].default_value = 10.0
        noise.inputs['Roughness'].default_value = 0.6
        
        # Voronoi for crystal-like patterns
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-400, 0)
        voronoi.feature = 'F1'
        voronoi.inputs['Scale'].default_value = 15.0
        
        # Color ramp for variation
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 100)
        color_ramp.color_ramp.elements[0].color = (0.8, 0.6, 0.7, 1.0)
        color_ramp.color_ramp.elements[1].color = (1.0, 0.8, 0.9, 1.0)
        
        # Mix for combining textures
        mix = nodes.new(type='ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.location = (-200, -100)
        mix.inputs['Factor'].default_value = 0.3
        
        # Link texture system
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix.inputs['A'])
        links.new(voronoi.outputs['Distance'], mix.inputs['Factor'])
        
        # Connect to principled base color
        links.new(mix.outputs['Result'], principled.inputs['Base Color'])
    
    def get_default_params(self) -> dict:
        return {
            'base_color': [0.9, 0.7, 0.8],
            'transmission': 0.95,
            'alpha': 0.8,
            'ior': 1.45,
            'roughness': 0.1,
            'subsurface': 0.3,
            'subsurface_color': [1.0, 0.4, 0.6],
            'texture_scale': [3.0, 3.0, 3.0]
        }


class CinematicCrystalMaterial(BaseMaterialStyle):
    """Material for internal crystals"""
    
    def create_material(self, material_data: dict, name: str = "CinematicCrystal") -> bpy.types.Material:
        """Create internal crystal material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        
        # Principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        # Crystal properties
        crystal_color = material_data.get('crystal_color', [0.8, 0.3, 0.5])
        principled.inputs['Base Color'].default_value = (*crystal_color, 1.0)
        principled.inputs['Transmission Weight'].default_value = 0.9
        principled.inputs['IOR'].default_value = 1.5
        principled.inputs['Roughness'].default_value = 0.05
        
        # Add emission for internal glow
        principled.inputs['Emission Color'].default_value = (*crystal_color, 1.0)
        principled.inputs['Emission Strength'].default_value = material_data.get('emission_strength', 0.3)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        material.blend_method = 'BLEND'
        
        return material
    
    def get_default_params(self) -> dict:
        return {
            'crystal_color': [0.8, 0.3, 0.5],
            'emission_strength': 0.3
        }


class CinematicLightingSetup(BaseLightingSetup):
    """Cinematic lighting for dramatic geode showcase"""
    
    def setup_lights(self, lighting_data: dict):
        """Set up cinematic lighting"""
        self._clear_lights()
        
        # Main key light with purple/pink color
        bpy.ops.object.light_add(type='AREA', location=(4, -3, 5))
        key_light = bpy.context.active_object
        key_light.name = "CinematicKey"
        key_light.rotation_euler = (math.radians(25), 0, math.radians(35))
        key_light.data.energy = lighting_data.get('key_energy', 100)
        key_light.data.size = 3.0
        key_light.data.color = lighting_data.get('key_color', [1.0, 0.4, 0.8])
        
        # Rim light for edge definition
        bpy.ops.object.light_add(type='AREA', location=(-4, 2, 3))
        rim_light = bpy.context.active_object
        rim_light.name = "CinematicRim"
        rim_light.rotation_euler = (math.radians(45), 0, math.radians(-45))
        rim_light.data.energy = lighting_data.get('rim_energy', 50)
        rim_light.data.size = 2.0
        rim_light.data.color = lighting_data.get('rim_color', [0.6, 0.2, 0.9])
        
        # Fill light for internal illumination
        bpy.ops.object.light_add(type='POINT', location=(0, 0, -2))
        fill_light = bpy.context.active_object
        fill_light.name = "InternalFill"
        fill_light.data.energy = lighting_data.get('fill_energy', 30)
        fill_light.data.color = lighting_data.get('fill_color', [1.0, 0.6, 0.8])
        
        # Accent light for atmosphere
        bpy.ops.object.light_add(type='SPOT', location=(2, 4, 6))
        accent_light = bpy.context.active_object
        accent_light.name = "AtmosphereAccent"
        accent_light.rotation_euler = (math.radians(-30), 0, math.radians(-20))
        accent_light.data.energy = lighting_data.get('accent_energy', 60)
        accent_light.data.spot_size = math.radians(45)
        accent_light.data.color = lighting_data.get('accent_color', [0.8, 0.2, 0.6])
        
        print("✨ Cinematic lighting setup complete")
    
    def _clear_lights(self):
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)
    
    def get_default_params(self) -> dict:
        return {
            'key_energy': 100,
            'key_color': [1.0, 0.4, 0.8],
            'rim_energy': 50,
            'rim_color': [0.6, 0.2, 0.9],
            'fill_energy': 30,
            'fill_color': [1.0, 0.6, 0.8],
            'accent_energy': 60,
            'accent_color': [0.8, 0.2, 0.6]
        }


class TransparentWorldEnvironment(BaseWorldEnvironment):
    """Transparent world environment for showcase"""
    
    def setup_world(self, world_data: dict):
        """Set up transparent world environment"""
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("TransparentWorld")
            bpy.context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        nodes.clear()
        
        # Transparent background
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (-200, 300)
        background.inputs['Color'].default_value = (0, 0, 0, 0)
        background.inputs['Strength'].default_value = 0.0
        
        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (0, 300)
        
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        print("🌍 Transparent world environment complete")
    
    def get_default_params(self) -> dict:
        return {}


def create_cinematic_geode_showcase():
    """Create a cinematic geode showcase"""
    print("💎 Creating Cinematic Geode Showcase")
    print("=" * 50)
    
    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Register cinematic components
    mesh_creator.register_generator('cinematic_geode', CinematicGeodeGenerator())
    material_manager.register_style('cinematic_geode', CinematicGeodeMaterial())
    material_manager.register_style('cinematic_crystal', CinematicCrystalMaterial())
    lighting_manager.register_lighting_setup('cinematic', CinematicLightingSetup())
    lighting_manager.register_world_environment('transparent', TransparentWorldEnvironment())
    
    # Create cinematic geode specification
    gem_data = {
        'name': 'CinematicGeodeShowcase',
        'description': 'A beautiful translucent geode with internal crystal formations',
        'base_shape': 'cinematic_geode',
        'geometry': {
            'geode_scale': [1.3, 1.0, 1.5],
            'surface_variation': 0.12,
            'wall_thickness': 0.04,
            'crystal_count': 15
        },
        'material': {
            'style': 'cinematic_geode',
            'base_color': [0.95, 0.75, 0.85],
            'transmission': 0.92,
            'alpha': 0.85,
            'ior': 1.45,
            'roughness': 0.08,
            'subsurface': 0.4,
            'subsurface_color': [1.0, 0.5, 0.7]
        },
        'lighting': {
            'setup': 'cinematic',
            'key_energy': 120,
            'key_color': [1.0, 0.3, 0.7],
            'rim_energy': 60,
            'rim_color': [0.5, 0.1, 0.8],
            'fill_energy': 40,
            'fill_color': [1.0, 0.7, 0.9],
            'accent_energy': 80,
            'accent_color': [0.9, 0.2, 0.5]
        },
        'world': {
            'environment': 'transparent'
        },
        'render_settings': {
            'samples': 256,
            'resolution': [1000, 1200]
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
    
    # Create the cinematic geode
    print("💎 Creating cinematic geode geometry...")
    geode_obj = mesh_creator.create_gem_geometry(gem_data)
    
    print("🎨 Applying cinematic geode material...")
    geode_material = material_manager.create_material(gem_data)
    geode_obj.data.materials.append(geode_material)
    
    # Apply crystal material to internal crystals
    print("✨ Applying crystal materials...")
    crystal_material = material_manager.create_material(
        {'crystal_color': [0.9, 0.4, 0.6], 'emission_strength': 0.4}, 
        'cinematic_crystal'
    )
    
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('InternalCrystal'):
            obj.data.materials.append(crystal_material)
    
    print("💡 Setting up cinematic lighting...")
    lighting_manager.setup_lighting(gem_data)
    
    print("🌍 Creating transparent environment...")
    lighting_manager.setup_world(gem_data)
    
    # Setup camera
    print("📷 Positioning cinematic camera...")
    setup_cinematic_camera()
    
    # Setup render settings
    print("🎬 Configuring cinematic render...")
    setup_cinematic_render(gem_data['render_settings'])
    
    # Render the cinematic geode
    render_path = Path(__file__).parent / "examples" / "cinematic_geode_showcase.png"
    bpy.context.scene.render.filepath = str(render_path)
    
    print("📸 Rendering cinematic geode showcase...")
    bpy.ops.render.render(write_still=True)
    
    print("=" * 50)
    print("🏆 CINEMATIC GEODE SHOWCASE COMPLETE!")
    print(f"🖼️ Render: {render_path}")
    print("✨ Cinematic Features:")
    print("   - Translucent geode with hollow interior")
    print("   - Internal crystal formations with emission")
    print("   - Dramatic purple/pink lighting setup")
    print("   - Subsurface scattering for internal glow")
    print("   - Transparent background for showcase")
    print("   - High-quality materials with transmission")
    
    return geode_obj


def setup_cinematic_camera():
    """Set up camera for cinematic showcase with proper framing"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)
    
    # Create camera positioned to frame geode with space around it
    bpy.ops.object.camera_add(location=(5.5, -6.0, 3.5))
    camera = bpy.context.active_object
    camera.name = "CinematicCamera"
    
    # Dramatic angle to show interior with proper framing
    camera.rotation_euler = (math.radians(65), 0, math.radians(40))
    
    # Camera settings for proper framing with space
    camera.data.lens = 50  # Wider lens for better framing with space
    camera.data.dof.use_dof = False  # Full focus for showcase
    
    bpy.context.scene.camera = camera


def setup_cinematic_render(render_settings: dict):
    """Set up render settings for cinematic geode"""
    scene = bpy.context.scene
    
    # Use Cycles for realistic materials
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 256)
    
    # Portrait resolution for geode
    resolution = render_settings.get('resolution', [1000, 1200])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Cinematic color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.2
    scene.view_settings.gamma = 1.0
    
    # Quality settings
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    
    # Transparency for showcase
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 90


if __name__ == "__main__":
    create_cinematic_geode_showcase()