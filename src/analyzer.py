import os
import json
from typing import Dict, List, Any, Optional
from .midi_parser import MIDIParser
from .time_alignment import TimeAlignment, align_midi_files
from .phrase_segmentation import PhraseSegmentation
from .error_analysis import ErrorAnalysis
from .json_summarization import JSONSummarization


class MIDIAnalyzer:
    """
    Main orchestrator for the MIDI analysis pipeline.
    Handles both solo performance analysis and reference-based comparison.
    """
    
    def __init__(self):
        """Initialize all analysis components."""
        self.parser = MIDIParser()
        self.analysis_results = {}
    
    def analyze_solo_performance(self, performance_path: str) -> Dict[str, Any]:
        """
        Analyze a performance without reference (for practice sessions).
        
        Args:
            performance_path: Path to the performance MIDI file
            
        Returns:
            Dictionary containing solo performance analysis
        """
        print(f"Analyzing solo performance: {performance_path}")
        
        # Parse the performance
        performance_data = self.parser.parse_midi(performance_path)
        
        if not performance_data:
            raise ValueError(f"Failed to parse performance MIDI: {performance_path}")
        
        # Basic analysis
        notes = performance_data.get('notes', [])
        total_duration = performance_data.get('total_duration', 0)
        
        # Calculate basic metrics
        metrics = self._calculate_basic_metrics(notes, total_duration)
        
        self.analysis_results = {
            'analysis_type': 'solo_performance',
            'performance_file': performance_path,
            'parsed_data': performance_data,
            'metrics': metrics,
            'practice_recommendations': self._generate_solo_recommendations(metrics)
        }
        
        return self.analysis_results
    
