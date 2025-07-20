# Changelog

All notable changes to OpenStone will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-20

### Added
- **Modular Architecture**: Complete refactor into extensible modular system
  - `MeshCreator`: Extensible mesh generation system with built-in generators
  - `MaterialManager`: Advanced material system with multiple styles
  - `LightingManager`: Dynamic lighting and world environment system
  - `AIGemGenerator`: Enhanced AI generation with fallback support

### Mesh Generators
- `OrganicCrystalGenerator`: Natural, irregular crystal formations
- `CutCrystalGenerator`: Precisely cut gemstone shapes
- `RawCrystalGenerator`: Rough, uncut crystal clusters  
- `GeodeGenerator`: Hollow geode formations with internal crystals
- `CinematicCrystalGenerator`: Dramatic angular cuts for film-style renders

### Material Styles
- `RealisticGemStyle`: Photorealistic materials using Principled BSDF
- `StylizedGemStyle`: Artistic, emission-based materials
- `CrystallineStyle`: Complex internal crystal structures with facets
- `MetallicAccentStyle`: Gemstones with metallic engravings
- `CinematicGemStyle`: Complex internal lighting for dramatic effects

### Lighting Setups
- `StudioLightingSetup`: Professional 3-point lighting
- `NaturalLightingSetup`: Outdoor sun and sky lighting
- `DramaticLightingSetup`: High-contrast, moody lighting
- `CinematicLightingSetup`: Film-style multi-light setup with colored lights

### World Environments
- `HDRIWorldEnvironment`: HDRI-based environment lighting
- `GradientWorldEnvironment`: Smooth color gradients
- `SolidColorWorldEnvironment`: Simple solid color backgrounds
- `CinematicWorldEnvironment`: Atmospheric backgrounds with particles

### Features
- **OpenStone Main CLI**: New command-line interface (`openstone_main.py`)
- **Cinematic Render System**: Complete cinematic rendering pipeline
- **Extensible Architecture**: Easy registration of custom components
- **Example Scripts**: Comprehensive tutorials for custom components
- **Fallback AI Generation**: Works without OpenAI API using procedural generation
- **Enhanced Documentation**: Complete modular system documentation

### Examples
- `custom_mesh_example.py`: Tutorial for creating custom mesh generators
- `custom_material_example.py`: Tutorial for custom material styles
- `custom_lighting_example.py`: Tutorial for custom lighting setups
- `create_cinematic_render.py`: Complete cinematic rendering workflow

### Technical Improvements
- **Type Hints**: Full type annotation throughout codebase
- **Abstract Base Classes**: Proper inheritance structure for extensions
- **Error Handling**: Comprehensive error handling and fallbacks
- **Code Organization**: Clean separation of concerns
- **Documentation**: Extensive docstrings and examples

### Dependencies
- Added `requirements.txt` with proper dependency management
- OpenAI API support with graceful fallback
- Blender 4.5+ compatibility improvements

### Project Structure
- Reorganized into proper Python package structure
- Added comprehensive `.gitignore`
- Enhanced `README.md` with modular system documentation
- Added `CHANGELOG.md` for version tracking

## [0.1.0] - 2025-01-19

### Added
- Initial release with basic functionality
- `ai_gem_generator.py`: Basic AI-powered gemstone generation
- `blender_gem_creator.py`: Blender integration for geometry and rendering
- `run_gem_creator.py`: Simple demo script
- Basic OpenAI integration for text-to-gem generation
- Organic crystal geometry creation
- Advanced material system with realistic properties
- Professional lighting and rendering setup
- MIT License
- Basic documentation and contribution guidelines

### Features
- Text-to-gem generation using OpenAI
- Organic crystalline structure creation
- Realistic material properties
- Metallic engraving patterns
- Professional lighting setup
- High-quality Cycles rendering

### Dependencies
- Blender 3.0+ support
- OpenAI API integration
- Python 3.8+ compatibility