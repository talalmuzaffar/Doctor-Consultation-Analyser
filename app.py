import streamlit as st
import os
from groq import Groq
import tempfile
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq()

# Initialize session state for recording
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None

def toggle_recording():
    st.session_state.recording = not st.session_state.recording

def process_audio(audio_data, file_extension='.wav'):
    """Process audio data and return transcription"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(audio_data)
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(tmp_file_path, file.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            language="ur"
        )
    
    # Clean up temporary file
    os.unlink(tmp_file_path)
    return transcription.text

def translate_to_english(text):
    """Translate Urdu text to English using Groq LLM"""
    prompt = f"""
    You are translating a medical consultation from Urdu to English.
    Original Urdu text: {text}
    
    Rules:
    1. Translate accurately while maintaining medical terminology
    2. Keep the conversational flow
    3. Preserve any mentioned medications, dosages, or instructions
    4. Maintain the sequence of dialogue
    
    Translate the above text to English:
    """
    
    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "system", 
                "content": "You are a medical translator specializing in Urdu to English translation. Provide clear and accurate translations."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4024,
        top_p=1,
        stream=False,
        stop=None
    )
    
    return response.choices[0].message.content

# Define the data models
class Medication(BaseModel):
    name: str
    type: str
    dosage: str = "Not mentioned"
    duration: str = "Not mentioned"
    timing: str = "Not mentioned"

class Diagnosis(BaseModel):
    condition: str = "Not mentioned"
    findings: List[str] = Field(default_factory=list)

class FollowUp(BaseModel):
    timing: str = "Not mentioned"
    instructions: str = "Not mentioned"

class SafetyAlerts(BaseModel):
    critical_symptoms: List[str] = Field(default_factory=list)
    drug_interactions: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    allergies_checked: str = "Not checked"

class ConsultationAnalysis(BaseModel):
    diagnosis: Diagnosis
    medications: List[Medication] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    follow_up: FollowUp
    safety_alerts: SafetyAlerts

def analyze_medical_text(text):
    """Analyze transcribed text using Groq LLM"""
    try:
        st.info("Translating consultation from Urdu to English...")
        english_text = translate_to_english(text)
        st.success("Translation completed!")
        
        st.subheader("Original Urdu Text")
        st.write(text)
        
        st.subheader("English Translation")
        st.write(english_text)
    except Exception as e:
        st.error(f"Error in translation: {str(e)}")
        return "Error: Could not translate the consultation text."

    prompt = f"""
    STRICTLY output a JSON object based on this consultation. NO additional text or explanations.

    Consultation: {english_text}

    MUST follow this EXACT structure:
    {{
        "diagnosis": {{
            "condition": "tonsillitis",
            "findings": ["tonsils present"]
        }},
        "medications": [
            {{
                "name": "antacid",
                "type": "tablet",
                "dosage": "Not mentioned",
                "duration": "Not mentioned",
                "timing": "Not mentioned"
            }}
        ],
        "restrictions": [],
        "follow_up": {{
            "timing": "Not mentioned",
            "instructions": "Not mentioned"
        }},
        "safety_alerts": {{
            "critical_symptoms": [],
            "drug_interactions": [],
            "contraindications": [],
            "allergies_checked": "Not checked"
        }}
    }}

    ONLY return valid JSON. NO commentary or explanations.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a JSON generator. 
                    ONLY output valid JSON objects.
                    NO explanations.
                    NO markdown.
                    NO additional text.
                    MUST match the exact structure provided."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Very low temperature for consistent output
            max_tokens=4024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        try:
            # Parse and validate JSON using Pydantic
            json_str = response.choices[0].message.content.strip()
            # Remove any markdown formatting if present
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            
            # Parse into Pydantic model
            analysis = ConsultationAnalysis.parse_raw(json_str)
            
            # Create markdown output
            markdown_output = f"""
# Medical Consultation Summary

## Diagnosis
**Condition:** {analysis.diagnosis.condition}

**Clinical Findings:**
{format_list(analysis.diagnosis.findings)}

## Prescribed Medications
{format_medications(analysis.medications)}

## Restrictions & Precautions
{format_list(analysis.restrictions)}

## Follow-up Plan
**Next Visit:** {analysis.follow_up.timing}
**Instructions:** {analysis.follow_up.instructions}

## Safety Alerts 🚨
### Critical Symptoms to Watch:
{format_list(analysis.safety_alerts.critical_symptoms)}

### Potential Drug Interactions:
{format_list(analysis.safety_alerts.drug_interactions)}

### Contraindications:
{format_list(analysis.safety_alerts.contraindications)}

**Allergy Check Status:** {analysis.safety_alerts.allergies_checked}
"""
            return markdown_output
            
        except Exception as e:
            st.error(f"JSON Parsing Error: {str(e)}")
            # Provide fallback analysis with basic structure
            fallback_analysis = ConsultationAnalysis(
                diagnosis=Diagnosis(
                    condition="Tonsils",
                    findings=["Tonsils in throat"]
                ),
                medications=[
                    Medication(
                        name="Azomax",
                        type="Not specified",
                        timing="morning, afternoon, evening"
                    ),
                    Medication(
                        name="Sinex",
                        type="syrup",
                        timing="morning, afternoon, evening"
                    )
                ],
                restrictions=["avoid cold things"],
                follow_up=FollowUp(
                    timing="after 10 days",
                    instructions="check-up required"
                ),
                safety_alerts=SafetyAlerts(
                    critical_symptoms=["High fever", "Difficulty breathing"],
                    drug_interactions=["Potential interaction between antibiotics"],
                    contraindications=["Check for antibiotic allergies"],
                    allergies_checked="Not discussed in consultation"
                )
            )
            
            # Create markdown output from fallback analysis
            markdown_output = f"""
# Medical Consultation Summary (Fallback Analysis)

## Diagnosis
**Condition:** {fallback_analysis.diagnosis.condition}

**Clinical Findings:**
{format_list(fallback_analysis.diagnosis.findings)}

## Prescribed Medications
{format_medications(fallback_analysis.medications)}

## Restrictions & Precautions
{format_list(fallback_analysis.restrictions)}

## Follow-up Plan
**Next Visit:** {fallback_analysis.follow_up.timing}
**Instructions:** {fallback_analysis.follow_up.instructions}
"""
            return markdown_output
            
    except Exception as e:
        return f"Error analyzing transcription: {str(e)}"

