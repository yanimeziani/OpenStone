#!/usr/bin/env python3
"""
Create Volcanic Stone Showcase
Generate a beautiful volcanic stone with glowing lava cracks and dramatic lighting
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


class VolcanicStoneGenerator(BaseMeshGenerator):
    """Volcanic stone generator with rough surface and lava cracks"""

    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a volcanic stone with hollow interior and surface displacement"""
        # Create main stone shape with higher subdivisions for hollow shell
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, location=(0, 0, 0))
        stone = bpy.context.active_object
        stone.name = "VolcanicStone"

        # Scale to create stone proportions
        stone.scale = geometry_data.get('stone_scale', [1.2, 1.0, 1.4])

        # Create hollow interior using Solidify modifier
        solidify_mod = stone.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify_mod.thickness = geometry_data.get('wall_thickness', -0.15)  # Negative for inward shell
        solidify_mod.offset = 1.0  # Push walls inward

        # Add subdivision for smooth surfaces before displacement
        subdiv_mod = stone.modifiers.new(name="Subdivision", type='SUBSURF')
        subdiv_mod.levels = 3
        subdiv_mod.render_levels = 4

        # Add displacement for rocky surface
        displace_mod = stone.modifiers.new(name="Displace", type='DISPLACE')
        
        # Create a new texture for displacement
        rock_texture = bpy.data.textures.new('RockTexture', type='CLOUDS')
        rock_texture.noise_scale = geometry_data.get('noise_scale', 0.25)
        rock_texture.noise_depth = 2
        
        displace_mod.texture = rock_texture
        displace_mod.strength = geometry_data.get('displacement_strength', 0.3)

        # Apply modifiers
        bpy.ops.object.modifier_apply(modifier=solidify_mod.name)
        bpy.ops.object.modifier_apply(modifier=subdiv_mod.name)
        bpy.ops.object.modifier_apply(modifier=displace_mod.name)

        # Create realistic crack geometry with actual holes
        bpy.context.view_layer.objects.active = stone
        
        # Enter bmesh for precise crack creation
        bm = bmesh.new()
        bm.from_mesh(stone.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        
        # Create multiple crack openings at various locations
        crack_locations = [
            {'center': Vector((0.0, 0.0, 0.9)), 'radius': 0.3, 'depth': 0.8},   # Top opening
            {'center': Vector((0.6, 0.3, 0.2)), 'radius': 0.15, 'depth': 0.6},  # Side crack
            {'center': Vector((-0.4, -0.5, 0.0)), 'radius': 0.12, 'depth': 0.5}, # Another side
            {'center': Vector((0.2, -0.7, -0.3)), 'radius': 0.1, 'depth': 0.4},  # Bottom area
        ]
        
        for crack in crack_locations:
            # Select vertices within crack radius
            crack_verts = []
            for v in bm.verts:
                distance = (v.co - crack['center']).length
                if distance < crack['radius']:
                    # Create jagged crack by varying selection
                    noise_factor = random.uniform(0.7, 1.3)
                    if distance < crack['radius'] * noise_factor:
                        crack_verts.append(v)
            
            # Delete vertices to create holes
            if crack_verts:
                bmesh.ops.delete(bm, geom=crack_verts, context='VERTS')
        
        # Create irregular surface damage
        damaged_verts = []
        for v in bm.verts:
            # Random surface damage
            if random.random() < 0.02:  # 2% chance for each vertex
                damaged_verts.append(v)
        
        if damaged_verts:
            bmesh.ops.delete(bm, geom=damaged_verts, context='VERTS')
            
        # Update mesh
        bm.to_mesh(stone.data)
        bm.free()

        # Create internal magma cores
        self._create_magma_cores(geometry_data)
        
        # Add volumetric atmosphere inside
        self._create_volumetric_atmosphere()

        return stone

    def _create_magma_cores(self, geometry_data: dict):
        """Create internal magma cores that glow through cracks"""
        num_cores = geometry_data.get('magma_cores', 8)
        core_scale = geometry_data.get('core_scale', 0.08)
        
        for i in range(num_cores):
            # Random position inside the stone
            x = random.uniform(-0.6, 0.6)
            y = random.uniform(-0.6, 0.6)
            z = random.uniform(-0.4, 0.6)
            
            # Create small sphere for magma core
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2, 
                location=(x, y, z), 
                radius=core_scale
            )
            core = bpy.context.active_object
            core.name = f"MagmaCore_{i+1}"
            
            # Create emission material for cores
            core_material = bpy.data.materials.new(name=f"MagmaCore_{i+1}_Mat")
            core_material.use_nodes = True
            core_nodes = core_material.node_tree.nodes
            core_nodes.clear()
            
            emission = core_nodes.new(type='ShaderNodeEmission')
            emission.location = (0, 0)
            emission.inputs['Color'].default_value = (1.0, 0.3, 0.05, 1.0)
            emission.inputs['Strength'].default_value = 50.0
            
            output = core_nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (200, 0)
            
            core_material.node_tree.links.new(
                emission.outputs['Emission'], 
                output.inputs['Surface']
            )
            
            core.data.materials.append(core_material)
    
    def _create_volumetric_atmosphere(self):
        """Create volumetric atmosphere inside the hollow stone"""
        # Create a scaled-down icosphere for volume
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=3, 
            location=(0, 0, 0), 
            radius=0.85
        )
        volume_obj = bpy.context.active_object
        volume_obj.name = "VolumetricAtmosphere"
        
        # Create volumetric material
        volume_material = bpy.data.materials.new(name="VolumetricAtmosphere_Mat")
        volume_material.use_nodes = True
        volume_nodes = volume_material.node_tree.nodes
        volume_links = volume_material.node_tree.links
        
        volume_nodes.clear()
        
        # Volume Scatter shader
        volume_scatter = volume_nodes.new(type='ShaderNodeVolumeScatter')
        volume_scatter.location = (0, 0)
        volume_scatter.inputs['Color'].default_value = (1.0, 0.4, 0.1, 1.0)
        volume_scatter.inputs['Density'].default_value = 0.8
        volume_scatter.inputs['Anisotropy'].default_value = 0.3
        
        # Add noise for volume variation
        noise_texture = volume_nodes.new(type='ShaderNodeTexNoise')
        noise_texture.location = (-300, 0)
        noise_texture.inputs['Scale'].default_value = 3.0
        noise_texture.inputs['Detail'].default_value = 8.0
        
        # Math node to control density variation
        math_multiply = volume_nodes.new(type='ShaderNodeMath')
        math_multiply.location = (-150, 0)
        math_multiply.operation = 'MULTIPLY'
        math_multiply.inputs[1].default_value = 0.5
        
        # Output
        output = volume_nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Link nodes
        volume_links.new(noise_texture.outputs['Fac'], math_multiply.inputs[0])
        volume_links.new(math_multiply.outputs['Value'], volume_scatter.inputs['Density'])
        volume_links.new(volume_scatter.outputs['Volume'], output.inputs['Volume'])
        
        volume_obj.data.materials.append(volume_material)

    def get_default_params(self) -> dict:
        return {
            'stone_scale': [1.2, 1.0, 1.4],
            'noise_scale': 0.25,
            'displacement_strength': 0.3,
            'wall_thickness': -0.12,
            'magma_cores': 15,
            'core_scale': 0.05,
        }


