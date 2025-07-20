#!/usr/bin/env python3
"""
Simple script to render an example gemstone image for README
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector
import json
import sys
from pathlib import Path

def clear_scene():
    """Clear the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_simple_crystal():
    """Create a simple crystal geometry"""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, location=(0, 0, 0))
    crystal = bpy.context.active_object
    crystal.name = "ExampleCrystal"
    
    # Add some reshaping to make it more crystal-like
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(1, 1.4, 1.2))
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return crystal

def create_crystal_material():
    """Create a simple crystal material"""
    material = bpy.data.materials.new(name="ExampleCrystalMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Set material properties for amethyst
    principled.inputs['Base Color'].default_value = (0.6, 0.3, 0.9, 1.0)  # Purple
    principled.inputs['Transmission Weight'].default_value = 0.9
    principled.inputs['Roughness'].default_value = 0.05
    principled.inputs['IOR'].default_value = 1.6
    
    # Add output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Link nodes
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return material

def setup_lighting():
    """Set up simple lighting for the scene"""
    # Add key light
    bpy.ops.object.light_add(type='AREA', location=(3, 3, 5))
    key_light = bpy.context.active_object
    key_light.data.energy = 50
    key_light.data.size = 2
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-2, 1, 3))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 20
    fill_light.data.size = 1.5
    
    # Add rim light
    bpy.ops.object.light_add(type='AREA', location=(0, -4, 2))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 30
    rim_light.data.size = 1

def setup_camera():
    """Set up camera for the render"""
    bpy.ops.object.camera_add(location=(4, -6, 3))
    camera = bpy.context.active_object
    
    # Point camera at crystal
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    # Create an empty target object
    bpy.ops.object.empty_add(location=(0, 0, 0))
    target = bpy.context.active_object
    target.name = "CameraTarget"
    constraint.target = target
    
    # Set as active camera
    bpy.context.scene.camera = camera

def setup_render_settings():
    """Set up render settings"""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.resolution_x = 800
    scene.render.resolution_y = 800
    scene.render.filepath = '/Users/yanimeziani/Desktop/PRISMATICS/openstone/examples/example_crystal.png'
    scene.render.image_settings.file_format = 'PNG'

def main():
    """Main function"""
    print("🎨 Creating example crystal render...")
    
    # Clear scene
    clear_scene()
    
    # Create crystal
    crystal = create_simple_crystal()
    
    # Create and assign material
    material = create_crystal_material()
    crystal.data.materials.append(material)
    
    # Set up lighting
    setup_lighting()
    
    # Set up camera
    setup_camera()
    
    # Set up render settings
    setup_render_settings()
    
    # Render
    print("🎬 Rendering...")
    bpy.ops.render.render(write_still=True)
    print("✅ Render complete!")
    print("📁 Saved to: examples/example_crystal.png")

if __name__ == "__main__":
    main()