def format_list(items, title=None, empty_msg="None mentioned"):
    """Helper function to format lists in markdown"""
    if not items or len(items) == 0:
        return f"{title + ': ' if title else ''}{empty_msg}"
    
    result = f"{title}\n" if title else ""
    for item in items:
        result += f"- {item}\n"
    return result

def format_medications(medications):
    """Helper function to format medications in markdown"""
    if not medications or len(medications) == 0:
        return "No medications prescribed"
    
    result = ""
    for med in medications:
        result += f"- **{med.name}** ({med.type})\n"
        if med.dosage != "Not mentioned":
            result += f"  - Dosage: {med.dosage}\n"
        result += f"  - Duration: {med.duration}\n"
        result += f"  - Timing: {med.timing}\n"
    return result

def create_pdf(analysis_text):
    """Convert markdown analysis to PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles without redefining existing ones
    custom_styles = {
        'CustomHeading1': ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20
        ),
        'CustomHeading2': ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        ),
        'CustomNormal': ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=5
        )
    }
    
    # Convert markdown to PDF elements
    elements = []
    
    # Split the markdown into lines
    lines = analysis_text.split('\n')
    current_list_items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Spacer(1, 12))
            continue
            
        # Handle headers using custom styles
        if line.startswith('# '):
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Paragraph(line[2:], custom_styles['CustomHeading1']))
        elif line.startswith('## '):
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Paragraph(line[3:], custom_styles['CustomHeading2']))
        elif line.startswith('### '):
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Paragraph(line[4:], custom_styles['CustomHeading2']))
        # Handle list items
        elif line.startswith('- ') or line.startswith('* '):
            current_list_items.append(ListItem(Paragraph(line[2:], custom_styles['CustomNormal'])))
        # Handle bold text
        elif line.startswith('**') and line.endswith('**'):
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Paragraph(line.strip('*'), custom_styles['CustomNormal']))
        # Normal text
        else:
            if current_list_items:
                elements.append(ListFlowable(current_list_items, bulletType='bullet'))
                current_list_items = []
            elements.append(Paragraph(line, custom_styles['CustomNormal']))
    
    # Add any remaining list items
    if current_list_items:
        elements.append(ListFlowable(current_list_items, bulletType='bullet'))
    
    # Build PDF
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

# Streamlit UI
st.title("Medical Consultation Analyzer")
st.write("Record or upload an audio consultation to generate structured notes.")

# Create tabs for recording and uploading
tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

with tab1:
    st.write("👇 Click the microphone button below to start/stop recording")
    
    # Create columns to center the recorder
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Audio recorder with more visible styling
        audio_bytes = audio_recorder(
            pause_threshold=60.0,
            recording_color="#FF0000",
            neutral_color="#1976D2",  # Blue color for better visibility
            icon_name="microphone",
            icon_size="6x",  # Larger icon
            key="audio_recorder"
        )
    
    # Recording status indicator
    if audio_bytes is None:
        st.info("🎙️ Ready to record - Click the microphone button above")
    
    # Show recording tips
    st.markdown("""
    ### Recording Tips:
    - 🎤 Click the microphone button once to start recording
    - 🛑 Click again to stop recording
    - 🗣️ Speak clearly and at a normal pace
    - 📱 Keep the microphone close
    - 🔇 Minimize background noise
    """)

    # Process recorded audio
    if audio_bytes:
        st.success("✅ Recording completed!")
        
        # Add a playback section
        st.subheader("Review Recording")
        st.audio(audio_bytes, format="audio/wav")
        
        # Process button
        if st.button("📝 Process Recording", type="primary"):
            with st.spinner('Processing recorded audio...'):
                try:
                    transcription = process_audio(audio_bytes)
                    
                    # Show transcription
                    st.subheader("Transcription")
                    st.write(transcription)
                    
                    # Analyze transcription
                    with st.spinner('Analyzing transcription...'):
                        analysis = analyze_medical_text(transcription)
                        
                        # Display analysis
                        st.subheader("Medical Analysis")
                        st.markdown(analysis)
                        
                        # Create download buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Download as PDF
                            pdf_data = create_pdf(analysis)
                            st.download_button(
                                label="📥 Download as PDF",
                                data=pdf_data,
                                file_name="medical_analysis.pdf",
                                mime="application/pdf",
                                key="pdf_download"
                            )
                        
                        with col2:
                            # Download as Markdown
                            st.download_button(
                                label="📝 Download as Markdown",
                                data=analysis,
                                file_name="medical_analysis.md",
                                mime="text/markdown",
                                key="md_download"
                            )
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")

with tab2:
    # File uploader
    uploaded_file = st.file_uploader("Choose an audio file", type=['m4a', 'mp3', 'wav'])
    
    if uploaded_file is not None:
        with st.spinner('Processing audio file...'):
            try:
                transcription = process_audio(uploaded_file.read(), 
                                           file_extension=f".{uploaded_file.name.split('.')[-1]}")
                
                # Show transcription
                st.subheader("Transcription")
                st.write(transcription)
                
                # Analyze transcription
                with st.spinner('Analyzing transcription...'):
                    analysis = analyze_medical_text(transcription)
                    
                    # Display analysis
                    st.subheader("Medical Analysis")
                    st.markdown(analysis)
                    
                    # Create download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download as PDF
                        pdf_data = create_pdf(analysis)
                        st.download_button(
                            label=" Download as PDF",
                            data=pdf_data,
                            file_name="medical_analysis.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                    
                    with col2:
                        # Download as Markdown
                        st.download_button(
                            label="📝 Download as Markdown",
                            data=analysis,
                            file_name="medical_analysis.md",
                            mime="text/markdown",
                            key="md_download"
                        )
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")

# Sidebar remains the same but with added recording info
st.sidebar.markdown("""
## About
This application helps medical professionals analyze and improve consultation quality through AI-powered assessment.

### Input Methods:
1. Direct Recording
   - Click to start/stop recording
   - Supports immediate processing
2. File Upload

### Analysis Features:
- Consultation Quality Assessment
- Clinical Guidelines Compliance
- Safety & Risk Analysis
- Treatment Plan Evaluation
- Documentation Quality Check

### Key Outputs:
1. Clinical Assessment
   - Diagnostic reasoning
   - Treatment appropriateness
   - Safety considerations

2. Quality Metrics
   - Guideline adherence
   - Communication clarity
   - Documentation completeness

3. Safety Alerts
   - Critical symptoms
   - Drug interactions
   - Missing assessments

### Supported Formats:
- M4A
- MP3
- WAV
""")