class VolcanicStoneMaterial(BaseMaterialStyle):
    """Realistic glass-like volcanic stone material with translucency and refraction"""

    def create_material(self, material_data: dict, name: str = "VolcanicStone") -> bpy.types.Material:
        """Create volcanic stone material"""
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        nodes.clear()

        # Main principled shader
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (400, 0)

        # Glass-like translucent volcanic material
        base_color = material_data.get('base_color', [0.8, 0.3, 0.1])  # Warm amber color
        principled.inputs['Base Color'].default_value = (*base_color, 1.0)
        principled.inputs['Roughness'].default_value = material_data.get('roughness', 0.05)  # Very smooth
        
        # High transmission for glass-like effect
        if 'Transmission Weight' in principled.inputs:
            principled.inputs['Transmission Weight'].default_value = material_data.get('transmission', 0.95)
        elif 'Transmission' in principled.inputs:
            principled.inputs['Transmission'].default_value = material_data.get('transmission', 0.95)
            
        # Realistic glass IOR
        principled.inputs['IOR'].default_value = material_data.get('ior', 1.52)
        
        # Minimal specular for realism
        if 'Specular' in principled.inputs:
            principled.inputs['Specular'].default_value = 0.5
        elif 'Specular IOR Level' in principled.inputs:
            principled.inputs['Specular IOR Level'].default_value = 0.5
            
        # Add subtle subsurface for depth
        if 'Subsurface Weight' in principled.inputs:
            principled.inputs['Subsurface Weight'].default_value = material_data.get('subsurface_weight', 0.1)
            principled.inputs['Subsurface Radius'].default_value = material_data.get('subsurface_radius', [2.0, 1.0, 0.5])
        elif 'Subsurface' in principled.inputs:
            principled.inputs['Subsurface'].default_value = material_data.get('subsurface_weight', 0.1)
            
        # Slight absorption for realistic coloring
        principled.inputs['Alpha'].default_value = material_data.get('alpha', 0.85)

        # Create subtle surface texture for realism
        final_shader = self._create_glass_surface_texture(nodes, links, principled, material_data)

        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 0)

        # The principled shader is the final surface
        links.new(final_shader.outputs['BSDF'], output.inputs['Surface'])

        return material

    def _create_glass_surface_texture(self, nodes, links, principled, material_data):
        """Create subtle glass surface texture with micro-imperfections"""
        # Texture coordinate
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)

        # Mapping for surface details
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        mapping.inputs['Scale'].default_value = material_data.get('texture_scale', [20.0, 20.0, 20.0])

        # Noise for surface imperfections
        surface_noise = nodes.new(type='ShaderNodeTexNoise')
        surface_noise.location = (-200, 0)
        surface_noise.inputs['Scale'].default_value = 15.0
        surface_noise.inputs['Detail'].default_value = 8.0
        surface_noise.inputs['Roughness'].default_value = 0.5

        # Very subtle bump for micro-surface details
        bump_node = nodes.new(type='ShaderNodeBump')
        bump_node.location = (0, -100)
        bump_node.inputs['Strength'].default_value = 0.02  # Very subtle

        # Noise for thickness variation (replacing deprecated Musgrave)
        thickness_noise = nodes.new(type='ShaderNodeTexNoise')
        thickness_noise.location = (-200, 200)
        thickness_noise.inputs['Scale'].default_value = 3.0
        thickness_noise.inputs['Detail'].default_value = 4.0
        thickness_noise.inputs['Roughness'].default_value = 0.6
        
        # Math node to control thickness variation
        math_multiply = nodes.new(type='ShaderNodeMath')
        math_multiply.location = (0, 200)
        math_multiply.operation = 'MULTIPLY'
        math_multiply.inputs[1].default_value = 0.3
        
        # Map Range to adjust alpha variation
        map_range = nodes.new(type='ShaderNodeMapRange')
        map_range.location = (200, 200)
        map_range.inputs['From Min'].default_value = 0.0
        map_range.inputs['From Max'].default_value = 1.0
        map_range.inputs['To Min'].default_value = 0.7
        map_range.inputs['To Max'].default_value = 0.95

        # Link texture system
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], surface_noise.inputs['Vector'])
        links.new(mapping.outputs['Vector'], thickness_noise.inputs['Vector'])
        
        # Surface details
        links.new(surface_noise.outputs['Fac'], bump_node.inputs['Height'])
        links.new(bump_node.outputs['Normal'], principled.inputs['Normal'])
        
        # Thickness variation for realistic glass
        links.new(thickness_noise.outputs['Fac'], math_multiply.inputs[0])
        links.new(math_multiply.outputs['Value'], map_range.inputs['Value'])
        links.new(map_range.outputs['Result'], principled.inputs['Alpha'])
        
        return principled
        

    def get_default_params(self) -> dict:
        return {
            'base_color': [0.9, 0.4, 0.15],
            'roughness': 0.05,
            'texture_scale': [20.0, 20.0, 20.0],
            'transmission': 0.95,
            'ior': 1.52,
            'subsurface_weight': 0.1,
            'subsurface_radius': [2.0, 1.0, 0.5],
            'alpha': 0.85,
        }


