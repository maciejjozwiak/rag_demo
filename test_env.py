#!/usr/bin/env python3
"""
Test if .env file is being loaded correctly
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Environment Variable Test")
print("=" * 60)

print(f"\n.env file location: {env_path}")
print(f".env file exists: {env_path.exists()}")

print("\n" + "-" * 60)
print("API Keys Status:")
print("-" * 60)

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"✅ OPENAI_API_KEY found")
    print(f"   Starts with: {openai_key[:15]}...")
    print(f"   Length: {len(openai_key)} characters")
else:
    print("❌ OPENAI_API_KEY not found")

# Check Anthropic
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_key:
    print(f"✅ ANTHROPIC_API_KEY found")
    print(f"   Value: {anthropic_key}")
    if anthropic_key == "your_anthropic_api_key_here":
        print("   ⚠️  Still has placeholder value - replace with real key!")
else:
    print("❌ ANTHROPIC_API_KEY not found")

print("\n" + "=" * 60)

if openai_key and openai_key.startswith("sk-"):
    print("✅ Ready to use OpenAI!")
elif anthropic_key and anthropic_key.startswith("sk-ant-"):
    print("✅ Ready to use Anthropic!")
else:
    print("⚠️  No valid API key found. Check your .env file.")

print("=" * 60)