# Update the analyze_with_reference method in analyzer.py (around line 86-95)
    def analyze_with_reference(self, 
                            reference_path: str, 
                            performance_path: str,
                            output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis comparing performance with reference.
        
        Args:
            reference_path: Path to reference MIDI file
            performance_path: Path to performance MIDI file
            output_dir: Optional directory to save analysis reports
            
        Returns:
            Dictionary containing complete analysis results
        """
        print(f"Analyzing performance against reference...")
        print(f"Reference: {reference_path}")
        print(f"Performance: {performance_path}")
        
        # Parse both files
        print("1. Parsing MIDI files...")
        reference_parsed = self.parser.parse_midi(reference_path)
        performance_parsed = self.parser.parse_midi(performance_path)
        
        if not reference_parsed or not performance_parsed:
            raise ValueError("Failed to parse one or both MIDI files")
        
        # Create PrettyMIDI objects directly for time alignment
        print("2. Performing time alignment...")
        import pretty_midi
        
        try:
            # Create PrettyMIDI objects from file paths
            reference_midi = pretty_midi.PrettyMIDI(reference_path)
            performance_midi = pretty_midi.PrettyMIDI(performance_path)
            
            aligner = TimeAlignment(reference_midi, performance_midi)
        except Exception as e:
            print(f"Warning: Could not create PrettyMIDI objects, using parsed data: {e}")
            # Fall back to using parsed data
            aligner = TimeAlignment(reference_parsed, performance_parsed)
        
        alignment_result = aligner.compute_dtw_alignment()
        aligned_notes = aligner.align_notes()
        alignment_stats = aligner.get_alignment_statistics(aligned_notes)
        
        # Rest of the method remains the same...
        # Phrase segmentation (on reference)
        print("3. Segmenting musical phrases...")
        phrase_segmenter = PhraseSegmentation(reference_parsed)
        segmented_data = phrase_segmenter.segment_phrases()
        
        
        # Error analysis
        print("4. Analyzing performance errors...")
        error_analyzer = ErrorAnalysis({
            'reference': reference_parsed,
            'performance': performance_parsed,
            'alignment': aligned_notes
        })
        error_analysis = error_analyzer.analyze_performance()  
        
        # JSON summarization for GPT
        print("5. Generating comprehensive summary...")
        analysis_data = {
            'reference_data': reference_parsed,
            'performance_data': performance_parsed,
            'alignment': aligned_notes,
            'alignment_statistics': alignment_stats,
            'phrases': segmented_data,
            'error_analysis': error_analysis
        }
        
        summarizer = JSONSummarization(analysis_data)
        gpt_summary = summarizer.create_summary()
        
        # Compile final results
        self.analysis_results = {
            'analysis_type': 'reference_comparison',
            'reference_file': reference_path,
            'performance_file': performance_path,
            'timestamp': self._get_timestamp(),
            'parsed_data': {
                'reference': reference_parsed,
                'performance': performance_parsed
            },
            'time_alignment': {
                'aligned_notes': aligned_notes,
                'statistics': alignment_stats
            },
            'musical_structure': segmented_data,
            'performance_analysis': error_analysis,
            'gpt_ready_summary': gpt_summary
        }
        
        # Save reports if output directory provided
        if output_dir:
            self._save_analysis_reports(output_dir)
        
        print("Analysis complete!")
        return self.analysis_results
    def _calculate_basic_metrics(self, notes: List[Dict], total_duration: float) -> Dict[str, Any]:
        """Calculate basic performance metrics for solo analysis."""
        if not notes:
            return {}
        
        velocities = [note['velocity'] for note in notes]
        durations = [note['duration'] for note in notes]
        
        return {
            'note_count': len(notes),
            'total_duration': total_duration,
            'notes_per_second': len(notes) / total_duration if total_duration > 0 else 0,
            'velocity_stats': {
                'mean': sum(velocities) / len(velocities),
                'min': min(velocities),
                'max': max(velocities),
                'dynamic_range': max(velocities) - min(velocities)
            },
            'duration_stats': {
                'mean': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations)
            },
            'pitch_range': {
                'min': min(note['pitch'] for note in notes),
                'max': max(note['pitch'] for note in notes)
            }
        }
    
    def _generate_solo_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate practice recommendations based on solo performance metrics."""
        recommendations = []
        
        # Dynamic control recommendations
        velocity_stats = metrics.get('velocity_stats', {})
        dynamic_range = velocity_stats.get('dynamic_range', 0)
        if dynamic_range < 30:
            recommendations.append("Try to incorporate more dynamic variation in your playing")
        
        # Note density recommendations
        notes_per_second = metrics.get('notes_per_second', 0)
        if notes_per_second > 10:
            recommendations.append("Fast passage detected - consider using metronome for even timing")
        elif notes_per_second < 2:
            recommendations.append("Slow passage - focus on musical expression and phrasing")
        
        # Duration consistency
        duration_stats = metrics.get('duration_stats', {})
        duration_std = duration_stats.get('std', 0)  # Would need to calculate std
        if duration_std > 0.5:  # Example threshold
            recommendations.append("Work on consistent note durations for cleaner articulation")
        
        return recommendations
    
    def _save_analysis_reports(self, output_dir: str):
        """Save various analysis reports to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save full analysis results
        full_report_path = os.path.join(output_dir, 'full_analysis.json')
        with open(full_report_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        # Save GPT-ready summary
        gpt_summary_path = os.path.join(output_dir, 'gpt_summary.json')
        gpt_summary = self.analysis_results.get('gpt_ready_summary', {})
        with open(gpt_summary_path, 'w') as f:
            json.dump(gpt_summary, f, indent=2, default=str)
        
        # Save alignment report
        alignment_path = os.path.join(output_dir, 'alignment_report.json')
        alignment_data = {
            'aligned_notes': self.analysis_results['time_alignment']['aligned_notes'],
            'statistics': self.analysis_results['time_alignment']['statistics']
        }
        with open(alignment_path, 'w') as f:
            json.dump(alignment_data, f, indent=2, default=str)
        
        print(f"Analysis reports saved to: {output_dir}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis records."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def print_analysis_summary(self):
        """Print a human-readable summary of the analysis results."""
        if not self.analysis_results:
            print("No analysis results available. Run an analysis first.")
            return
        
        analysis_type = self.analysis_results.get('analysis_type', 'unknown')
        
        print("\n" + "="*50)
        print("MIDI ANALYSIS SUMMARY")
        print("="*50)
        
        if analysis_type == 'solo_performance':
            self._print_solo_summary()
        elif analysis_type == 'reference_comparison':
            self._print_reference_summary()
        
        print("="*50)
    
    def _print_solo_summary(self):
        """Print summary for solo performance analysis."""
        metrics = self.analysis_results.get('metrics', {})
        performance_file = self.analysis_results.get('performance_file', 'Unknown')
        
        print(f"Performance File: {performance_file}")
        print(f"Total Notes: {metrics.get('note_count', 0)}")
        print(f"Duration: {metrics.get('total_duration', 0):.2f} seconds")
        print(f"Note Density: {metrics.get('notes_per_second', 0):.2f} notes/sec")
        
        print("\nPRACTICE RECOMMENDATIONS:")
        recommendations = self.analysis_results.get('practice_recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  No specific recommendations available.")
    
    def _print_reference_summary(self):
        """Print summary for reference-based analysis."""
        stats = self.analysis_results['time_alignment']['statistics']
        alignment_summary = stats.get('alignment_summary', {})
        timing_analysis = stats.get('timing_analysis', {})
        
        print(f"Reference: {self.analysis_results.get('reference_file', 'Unknown')}")
        print(f"Performance: {self.analysis_results.get('performance_file', 'Unknown')}")
        
        print(f"\nALIGNMENT RESULTS:")
        print(f"  Successfully Aligned: {alignment_summary.get('successfully_aligned', 0)} notes")
        print(f"  Missing Notes: {alignment_summary.get('missing_notes', 0)}")
        print(f"  Extra Notes: {alignment_summary.get('extra_notes', 0)}")
        print(f"  Alignment Rate: {alignment_summary.get('alignment_rate', 0)*100:.1f}%")
        
        print(f"\nTIMING ANALYSIS:")
        print(f"  Avg Time Difference: {timing_analysis.get('mean_time_difference', 0):.3f}s")
        print(f"  Timing Consistency: ±{timing_analysis.get('std_time_difference', 0):.3f}s")
        print(f"  Rushing Tendency: {timing_analysis.get('rushing_tendency', 0)*100:.1f}%")
        print(f"  Dragging Tendency: {timing_analysis.get('dragging_tendency', 0)*100:.1f}%")


# Convenience functions for quick analysis
def quick_analyze(performance_path: str) -> Dict[str, Any]:
    """Quick analysis of a solo performance."""
    analyzer = MIDIAnalyzer()
    return analyzer.analyze_solo_performance(performance_path)

def compare_performance(reference_path: str, performance_path: str, 
                      output_dir: str = None) -> Dict[str, Any]:
    """Compare performance against reference."""
    analyzer = MIDIAnalyzer()
    return analyzer.analyze_with_reference(reference_path, performance_path, output_dir)

def print_parsed_data(self, performance_path: str):
    """
    Parse a MIDI file and print the parsed data structure.
    """
    try:
        performance_data = self.parser.parse_midi(performance_path)
        
        print("\n" + "="*50)
        print("MIDI PARSED DATA")
        print("="*50)
        print(f"Total notes: {len(performance_data.get('notes', []))}")
        print(f"Total duration: {performance_data.get('total_duration', 0):.2f} seconds")
        print(f"Instruments: {performance_data.get('instruments', [])}")
        
        print("\nFIRST 5 NOTES:")
        notes = performance_data.get('notes', [])
        for i, note in enumerate(notes[:5]):
            print(f"Note {i+1}: pitch={note['pitch']}, start={note['start']:.2f}s, "
                  f"duration={note['duration']:.2f}s, velocity={note['velocity']}")
        
        if len(notes) > 5:
            print(f"... and {len(notes) - 5} more notes")
            
        return performance_data
        
    except Exception as e:
        print(f"Error parsing MIDI file: {e}")
        return None
    