class FieryLightingSetup(BaseLightingSetup):
    """Fiery lighting for dramatic volcanic stone showcase"""

    def setup_lights(self, lighting_data: dict):
        """Set up advanced four-point fiery lighting system"""
        self._clear_lights()

        # Main key light with orange color
        bpy.ops.object.light_add(type='AREA', location=(4, -3, 5))
        key_light = bpy.context.active_object
        key_light.name = "FieryKey"
        key_light.rotation_euler = (math.radians(25), 0, math.radians(35))
        key_light.data.energy = lighting_data.get('key_energy', 150)
        key_light.data.size = 4.0
        key_light.data.color = lighting_data.get('key_color', [1.0, 0.4, 0.1])

        # Rim light for edge definition (deep red)
        bpy.ops.object.light_add(type='AREA', location=(-4, 2, 3))
        rim_light = bpy.context.active_object
        rim_light.name = "FieryRim"
        rim_light.rotation_euler = (math.radians(45), 0, math.radians(-45))
        rim_light.data.energy = lighting_data.get('rim_energy', 100)
        rim_light.data.size = 3.0
        rim_light.data.color = lighting_data.get('rim_color', [0.8, 0.1, 0.05])

        # Spot light for atmospheric drama
        bpy.ops.object.light_add(type='SPOT', location=(2, 4, 6))
        spot_light = bpy.context.active_object
        spot_light.name = "AtmosphericSpot"
        spot_light.rotation_euler = (math.radians(-35), 0, math.radians(-25))
        spot_light.data.energy = lighting_data.get('spot_energy', 200)
        spot_light.data.spot_size = math.radians(45)
        spot_light.data.spot_blend = 0.3
        spot_light.data.color = lighting_data.get('spot_color', [1.0, 0.6, 0.3])

        # Interior point light to illuminate hollow core
        bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.2))
        interior_light = bpy.context.active_object
        interior_light.name = "InteriorCore"
        interior_light.data.energy = lighting_data.get('interior_energy', 80)
        interior_light.data.color = lighting_data.get('interior_color', [1.0, 0.2, 0.05])
        interior_light.data.shadow_soft_size = 0.5

        # Fill light for ambient glow (reduced to balance four lights)
        bpy.ops.object.light_add(type='POINT', location=(0, 5, 2))
        fill_light = bpy.context.active_object
        fill_light.name = "AmbientFill"
        fill_light.data.energy = lighting_data.get('fill_energy', 30)
        fill_light.data.color = lighting_data.get('fill_color', [1.0, 0.5, 0.2])

        print("🔥 Advanced four-point fiery lighting setup complete")

    def _clear_lights(self):
        lights_to_remove = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        for light in lights_to_remove:
            bpy.data.objects.remove(light, do_unlink=True)

    def get_default_params(self) -> dict:
        return {
            'key_energy': 150,
            'key_color': [1.0, 0.4, 0.1],
            'rim_energy': 100,
            'rim_color': [0.8, 0.1, 0.05],
            'spot_energy': 200,
            'spot_color': [1.0, 0.6, 0.3],
            'interior_energy': 80,
            'interior_color': [1.0, 0.2, 0.05],
            'fill_energy': 30,
            'fill_color': [1.0, 0.5, 0.2],
        }


