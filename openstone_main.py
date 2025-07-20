#!/usr/bin/env python3
"""
OpenStone Main Script
Uses the modular architecture for creating gemstones
"""

import sys
import json
from pathlib import Path

# Add openstone package to path
sys.path.insert(0, str(Path(__file__).parent))

from openstone import AIGemGenerator, MeshCreator, MaterialManager, LightingManager


def clear_scene():
    """Clear the current Blender scene"""
    import bpy
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def setup_camera():
    """Set up camera for the render"""
    import bpy
    from mathutils import Vector
    
    bpy.ops.object.camera_add(location=(4, -6, 3))
    camera = bpy.context.active_object
    
    # Point camera at origin
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    # Create target
    bpy.ops.object.empty_add(location=(0, 0, 0))
    target = bpy.context.active_object
    target.name = "CameraTarget"
    constraint.target = target
    
    bpy.context.scene.camera = camera


def setup_render_settings(render_data: dict):
    """Set up render settings"""
    import bpy
    
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = render_data.get('samples', 256)
    
    resolution = render_data.get('resolution', [1920, 1080])
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    
    scene.render.image_settings.file_format = 'PNG'


def create_gemstone_from_json(json_path: str, output_dir: str = None):
    """Create a complete gemstone from JSON specification
    
    Args:
        json_path: Path to the JSON specification file
        output_dir: Optional output directory for renders
    """
    import bpy
    
    # Initialize managers
    ai_generator = AIGemGenerator()
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    # Load gem specification
    gem_data = ai_generator.load_gem_json(json_path)
    gem_name = gem_data.get('name', 'UnknownGem')
    
    print(f"🎉 Creating gemstone: {gem_name}")
    print("=" * 50)
    
    # Clear scene
    clear_scene()
    
    # Create geometry
    gem_obj = mesh_creator.create_gem_geometry(gem_data)
    
    # Create and assign material
    material = material_manager.create_material(gem_data)
    gem_obj.data.materials.append(material)
    
    # Setup lighting
    lighting_manager.setup_lighting(gem_data)
    
    # Setup world environment
    lighting_manager.setup_world(gem_data)
    
    # Setup camera
    setup_camera()
    
    # Setup render settings
    render_data = gem_data.get('render_settings', {})
    setup_render_settings(render_data)
    
    # Save scene
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    scene_file = output_path / f"{gem_name}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    
    print(f"💎 Gemstone creation complete!")
    print(f"📁 Scene saved: {scene_file}")
    
    return gem_obj


def render_gemstone(output_path: str = None):
    """Render the current scene
    
    Args:
        output_path: Optional path for the rendered image
    """
    import bpy
    
    if not output_path:
        output_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals" / "render.png"
    
    bpy.context.scene.render.filepath = str(output_path)
    
    print("🎬 Rendering...")
    bpy.ops.render.render(write_still=True)
    print(f"✅ Render complete: {output_path}")


def create_and_render_gemstone(prompt: str, output_dir: str = None, use_ai: bool = True):
    """Complete workflow: generate, create, and render a gemstone
    
    Args:
        prompt: Text description of the gemstone
        output_dir: Optional output directory
        use_ai: Whether to use AI generation
    """
    # Initialize AI generator
    ai_generator = AIGemGenerator()
    
    # Generate gemstone specification
    gem_data = ai_generator.generate_gem_json(prompt, use_ai=use_ai)
    
    # Save JSON
    json_path = ai_generator.save_gem_json(gem_data)
    
    # Create gemstone
    gem_obj = create_gemstone_from_json(json_path, output_dir)
    
    # Render
    gem_name = gem_data.get('name', 'UnknownGem')
    if output_dir:
        render_path = Path(output_dir) / f"{gem_name}.png"
    else:
        render_path = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals" / f"{gem_name}.png"
    
    render_gemstone(str(render_path))
    
    return gem_obj, str(render_path)


def list_available_options():
    """List all available generators, materials, lighting, and world options"""
    mesh_creator = MeshCreator()
    material_manager = MaterialManager()
    lighting_manager = LightingManager()
    
    print("🔷 Available Mesh Generators:")
    for name in mesh_creator.list_generators():
        print(f"  - {name}")
    
    print("\n🎨 Available Material Styles:")
    for name in material_manager.list_styles():
        print(f"  - {name}")
    
    print("\n💡 Available Lighting Setups:")
    for name in lighting_manager.list_lighting_setups():
        print(f"  - {name}")
    
    print("\n🌍 Available World Environments:")
    for name in lighting_manager.list_world_environments():
        print(f"  - {name}")


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("OpenStone: Crystal Gemstone Generation & Rendering Pipeline")
        print("\nUsage:")
        print("  python openstone_main.py <command> [args...]")
        print("\nCommands:")
        print("  generate <prompt>           - Generate and render a gemstone from text")
        print("  create <json_file>          - Create gemstone from JSON file")
        print("  list                        - List available options")
        print("\nExamples:")
        print("  python openstone_main.py generate 'A mystical blue crystal'")
        print("  python openstone_main.py create gem_spec.json")
        print("  python openstone_main.py list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'generate':
            if len(sys.argv) < 3:
                print("Error: Please provide a prompt")
                sys.exit(1)
            
            prompt = " ".join(sys.argv[2:])
            print(f"Generating gemstone: {prompt}")
            create_and_render_gemstone(prompt)
            
        elif command == 'create':
            if len(sys.argv) < 3:
                print("Error: Please provide a JSON file path")
                sys.exit(1)
            
            json_file = sys.argv[2]
            if not Path(json_file).exists():
                print(f"Error: JSON file not found: {json_file}")
                sys.exit(1)
            
            print(f"Creating gemstone from: {json_file}")
            create_gemstone_from_json(json_file)
            
        elif command == 'list':
            list_available_options()
            
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()