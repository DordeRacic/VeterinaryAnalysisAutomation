import streamlit as st
import cv2
import pandas as pd
import numpy as np
import tempfile
import os

st.title("Canine Visual Navigation Analyzer")
st.write("Upload a video of your dog navigating an obstacle course to analyze visual behavior.")

uploaded_file = st.file_uploader("Choose a .mp4 or .mov file", type=["mp4", "mov"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # --- ANALYSIS ---
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0

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

    if len(positions) > 1:
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

        preemptive = df['Preemptive Navigation'].sum()
        reactive = df['Reactive Turn'].sum()
        circling = df['Disoriented Circling'].sum()

        if preemptive >= 10 and reactive <= 15:
            visual_status = 'Visual'
        elif preemptive >= 5:
            visual_status = 'Visually Impaired'
        else:
            visual_status = 'Blind'

        st.subheader("Behavioral Summary")
        st.write(f"Mean Speed: {df['Speed (pixels/sec)'].mean():.1f} px/sec")
        st.write(f"Preemptive Navigations: {int(preemptive)}")
        st.write(f"Reactive Turns: {int(reactive)}")
        st.write(f"Disoriented Circling Events: {int(circling)}")
        st.success(f"Predicted Visual Status: **{visual_status}**")

        st.subheader("Raw Data Table")
        st.dataframe(df[['Time (s)', 'X', 'Y', 'Speed (pixels/sec)', 'Preemptive Navigation', 'Reactive Turn', 'Disoriented Circling']])
    else:
        st.error("Not enough motion detected to analyze behavior.")