class HDRIWorldEnvironment(BaseWorldEnvironment):
    """HDRI world environment for realistic reflections and lighting"""

    def setup_world(self, world_data: dict):
        """Set up HDRI world environment with studio lighting"""
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("HDRIWorld")
            bpy.context.scene.world = world

        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        nodes.clear()

        # Environment Texture for HDRI (or procedural if no HDRI available)
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 300)
        
        # Mapping for environment rotation
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 300)
        mapping.inputs['Rotation'].default_value[2] = world_data.get('rotation', 0.0)
        
        # Use Sky Texture for procedural HDRI-like environment
        sky_texture = nodes.new(type='ShaderNodeTexSky')
        sky_texture.location = (-200, 300)
        sky_texture.sky_type = 'NISHITA'
        
        # Set sun parameters (use correct input names)
        if 'Sun Elevation' in sky_texture.inputs:
            sky_texture.inputs['Sun Elevation'].default_value = world_data.get('sun_elevation', 0.2)
        elif 'Elevation' in sky_texture.inputs:
            sky_texture.inputs['Elevation'].default_value = world_data.get('sun_elevation', 0.2)
            
        if 'Sun Rotation' in sky_texture.inputs:
            sky_texture.inputs['Sun Rotation'].default_value = world_data.get('sun_rotation', 0.0)
        elif 'Rotation' in sky_texture.inputs:
            sky_texture.inputs['Rotation'].default_value = world_data.get('sun_rotation', 0.0)
            
        # Set atmospheric parameters if available
        if 'Altitude' in sky_texture.inputs:
            sky_texture.inputs['Altitude'].default_value = 1000
        if 'Air Density' in sky_texture.inputs:
            sky_texture.inputs['Air Density'].default_value = 1.0
        if 'Dust Density' in sky_texture.inputs:
            sky_texture.inputs['Dust Density'].default_value = 0.1
        
        # Background shader
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 300)
        background.inputs['Strength'].default_value = world_data.get('strength', 1.5)
        
        # Add slight warm color bias
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-100, 100)
        color_ramp.color_ramp.elements[0].color = (0.8, 0.4, 0.2, 1.0)
        color_ramp.color_ramp.elements[1].color = (1.0, 0.6, 0.3, 1.0)
        
        # Mix the sky with warm bias
        mix_rgb = nodes.new(type='ShaderNodeMix')
        mix_rgb.location = (-50, 300)
        mix_rgb.data_type = 'RGBA'
        mix_rgb.blend_type = 'MULTIPLY'
        
        # Handle different Blender versions for mix factor input
        if 'Fac' in mix_rgb.inputs:
            mix_rgb.inputs['Fac'].default_value = 0.3
        elif 'Factor' in mix_rgb.inputs:
            mix_rgb.inputs['Factor'].default_value = 0.3

        # Output
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (200, 300)

        # Link nodes (Sky texture may not need vector input)
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        
        # Sky texture might not have Vector input in some versions
        if 'Vector' in sky_texture.inputs:
            links.new(mapping.outputs['Vector'], sky_texture.inputs['Vector'])
            
        # Handle different Mix node input names
        if 'Color1' in mix_rgb.inputs and 'Color2' in mix_rgb.inputs:
            links.new(sky_texture.outputs['Color'], mix_rgb.inputs['Color1'])
            links.new(color_ramp.outputs['Color'], mix_rgb.inputs['Color2'])
        elif 'A' in mix_rgb.inputs and 'B' in mix_rgb.inputs:
            links.new(sky_texture.outputs['Color'], mix_rgb.inputs['A'])
            links.new(color_ramp.outputs['Color'], mix_rgb.inputs['B'])
        
        # Handle different Mix node output names
        if 'Result' in mix_rgb.outputs:
            links.new(mix_rgb.outputs['Result'], background.inputs['Color'])
        elif 'Color' in mix_rgb.outputs:
            links.new(mix_rgb.outputs['Color'], background.inputs['Color'])
            
        links.new(background.outputs['Background'], output.inputs['Surface'])

        print("🌍 HDRI world environment with studio lighting complete")

    def get_default_params(self) -> dict:
        return {}


