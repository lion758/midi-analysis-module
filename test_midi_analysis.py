import sys
import os
from pathlib import Path

# Add the module to Python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzer import MIDIAnalyzer, quick_analyze, compare_performance
from src.midi_parser import MIDIParser

def test_with_sample_midi():
    """Test the module with sample MIDI files"""
    
    # Initialize the analyzer
    analyzer = MIDIAnalyzer()
    parser = MIDIParser()
    
    # Use raw strings or forward slashes for Windows paths
    # Option 1: Raw string (prefix with r)
    solo_midi_path = r"C:\Users\majah\OneDrive\Desktop\MIDI_A_Module\midi-analysis-module\sample_files\performance.mid"
    
    # Option 2: Forward slashes (also works on Windows)
    # solo_midi_path = "C:/Users/majah/OneDrive/Desktop/MIDI_A_Module/midi-analysis-module/sample_files/performance.mid"
    
    # Option 3: Double backslashes
    # solo_midi_path = "C:\\Users\\majah\\OneDrive\\Desktop\\MIDI_A_Module\\midi-analysis-module\\sample_files\\performance.mid"
    
    print("=" * 60)
    print("TEST 1: Solo Performance Analysis")
    print("=" * 60)
    
    if os.path.exists(solo_midi_path):
        try:
            print(f"Found file: {solo_midi_path}")
            print(f"File size: {os.path.getsize(solo_midi_path)} bytes")
            
            # First, test just the parser
            print("\nTesting MIDI parser...")
            parsed_data = parser.parse_midi(solo_midi_path)
            
            if parsed_data:
                print(f"✓ Successfully parsed MIDI file")
                print(f"  Total notes: {len(parsed_data.get('notes', []))}")
                print(f"  Duration: {parsed_data.get('total_duration', 0):.2f} seconds")
                
                # Show first few notes
                notes = parsed_data.get('notes', [])
                if notes:
                    print(f"  First 3 notes:")
                    for i, note in enumerate(notes[:3]):
                        print(f"    Note {i+1}: pitch={note['pitch']} ({note.get('pitch_name', 'N/A')}), "
                              f"start={note['start']:.2f}s, duration={note['duration']:.3f}s")
                
                # Now try full analysis
                print("\nRunning full analysis...")
                solo_result = analyzer.analyze_solo_performance(solo_midi_path)
                analyzer.print_analysis_summary()
                
                # Save results
                with open("solo_analysis_results.json", "w") as f:
                    import json
                    json.dump(solo_result, f, indent=2, default=str)
                print("✓ Solo analysis saved to solo_analysis_results.json")
                
                # Check if we can open the file
                try:
                    with open("solo_analysis_results.json", "r") as f:
                        data = json.load(f)
                    print("✓ Results file is valid JSON")
                except json.JSONDecodeError as e:
                    print(f"✗ Error in JSON output: {e}")
                
            else:
                print("✗ Parser returned empty data")
                
        except Exception as e:
            print(f"✗ Error in analysis: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ File not found: {solo_midi_path}")
        print("\nAvailable files in sample_files directory:")
        sample_dir = r"C:\Users\majah\OneDrive\Desktop\MIDI_A_Module\midi-analysis-module\sample_files"
        if os.path.exists(sample_dir):
            for file in os.listdir(sample_dir):
                print(f"  - {file}")
        else:
            print(f"  Directory doesn't exist: {sample_dir}")
    
    # Example 2: Test reference vs performance analysis
    print("\n" + "=" * 60)
    print("TEST 2: Reference vs Performance Analysis")
    print("=" * 60)
    
    # Using forward slashes to avoid escape issues
    reference_path = "C:/Users/majah/OneDrive/Desktop/MIDI_A_Module/midi-analysis-module/sample_files/reference.mid"
    performance_path = "C:/Users/majah/OneDrive/Desktop/MIDI_A_Module/midi-analysis-module/sample_files/performance.mid"
    
    # Or use raw strings
    # reference_path = r"C:\Users\majah\OneDrive\Desktop\MIDI_A_Module\midi-analysis-module\sample_files\reference.mid"
    # performance_path = r"C:\Users\majah\OneDrive\Desktop\MIDI_A_Module\midi-analysis-module\sample_files\performance.mid"
    
    print(f"Reference path: {reference_path}")
    print(f"Performance path: {performance_path}")
    
    if os.path.exists(reference_path) and os.path.exists(performance_path):
        try:
            print("✓ Both files exist")
            print("Starting comparison analysis...")
            
            # Create output directory
            output_dir = "analysis_results"
            os.makedirs(output_dir, exist_ok=True)
            
            # Use the convenience function
            result = compare_performance(
                reference_path=reference_path,
                performance_path=performance_path,
                output_dir=output_dir
            )
            
            print("\n✓ Analysis complete!")
            print(f"Results saved to: {output_dir}/")
            
            # Print key metrics
            if 'performance_analysis' in result:
                metrics = result['performance_analysis'].get('metrics', {})
                if 'performance_score' in metrics:
                    score = metrics['performance_score'].get('overall_score', 0)
                    grade = metrics['performance_score'].get('grade', 'N/A')
                    print(f"\nPerformance Score: {score:.1f}%")
                    print(f"Grade: {grade}")
                    
        except Exception as e:
            print(f"✗ Error in reference analysis: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ One or both files not found")
        if not os.path.exists(reference_path):
            print(f"  Missing: {reference_path}")
        if not os.path.exists(performance_path):
            print(f"  Missing: {performance_path}")

