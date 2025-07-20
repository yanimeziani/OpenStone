#!/usr/bin/env python3
"""
Mesh Creator Module
Extensible system for creating different types of gemstone meshes
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Euler
import math
import random
from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod


class BaseMeshGenerator(ABC):
    """Abstract base class for mesh generators"""
    
    @abstractmethod
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate a mesh based on geometry data
        
        Args:
            geometry_data: Dictionary containing geometry parameters
            
        Returns:
            Blender object with generated mesh
        """
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters for this mesh type
        
        Returns:
            Dictionary of default parameter values
        """
        pass


class OrganicCrystalGenerator(BaseMeshGenerator):
    """Generator for organic crystal shapes"""
    
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate an organic crystal mesh"""
        faces = geometry_data.get('crystal_faces', 8)
        irregularity = geometry_data.get('irregularity', 0.3)
        surface_detail = geometry_data.get('surface_detail', 0.7)
        scale = geometry_data.get('scale', [1.0, 1.4, 1.0])
        
        # Create base icosphere
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, location=(0, 0, 0))
        crystal = bpy.context.active_object
        crystal.name = "OrganicCrystal"
        
        # Enter edit mode and modify
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Scale to desired proportions
        bpy.ops.transform.resize(value=scale)
        
        # Add subdivision for detail
        bpy.ops.mesh.subdivide(number_cuts=1)
        
        # Add some randomization for organic feel
        bpy.ops.transform.vertex_random(offset=irregularity)
        
        # Add surface detail through another subdivision and slight displacement
        if surface_detail > 0.5:
            bpy.ops.mesh.subdivide(number_cuts=1)
            bpy.ops.transform.vertex_random(offset=surface_detail * 0.1)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return crystal
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'crystal_faces': 8,
            'irregularity': 0.3,
            'surface_detail': 0.7,
            'scale': [1.0, 1.4, 1.0]
        }


class CutCrystalGenerator(BaseMeshGenerator):
    """Generator for precisely cut crystal shapes"""
    
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate a cut crystal mesh"""
        faces = geometry_data.get('crystal_faces', 12)
        scale = geometry_data.get('scale', [1.0, 1.2, 1.0])
        
        # Create base with more geometric precision
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
        crystal = bpy.context.active_object
        crystal.name = "CutCrystal"
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Create more geometric faces
        bpy.ops.mesh.subdivide(number_cuts=1)
        bpy.ops.mesh.inset_faces(thickness=0.1, depth=0.05)
        
        # Scale to desired proportions
        bpy.ops.transform.resize(value=scale)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return crystal
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'crystal_faces': 12,
            'scale': [1.0, 1.2, 1.0]
        }


class RawCrystalGenerator(BaseMeshGenerator):
    """Generator for raw, uncut crystal shapes"""
    
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate a raw crystal mesh"""
        faces = geometry_data.get('crystal_faces', 6)
        irregularity = geometry_data.get('irregularity', 0.5)
        scale = geometry_data.get('scale', [1.0, 1.5, 1.0])
        
        # Start with a cube for more angular raw look
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        crystal = bpy.context.active_object
        crystal.name = "RawCrystal"
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Add more geometry
        bpy.ops.mesh.subdivide(number_cuts=2)
        
        # Scale to desired proportions
        bpy.ops.transform.resize(value=scale)
        
        # Add significant randomization for raw appearance
        bpy.ops.transform.vertex_random(offset=irregularity)
        
        # Add some face extrusion for natural crystal growth
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_random(ratio=0.3)
        bpy.ops.mesh.extrude_faces_move(TRANSFORM_OT_shrink_fatten={"value": 0.2})
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return crystal
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'crystal_faces': 6,
            'irregularity': 0.5,
            'scale': [1.0, 1.5, 1.0]
        }