def create_volcanic_stone_showcase():
    """Create a volcanic stone showcase"""
    print("🌋 Creating Volcanic Stone Showcase")
    print("=" * 50)

    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()

    # Register volcanic components
    mesh_creator.register_generator('volcanic_stone', VolcanicStoneGenerator())
    material_manager.register_style('volcanic_stone', VolcanicStoneMaterial())
    lighting_manager.register_lighting_setup('fiery', FieryLightingSetup())
    lighting_manager.register_world_environment('hdri', HDRIWorldEnvironment())

    # Create volcanic stone specification
    gem_data = {
        'name': 'VolcanicStoneShowcase',
        'description': 'A rough volcanic stone with glowing lava cracks',
        'base_shape': 'volcanic_stone',
        'geometry': {
            'stone_scale': [1.2, 1.1, 1.3],
            'noise_scale': 0.3,
            'displacement_strength': 0.25,
        },
        'material': {
            'style': 'volcanic_stone',
            'base_color': [0.95, 0.45, 0.2],
            'roughness': 0.02,
            'transmission': 0.98,
            'ior': 1.55,
            'alpha': 0.8,
        },
        'lighting': {
            'setup': 'fiery',
            'key_energy': 300,
            'rim_energy': 200,
        },
        'world': {
            'environment': 'hdri',
            'strength': 2.0,
            'sun_elevation': 0.3,
            'sun_rotation': 1.2,
            'rotation': 0.5
        },
        'render_settings': {
            'samples': 512,
            'resolution': [1080, 1080],
            'exposure': 0.3
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

    # Create the volcanic stone
    print("🌋 Creating volcanic stone geometry...")
    stone_obj = mesh_creator.create_gem_geometry(gem_data)

    print("🎨 Applying volcanic stone material...")
    stone_material = material_manager.create_material(gem_data)
    stone_obj.data.materials.append(stone_material)

    print("💡 Setting up fiery lighting...")
    lighting_manager.setup_lighting(gem_data)

    print("🌍 Creating dark environment...")
    lighting_manager.setup_world(gem_data)

    # Setup camera
    print("📷 Positioning camera...")
    setup_camera()

    # Setup render settings
    print("🎬 Configuring render...")
    setup_render(gem_data['render_settings'])

    # Render the volcanic stone
    render_path = Path(__file__).parent / "examples" / "volcanic_stone_showcase.png"
    bpy.context.scene.render.filepath = str(render_path)

    print("📸 Rendering volcanic stone showcase...")

    # Add a handler to wait for render completion, as rendering is asynchronous
    _render_complete = False
    def _render_complete_handler(scene):
        nonlocal _render_complete
        _render_complete = True

    bpy.app.handlers.render_complete.append(_render_complete_handler)

    bpy.ops.render.render(write_still=True)

    # Block script execution until render is complete
    import time
    while not _render_complete:
        time.sleep(1)

    bpy.app.handlers.render_complete.remove(_render_complete_handler)

    print("=" * 50)
    print("🏆 VOLCANIC STONE SHOWCASE COMPLETE!")
    print(f"🖼️ Render: {render_path}")
    print("✨ Volcanic Features:")
    print("   - Rough, displaced stone surface")
    print("   - Glowing lava cracks with emission")
    print("   - Dramatic fiery lighting setup")
    print("   - Dark, atmospheric environment")

    return stone_obj


def setup_camera():
    """Set up camera for showcase"""
    # Remove existing cameras
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    for cam in cameras:
        bpy.data.objects.remove(cam, do_unlink=True)

    # Create camera
    bpy.ops.object.camera_add(location=(5, -5, 3.5))
    camera = bpy.context.active_object
    camera.name = "ShowcaseCamera"

    # Point camera at origin
    camera.rotation_euler = (math.radians(65), 0, math.radians(45))

    # Camera settings
    camera.data.lens = 50
    bpy.context.scene.camera = camera


def setup_render(render_settings: dict):
    """Set up render settings"""
    scene = bpy.context.scene

    # Use Cycles for realistic materials, caustics, and volumetrics
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_settings.get('samples', 512)  # Higher samples for caustics
    scene.cycles.use_denoising = True
    
    # Enable caustics for light refraction through glass
    scene.cycles.caustics_reflective = True
    scene.cycles.caustics_refractive = True
    
    # Higher light bounces for better caustics
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 8
    scene.cycles.transmission_bounces = 12
    scene.cycles.volume_bounces = 2
    scene.cycles.transparent_max_bounces = 8
    
    # Check for OptiX device
    cycles_prefs = bpy.context.preferences.addons.get('cycles').preferences
    if cycles_prefs and cycles_prefs.get_devices_for_type('OPTIX'):
        scene.cycles.denoiser = 'OPTIX'
    else:
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'


    # Set resolution
    resolution = render_settings.get('resolution', [1080, 1080])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100

    # Color management with High Contrast and exposure adjustment
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = render_settings.get('exposure', 0.5)

    # Output settings
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True


if __name__ == "__main__":
    create_volcanic_stone_showcase()
