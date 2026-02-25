# setup.py - Minimal working version
import sys

print(f"Python version: {sys.version}")
print("MIDI Analysis Module setup")

# Just define package info - no setup() call needed for basic use
package_info = {
    'name': 'midi-analysis-module',
    'version': '0.1.0',
    'dependencies': [
        'pretty-midi',
        'mido', 
        'python-rtmidi',
        'numpy',
        'scipy',
        'fastdtw',
        'matplotlib',
        'pandas',
        'openai'
    ]
}

print(f"\nPackage: {package_info['name']} v{package_info['version']}")
print("\nInstall dependencies with:")
print("  pip install -r requirements.txt")
