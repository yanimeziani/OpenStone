# Crystal Gemstone Generation & Rendering Pipeline

A comprehensive system for generating organic gemstones with metallic engravings and rendering them with professional quality materials and lighting.

## Overview

This pipeline consists of three main components:

1. **Gem JSON Generator** (`gem_json_generator.py`) - Creates detailed gemstone definitions from text prompts
2. **Organic Geometry Creator** (`organic_geometry_creator.py`) - Creates organic crystalline structures from basic shapes
3. **Material & Render Pipeline** (`material_render_pipeline.py`) - Creates advanced materials with surface imperfections and renders

## Features

- 🎯 **Text-to-Gem Generation**: Create gemstones from natural language descriptions
- 🔷 **Organic Geometry**: Transform basic shapes (sphere, cube, torus, etc.) into organic crystalline structures
- ✨ **Advanced Materials**: Realistic gemstone materials with surface imperfections, internal structure, and emission effects
- 🏆 **Metallic Engravings**: Gold, silver, platinum, and copper engravings with various patterns
- 💡 **Professional Lighting**: Cinematic lighting setup with key, fill, and rim lights
- 🎨 **High-Quality Rendering**: 4K renders with Cycles engine and GPU acceleration

## Quick Start

### Option 1: Blender Script (Recommended)

1. Open Blender
2. Go to **Scripting** workspace
3. Open `blender_gem_pipeline.py`
4. Run the script
5. The script will generate a mystical blue crystal with golden engravings

### Option 2: Command Line

```bash
# Generate a gem from prompt
python gem_master_pipeline.py "A mystical blue crystal with golden engravings"

# Or use existing JSON file
python gem_master_pipeline.py --json my_gem.json
```

### Option 3: Individual Components

```bash
# Generate JSON definition
python gem_json_generator.py "A fiery ruby with silver engravings"

# Create geometry (requires Blender)
blender -b -P organic_geometry_creator.py -- my_gem.json

# Render with materials (requires Blender)
blender -b -P material_render_pipeline.py -- my_gem.json
```

## File Structure

```
crystal/
├── gem_json_generator.py          # JSON definition generator
├── organic_geometry_creator.py    # Blender geometry creator
├── material_render_pipeline.py    # Blender material & render pipeline
├── blender_gem_pipeline.py        # Complete Blender pipeline
├── gem_master_pipeline.py         # Master orchestration script
├── rendered_crystals/             # Output directory
│   ├── MysticalBlueGem.json
│   ├── MysticalBlueGem.png
│   └── ...
└── README.md
```

## Gem Types Supported

- **Ruby**: Deep red with fiery glow
- **Emerald**: Rich green with natural inclusions
- **Sapphire**: Deep blue with royal appearance
- **Diamond**: Crystal clear with high refraction
- **Amethyst**: Purple with mystical properties
- **Topaz**: Golden yellow with warm glow
- **Opal**: Iridescent with rainbow effects
- **Mystical Crystal**: Custom magical properties

## Base Shapes

- **Sphere**: Classic round gemstone
- **Cube**: Geometric faceted stone
- **Torus**: Ring-shaped crystal
- **Cylinder**: Pillar-like structure
- **Icosphere**: Highly detailed spherical

## Metal Types for Engravings

- **Gold**: Classic golden appearance
- **Silver**: Bright metallic silver
- **Platinum**: Cool white metallic
- **Copper**: Warm reddish metallic

## Material Features

### Surface Imperfections
- Scratches and surface wear
- Bump mapping for texture
- Noise-based surface variation
- Roughness variation

### Internal Structure
- Crystal growth patterns
- Inclusions and fractures
- Subsurface scattering
- Internal glow effects

### Advanced Properties
- Index of Refraction (IOR)
- Transmission and transparency
- Subsurface scattering
- Emission for internal glow

## Lighting Setup

### Professional Three-Point Lighting
- **Key Light**: Main illumination
- **Fill Light**: Soft fill to reduce shadows
- **Rim Light**: Backlight for separation

### World Environment
- Customizable background colors
- Adjustable world strength
- Professional gradient backgrounds

## Render Settings

### Quality Presets
- **Production**: 4K resolution, 2048 samples
- **Preview**: 1080p resolution, 512 samples
- **Fast**: 720p resolution, 256 samples

### Engine Features
- Cycles render engine
- GPU acceleration support
- Denoising (OpenImageDenoise)
- High dynamic range (16-bit)

## Example Prompts

```bash
# Mystical crystal
"A mystical blue crystal with golden engravings"

# Precious gem
"A fiery ruby with silver geometric patterns"

# Organic gem
"An organic emerald with copper floral engravings"

# Geometric crystal
"A faceted diamond with platinum symbolic markings"

# Fantasy gem
"A glowing amethyst with golden mystical symbols"
```

## Output

The pipeline generates:

1. **JSON Definition**: Complete gemstone specification
2. **Blender File**: `.blend` file with geometry and materials
3. **High-Quality Render**: PNG image with professional lighting
4. **GLB Export**: 3D model for web/AR applications

## Requirements

- **Blender 3.0+** (4.5+ recommended)
- **Python 3.8+**
- **GPU with CUDA/OpenCL** (optional, for faster rendering)

## Installation

1. Clone or download the scripts
2. Place them in your Blender scripts directory or project folder
3. Ensure Blender is in your PATH (for command-line usage)

## Customization

### Adding New Gem Types

Edit the `material_presets` in `gem_json_generator.py`:

```python
"new_gem": {
    "base_color": [0.5, 0.3, 0.8, 1.0],
    "secondary_color": [0.6, 0.4, 0.9, 1.0],
    "ior": 1.6,
    "roughness": 0.02,
    "transmission": 0.7,
    "subsurface": 0.5,
    "emission_strength": 8.0
}
```

### Custom Engraving Patterns

Add new patterns in `organic_geometry_creator.py`:

```python
def _create_custom_pattern(self, obj, engraving_data):
    # Your custom pattern logic here
    pass
```

### Advanced Material Nodes

Modify `material_render_pipeline.py` to add custom shader nodes:

```python
# Add custom noise texture
custom_noise = nodes.new(type='ShaderNodeTexNoise')
custom_noise.inputs['Scale'].default_value = 10.0
```

## Troubleshooting

### Common Issues

1. **Blender not found**: Ensure Blender is in your system PATH
2. **GPU rendering fails**: Switch to CPU rendering in render settings
3. **Memory issues**: Reduce sample count or resolution
4. **Import errors**: Ensure all scripts are in the same directory

### Performance Tips

- Use GPU rendering for faster results
- Reduce sample count for preview renders
- Lower resolution for quick tests
- Close other applications during rendering

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

- Blender Foundation for the amazing 3D software
- Cycles render engine for photorealistic rendering
- The Blender Python API for automation capabilities # OpenStones
# OpenStones
