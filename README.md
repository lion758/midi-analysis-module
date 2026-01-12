# MIDI Analysis Module

Automatic performance analysis and feedback generation for music education.

## Installation
```bash
git clone https://github.com/majahonkebmd/midi-analysis-module.git
cd midi-analysis-module
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
## running through analyzer.py 
```bash
python -c "from src.analyzer import compare_performance; compare_performance('sample_files/reference.mid','sample_files/performance.mid','analysis_results')"
```

