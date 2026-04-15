# Gesture
This project implements a real-time gesture-controlled cursor system using computer vision. It uses MediaPipe (built on TensorFlow Lite) for hand tracking and OpenCV for video processing.  The system detects hand landmarks and maps finger movements to mouse actions such as cursor movement, clicking, and scrolling using PyAutoGUI.
# 🖐️ Gesture Controlled Cursor using Computer Vision

A real-time gesture-based cursor control system built using Python, OpenCV, and MediaPipe. This project enables users to control the mouse cursor using hand gestures captured via a webcam.

---

## 🚀 Project Overview

This project implements a gesture-controlled cursor system using computer vision techniques. It uses **MediaPipe's pre-trained hand tracking model (TensorFlow Lite backend)** to detect hand landmarks in real time.

The system maps hand gestures such as finger movements and pinches into mouse actions like cursor movement, clicking, and scrolling.

⚠️ **Important Note:**  
This project is still under development and not fully polished. It requires further improvements in gesture accuracy, stability, and performance.

---

## 🧠 Core Concept

The system works by:
1. Capturing video from the webcam using OpenCV
2. Detecting hand landmarks using MediaPipe
3. Interpreting gestures based on landmark positions
4. Mapping gestures to mouse actions using PyAutoGUI

---

## 🛠️ Tech Stack

### 🐍 Python
- Core programming language used for implementation

### 📷 OpenCV
- Used for video capture and frame processing
- Converts frames to RGB for MediaPipe processing
- Displays output window with FPS

### ✋ MediaPipe (TensorFlow Lite Backend)
- Provides pre-trained hand tracking model
- Detects 21 hand landmarks in real time
- Enables gesture recognition without training a custom AI model

### 🖱️ PyAutoGUI
- Controls system mouse
- Used for:
  - Moving cursor
  - Left click
  - Right click
  - Scrolling

### 🔢 NumPy
- Used for interpolation and coordinate mapping

### 📐 Math Library
- Used for calculating distances between landmarks

### ⏱️ Time Module
- Used for FPS calculation and performance tracking

---

## ⚙️ Features

- 🖱️ Cursor movement using index finger
- 👆 Left click using thumb + index finger pinch
- 👉 Right click using index + middle finger pinch
- 🔄 Scroll using two-finger vertical movement
- 🎯 Smooth cursor movement using interpolation
- 📊 FPS display for performance monitoring
- 📷 Real-time hand tracking

---

## 🧾 Gesture Mapping

| Gesture | Action |
|--------|--------|
| Index finger up | Move cursor |
| Thumb + Index pinch | Left click |
| Index + Middle pinch | Right click |
| Two fingers up (move vertically) | Scroll |

---

## 🧪 How It Works (Technical)

- MediaPipe detects hand landmarks (21 points)
- Specific landmarks used:
  - Index tip (8)
  - Thumb tip (4)
  - Middle tip (12)
- Distance between landmarks determines gestures

Example:
```python
distance = hypot(p2.x - p1.x, p2.y - p1.y)
