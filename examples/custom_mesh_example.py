#!/usr/bin/env python3
"""
Example: Creating a Custom Mesh Generator

This example shows how to create your own mesh generator
for unique gemstone shapes.
"""

import sys
from pathlib import Path

# Add openstone to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import bpy
import bmesh
from mathutils import Vector
from openstone.mesh_creator import BaseMeshGenerator, MeshCreator


class StarCrystalGenerator(BaseMeshGenerator):
    """Custom generator that creates star-shaped crystals"""
    
    def generate(self, geometry_data: dict) -> bpy.types.Object:
        """Generate a star-shaped crystal"""
        points = geometry_data.get('star_points', 5)
        inner_radius = geometry_data.get('inner_radius', 0.5)
        outer_radius = geometry_data.get('outer_radius', 1.0)
        height = geometry_data.get('height', 2.0)
        
        # Create mesh using bmesh
        bm = bmesh.new()
        
        # Create star base
        star_verts = []
        import math
        
        for i in range(points * 2):
            angle = (i * math.pi) / points
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            star_verts.append(bm.verts.new((x, y, 0)))
        
        # Create top point
        top_vert = bm.verts.new((0, 0, height))
        
        # Create faces
        for i in range(len(star_verts)):
            next_i = (i + 1) % len(star_verts)
            bm.faces.new([star_verts[i], star_verts[next_i], top_vert])
        
        # Create bottom face
        bm.faces.new(star_verts)
        
        # Create mesh object
        mesh = bpy.data.meshes.new("StarCrystal")
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new("StarCrystal", mesh)
        bpy.context.collection.objects.link(obj)
        
        return obj
    
    def get_default_params(self) -> dict:
        return {
            'star_points': 5,
            'inner_radius': 0.5,
            'outer_radius': 1.0,
            'height': 2.0
        }


def demo_custom_mesh():
    """Demonstrate the custom mesh generator"""
    print("🌟 Custom Star Crystal Generator Demo")
    print("=" * 40)
    
    # Create mesh creator and register our custom generator
    mesh_creator = MeshCreator()
    mesh_creator.register_generator('star_crystal', StarCrystalGenerator())
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create a star crystal
    gem_data = {
        'name': 'StarDemo',
        'base_shape': 'star_crystal',
        'geometry': {
            'star_points': 6,
            'inner_radius': 0.6,
            'outer_radius': 1.2,
            'height': 2.5
        }
    }
    
    star_crystal = mesh_creator.create_gem_geometry(gem_data)
    
    print("✅ Star crystal created!")
    print("💡 Try modifying the parameters in gem_data['geometry']")
    
    return star_crystal


if __name__ == "__main__":
    demo_custom_mesh()