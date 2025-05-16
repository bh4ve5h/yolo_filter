import streamlit as st
import os
import uuid
import shutil
import subprocess
from pathlib import Path

# --- Setup ---
st.set_page_config(page_title="Object Detection", layout="centered")
st.title("🎯 Object Detection")
st.markdown("1. Upload a video ⬆️\n2. Click '🚀 Run Detection'\n3. Download ⬇️")

# --- Clean old files ---
def clean_files():
    for f in os.listdir():
        if f.startswith(("input_", "output_")) and f.endswith((".mp4", ".mov", ".avi")):
            os.remove(f)
    shutil.rmtree("runs/detect", ignore_errors=True)

# --- Run detection and preserve audio ---
def run_detection(input_path, output_name):
    output_dir = f"detect_{uuid.uuid4().hex[:6]}"
    os.system(f"python detect.py --source '{input_path}' --conf 0.4 --name {output_dir} --exist-ok")

    detect_path = Path("runs/detect") / output_dir
    detected_video = next(detect_path.glob("*.mp4"), None)

    if detected_video:
        audio_file = f"temp_audio.aac"
        final_video = f"{output_name}"

        subprocess.run(f"ffmpeg -y -i '{input_path}' -vn -acodec copy '{audio_file}'", shell=True)
        subprocess.run(f"ffmpeg -y -i '{detected_video}' -i '{audio_file}' -c:v copy -c:a aac '{final_video}'", shell=True)

        os.remove(audio_file)
        return final_video
    return None

# --- Upload & Process ---
video = st.file_uploader("📤 Upload a video", type=["mp4", "mov", "avi"])

if video:
    clean_files()
    input_name = f"input_{uuid.uuid4().hex[:6]}_{video.name}"
    with open(input_name, "wb") as f:
        f.write(video.read())
    st.success(f"✅ Uploaded: {video.name}")

    if st.button("🚀 Run Detection"):
        with st.spinner("Let him cook... ⏳ this might take a bit, depending on your clip’s length and how spicy the content is."):
            output_name = f"output_{video.name}"
            result = run_detection(input_name, output_name)

            if result:
                st.success("Done ✅")
                with open(result, "rb") as f:
                    st.download_button("⬇️ Download Output", f, file_name=output_name, mime="video/mp4")
            else:
                st.error("⚠️ No output video found.")
