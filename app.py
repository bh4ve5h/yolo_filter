import streamlit as st
from ultralytics import YOLO
import tempfile
import os
import subprocess
import shutil

st.set_page_config(page_title="YOLO Video Detection", layout="centered")

st.title("🎯 YOLOv8 Video Detection App")
st.markdown("Upload a video, run object detection, and download the result with original audio.")

# Load model once
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# Upload video
uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_video:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_video_path = os.path.join(tmpdir, "input_video.mp4")
        output_video_path = os.path.join(tmpdir, "output_detected.mp4")
        final_video_path = os.path.join(tmpdir, "final_output.mp4")

        # Save uploaded file
        with open(input_video_path, "wb") as f:
            f.write(uploaded_video.read())

        st.video(input_video_path)
        st.success("Video uploaded successfully!")

        if st.button("🚀 Run YOLO Detection"):
            with st.spinner("Running detection..."):
                model.predict(source=input_video_path, save=True, save_txt=False, project=tmpdir, name="yolo_output", exist_ok=True)

                # Get output video path from YOLO output
                detected_video_path = os.path.join(tmpdir, "yolo_output", "input_video.mp4")

                if not os.path.exists(detected_video_path):
                    st.error("Detection failed: Output video not found.")
                else:
                    # Extract audio from original
                    audio_path = os.path.join(tmpdir, "audio.aac")
                    subprocess.run(["ffmpeg", "-y", "-i", input_video_path, "-q:a", "0", "-map", "a", audio_path],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # Merge audio with detected video
                    subprocess.run(["ffmpeg", "-y", "-i", detected_video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", final_video_path],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    st.success("✅ Detection complete! Preview below:")
                    st.video(final_video_path)

                    # Download button
                    with open(final_video_path, "rb") as f:
                        st.download_button("📥 Download Final Video", f, file_name="yolo_output_with_audio.mp4", mime="video/mp4")
