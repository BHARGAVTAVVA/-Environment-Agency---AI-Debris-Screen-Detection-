# minimal_app.py - UPDATED VERSION WITH EMAIL ALERTS
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="Water Blockage Detection", layout="centered")

# ============================================
# HARDCODED CONFIGURATION
# ============================================
CONFIDENCE_THRESHOLD = 0.25  # Fixed confidence threshold
EMAIL_ALERTS_ENABLED = True  # Always enable email alerts
MODEL_PATH = "D:/Bhargav/Bhargav/best.pt"

# Email configuration - HARDCODED
EMAIL_CONFIG = {
    'sender': 'enviromentalagencyalerts181@gmail.com',
    'receivers': [
        'vigneshgoudk24@gmail.com',
        'reddysir4321@gmail.com',
        'bhargavtavva1310@s.com',
        'shashe99@gmail.com'
    ],
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'app_password': 'ascj qgzs opja rjxn'  # Hardcoded app password
}

def send_blockage_alert(image_filename, blocked_count, detection_details):
    """Send email alert when blockages are detected"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender']
        msg['To'] = ', '.join(EMAIL_CONFIG['receivers'])
        msg['Subject'] = f"🚨 URGENT: Water Blockage Detected ({blocked_count} blockages)"
        
        # Create email body
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #d9534f;">🚨 WATER BLOCKAGE ALERT</h2>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 5px solid #d9534f;">
                <h3>⚠️ Immediate Attention Required</h3>
                <p><strong>Time:</strong> {current_time}</p>
                <p><strong>Image File:</strong> {image_filename}</p>
                <p><strong>Blockages Detected:</strong> {blocked_count}</p>
                <p><strong>Status:</strong> <span style="color: #d9534f; font-weight: bold;">CRITICAL</span></p>
            </div>
            
            <div style="margin-top: 20px;">
                <h3>📋 Detection Details:</h3>
                <ul>
        """
        
        for i, det in enumerate(detection_details, 1):
            if det['Class'] == 'Blocked':
                body += f"<li><strong>#{i}: BLOCKED</strong> - Confidence: {det['Confidence']} - BBox: {det['BBox']}</li>"
        
        body += f"""
                </ul>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #e7f3fe; border-radius: 5px;">
                <h3>📞 Required Actions:</h3>
                <ol>
                    <li>Inspect the detected blockage locations immediately</li>
                    <li>Clear any obstructions in water flow</li>
                    <li>Check for related infrastructure damage</li>
                    <li>Document the issue and resolution</li>
                </ol>
            </div>
            
            <div style="margin-top: 30px; font-size: 12px; color: #666;">
                <p>This is an automated alert from the Water Flow Blockage Detection System.</p>
                <p>🚰 Environmental Agency Monitoring System</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['app_password'])
            server.send_message(msg)
            
        return True
    except Exception as e:
        st.error(f"❌ Email alert failed: {str(e)}")
        return False

st.title("🚰 Water Flow Blockage Detection")
st.markdown("Upload an image to detect blockages in water flow systems")

# File uploader with all image types
uploaded_file = st.file_uploader(
    "Upload Image", 
    type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
    help="Upload any image file (JPG, PNG, BMP, TIFF, WebP)"
)

if uploaded_file is not None:
    try:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Original Image")
            
            # Get file size in MB
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            # Load and display image
            image = Image.open(uploaded_file)
            
            # Show file info
            st.info(f"📄 **File:** {uploaded_file.name}")
            st.info(f"📏 **Size:** {file_size_mb:.2f} MB")
            st.info(f"🖼️ **Dimensions:** {image.size[0]}x{image.size[1]}")
            st.info(f"🎨 **Format:** {image.format if image.format else 'Unknown'}")
            
            # Check for large images
            if file_size_mb > 10:
                st.warning("⚠️ Large file detected. Processing may take longer.")
            
            # Convert image to RGB if needed
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    rgb_image.paste(image, mask=image.split()[3])
                else:
                    rgb_image.paste(image)
                image = rgb_image
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if image is too large
            max_size = 1920
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                st.warning(f"🔄 Image resized to {new_size[0]}x{new_size[1]} for processing")
            
            st.image(image, caption="Original Image", use_column_width=True)
        
        with col2:
            st.subheader("🔍 Detection Results")
            
            if st.button("🚀 Detect Blockages", type="primary", use_container_width=True):
                with st.spinner("🔬 Analyzing image for blockages..."):
                    try:
                        # Load model
                        model = YOLO(MODEL_PATH)
                        
                        # Convert to numpy array
                        img_array = np.array(image)
                        
                        # Predict with fixed confidence threshold
                        results = model.predict(img_array, conf=CONFIDENCE_THRESHOLD, verbose=False)
                        
                        # Initialize counters
                        detections = []
                        blocked_count = 0
                        unblocked_count = 0
                        other_count = 0
                        blocked_detections = []  # Store only blocked detections for email
                        
                        for r in results:
                            if len(r.boxes) > 0:
                                # Get annotated image
                                result_img = r.plot()
                                result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
                                
                                # Display detected image
                                st.image(result_img, caption="Detection Results", use_column_width=True)
                                
                                # Count detections by class
                                for box in r.boxes:
                                    cls = int(box.cls[0])
                                    conf = float(box.conf[0])
                                    class_names = ['Blocked', 'Unblocked', 'Other']
                                    
                                    detection_info = {
                                        'Class': class_names[cls],
                                        'Confidence': f"{conf:.2f}",
                                        'BBox': f"[{int(box.xyxy[0][0])}, {int(box.xyxy[0][1])}, {int(box.xyxy[0][2])}, {int(box.xyxy[0][3])}]"
                                    }
                                    
                                    if cls == 0:
                                        blocked_count += 1
                                        blocked_detections.append(detection_info)
                                    elif cls == 1:
                                        unblocked_count += 1
                                    else:
                                        other_count += 1
                                    
                                    detections.append(detection_info)
                                
                                # Show summary statistics
                                st.success(f"✅ Found {len(detections)} object(s)")
                                
                                # Display metrics
                                metric_cols = st.columns(3)
                                with metric_cols[0]:
                                    if blocked_count > 0:
                                        st.error(f"🚨 **Blocked:** {blocked_count}")
                                    else:
                                        st.success(f"✅ **Blocked:** {blocked_count}")
                                
                                with metric_cols[1]:
                                    st.info(f"🟢 **Unblocked:** {unblocked_count}")
                                
                                with metric_cols[2]:
                                    st.info(f"🔵 **Other:** {other_count}")
                                
                                # Show detailed detections
                                if detections:
                                    st.subheader("📋 Detection Details")
                                    for i, det in enumerate(detections, 1):
                                        if det['Class'] == 'Blocked':
                                            st.error(f"{i}. {det['Class']} - Confidence: {det['Confidence']}")
                                        else:
                                            st.write(f"{i}. {det['Class']} - Confidence: {det['Confidence']}")
                                
                                # Final warning if blockages found
                                if blocked_count > 0:
                                    st.error(f"⚠️ **WARNING:** {blocked_count} blockage(s) detected! Immediate attention required.")
                                    #st.balloons()  # Visual alert
                                    
                                    # Send email alert (always enabled)
                                    if EMAIL_ALERTS_ENABLED:
                                        email_sent = False
                                        with st.spinner("📧 Sending email alerts..."):
                                            email_sent = send_blockage_alert(
                                                uploaded_file.name, 
                                                blocked_count, 
                                                blocked_detections
                                            )
                                        
                                        if email_sent:
                                            st.success(f"✅ Email alerts sent to {len(EMAIL_CONFIG['receivers'])} recipients")
                                            st.info("📧 Check your inbox for alert emails")
                                        else:
                                            st.warning("⚠️ Email alerts could not be sent.")
                                else:
                                    st.success("🎉 **ALL CLEAR:** No blockages detected. Water flow is normal.")
                                
                            else:
                                st.image(image, caption="No Objects Detected", use_column_width=True)
                                st.info("🔍 No objects detected.")
                        
                    except Exception as e:
                        st.error(f"❌ Error during detection: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Error loading image: {str(e)}")
        st.info("Try uploading a different image format (JPG recommended).")

else:
    # Show instructions when no file uploaded
    st.info("👆 Please upload an image file to begin detection")
    
    # Display system configuration
    st.markdown("### ⚙️ System Configuration (Hardcoded)")
    
    config_cols = st.columns(2)
    with config_cols[0]:
        st.info(f"**Confidence Threshold:** {CONFIDENCE_THRESHOLD}")
        st.info(f"**Email Alerts:** {'✅ ENABLED' if EMAIL_ALERTS_ENABLED else '❌ DISABLED'}")
        st.info(f"**Model Path:** {MODEL_PATH}")
    
    with config_cols[1]:
        st.info(f"**Email Recipients:** {len(EMAIL_CONFIG['receivers'])}")
        st.info(f"**SMTP Server:** {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
    
    # How to use section
    st.markdown("### 📝 How to use:")
    st.markdown("""
    1. Click **"Browse files"** or drag & drop an image
    2. Click **"Detect Blockages"** button
    3. View results and detection details
    
    **⚠️ Automatic Email Alerts:**
    - When blockages are detected, alerts are automatically sent to all recipients
    - No manual configuration needed
    
    **Detection Classes:**
    - 🟥 **Blocked** - Obstructed flow
    - 🟩 **Unblocked** - Normal flow
    - 🟦 **Other** - Other objects
    
    **Supported formats:** JPG, JPEG, PNG, BMP, TIFF, WebP
    **Max recommended size:** 20MB
    """)
    
    # Email recipients
    with st.expander("📧 Email Configuration"):
        st.markdown(f"**Sender:** `{EMAIL_CONFIG['sender']}`")
        st.markdown("**Recipients:**")
        for receiver in EMAIL_CONFIG['receivers']:
            st.text(f"• {receiver}")
        st.markdown(f"**SMTP:** `{EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}`")

# Footer
st.markdown("---")
st.markdown("🚰 **Water Flow Blockage Detection System** | Powered by YOLOv8 | 📧 Email Alerts: ALWAYS ON")