def list_midi_files():
    """List all MIDI files in the project"""
    print("=" * 60)
    print("SEARCHING FOR MIDI FILES")
    print("=" * 60)
    
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Search recursively
    midi_extensions = ['.mid', '.midi', '.MID', '.MIDI']
    midi_files = []
    
    for ext in midi_extensions:
        midi_files.extend(current_dir.rglob(f"*{ext}"))
    
    if midi_files:
        print(f"Found {len(midi_files)} MIDI files:")
        for i, midi_file in enumerate(midi_files, 1):
            size = midi_file.stat().st_size
            print(f"  {i}. {midi_file.relative_to(current_dir)} ({size} bytes)")
        
        # Test with the first file
        test_file = str(midi_files[0])
        print(f"\nTesting with: {test_file}")
        
        parser = MIDIParser()
        parsed = parser.parse_midi(test_file)
        
        if parsed:
            print(f"✓ Successfully parsed")
            print(f"  Notes: {len(parsed.get('notes', []))}")
            print(f"  Duration: {parsed.get('total_duration', 0):.2f}s")
            
            # Ask if user wants to run full analysis
            response = input("\nRun full analysis on this file? (y/n): ")
            if response.lower() == 'y':
                analyzer = MIDIAnalyzer()
                result = analyzer.analyze_solo_performance(test_file)
                analyzer.print_analysis_summary()
        else:
            print("✗ Failed to parse file")
    else:
        print("No MIDI files found in current directory or subdirectories.")
        print("\nPlease add MIDI files to your project.")

def create_simple_test_midi():
    """Create a simple test MIDI file if none exist"""
    try:
        import pretty_midi
        
        print("=" * 60)
        print("CREATING TEST MIDI FILE")
        print("=" * 60)
        
        # Create a simple C major scale
        midi = pretty_midi.PrettyMIDI()
        piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
        piano = pretty_midi.Instrument(program=piano_program)
        
        # Add a C major scale
        notes = []
        start_time = 0.5
        for i, pitch in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):  # C major scale
            note = pretty_midi.Note(
                velocity=80,
                pitch=pitch,
                start=start_time + i * 0.5,
                end=start_time + i * 0.5 + 0.4
            )
            piano.notes.append(note)
            notes.append({
                'pitch': pitch,
                'start': note.start,
                'end': note.end,
                'duration': 0.4
            })
        
        midi.instruments.append(piano)
        
        # Save the file
        test_file = "test_scale.mid"
        midi.write(test_file)
        
        print(f"✓ Created test MIDI file: {test_file}")
        print(f"  Contains {len(notes)} notes (C major scale)")
        print(f"  Duration: {(notes[-1]['end'] - notes[0]['start']):.2f} seconds")
        
        return test_file
        
    except ImportError:
        print("✗ pretty_midi not installed. Install it with:")
        print("  pip install pretty_midi")
        return None

if __name__ == "__main__":
    print("MIDI Analysis Module Test Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"Working directory: {current_dir}")
    
    # Check if src directory exists
    if not (current_dir / "src").exists():
        print("✗ 'src' directory not found!")
        print("Make sure you're running this from the directory containing 'src/'")
        print("Current directory contents:")
        for item in current_dir.iterdir():
            print(f"  - {item.name}")
    else:
        print("✓ Found 'src' directory")
    
    # Check for sample_files directory
    sample_dir = current_dir / "sample_files"
    if sample_dir.exists():
        print(f"✓ Found 'sample_files' directory")
        midi_files = list(sample_dir.glob("*.mid")) + list(sample_dir.glob("*.midi"))
        if midi_files:
            print(f"  Contains {len(midi_files)} MIDI files")
        else:
            print("  No MIDI files found in sample_files")
    else:
        print("✗ 'sample_files' directory not found")
        os.makedirs(sample_dir, exist_ok=True)
        print(f"  Created empty directory: {sample_dir}")
        print("  Please add MIDI files to this directory")
    
    print("\n" + "=" * 60)
    print("CHOOSE TEST OPTION:")
    print("=" * 60)
    print("1. Use specific file paths (edit in script)")
    print("2. Search for MIDI files in project")
    print("3. Create a test MIDI file")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_with_sample_midi()
    elif choice == "2":
        list_midi_files()
    elif choice == "3":
        test_file = create_simple_test_midi()
        if test_file:
            # Test with the created file
            parser = MIDIParser()
            parsed = parser.parse_midi(test_file)
            if parsed:
                print(f"\n✓ Test successful! Parsed {len(parsed.get('notes', []))} notes")
                # Ask if they want to run full analysis
                response = input("\nRun full analysis on test file? (y/n): ")
                if response.lower() == 'y':
                    analyzer = MIDIAnalyzer()
                    result = analyzer.analyze_solo_performance(test_file)
                    analyzer.print_analysis_summary()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice")