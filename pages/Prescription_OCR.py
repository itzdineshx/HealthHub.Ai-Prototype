# pages/Prescription_OCR.py

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import os
import sys

# Add parent directory to path to ensure module imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.theme import apply_theme

# Apply dark theme with page config
apply_theme("📄 Prescription OCR", set_page=True)

# Page content
st.markdown("""
<div class="card fade-in">
    <h3>Medical Prescription OCR</h3>
    <p>Upload an image of your prescription to extract the text. This tool helps you digitize handwritten or printed prescriptions for easier storage and reference.</p>
</div>
""", unsafe_allow_html=True)

# Check if required packages are installed
try:
    import pytesseract
    tesseract_installed = True
except ImportError:
    tesseract_installed = False

try:
    import pdf2image
    pdf_support = True
except ImportError:
    pdf_support = False

# Display warning if requirements aren't met
if not tesseract_installed:
    st.warning("""
        📦 **Tesseract OCR not found**. This feature requires Tesseract OCR to be installed.
        
        Installation steps:
        1. Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
        2. Run `pip install pytesseract`
        
        Demo mode activated with pre-generated results.
    """)
    # We'll proceed with mock data if Tesseract isn't installed

if not pdf_support and tesseract_installed:
    st.info("📄 PDF support is not available. Install pdf2image package for PDF processing.")

# Set up Tesseract path - with better error handling
tesseract_path = None
if tesseract_installed:
    if os.name == 'nt':  # Windows
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for path in common_paths:
            if os.path.exists(path):
                tesseract_path = path
                break
        
        # Only set path if found
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            st.warning("⚠️ Tesseract installation not found in common locations. Using system PATH.")

