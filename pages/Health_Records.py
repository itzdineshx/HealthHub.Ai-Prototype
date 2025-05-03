# pages/7_Health_Records.py

import streamlit as st
from utils.blockchain import store_hash, fetch_records
import tempfile
import os
import sys
from datetime import datetime

# Import our theme first, before any other Streamlit commands
from utils.theme import apply_theme, card, badge, styled_table

# Set page config through the theme function
apply_theme("🔐 Health Records", set_page=True)

intro_text = """
Securely store and manage your health documents with blockchain verification. 
Your records are encrypted and immutable, giving you peace of mind about their authenticity and privacy.
"""

st.markdown(f"<div class='fade-in'>{intro_text}</div>", unsafe_allow_html=True)

# Check if mock mode is enabled
mock_mode = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")
if mock_mode:
    st.info("⚠️ Running in mock mode - blockchain transactions are simulated for demonstration purposes")

# Use tabs for better organization
tab1, tab2 = st.tabs(["My Records", "Upload New Record"])

with tab1:
    # Records View
    with st.container():
        st.markdown("""
        <div class="card fade-in">
            <h3>My Health Records</h3>
            <p>View and manage your secure health documents</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Load records with spinner for better UX
        with st.spinner("Loading your records..."):
            recs = fetch_records(user_id=st.session_state.get("user_id", "current_user"))
        
        if recs:
            st.success(f"Found {len(recs)} records in your health vault")
            
            # Records filter options
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown("#### Filter by:")
                
            # Table view of records
            st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
            
            record_data = []
            for r in recs:
                # Format date from timestamp if available
                try:
                    if isinstance(r.get('timestamp'), str):
                        date_str = r.get('timestamp', '').split('T')[0]
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%b %d, %Y')
                    else:
                        formatted_date = "Unknown date"
                except:
                    formatted_date = "Unknown date"
                
                # Create record data entry
                record_data.append({
                    "Date": formatted_date,
                    "File": r['filename'],
                    "Status": "Verified" if r.get('tx_hash') else "Pending",
                    "Type": r['filename'].split('.')[-1].upper(),
                    "Details": f"<a href='#' onclick=\"alert('Viewing record: {r['filename']}');\">View</a>"
                })
            
            # Display the styled table
            st.markdown(
                styled_table(
                    record_data, 
                    ["Date", "File", "Status", "Type", "Details"]
                ),
                unsafe_allow_html=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Detailed record viewer
            st.markdown("<div class='card fade-in'>", unsafe_allow_html=True)
            st.subheader("Record Details")
            
            selected_record = st.selectbox(
                "Select a record to view details", 
                options=[r['filename'] for r in recs],
                key="record_selector"
            )
            
            # Find the selected record
            selected_data = next((r for r in recs if r['filename'] == selected_record), None)
            
            if selected_data:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**File:** {selected_data['filename']}")
                    st.markdown(f"**Hash:** `{selected_data['file_hash']}`")
                    st.markdown(f"**Transaction:** `{selected_data['tx_hash'][:10]}...{selected_data['tx_hash'][-8:]}`")
                    st.markdown(f"**Block Number:** {selected_data['block_number']}")
                    
                    # Add verification link for non-mock mode
                    if not mock_mode and selected_data.get('tx_hash'):
                        tx_hash = selected_data['tx_hash']
                        etherscan_url = f"https://etherscan.io/tx/{tx_hash}"
                        st.markdown(f"[🔍 Verify on Etherscan]({etherscan_url})")
                
                with col2:
                    # Add visual verification badge
                    st.markdown("""
                    <div style="text-align: center; margin-top: 1rem;">
                        <div style="font-size: 4rem; color: #3E885B;">✓</div>
                        <div style="font-weight: bold; color: #3E885B;">Blockchain Verified</div>
                        <div style="color: var(--muted-color); font-size: 0.9rem;">This record has been verified on the blockchain</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            # Empty state with guidance
            st.warning("No records found in your health vault")
            
            st.markdown("""
            <div class="card fade-in" style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem;">📄</div>
                <h3>Your Health Vault is Empty</h3>
                <p>Upload your first health record using the "Upload New Record" tab above to get started.</p>
                <p>You can securely store:</p>
                <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">🏥</div>
                        <div>Medical Reports</div>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">💉</div>
                        <div>Lab Results</div>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">💊</div>
                        <div>Prescriptions</div>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">💉</div>
                        <div>Vaccination Records</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    # Upload View
    st.markdown("""
    <div class="card fade-in">
        <h3>Upload Health Record</h3>
        <p>Add a new document to your secure health vault</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Enhanced file upload section
        st.markdown("""
        <div style="border: 2px dashed #ccc; padding: 2rem; text-align: center; border-radius: 10px; margin-bottom: 1rem;">
            <div style="font-size: 3rem; color: var(--primary-color);">📄</div>
            <h3>Drag & Drop Files Here</h3>
            <p>or click to browse for files</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload widget
        rpt = st.file_uploader(
            "Upload your health report", 
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"], 
            label_visibility="collapsed"
        )
        
        # Display uploaded file
        if rpt:
            file_size_kb = rpt.size / 1024
            
            st.success(f"File uploaded: {rpt.name} ({file_size_kb:.1f} KB)")
            
            # Preview for images
            if rpt.type.startswith('image/'):
                st.image(rpt, caption=rpt.name, width=400)
            elif rpt.type == 'application/pdf':
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 1rem; background-color: #f8f9fa; border-radius: 5px;">
                    <div style="font-size: 2rem; color: #d00;">📄</div>
                    <div>
                        <div style="font-weight: bold;">{rpt.name}</div>
                        <div style="color: var(--muted-color); font-size: 0.8rem;">PDF Document • {file_size_kb:.1f} KB</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 1rem; background-color: #f8f9fa; border-radius: 5px;">
                    <div style="font-size: 2rem;">📄</div>
                    <div>
                        <div style="font-weight: bold;">{rpt.name}</div>
                        <div style="color: var(--muted-color); font-size: 0.8rem;">Document • {file_size_kb:.1f} KB</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card fade-in">
            <h4>Record Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        record_type = st.selectbox(
            "Record Type", 
            ["Medical Report", "Lab Results", "Prescription", "Vaccination", "Insurance", "Other"]
        )
        
        doctor = st.text_input("Provider/Doctor Name (optional)")
        
        date = st.date_input("Record Date", max_value=datetime.now())
        
        notes = st.text_area("Notes (optional)", placeholder="Add any additional information about this record")
    
    # Upload action
    if rpt:
        upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
        
        with upload_col2:
            if st.button("Secure & Store On Blockchain", use_container_width=True):
                # Processing with better visual feedback
                with st.status("Processing your health record...") as status:
                    st.write("Computing document hash...")
                    st.progress(0.3)
                    
                    st.write("Sending to blockchain...")
                    st.progress(0.6)
                    
                    try:
                        # Save file to temp location for processing
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{rpt.name}") as tmp:
                            tmp.write(rpt.getvalue())
                            tmp_path = tmp.name
                        
                        # Get metadata
                        metadata = {
                            "filename": rpt.name,
                            "type": record_type,
                            "provider": doctor,
                            "date": str(date),
                            "notes": notes,
                            "timestamp": datetime.now().isoformat(),
                            "user_id": st.session_state.get("user_id", "current_user")
                        }
                        
                        # Store record hash with metadata
                        result = store_hash(tmp_path, metadata)
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        st.progress(1.0)
                        status.update(label="✅ Record uploaded successfully!", state="complete")
                        
                        # Display transaction result
                        st.success("Your health record has been securely stored!")
                        
                        if not mock_mode and result.get('tx_hash'):
                            st.markdown(f"""
                            <div class="card fade-in">
                                <h4>Blockchain Transaction Details</h4>
                                <p><strong>Transaction Hash:</strong> <code>{result['tx_hash']}</code></p>
                                <p><strong>Block Number:</strong> {result['block_number']}</p>
                                <p><a href="https://etherscan.io/tx/{result['tx_hash']}" target="_blank">View on Etherscan</a></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        status.update(label="❌ Upload failed", state="error")
                        st.error(f"Error processing your document: {str(e)}")
                        
                        # Offer troubleshooting help
                        st.markdown("""
                        <div class="card">
                            <h4>Troubleshooting</h4>
                            <ul>
                                <li>Check that your file is not corrupted</li>
                                <li>Try a smaller file size (under 10MB)</li>
                                <li>Make sure your file type is supported</li>
                                <li>Check your internet connection</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

# Information about privacy
st.markdown("""
<div class="card fade-in" style="margin-top: 2rem;">
    <h4>🔒 Privacy Information</h4>
    <p>
        Your health records are encrypted and stored securely. Only the hash (digital fingerprint) of your document
        is stored on the blockchain, not the actual content. This ensures the authenticity of your records
        while maintaining privacy.
    </p>
</div>
""", unsafe_allow_html=True)
