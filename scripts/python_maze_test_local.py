import cv2
import pandas as pd
import numpy as np
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# --- Set up paths ---
base_dir = Path(__file__).resolve().parents[1]
video_folder = base_dir / 'videos'
output_folder = base_dir / 'video_results'
os.makedirs(output_folder, exist_ok=True)

video_extensions = ['.mp4', '.mov']
combined_output_path = output_folder / "combined_analysis.csv"

# --- Video processing function ---
def process_video(file_path):
    filename = file_path.name
    video_path = str(file_path)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps <= 0:
        cap.release()
        return None  # Skip invalid videos

    positions = []
    frame_idx = 0
    fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % 10 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fgmask = fgbg.apply(gray)
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 500:
                    x, y, w, h = cv2.boundingRect(largest)
                    center_x, center_y = x + w // 2, y + h // 2
                    positions.append((frame_idx / fps, center_x, center_y))

        frame_idx += 1

    cap.release()

    if len(positions) <= 1:
        return None  # Not enough motion to analyze

    # Create DataFrame of frame-level metrics
    df = pd.DataFrame(positions, columns=["Time (s)", "X", "Y"])
    df['DeltaX'] = df['X'].diff()
    df['DeltaY'] = df['Y'].diff()
    df['Distance'] = np.sqrt(df['DeltaX']**2 + df['DeltaY']**2)
    df['Time Delta (s)'] = df['Time (s)'].diff()
    df['Speed (pixels/sec)'] = df['Distance'] / df['Time Delta (s)']
    df['Direction Change'] = df[['DeltaX', 'DeltaY']].diff().pow(2).sum(axis=1).pow(0.5)
    df['Preemptive Navigation'] = df['Direction Change'].between(20, 200)
    df['Reactive Turn'] = df['Direction Change'] > 300
    df['Disoriented Circling'] = (df['Speed (pixels/sec)'] < 100) & (df['Direction Change'] > 100)

    # Aggregate per video
    preemptive_total = df['Preemptive Navigation'].sum()
    reactive_total = df['Reactive Turn'].sum()
    circling_total = df['Disoriented Circling'].sum()
    mean_speed = df['Speed (pixels/sec)'].mean()

    # Recalibrated classification thresholds
    if preemptive_total >= 15 and reactive_total <= 20:
        visual_status = 'Visual'
    elif preemptive_total >= 8:
        visual_status = 'Visually Impaired'
    else:
        visual_status = 'Blind'

    return {
        'File Name': filename,
        'Preemptive Navigation': int(preemptive_total),
        'Reactive Turn': int(reactive_total),
        'Disoriented Circling': int(circling_total),
        'Mean Speed (pixels/sec)': mean_speed,
        'Visual Status': visual_status
    }

# --- Get all valid video files ---
video_files = [f for f in video_folder.iterdir() if f.suffix.lower() in video_extensions]

# --- Process videos in parallel ---
all_results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_video, video_files))
    all_results = [r for r in results if r is not None]  # Remove skipped videos

# --- Save one-row-per-video summary ---
if all_results:
    combined_df = pd.DataFrame(all_results)
    combined_df.to_csv(combined_output_path, index=False)
    print(f"Summary saved to {combined_output_path}")