# Tips for better results
st.markdown("""
<div class="card">
    <h4>💡 Tips for Better Results</h4>
    <ul>
        <li>Use clear, well-lit images with good contrast</li>
        <li>Ensure the text is focused and not blurry</li>
        <li>Crop the image to include only the prescription</li>
        <li>Capture the image directly from above to avoid distortion</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload a prescription image", type=['jpg', 'jpeg', 'png', 'pdf'])

# Function to safely extract text using OCR
def extract_text_safely(image):
    if not tesseract_installed:
        # Return mock data if Tesseract isn't installed
        return """
        PRESCRIPTION
        
        Patient: John Doe
        Date: 06/15/2023
        
        Rx:
        Amoxicillin 500mg
        Take 1 tablet by mouth three times daily for 10 days
        
        Ibuprofen 200mg
        Take 2 tablets by mouth every 6 hours as needed for pain
        
        Refills: 0
        
        Dr. Jane Smith, MD
        License: 12345
        """
    
    try:
        # Extract text using pytesseract with error handling
        custom_config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(image, config=custom_config)
    except Exception as e:
        st.error(f"Text extraction failed: {str(e)}")
        return "Error extracting text. Please try a different image or adjust processing options."

# Image processing options
if uploaded_file is not None:
    try:
        # Process different file types
        if uploaded_file.name.lower().endswith('.pdf'):
            if pdf_support:
                # Convert first PDF page to image
                with st.spinner("Converting PDF to image..."):
                    try:
                        pdf_pages = pdf2image.convert_from_bytes(uploaded_file.read())
                        if pdf_pages:
                            image = pdf_pages[0]  # Take first page
                            st.markdown("### PDF Preview (First Page)")
                            st.image(image, width=400)
                        else:
                            st.error("Could not read PDF pages. The file may be corrupted or empty.")
                            st.stop()
                    except Exception as e:
                        st.error(f"PDF conversion failed: {str(e)}")
                        st.stop()
            else:
                st.error("PDF processing requires the pdf2image package. Please install it and try again.")
                st.stop()
        else:
            # Regular image file
            try:
                # Display original image
                st.markdown("### Original Image")
                image = Image.open(uploaded_file)
                st.image(image, width=400)
            except Exception as e:
                st.error(f"Failed to open image: {str(e)}")
                st.info("Make sure the file is a valid image format (JPG, JPEG, PNG).")
                st.stop()
        
        # Image processing options in an expander
        with st.expander("Image Processing Options (optional)"):
            st.markdown("Adjust these settings if the text extraction isn't accurate enough")
            
            # Image preprocessing options
            col1, col2 = st.columns(2)
            
            with col1:
                grayscale = st.checkbox("Convert to grayscale", value=True)
                threshold = st.checkbox("Apply threshold", value=True)
                
            with col2:
                denoise = st.checkbox("Reduce noise", value=False)
                thresh_value = st.slider("Threshold value", 0, 255, 127) if threshold else 127
        
        # Process button
        if st.button("Extract Text from Prescription", use_container_width=True):
            with st.spinner("Processing image and extracting text..."):
                try:
                    # Convert the PIL Image to OpenCV format
                    img = np.array(image)
                    
                    # Apply preprocessing based on options selected
                    if grayscale and len(img.shape) == 3:  # Check if image is color
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                    
                    if denoise and len(img.shape) == 2:
                        img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
                        
                    if threshold and len(img.shape) == 2:  # Check if image is grayscale
                        _, img = cv2.threshold(img, thresh_value, 255, cv2.THRESH_BINARY)
                    
                    # Display the processed image
                    st.markdown("### Processed Image")
                    st.image(img, width=400)
                    
                    # Extract text safely
                    extracted_text = extract_text_safely(img)
                    
                    # Display the extracted text
                    st.markdown("### Extracted Text")
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.text_area("Extracted prescription text", value=extracted_text, height=250, key="extracted", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Process and display medication information
                    st.markdown("### Detected Medication Information")
                    
                    # Split text into lines for analysis
                    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                    
                    if not lines:
                        st.info("No medication information detected. Try adjusting the image processing options.")
                    else:
                        # Simple heuristics to identify medication-related information
                        medications = []
                        keywords = ['mg', 'tablet', 'capsule', 'take', 'dose', 'daily', 
                                   'twice', 'once', 'every', 'hours', 'days', 'prescription',
                                   'refill', 'medication', 'rx', 'medicine']
                        
                        for line in lines:
                            if any(word in line.lower() for word in keywords):
                                medications.append(line)
                        
                        if medications:
                            # Create a styled table for medications
                            med_table = "<table class='styled-table'><thead><tr><th>Medication Information</th></tr></thead><tbody>"
                            for med in medications:
                                med_table += f"<tr><td>{med}</td></tr>"
                            med_table += "</tbody></table>"
                            
                            st.markdown(med_table, unsafe_allow_html=True)
                        else:
                            st.info("No specific medication information detected. The text may still contain relevant data.")
                    
                    # Provide download option for the extracted text
                    text_bytes = extracted_text.encode()
                    st.download_button(
                        label="Download Extracted Text",
                        data=io.BytesIO(text_bytes),
                        file_name="prescription_text.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.info("Try using a clearer image or adjusting the processing options.")
    
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please try a different file or a simpler image.")

# Add sample prescription button
with st.expander("No prescription to upload? Try a sample"):
    if st.button("Load Sample Prescription"):
        # Use a sample prescription image
        sample_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_prescription.jpg")
        
        # Check if sample exists, otherwise use an external URL
        if os.path.exists(sample_path):
            sample_image = Image.open(sample_path)
        else:
            # Use a placeholder image if sample isn't found
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a sample prescription image
            sample_image = Image.new('RGB', (800, 600), color=(255, 255, 255))
            d = ImageDraw.Draw(sample_image)
            
            # Add text to the image
            d.text((50, 50), "SAMPLE PRESCRIPTION", fill=(0, 0, 0))
            d.text((50, 100), "Patient: John Doe", fill=(0, 0, 0))
            d.text((50, 130), "Date: 06/15/2023", fill=(0, 0, 0))
            d.text((50, 180), "Rx:", fill=(0, 0, 0))
            d.text((70, 220), "Amoxicillin 500mg", fill=(0, 0, 0))
            d.text((70, 250), "Take 1 tablet by mouth three times daily for 10 days", fill=(0, 0, 0))
            d.text((70, 300), "Ibuprofen 200mg", fill=(0, 0, 0))
            d.text((70, 330), "Take 2 tablets by mouth every 6 hours as needed for pain", fill=(0, 0, 0))
            d.text((50, 400), "Refills: 0", fill=(0, 0, 0))
            d.text((50, 500), "Dr. Jane Smith, MD", fill=(0, 0, 0))
            d.text((50, 530), "License: 12345", fill=(0, 0, 0))
        
        # Display the sample
        st.markdown("### Sample Prescription")
        st.image(sample_image, width=400)
        
        # Extract text from the sample
        if tesseract_installed:
            with st.spinner("Processing sample image..."):
                extracted_text = extract_text_safely(np.array(sample_image))
                
                # Display the extracted text
                st.markdown("### Extracted Text")
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.text_area("Sample extracted text", value=extracted_text, height=250, key="sample_text", label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show mock data
            mock_text = """
            SAMPLE PRESCRIPTION
            
            Patient: John Doe
            Date: 06/15/2023
            
            Rx:
            Amoxicillin 500mg
            Take 1 tablet by mouth three times daily for 10 days
            
            Ibuprofen 200mg
            Take 2 tablets by mouth every 6 hours as needed for pain
            
            Refills: 0
            
            Dr. Jane Smith, MD
            License: 12345
            """
            
            st.markdown("### Extracted Text (Sample)")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.text_area("Mock prescription text", value=mock_text, height=250, key="mock_text", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

# Information about privacy
st.markdown("""
<div class="card fade-in" style="margin-top: 2rem;">
    <h4>🔒 Privacy Information</h4>
    <p>
        Your prescription images are processed securely within this application and are not stored permanently.
        The extracted text is not shared with any third parties, and all uploaded data is discarded when you close
        this application or upload a new image.
    </p>
</div>
""", unsafe_allow_html=True)

# Add information about verification
st.markdown("""
<div class="card fade-in">
    <h4>⚠️ Important Notice</h4>
    <p>
        The extracted text may contain errors. Always verify the information with your original prescription
        and consult with your healthcare provider or pharmacist if you have any questions about your medication.
    </p>
</div>
""", unsafe_allow_html=True)
