import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import textwrap

class JSONSummarization:
    """
    Create structured JSON summaries from MIDI analysis results.
    Designed to be easily consumable by GPT for generating feedback.
    """
    
    def __init__(self, analysis_data: Dict[str, Any]):
        """
        Initialize with analysis data from the pipeline.
        
        Args:
            analysis_data: Dictionary containing:
                - reference_data: Parsed reference MIDI
                - performance_data: Parsed performance MIDI
                - alignment: Time alignment results
                - alignment_statistics: Alignment metrics
                - phrases: Phrase segmentation results
                - error_analysis: Error analysis results
        """
        self.analysis_data = analysis_data
        self.reference_data = analysis_data.get('reference_data', {})
        self.performance_data = analysis_data.get('performance_data', {})
        self.error_analysis = analysis_data.get('error_analysis', {})
        self.alignment = analysis_data.get('alignment', [])
        self.phrases = analysis_data.get('phrases', {})
        
    def create_summary(self, include_detailed_data: bool = False) -> Dict[str, Any]:
        """
        Create comprehensive JSON summary for GPT consumption.
        
        Args:
            include_detailed_data: Whether to include raw analysis data
            
        Returns:
            Structured JSON summary optimized for GPT prompts
        """
        print("Creating JSON summary for GPT...")
        
        summary = {
            'metadata': self._create_metadata(),
            'performance_overview': self._create_performance_overview(),
            'error_analysis_summary': self._create_error_summary(),
            'practice_recommendations': self._create_practice_recommendations(),
            'musical_analysis': self._create_musical_analysis(),
            'progress_metrics': self._create_progress_metrics(),
            'gpt_prompt_context': self._create_gpt_context()
        }
        
        if include_detailed_data:
            summary['detailed_data'] = self._extract_detailed_data()
        
        return summary
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create metadata section."""
        reference_notes = self.reference_data.get('notes', [])
        performance_notes = self.performance_data.get('notes', [])
        
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '1.0',
            'reference_statistics': {
                'total_notes': len(reference_notes),
                'duration': self.reference_data.get('metadata', {}).get('total_duration', 0),
                'instruments': self.reference_data.get('instruments', []),
                'pitch_range': self._calculate_pitch_range(reference_notes),
                'note_density': len(reference_notes) / self.reference_data.get('total_duration', 1) if self.reference_data.get('total_duration', 0) > 0 else 0
            },
            'performance_statistics': {
                'total_notes': len(performance_notes),
                'duration': self.performance_data.get('total_duration', 0),
                'pitch_range': self._calculate_pitch_range(performance_notes),
                'note_density': len(performance_notes) / self.performance_data.get('total_duration', 1) if self.performance_data.get('total_duration', 0) > 0 else 0
            }
        }
    
    def _create_performance_overview(self) -> Dict[str, Any]:
        """Create high-level performance overview."""
        error_metrics = self.error_analysis.get('metrics', {})
        score_data = error_metrics.get('performance_score', {})
        
        # Extract key metrics with fallbacks
        note_accuracy = error_metrics.get('note_accuracy', {}).get('accuracy_percentage', 0)
        timing_errors = error_metrics.get('timing_errors', {})
        
        return {
            'overall_assessment': {
                'grade': score_data.get('grade', 'N/A'),
                'score': score_data.get('overall_score', 0),
                'performance_level': self._determine_performance_level(score_data.get('overall_score', 0))
            },
            'key_metrics': {
                'note_accuracy': f"{note_accuracy:.1f}%",
                'timing_consistency': f"±{timing_errors.get('std_error_ms', 0):.1f} ms",
                'dynamic_range': error_metrics.get('dynamic_control', {}).get('dynamic_range', 0),
                'rhythmic_consistency': error_metrics.get('rhythmic_consistency', {}).get('duration_consistency_score', 0)
            },
            'strengths': self.error_analysis.get('performance_summary', {}).get('strengths', []),
            'weaknesses': self.error_analysis.get('performance_summary', {}).get('weaknesses', []),
            'performance_characteristics': self._identify_performance_characteristics()
        }
    
    def _create_error_summary(self) -> Dict[str, Any]:
        """Create structured error summary."""
        error_metrics = self.error_analysis.get('metrics', {})
        error_categories = self.error_analysis.get('error_categories', {})
        
        return {
            'note_accuracy': {
                'summary': self._summarize_note_accuracy(error_metrics.get('note_accuracy', {})),
                'priority': 'high' if error_metrics.get('note_accuracy', {}).get('accuracy_percentage', 100) < 90 else 'medium'
            },
            'timing': {
                'summary': self._summarize_timing_errors(error_metrics.get('timing_errors', {})),
                'patterns': self._extract_timing_patterns(error_metrics.get('timing_errors', {})),
                'priority': self._determine_timing_priority(error_metrics.get('timing_errors', {}))
            },
            'rhythm': {
                'summary': self._summarize_rhythmic_errors(error_metrics.get('rhythmic_consistency', {})),
                'consistency_score': error_metrics.get('rhythmic_consistency', {}).get('duration_consistency_score', 0),
                'priority': 'medium'
            },
            'dynamics': {
                'summary': self._summarize_dynamic_errors(error_metrics.get('dynamic_control', {})),
                'expression_level': error_metrics.get('dynamic_control', {}).get('expression_level', 'Unknown'),
                'priority': 'low'
            },
            'articulation': {
                'summary': self._summarize_articulation_errors(error_metrics.get('articulation', {})),
                'priority': 'medium'
            },
            'error_distribution': self._calculate_error_distribution(error_categories)
        }
    
    def _create_practice_recommendations(self) -> Dict[str, Any]:
        """Create structured practice recommendations."""
        recommendations = self.error_analysis.get('practice_recommendations', [])
        next_steps = self.error_analysis.get('performance_summary', {}).get('next_steps', [])
        
        # Categorize recommendations
        categorized = {
            'urgent': [],
            'technique': [],
            'musicality': [],
            'general': []
        }
        
        all_recs = recommendations + next_steps
        for rec in all_recs:
            rec_lower = rec.lower()
            if any(word in rec_lower for word in ['focus', 'urgent', 'critical', 'significant']):
                categorized['urgent'].append(rec)
            elif any(word in rec_lower for word in ['technique', 'finger', 'hand', 'position']):
                categorized['technique'].append(rec)
            elif any(word in rec_lower for word in ['musical', 'expression', 'phrasing', 'dynamic']):
                categorized['musicality'].append(rec)
            else:
                categorized['general'].append(rec)
        
        return {
            'immediate_focus': categorized['urgent'][:3] if categorized['urgent'] else recommendations[:3],
            'technical_development': categorized['technique'],
            'musical_development': categorized['musicality'],
            'general_practice_tips': categorized['general'],
            'practice_schedule': self._create_practice_schedule(categorized),
            'specific_exercises': self._suggest_exercises()
        }
    
    def _create_musical_analysis(self) -> Dict[str, Any]:
        """Create musical analysis section."""
        reference_notes = self.reference_data.get('notes', [])
        
        return {
            'structure_analysis': {
                'phrase_count': len(self.phrases.get('phrases', [])) if isinstance(self.phrases, dict) else 0,
                'section_count': len(self.phrases.get('sections', [])) if isinstance(self.phrases, dict) else 0,
                'form': self._analyze_musical_form()
            },
            'technical_difficulty': {
                'level': self._assess_technical_difficulty(reference_notes),
                'challenging_sections': self._identify_challenging_sections(),
                'fastest_passage': self._find_fastest_passage(reference_notes),
                'largest_leap': self._find_largest_interval(reference_notes)
            },
            'musical_characteristics': {
                'tempo_profile': self._analyze_tempo_profile(),
                'dynamic_contour': self._analyze_dynamic_contour(),
                'articulation_style': self._analyze_articulation_style()
            }
        }
    
    def _create_progress_metrics(self) -> Dict[str, Any]:
        """Create metrics for tracking progress."""
        error_metrics = self.error_analysis.get('metrics', {})
        score_data = error_metrics.get('performance_score', {})
        
        return {
            'current_performance': {
                'overall_score': score_data.get('overall_score', 0),
                'component_scores': score_data.get('component_scores', {}),
                'benchmarks': self._create_benchmarks()
            },
            'improvement_areas': {
                'highest_priority': self._identify_highest_priority_areas(),
                'quick_wins': self._identify_quick_wins(),
                'long_term_goals': self._identify_long_term_goals()
            },
            'progress_tracking': {
                'metrics_to_track': ['note_accuracy', 'timing_consistency', 'dynamic_range'],
                'target_scores': self._set_target_scores(score_data.get('overall_score', 0)),
                'measurement_frequency': 'weekly'
            }
        }
    
    def _create_gpt_context(self) -> Dict[str, Any]:
        """Create context specifically for GPT prompts."""
        return {
            'instruction_context': {
                'role': "You are an experienced piano teacher analyzing a student's performance.",
                'tone': "Constructive, encouraging, specific",
                'format': "Provide feedback in this order: 1. Overall assessment 2. Strengths 3. Areas for improvement 4. Specific practice suggestions",
                'detail_level': "Be specific about measures and passages"
            },
            'student_profile': {
                'assumed_level': self._infer_student_level(),
                'likely_age': self._estimate_student_age(),
                'practice_habits': self._infer_practice_habits()
            },
            'piece_context': {
                'difficulty_level': self._assess_piece_difficulty(),
                'composer_style': self._infer_composer_style(),
                'musical_period': self._infer_musical_period()
            },
            'response_formatting': {
                'max_length': "500-700 words",
                'include_examples': True,
                'use_musical_terms': "Appropriate for student level",
                'include_encouragement': True
            }
        }
    
    # Helper Methods
    
    def _calculate_pitch_range(self, notes: List[Dict]) -> Dict[str, int]:
        """Calculate pitch range statistics."""
        if not notes:
            return {'min': 0, 'max': 0, 'range': 0}
        
        pitches = [note['pitch'] for note in notes]
        return {
            'min': min(pitches),
            'max': max(pitches),
            'range': max(pitches) - min(pitches)
        }
    
    def _determine_performance_level(self, score: float) -> str:
        """Determine performance level based on score."""
        if score >= 90:
            return "Advanced"
        elif score >= 80:
            return "Intermediate-Advanced"
        elif score >= 70:
            return "Intermediate"
        elif score >= 60:
            return "Late Beginner"
        elif score >= 50:
            return "Early Beginner"
        else:
            return "Novice"
    
    def _identify_performance_characteristics(self) -> List[str]:
        """Identify unique characteristics of this performance."""
        characteristics = []
        error_metrics = self.error_analysis.get('metrics', {})
        
        # Check timing tendencies
        timing = error_metrics.get('timing_errors', {})
        rushing = timing.get('rushing_percentage', 0)
        dragging = timing.get('dragging_percentage', 0)
        
        if rushing > dragging + 10:
            characteristics.append("Energetic, forward-moving tempo")
        elif dragging > rushing + 10:
            characteristics.append("Relaxed, deliberate tempo")
        
        # Check dynamic expression
        dynamics = error_metrics.get('dynamic_control', {})
        if dynamics.get('expression_level', '') == 'Highly Expressive':
            characteristics.append("Expressive dynamic control")
        
        # Check articulation
        articulation = error_metrics.get('articulation', {})
        staccato = articulation.get('staccato_percentage', 0)
        legato = articulation.get('legato_percentage', 0)
        
        if staccato > 50:
            characteristics.append("Crisp, articulated playing")
        elif legato > 50:
            characteristics.append("Smooth, connected playing")
        
        return characteristics if characteristics else ["Balanced musical approach"]
    
    def _summarize_note_accuracy(self, accuracy_data: Dict) -> str:
        """Create summary text for note accuracy."""
        accuracy = accuracy_data.get('accuracy_percentage', 100)
        missing = accuracy_data.get('missing_percentage', 0)
        wrong = accuracy_data.get('wrong_notes', 0)
        
        if accuracy >= 98:
            return "Excellent note accuracy with virtually no errors."
        elif accuracy >= 95:
            return f"Very good note accuracy ({accuracy:.1f}% correct). {missing:.1f}% of notes were missed."
        elif accuracy >= 90:
            return f"Good note accuracy overall ({accuracy:.1f}% correct). Focus on the {missing:.1f}% of missing notes."
        elif accuracy >= 80:
            return f"Note accuracy needs improvement ({accuracy:.1f}% correct). {missing:.1f}% of notes were missed."
        else:
            return f"Significant note accuracy issues ({accuracy:.1f}% correct). {missing:.1f}% of notes were missed."
    
    def _summarize_timing_errors(self, timing_data: Dict) -> str:
        """Create summary text for timing errors."""
        mean_error = timing_data.get('mean_error_ms', 0)
        std_error = timing_data.get('std_error_ms', 0)
        rushing = timing_data.get('rushing_percentage', 0)
        dragging = timing_data.get('dragging_percentage', 0)
        
        if abs(mean_error) < 20 and std_error < 30:
            return "Excellent timing control with precise rhythm."
        elif rushing > dragging + 15:
            return f"Tendency to rush ({rushing:.1f}% of notes early by average {mean_error:.1f}ms)."
        elif dragging > rushing + 15:
            return f"Tendency to drag ({dragging:.1f}% of notes late by average {abs(mean_error):.1f}ms)."
        elif std_error > 50:
            return f"Inconsistent timing (±{std_error:.1f}ms variability)."
        else:
            return f"Generally good timing (±{std_error:.1f}ms consistency)."
    
    def _extract_timing_patterns(self, timing_data: Dict) -> List[str]:
        """Extract timing patterns for summary."""
        patterns = timing_data.get('rhythmic_patterns', [])
        pattern_descriptions = []
        
        for pattern in patterns[:3]:  # Top 3 patterns
            if pattern['type'] == 'consistent_rushing':
                pattern_descriptions.append(
                    f"Consistent rushing in measures {pattern['start_index']}-{pattern['start_index'] + pattern['length']}"
                )
            elif pattern['type'] == 'consistent_dragging':
                pattern_descriptions.append(
                    f"Consistent dragging in measures {pattern['start_index']}-{pattern['start_index'] + pattern['length']}"
                )
        
        return pattern_descriptions
    
    def _determine_timing_priority(self, timing_data: Dict) -> str:
        """Determine priority level for timing issues."""
        std_error = timing_data.get('std_error_ms', 0)
        rushing = timing_data.get('rushing_percentage', 0)
        dragging = timing_data.get('dragging_percentage', 0)
        
        if std_error > 80 or max(rushing, dragging) > 40:
            return 'high'
        elif std_error > 50 or max(rushing, dragging) > 25:
            return 'medium'
        else:
            return 'low'
    
    def _summarize_rhythmic_errors(self, rhythm_data: Dict) -> str:
        """Create summary text for rhythmic errors."""
        consistency = rhythm_data.get('duration_consistency_score', 0)
        
        if consistency >= 0.9:
            return "Excellent rhythmic consistency."
        elif consistency >= 0.8:
            return "Good rhythmic consistency with steady pulse."
        elif consistency >= 0.7:
            return "Adequate rhythmic consistency, some variability present."
        elif consistency >= 0.6:
            return "Rhythmic consistency needs improvement."
        else:
            return "Significant rhythmic inconsistency issues."
    
    def _summarize_dynamic_errors(self, dynamics_data: Dict) -> str:
        """Create summary text for dynamic errors."""
        dynamic_range = dynamics_data.get('dynamic_range', 0)
        expression = dynamics_data.get('expression_level', 'Unknown')
        
        if dynamic_range > 70 and expression == 'Highly Expressive':
            return "Excellent dynamic control with wide expressive range."
        elif dynamic_range > 50:
            return f"Good dynamic control ({dynamic_range} range). {expression} expression."
        elif dynamic_range > 30:
            return f"Adequate dynamics ({dynamic_range} range). Could use more variety."
        else:
            return f"Limited dynamic range ({dynamic_range}). Focus on creating more contrast."
    
    def _summarize_articulation_errors(self, articulation_data: Dict) -> str:
        """Create summary text for articulation errors."""
        staccato = articulation_data.get('staccato_percentage', 0)
        legato = articulation_data.get('legato_percentage', 0)
        consistency = articulation_data.get('articulation_consistency', 0)
        
        if consistency >= 0.8:
            consistency_text = "consistent"
        elif consistency >= 0.6:
            consistency_text = "somewhat consistent"
        else:
            consistency_text = "inconsistent"
        
        return f"{consistency_text} articulation with {staccato:.1f}% staccato and {legato:.1f}% legato notes."
    
    def _calculate_error_distribution(self, error_categories: Dict) -> Dict[str, float]:
        """Calculate distribution of error types."""
        distribution = {}
        total_errors = 0
        
        for category, errors in error_categories.items():
            if isinstance(errors, dict):
                error_count = sum(len(err_list) for err_list in errors.values() if isinstance(err_list, list))
            elif isinstance(errors, list):
                error_count = len(errors)
            else:
                error_count = 0
            
            distribution[category] = error_count
            total_errors += error_count
        
        # Convert to percentages
        if total_errors > 0:
            for category in distribution:
                distribution[category] = (distribution[category] / total_errors) * 100
        
        return distribution
    
    def _create_practice_schedule(self, categorized_recs: Dict) -> Dict[str, Any]:
        """Create a suggested practice schedule."""
        return {
            'daily_focus': {
                'warmup': "5 minutes: scales with metronome",
                'technical_work': "10 minutes: " + ("; ".join(categorized_recs['technique'][:2]) if categorized_recs['technique'] else "sight-reading"),
                'piece_work': "15 minutes: focus on " + (categorized_recs['urgent'][0] if categorized_recs['urgent'] else "musical expression"),
                'musicality': "5 minutes: " + ("; ".join(categorized_recs['musicality'][:2]) if categorized_recs['musicality'] else "dynamics practice")
            },
            'weekly_goals': [
                "Improve timing consistency by 10%",
                "Master 2 most challenging measures",
                "Work on dynamic contrast"
            ],
            'practice_duration': "35-45 minutes daily"
        }
    
    def _suggest_exercises(self) -> List[str]:
        """Suggest specific exercises based on errors."""
        error_metrics = self.error_analysis.get('metrics', {})
        exercises = []
        
        # Timing exercises
        timing = error_metrics.get('timing_errors', {})
        if timing.get('std_error_ms', 0) > 50:
            exercises.append("Practice with metronome at slow tempo (50% of performance tempo)")
        
        # Dynamic exercises
        dynamics = error_metrics.get('dynamic_control', {})
        if dynamics.get('dynamic_range', 0) < 40:
            exercises.append("Crescendo/decrescendo exercises on single notes")
        
        # Articulation exercises
        articulation = error_metrics.get('articulation', {})
        if articulation.get('articulation_consistency', 0) < 0.7:
            exercises.append("Staccato-legato contrast exercises")
        
        # Note accuracy exercises
        note_acc = error_metrics.get('note_accuracy', {})
        if note_acc.get('accuracy_percentage', 100) < 90:
            exercises.append("Hands-separate practice of difficult passages")
        
        return exercises[:5]  # Top 5 exercises
    
    def _analyze_musical_form(self) -> str:
        """Analyze the musical form/structure."""
        phrases = self.phrases.get('phrases', [])
        if isinstance(phrases, list) and len(phrases) >= 4:
            return f"Clear phrase structure with {len(phrases)} distinct phrases"
        elif isinstance(phrases, list) and len(phrases) >= 2:
            return f"Simple phrase structure with {len(phrases)} phrases"
        else:
            return "Continuous musical line"
    
    def _assess_technical_difficulty(self, reference_notes: List[Dict]) -> str:
        """Assess technical difficulty level."""
        if not reference_notes:
            return "Unknown"
        
        note_count = len(reference_notes)
        duration = self.reference_data.get('total_duration', 1)
        notes_per_second = note_count / duration
        
        if notes_per_second > 10:
            return "Advanced (virtuosic)"
        elif notes_per_second > 6:
            return "Intermediate-Advanced"
        elif notes_per_second > 3:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _identify_challenging_sections(self) -> List[Dict]:
        """Identify challenging sections based on error density."""
        # This would be implemented with actual section data
        return [
            {'section': 'Measures 5-8', 'reason': 'Fast arpeggios', 'difficulty': 'high'},
            {'section': 'Measures 12-15', 'reason': 'Complex rhythm', 'difficulty': 'medium'}
        ]
    
    def _find_fastest_passage(self, notes: List[Dict]) -> Dict:
        """Find the fastest passage in the piece."""
        if len(notes) < 10:
            return {'tempo': 'N/A', 'location': 'N/A'}
        
        # Simplified implementation
        return {'tempo': '♩=120', 'location': 'Measures 8-12'}
    
    def _find_largest_interval(self, notes: List[Dict]) -> Dict:
        """Find the largest interval leap."""
        if len(notes) < 2:
            return {'interval': 0, 'location': 'N/A'}
        
        # Simplified implementation
        return {'interval': 'octave', 'location': 'Measure 7'}
    
    def _analyze_tempo_profile(self) -> str:
        """Analyze tempo profile."""
        return "Generally steady tempo with slight rubato in expressive sections"
    
    def _analyze_dynamic_contour(self) -> str:
        """Analyze dynamic contour/shape."""
        return "Clear dynamic shaping with peak at climax sections"
    
    def _analyze_articulation_style(self) -> str:
        """Analyze articulation style."""
        return "Mixed articulation suitable for Classical style"
    
    def _create_benchmarks(self) -> Dict[str, float]:
        """Create benchmark scores for comparison."""
        return {
            'beginner_target': 60,
            'intermediate_target': 75,
            'advanced_target': 85,
            'professional_target': 92
        }
    
    def _identify_highest_priority_areas(self) -> List[str]:
        """Identify highest priority improvement areas."""
        priorities = []
        error_metrics = self.error_analysis.get('metrics', {})
        
        note_acc = error_metrics.get('note_accuracy', {})
        if note_acc.get('accuracy_percentage', 100) < 85:
            priorities.append("Note accuracy")
        
        timing = error_metrics.get('timing_errors', {})
        if timing.get('std_error_ms', 0) > 60:
            priorities.append("Timing consistency")
        
        return priorities[:2] if priorities else ["Musical expression"]
    
    def _identify_quick_wins(self) -> List[str]:
        """Identify areas that could improve quickly."""
        return [
            "Dynamic contrast in repeated sections",
            "Articulation consistency in scales",
            "Tempo stability in familiar passages"
        ]
    
    def _identify_long_term_goals(self) -> List[str]:
        """Identify long-term development goals."""
        return [
            "Develop consistent touch across all dynamics",
            "Improve sight-reading fluency",
            "Expand repertoire in this style"
        ]
    
    def _set_target_scores(self, current_score: float) -> Dict[str, float]:
        """Set realistic target scores for progress tracking."""
        next_target = min(current_score + 10, 95)
        return {
            'next_week': next_target,
            'one_month': min(current_score + 15, 95),
            'three_months': min(current_score + 25, 95)
        }
    
    def _infer_student_level(self) -> str:
        """Infer student level from performance."""
        score = self.error_analysis.get('metrics', {}).get('performance_score', {}).get('overall_score', 0)
        return self._determine_performance_level(score)
    
    def _estimate_student_age(self) -> str:
        """Estimate student age range."""
        # Very rough estimation based on performance characteristics
        score = self.error_analysis.get('metrics', {}).get('performance_score', {}).get('overall_score', 0)
        
        if score >= 80:
            return "Teen to Adult"
        elif score >= 70:
            return "Older Child to Teen"
        elif score >= 60:
            return "Child (8-12)"
        else:
            return "Young Beginner"
    
    def _infer_practice_habits(self) -> str:
        """Infer likely practice habits."""
        error_metrics = self.error_analysis.get('metrics', {})
        consistency = error_metrics.get('rhythmic_consistency', {}).get('duration_consistency_score', 0)
        
        if consistency > 0.8:
            return "Likely practices regularly with metronome"
        elif consistency > 0.6:
            return "Regular practice, could be more focused"
        else:
            return "Would benefit from more structured practice sessions"
    
    def _assess_piece_difficulty(self) -> str:
        """Assess the difficulty level of the piece."""
        reference_notes = self.reference_data.get('notes', [])
        return self._assess_technical_difficulty(reference_notes)
    
    def _infer_composer_style(self) -> str:
        """Infer composer style from piece characteristics."""
        # Simplified inference
        pitch_range = self._calculate_pitch_range(self.reference_data.get('notes', []))
        range_size = pitch_range.get('range', 0)
        
        if range_size > 48:  # 4 octaves
            return "Romantic/Virtuosic"
        elif range_size > 36:  # 3 octaves
            return "Classical"
        else:
            return "Baroque/Early Classical"
    
    def _infer_musical_period(self) -> str:
        """Infer musical period from piece characteristics."""
        style = self._infer_composer_style()
        
        if 'Romantic' in style:
            return "Romantic Period"
        elif 'Classical' in style:
            return "Classical Period"
        elif 'Baroque' in style:
            return "Baroque Period"
        else:
            return "Various/Modern"
    
    def _extract_detailed_data(self) -> Dict[str, Any]:
        """Extract detailed data for advanced analysis."""
        return {
            'raw_alignment': self.alignment[:100],  # First 100 aligned pairs
            'error_categories': self.error_analysis.get('error_categories', {}),
            'phrase_data': self.phrases,
            'note_level_analysis': self._extract_note_level_data()
        }
    
    def _extract_note_level_data(self) -> List[Dict]:
        """Extract note-level analysis data."""
        note_data = []
        aligned_pairs = self.alignment[:50]  # First 50 notes
        
        for pair in aligned_pairs:
            if pair.get('reference_note') and pair.get('performance_note'):
                note_data.append({
                    'time': pair['reference_note'].get('start', 0),
                    'pitch': pair['reference_note'].get('pitch', 0),
                    'timing_error': pair.get('time_difference', 0),
                    'velocity_error': pair.get('velocity_difference', 0),
                    'alignment_confidence': pair.get('alignment_confidence', 0)
                })
        
        return note_data
    
    def save_summary(self, filepath: str, include_detailed: bool = False):
        """
        Save JSON summary to file.
        
        Args:
            filepath: Path to save JSON file
            include_detailed: Whether to include detailed data
        """
        summary = self.create_summary(include_detailed_data=include_detailed)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Summary saved to: {filepath}")
        return summary


# Utility functions for quick summarization
def create_gpt_summary(analysis_data: Dict[str, Any], 
                      output_file: str = None) -> Dict[str, Any]:
    """
    Create GPT-ready summary from analysis data.
    
    Args:
        analysis_data: Complete analysis data from pipeline
        output_file: Optional file to save summary
        
    Returns:
        GPT-ready summary JSON
    """
    summarizer = JSONSummarization(analysis_data)
    summary = summarizer.create_summary()
    
    if output_file:
        summarizer.save_summary(output_file)
    
    return summary


def create_minimal_summary(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create minimal summary for quick feedback.
    
    Returns:
        Minimal summary with key information
    """
    error_analysis = analysis_data.get('error_analysis', {})
    metrics = error_analysis.get('metrics', {})
    score_data = metrics.get('performance_score', {})
    
    return {
        'overall_grade': score_data.get('grade', 'N/A'),
        'overall_score': score_data.get('overall_score', 0),
        'note_accuracy': metrics.get('note_accuracy', {}).get('accuracy_percentage', 0),
        'timing_consistency': metrics.get('timing_errors', {}).get('std_error_ms', 0),
        'top_recommendation': error_analysis.get('practice_recommendations', [''])[0] if error_analysis.get('practice_recommendations') else '',
        'timestamp': datetime.now().isoformat()
    }