class GeodeGenerator(BaseMeshGenerator):
    """Generator for geode-like crystal formations"""
    
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate a geode mesh"""
        scale = geometry_data.get('scale', [1.2, 1.0, 1.2])
        cavity_depth = geometry_data.get('cavity_depth', 0.3)
        
        # Create hollow sphere-like shape
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
        crystal = bpy.context.active_object
        crystal.name = "Geode"
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Create the geode cavity
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Select top portion for cavity
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0, 0, 0.2), plane_no=(0, 0, 1), clear_inner=True)
        
        # Add crystal formations inside
        bpy.ops.mesh.inset_faces(thickness=0.1, depth=cavity_depth)
        
        bpy.ops.transform.resize(value=scale)
        bpy.ops.object.mode_set(mode='OBJECT')
        return crystal
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'scale': [1.2, 1.0, 1.2],
            'cavity_depth': 0.3
        }


class MeshCreator:
    """Main mesh creation system with extensible generators"""
    
    def __init__(self):
        """Initialize with built-in mesh generators"""
        self.generators = {
            'organic_crystal': OrganicCrystalGenerator(),
            'cut_crystal': CutCrystalGenerator(),
            'raw_crystal': RawCrystalGenerator(),
            'geode': GeodeGenerator()
        }
    
    def register_generator(self, name: str, generator: BaseMeshGenerator):
        """Register a new mesh generator
        
        Args:
            name: Unique name for the generator
            generator: Instance of BaseMeshGenerator
        """
        self.generators[name] = generator
        print(f"✅ Registered mesh generator: {name}")
    
    def list_generators(self) -> List[str]:
        """Get list of available generator names"""
        return list(self.generators.keys())
    
    def get_default_params(self, generator_name: str) -> Dict[str, Any]:
        """Get default parameters for a generator
        
        Args:
            generator_name: Name of the generator
            
        Returns:
            Dictionary of default parameters
        """
        if generator_name not in self.generators:
            raise ValueError(f"Unknown generator: {generator_name}")
        return self.generators[generator_name].get_default_params()
    
    def create_gem_geometry(self, gem_data: Dict[str, Any]) -> bpy.types.Object:
        """Create gemstone geometry from specification
        
        Args:
            gem_data: Complete gemstone specification
            
        Returns:
            Blender object with generated mesh
        """
        base_shape = gem_data.get('base_shape', 'organic_crystal')
        geometry_data = gem_data.get('geometry', {})
        
        if base_shape not in self.generators:
            print(f"⚠️ Unknown base shape '{base_shape}', using 'organic_crystal'")
            base_shape = 'organic_crystal'
        
        print(f"🔷 Creating {base_shape} geometry...")
        
        # Merge default params with provided params
        default_params = self.generators[base_shape].get_default_params()
        default_params.update(geometry_data)
        
        # Generate the mesh
        gem_obj = self.generators[base_shape].generate(default_params)
        
        # Apply common post-processing
        self._apply_common_modifiers(gem_obj, gem_data)
        
        return gem_obj
    
    def _apply_common_modifiers(self, obj: bpy.types.Object, gem_data: Dict[str, Any]):
        """Apply common modifiers to all gems
        
        Args:
            obj: Blender object to modify
            gem_data: Complete gemstone specification
        """
        # Add smooth shading
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        # Optionally add subdivision surface for smoother appearance
        geometry = gem_data.get('geometry', {})
        if geometry.get('smooth_subdivision', False):
            modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            modifier.levels = 1
            modifier.render_levels = 2


# Example of how to create a custom generator
class CustomDragonCrystalGenerator(BaseMeshGenerator):
    """Example custom generator for dragon-shaped crystals"""
    
    def generate(self, geometry_data: Dict[str, Any]) -> bpy.types.Object:
        """Generate a dragon-inspired crystal"""
        scale = geometry_data.get('scale', [2.0, 1.0, 1.2])
        spikes = geometry_data.get('spikes', True)
        
        # Start with elongated shape
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=1, depth=2, location=(0, 0, 0))
        crystal = bpy.context.active_object
        crystal.name = "DragonCrystal"
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Taper one end
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=6, type='GREATER')
        bpy.ops.transform.resize(value=(0.3, 0.3, 1))
        
        # Add spikes if requested
        if spikes:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_random(ratio=0.4)
            bpy.ops.mesh.extrude_faces_move(TRANSFORM_OT_shrink_fatten={"value": 0.3})
        
        bpy.ops.transform.resize(value=scale)
        bpy.ops.object.mode_set(mode='OBJECT')
        return crystal
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            'scale': [2.0, 1.0, 1.2],
            'spikes': True
        }