import pretty_midi
from typing import Dict, List, Any
import numpy as np

class MIDIParser:
    def __init__(self):
        self.parsed_data = {}
        self.midi_data = None
    
    def parse_midi(self, midi_path) -> Dict[str, Any]:
        """Parse MIDI file into comprehensive structured data."""
        try:
            self.midi_data = pretty_midi.PrettyMIDI(midi_path)
            
            return {
                'notes': self._extract_notes(),
                'metadata': self._extract_metadata(),
                'timing': self._extract_timing_info(),
                'harmony': self._extract_harmonic_content(),
                'structure': self._extract_musical_structure(),
                'performance_data': self._extract_performance_patterns()
            }
            
        except Exception as e:
            print(f"Error parsing MIDI file: {e}")
            return {}
    
    def _extract_notes(self) -> List[Dict]:
        """Extract detailed note information."""
        notes = []
        for i, instrument in enumerate(self.midi_data.instruments):
            for note in instrument.notes:
                note_data = {
                    'pitch': note.pitch,
                    'pitch_name': pretty_midi.note_number_to_name(note.pitch),
                    'start': note.start,
                    'end': note.end,
                    'velocity': note.velocity,
                    'duration': note.end - note.start,
                    'instrument': instrument.program,
                    'instrument_name': instrument.name,
                    'track_id': i,
                    'beat_position': self._get_beat_position(note.start),
                    'measure_position': self._get_measure_position(note.start)
                }
                notes.append(note_data)
        
        return sorted(notes, key=lambda x: x['start'])
    
    def _extract_metadata(self) -> Dict:
        """Extract MIDI file metadata."""
        # Calculate total duration from the actual notes, not just get_end_time()
        notes = self._extract_notes()
        if notes:
            max_end_time = max(note['end'] for note in notes)
        else:
            max_end_time = self.midi_data.get_end_time() if self.midi_data else 0
        
        return {
            'total_duration': max_end_time,  # Use the actual maximum end time
            'instruments': [
                {
                    'name': inst.name,
                    'program': inst.program,
                    'is_drum': inst.is_drum,
                    'note_count': len(inst.notes)
                } for inst in self.midi_data.instruments
            ],
            'key_signature_changes': [
                {
                    'key': str(ks.key),
                    'time': ks.time
                } for ks in self.midi_data.key_signature_changes
            ],
            'lyrics': [ly.text for ly in self.midi_data.lyrics] if hasattr(self.midi_data, 'lyrics') else []
        }
    def _extract_timing_info(self) -> Dict:
        """Extract tempo and time signature information."""
        # Get beats and downbeats for rhythmic analysis
        beats = self.midi_data.get_beats()
        downbeats = self.midi_data.get_downbeats()
        
        return {
            # 'tempo_changes': [
            #     {
            #         'tempo': tc.tempo,
            #         'time': tc.time,
            #         'bpm': tc.tempo
            #     } for tc in self.midi_data.tempo_changes
            # ],
            'time_signature_changes': [
                {
                    'numerator': ts.numerator,
                    'denominator': ts.denominator,
                    'time': ts.time
                } for ts in self.midi_data.time_signature_changes
            ],
            'average_tempo': self.midi_data.estimate_tempo(),
            'beats': beats.tolist() if beats is not None else [],
            'downbeats': downbeats.tolist() if downbeats is not None else [],
            'ticks_per_beat': getattr(self.midi_data, 'ticks_per_beat', None)
        }
    
    def _extract_harmonic_content(self) -> Dict:
        """Extract chords and harmonic analysis."""
        notes = self._extract_notes()
        
        # Simple chord detection (you can enhance this)
        chords = self._detect_chords(notes)
        
        return {
            'chords': chords,
            'pitch_range': {
                'min_pitch': min(note['pitch'] for note in notes) if notes else 0,
                'max_pitch': max(note['pitch'] for note in notes) if notes else 0,
                'pitch_variety': len(set(note['pitch'] for note in notes))
            }
        }
    
    def _extract_musical_structure(self) -> Dict:
        """Extract phrases and musical sections."""
        notes = self._extract_notes()
        
        return {
            'phrases': self._detect_phrases(notes),
            'sections': self._detect_sections(notes),
            'note_density': self._calculate_note_density(notes)
        }
    
    def _extract_performance_patterns(self) -> Dict:
        """Extract patterns useful for performance analysis."""
        notes = self._extract_notes()
        
        return {
            'velocity_profile': {
                'mean_velocity': np.mean([n['velocity'] for n in notes]) if notes else 0,
                'velocity_std': np.std([n['velocity'] for n in notes]) if notes else 0,
                'dynamic_range': {
                    'min': min(n['velocity'] for n in notes) if notes else 0,
                    'max': max(n['velocity'] for n in notes) if notes else 0
                }
            },
            'timing_consistency': self._analyze_timing_consistency(notes),
            'articulation_patterns': self._analyze_articulation(notes)
        }
    
    # Helper methods would go here...
    def _get_beat_position(self, time: float) -> float:
        """Calculate beat position within measure."""
        # Implementation depends on time signature
        pass
    
    def _get_measure_position(self, time: float) -> Dict:
        """Calculate measure and beat position."""
        pass
    
    def _detect_chords(self, notes: List[Dict]) -> List[Dict]:
        """Simple chord detection algorithm."""
        # Group notes by time windows to find simultaneous notes
        chords = []
        time_window = 0.05  # 50ms window for chord detection
        
        # Implementation for chord detection
        return chords
    
    def _detect_phrases(self, notes: List[Dict]) -> List[Dict]:
        """Detect musical phrases based on rests and patterns."""
        # Implementation for phrase detection
        return []
    
    def _detect_sections(self, notes: List[Dict]) -> List[Dict]:
        """Detect musical sections based on patterns and changes."""
        return []
    
    def _calculate_note_density(self, notes: List[Dict]) -> List[Dict]:
        """Calculate note density over time."""
        return []
    
    def _analyze_timing_consistency(self, notes: List[Dict]) -> Dict:
        """Analyze timing consistency for performance evaluation."""
        return {}
    
    def _analyze_articulation(self, notes: List[Dict]) -> Dict:
        """Analyze articulation patterns (staccato, legato)."""
        return {}
    
    def get_pretty_midi_object():
        return {}
    