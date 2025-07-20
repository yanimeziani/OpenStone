#!/usr/bin/env python3
"""
Simple script to demonstrate the gem creation workflow
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Demonstrate the gem creation workflow"""
    print("🎉 Crystal Gemstone Creator")
    print("=" * 40)
    
    # Step 1: Generate a gemstone JSON
    print("\n1️⃣ Generating gemstone specification...")
    prompt = "A mystical blue crystal with golden infinity symbol"
    
    try:
        result = subprocess.run([
            sys.executable, "ai_gem_generator.py", prompt
        ], capture_output=True, text=True, check=True)
        print("✅ Gemstone JSON generated successfully")
        
        # Find the generated JSON file
        generated_dir = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "generated_gems"
        json_files = list(generated_dir.glob("*.json"))
        
        if json_files:
            json_file = json_files[-1]  # Get the most recent file
            print(f"📁 JSON file: {json_file}")
            
            # Step 2: Create Blender scene
            print("\n2️⃣ Creating Blender scene...")
            blender_path = "/Applications/Blender.app/Contents/MacOS/blender"
            
            result = subprocess.run([
                blender_path, "--background", "--python", "blender_gem_creator.py", 
                "--", str(json_file)
            ], capture_output=True, text=True, check=True)
            
            print("✅ Blender scene created successfully")
            
            # Check for the .blend file
            rendered_dir = Path.home() / "Desktop" / "PRISMATICS" / "crystal" / "rendered_crystals"
            blend_files = list(rendered_dir.glob("*.blend"))
            
            if blend_files:
                blend_file = blend_files[-1]
                print(f"📁 Blend file: {blend_file}")
                print(f"🎉 You can now open {blend_file} in Blender to view your gemstone!")
            else:
                print("❌ No .blend file found")
                
        else:
            print("❌ No JSON files found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 