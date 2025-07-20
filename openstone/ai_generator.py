#!/usr/bin/env python3
"""
AI Gemstone Generator Module
Generates unique gemstone specifications using OpenAI API or fallback methods
"""

import json
import os
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
    
    def __init__(self, openai_api_key: Optional[str] = None, output_dir: Optional[Path] = None):
        """Initialize the AI gem generator
        
        Args:
            openai_api_key: Optional OpenAI API key
            output_dir: Optional output directory for generated JSON files
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
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
  "name": "GemName",
  "description": "Detailed description",
  "gem_type": "crystal|ruby|emerald|sapphire|diamond|amethyst",
  "base_shape": "organic_crystal|cut_crystal|raw_crystal",
  "geometry": {
    "crystal_faces": 6-16,
    "irregularity": 0.1-0.5,
    "surface_detail": 0.3-1.0,
    "scale": [x, y, z] (0.5-2.0 range)
  },
  "material": {
    "base_color": [r, g, b] (0.0-1.0),
    "transparency": 0.0-0.5,
    "roughness": 0.01-0.2,
    "ior": 1.3-2.4,
    "subsurface_scattering": 0.0-0.5,
    "dispersion": 0.01-0.1
  },
  "engraving": {
    "pattern": "infinity|mystical|geometric|organic|spiral|star|floral|dragon|phoenix|celtic|mandala|runes",
    "metal_type": "gold|silver|platinum|copper|bronze",
    "depth": 0.01-0.1,
    "width": 0.005-0.05,
    "metallic": 0.8-1.0,
    "roughness": 0.1-0.5
  },
  "lighting": {
    "hdri_strength": 0.5-3.0,
    "key_light_energy": 5-20,
    "fill_light_energy": 2-8,
    "rim_light_energy": 3-15
  },
  "render_settings": {
    "samples": 128-512,
    "resolution": [1920, 1080],
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
    
    def generate_fallback_gem(self, prompt: str) -> Dict[str, Any]:
        """Generate a fallback gemstone specification without AI"""
        print(f"🔮 Creating fallback gem for: '{prompt}'")
        
        # Parse prompt for key characteristics
        prompt_lower = prompt.lower()
        
        # Determine gem type and color based on prompt
        if 'amethyst' in prompt_lower or 'purple' in prompt_lower:
            gem_type = "amethyst"
            base_color = [0.6, 0.3, 0.9]
        elif 'ruby' in prompt_lower or 'red' in prompt_lower:
            gem_type = "ruby"
            base_color = [0.9, 0.1, 0.2]
        elif 'blue' in prompt_lower or 'sapphire' in prompt_lower:
            gem_type = "sapphire"
            base_color = [0.1, 0.3, 0.9]
        elif 'emerald' in prompt_lower or 'green' in prompt_lower:
            gem_type = "emerald"
            base_color = [0.1, 0.8, 0.3]
        else:
            gem_type = "crystal"
            base_color = [0.8, 0.9, 1.0]
        
        # Determine engraving pattern
        if 'mystical' in prompt_lower or 'magic' in prompt_lower:
            pattern = "mystical"
        elif 'infinity' in prompt_lower:
            pattern = "infinity"
        elif 'dragon' in prompt_lower:
            pattern = "dragon"
        elif 'geometric' in prompt_lower:
            pattern = "geometric"
        else:
            pattern = "mystical"
        
        # Generate fallback gem data
        return {
            "name": f"Generated_{gem_type.title()}",
            "description": f"A beautiful {gem_type} crystal with intricate {pattern} engravings",
            "gem_type": gem_type,
            "base_shape": "organic_crystal",
            "geometry": {
                "crystal_faces": random.randint(6, 12),
                "irregularity": round(random.uniform(0.15, 0.4), 2),
                "surface_detail": round(random.uniform(0.6, 0.9), 2),
                "scale": [
                    round(random.uniform(0.8, 1.2), 2),
                    round(random.uniform(1.0, 1.5), 2),
                    round(random.uniform(0.8, 1.2), 2)
                ]
            },
            "material": {
                "base_color": base_color,
                "transparency": round(random.uniform(0.1, 0.3), 2),
                "roughness": round(random.uniform(0.02, 0.08), 2),
                "ior": round(random.uniform(1.5, 1.8), 2),
                "subsurface_scattering": round(random.uniform(0.1, 0.3), 2),
                "dispersion": round(random.uniform(0.02, 0.05), 3)
            },
            "engraving": {
                "pattern": pattern,
                "metal_type": "silver",
                "depth": round(random.uniform(0.02, 0.05), 3),
                "width": round(random.uniform(0.01, 0.03), 3),
                "metallic": round(random.uniform(0.9, 1.0), 2),
                "roughness": round(random.uniform(0.1, 0.3), 2)
            },
            "lighting": {
                "hdri_strength": round(random.uniform(1.2, 2.0), 1),
                "key_light_energy": random.randint(8, 15),
                "fill_light_energy": random.randint(3, 6),
                "rim_light_energy": random.randint(5, 10)
            },
            "render_settings": {
                "samples": 256,
                "resolution": [1920, 1080],
                "exposure": round(random.uniform(0.4, 0.8), 1),
                "gamma": round(random.uniform(1.0, 1.2), 1),
                "saturation": round(random.uniform(1.2, 1.6), 1),
                "contrast": round(random.uniform(1.0, 1.3), 1)
            }
        }
    
    def generate_gem_json(self, prompt: str, use_ai: bool = True) -> Dict[str, Any]:
        """Generate gemstone JSON specification
        
        Args:
            prompt: Text description of the desired gemstone
            use_ai: Whether to use AI generation (falls back if unavailable)
            
        Returns:
            Dictionary containing complete gemstone specification
        """
        if not use_ai or not self.openai_available:
            if self.openai_available and use_ai:
                print("⚠️ OpenAI requested but not available, using fallback generation")
            return self.generate_fallback_gem(prompt)
        
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
            print("🔄 Falling back to local generation")
            return self.generate_fallback_gem(prompt)
    
    def save_gem_json(self, gem_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save gemstone JSON to file
        
        Args:
            gem_data: Gemstone specification dictionary
            filename: Optional custom filename
            
        Returns:
            Path to the saved JSON file
        """
        if filename is None:
            filename = f"{gem_data['name']}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(gem_data, f, indent=2)
        
        print(f"✅ JSON saved to: {filepath}")
        return str(filepath)

    def load_gem_json(self, filepath: str) -> Dict[str, Any]:
        """Load gemstone JSON from file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dictionary containing gemstone specification
        """
        with open(filepath, 'r') as f:
            gem_data = json.load(f)
        return gem_data