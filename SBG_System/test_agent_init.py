import sys
from src.agents.acoustic_agent import AcousticFaultAgent

print("Testing acoustic agent init...")
try:
    agent = AcousticFaultAgent()
    print("✓ Acoustic agent created successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
