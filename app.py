import streamlit as st
import os
import uuid
import shutil
import subprocess
from pathlib import Path

st.set_page_config(page_title="YOLOv5 Video Detection", layout="centered")
st.title("🎯 YOLOv5 Video Detection App")
st.markdown("Upload a video ⬆️ → Run detection 🚀 → Download result with audio ⬇️")

# --- Clean old runs ---
def clean_runs():
    for f in os.listdir():
        if f.startswith(("input_", "output_")) and f.endswith((".mp4", ".mov", ".avi")):
            os.remove(f)
    shutil.rmtree("runs/detect", ignore_errors=True)

# --- Run detection and merge audio ---
def run_yolov5_detection(input_video_path, output_name):
    run_id = f"detect_{uuid.uuid4().hex[:6]}"
    os.system(f"python detect.py --source \"{input_video_path}\" --conf 0.3 --name {run_id} --exist-ok")

    detect_dir = Path("runs/detect") / run_id
    detected_video = next(detect_dir.glob("*.mp4"), None)

    if detected_video:
        audio_path = f"temp_audio.aac"
        final_output = f"{output_name}"

        # Extract audio from original
        subprocess.run(
            f"ffmpeg -y -i \"{input_video_path}\" -vn -acodec copy \"{audio_path}\"",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # Merge audio into detected video
        subprocess.run(
            f"ffmpeg -y -i \"{detected_video}\" -i \"{audio_path}\" -c:v copy -c:a aac -strict experimental \"{final_output}\"",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        os.remove(audio_path)
        return final_output
    return None

# --- Streamlit App ---
video_file = st.file_uploader("📤 Upload a video", type=["mp4", "avi", "mov"])

if video_file:
    clean_runs()

    unique_name = f"input_{uuid.uuid4().hex[:6]}_{video_file.name}"
    with open(unique_name, "wb") as f:
        f.write(video_file.read())

    st.success(f"✅ Uploaded: {video_file.name}")

    if st.button("🚀 Run YOLOv5 Detection"):
        with st.spinner("Detecting objects…"):
            output_name = f"output_{video_file.name}"
            final_video = run_yolov5_detection(unique_name, output_name)

            if final_video and os.path.exists(final_video):
                st.success("✅ Done! Download your video below:")
                with open(final_video, "rb") as f:
                    st.download_button("⬇️ Download Output", f, file_name=output_name, mime="video/mp4")
            else:
                st.error("❌ No output video found. Make sure your model is working and video contains detectable content.")
