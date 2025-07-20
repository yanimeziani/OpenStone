#!/usr/bin/env python3
"""
AI Gemstone Generator
Generates unique gemstone specifications using OpenAI API
"""

import json
import os
import sys
import random
from pathlib import Path
from typing import Dict, Any, Optional

# Check if OpenAI is available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIGemGenerator:
    """AI-powered gemstone specification generator"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.output_dir = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "generated_gems"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI if available
        self.openai_available = OPENAI_AVAILABLE
        self.openai_api_key = None
        if self.openai_available:
            if openai_api_key:
                self.openai_api_key = openai_api_key
            else:
                self.openai_api_key = os.environ.get("OPENAI_API_KEY")
            
            if not self.openai_api_key:
                print("Warning: OpenAI API key not found. AI generation will not be available.")
                self.openai_available = False
    
    def generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate gemstone specification using OpenAI"""
        if not self.openai_available:
            raise RuntimeError("OpenAI not available")
        
        print(f"🤖 Generating gem concept with AI: '{prompt}'")
        
        system_message = """You are an expert 3D artist and gemologist specializing in creating stunning gemstone designs for Blender rendering with sophisticated mesh gradients and geological features.

Generate a complete gemstone specification in JSON format based on the user's description. The JSON MUST include ALL of these fields:

{
  "name": "UniqueGemName",
  "description": "Detailed description",
  "gem_type": "crystal/ruby/emerald/sapphire/diamond/amethyst/quartz/obsidian/granite/marble",
  "base_shape": "sphere/icosphere/cube/faceted/organic/crystal/pebble/loop",
  "geometry": {
    "subdivisions": 5-10,
    "scale": [1.0, 1.0, 1.0],
    "rotation": [0.0, 0.0, 0.0],
    "organic_modifiers": ["subdivision_surface", "displace", "bevel", "smooth"],
    "displacement": {"strength": 0.1-0.5, "scale": 2.0-5.0, "detail": 0.1-0.3},
    "subdivision_surface": {"levels": 2-4, "render_levels": 4-6},
    "bevel": {"width": 0.02-0.08, "segments": 3-8},
    "smooth": {"factor": 0.5-1.0, "iterations": 2-5}
  },
  "material": {
    "base_color": [r, g, b, 1.0],
    "secondary_color": [r, g, b, 1.0],
    "ior": 1.4-1.8,
    "roughness": 0.01-0.05,
    "transmission": 0.5-0.95,
    "subsurface": 0.3-0.8,
    "subsurface_radius": [r, g, b],
    "emission_strength": 0.0-15.0,
    "emission_color": [r, g, b, 1.0],
    "surface_imperfections": {
      "scratches": 0.02-0.1,
      "bumps": 0.05-0.2,
      "noise_scale": 15.0-50.0,
      "roughness_variation": 0.01-0.05,
      "fracture_strength": 0.1-0.4,
      "weathering_intensity": 0.3-0.8,
      "erosion_depth": 0.05-0.15,
      "strata_visibility": 0.2-0.6
    },
    "internal_structure": {
      "inclusions": 0.1-0.4,
      "fractures": 0.05-0.15,
      "crystal_growth": 0.3-0.7,
      "mineral_veins": 0.2-0.5,
      "geological_layers": 0.3-0.8,
      "crystal_clusters": 0.1-0.4
    },
    "mesh_gradients": {
      "primary_scale": 15.0-25.0,
      "secondary_scale": 25.0-35.0,
      "voronoi_scale": 20.0-30.0,
      "wave_scale": 18.0-28.0,
      "color_variation": 0.6-0.9,
      "gradient_intensity": 0.7-0.95
    }
  },
  "engraving": {
    "enabled": true/false,
    "metal_type": "gold/silver/platinum/bronze/copper",
    "pattern": "dragon/phoenix/celtic/mandala/runes/geometric/mystical/infinity/spiral/star/floral",
    "depth": 0.02-0.04,
    "width": 0.05-0.12,
    "position": [x, y, z],
    "rotation": [x, y, z],
    "contrast": 0.7-0.95,
    "bump_strength": 0.1-0.3
  },
  "lighting": {
    "world_strength": 0.8-1.5,
    "background_color": [r, g, b, 1.0],
    "key_light": {"strength": 2.0-4.0, "color": [r, g, b, 1.0], "position": [x, y, z]},
    "fill_light": {"strength": 0.5-1.5, "color": [r, g, b, 1.0], "position": [x, y, z]},
    "rim_light": {"strength": 1.0-2.5, "color": [r, g, b, 1.0], "position": [x, y, z]},
    "back_light": {"strength": 0.8-2.0, "color": [r, g, b, 1.0], "position": [x, y, z]}
  },
  "camera": {
    "position": [x, y, z],
    "rotation": [x, y, z],
    "lens": 50.0-85.0,
    "f_stop": 2.8-5.6,
    "focus_distance": 3.0-8.0
  },
  "render_settings": {
    "resolution_x": 1920,
    "resolution_y": 1080,
    "samples": 1024,
    "max_bounces": 16,
    "use_denoising": true,
    "denoiser": "OPENIMAGEDENOISE",
    "use_gpu_acceleration": true,
    "file_format": "PNG",
    "color_depth": "16",
    "exposure": 0.4-0.8,
    "gamma": 1.0-1.2,
    "saturation": 1.2-1.6,
    "contrast": 1.0-1.3
  }
}

Create beautiful, renderable gemstones with sophisticated mesh gradients, geological surface features, and realistic material properties that would look stunning in Blender with Cycles engine. Focus on creating unique, artistic gemstones with complex surface intricacies and organic color variations."""

        user_message = f"""Create a gemstone specification for: {prompt}

IMPORTANT: Generate a complete JSON object with ALL required fields. The response must be valid JSON with no additional text before or after the JSON object.

Make the gemstone unique and beautiful based on the description."""

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.9,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            if content:
                gem_data = json.loads(content)
            else:
                raise RuntimeError("Empty response from OpenAI")
            print("✅ AI generated gemstone concept successfully")
            return gem_data
            
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            raise
    
    def generate_gem_json(self, prompt: str, use_ai: bool = True) -> Dict[str, Any]:
        """Generate gemstone JSON specification"""
        if not use_ai or not self.openai_available:
            raise RuntimeError("AI generation is required and OpenAI is not available")
        
        try:
            gem_data = self.generate_with_openai(prompt)
            
            # Ensure all required fields are present
            required_fields = ['name', 'description', 'gem_type', 'base_shape', 'geometry', 'material', 'engraving', 'lighting', 'render_settings']
            missing_fields = [field for field in required_fields if field not in gem_data]
            
            if missing_fields:
                print(f"⚠️ AI response missing fields: {missing_fields}")
                # Retry with more specific prompt
                retry_prompt = f"Create a complete gemstone specification for: {prompt}. Must include: {', '.join(missing_fields)}"
                gem_data = self.generate_with_openai(retry_prompt)
            
            return gem_data
            
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            raise RuntimeError(f"Failed to generate gemstone: {e}")
    
    def save_gem_json(self, gem_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save gemstone JSON to file"""
        if filename is None:
            filename = f"{gem_data['name']}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(gem_data, f, indent=2)
        
        print(f"✅ JSON saved to: {filepath}")
        return str(filepath)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python ai_gem_generator.py <prompt>")
        print("Examples:")
        print("  python ai_gem_generator.py 'A mystical blue crystal with golden infinity symbol'")
        print("  python ai_gem_generator.py 'Deep red ruby with silver geometric patterns'")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    generator = AIGemGenerator()
    
    try:
        # Generate gemstone specification
        gem_data = generator.generate_gem_json(prompt)
        
        # Save to file
        json_file = generator.save_gem_json(gem_data)
        
        print(f"🎉 Generated gemstone: {gem_data.get('name', 'Unknown')}")
        print(f"📁 JSON file: {json_file}")
        print(f"💎 Gem type: {gem_data.get('gem_type', 'unknown')}")
        print(f"🔷 Base shape: {gem_data.get('base_shape', 'unknown')}")
        engraving = gem_data.get('engraving', {})
        print(f"🏆 Engraving: {engraving.get('pattern', 'none')} ({engraving.get('metal_type', 'none')})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 