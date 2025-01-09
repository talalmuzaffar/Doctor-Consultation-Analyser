# Doctor Consultation Analyzer

A sophisticated AI-powered application that transforms medical consultations into structured, analyzable documentation. Built with Streamlit and Groq AI, this tool specializes in Urdu-to-English medical translation, transcription, and comprehensive clinical analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.x-FF4B4B)

## 🌟 Key Features

### Audio Processing
- **Live Recording**
  - Real-time audio capture with visual feedback
  - Adjustable recording duration
  - Background noise reduction
  - Instant playback for verification

- **File Upload Support**
  - Multiple format support (M4A, MP3, WAV)
  - Large file handling
  - Error handling and validation

### Language Processing
- **Transcription**
  - Urdu speech-to-text conversion
  - Medical terminology recognition
  - High accuracy with Whisper Large V3 model

- **Translation**
  - Professional medical Urdu-to-English translation
  - Context-aware translation
  - Preservation of medical terms and measurements
  - Maintenance of consultation flow

### Clinical Analysis
- **Structured Data Extraction**
  - Diagnosis identification
  - Medication details parsing
  - Treatment plan structuring
  - Follow-up instructions

- **Safety Analysis**
  - Drug interaction warnings
  - Contraindication detection
  - Critical symptom alerts
  - Allergy check verification

### Documentation
- **Export Options**
  - Professional PDF reports
  - Markdown format
  - Structured clinical notes
  - Easy-to-read formatting

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the Repository**
```bash
git clone https://github.com/talalmuzaffar/Doctor-Consultation-Analyser
cd medical-consultation-analyzer
```

2. **Create and Activate Virtual Environment**
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For Unix/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
```

5. **Launch Application**
```bash
streamlit run app.py
```

## 💻 Usage Guide

### Recording a Consultation

1. **Start Recording**
   - Navigate to "Record Audio" tab
   - Click the microphone button
   - Speak clearly into your microphone

2. **Stop and Review**
   - Click the microphone again to stop
   - Review the recording using the playback controls
   - Click "Process Recording" to analyze

### Uploading Audio Files

1. **File Upload**
   - Go to "Upload Audio" tab
   - Drag and drop or select your audio file
   - Supported formats: M4A, MP3, WAV

### Analyzing Results

The analysis provides:
- Original Urdu transcription
- English translation
- Structured medical analysis including:
  - Diagnosis and findings
  - Medication details
  - Safety alerts
  - Follow-up plans

### Downloading Reports

- **PDF Format**
  - Professional layout
  - Sections clearly divided
  - Easy to print and share

- **Markdown Format**
  - Editable text format
  - Compatible with most text editors
  - Easy to integrate into other systems

## 🛠️ Technical Details

### Dependencies
```
streamlit>=1.10.0
groq>=0.1.0
python-dotenv>=0.19.0
audio-recorder-streamlit>=0.0.8
reportlab>=3.6.8
pydantic>=1.9.0
```

### Data Models
- `Medication`: Structured medication information
- `Diagnosis`: Clinical findings and conditions
- `FollowUp`: Follow-up planning details
- `SafetyAlerts`: Clinical warnings and precautions
- `ConsultationAnalysis`: Complete consultation structure

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki Link]
- **Issues**: Please report bugs via GitHub issues
- **Contact**: [Your Contact Information]

## 🙏 Acknowledgments

- Groq AI for providing powerful language models
- Streamlit team for the excellent web framework
- OpenAI's Whisper for transcription capabilities
- ReportLab for PDF generation
- All contributors and users of this project

## 🔄 Updates and Versions

- Current Version: 1.0.0
- Last Updated: [Date]
- Check releases for changelog

---

**Note**: This project is actively maintained. For the latest updates and features, please star and watch the repository.
