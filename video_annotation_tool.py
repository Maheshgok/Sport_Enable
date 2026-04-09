"""
Video Annotation Tool using Google MediaPipe
Captures movement characteristics and analyzes key joint movements
Uses MediaPipe 0.10.30+ task-based API with Python 3.13
"""

import cv2
import numpy as np
import pandas as pd
import os
import json
from datetime import datetime
from scipy.signal import find_peaks, correlate
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

# MediaPipe 0.10.30+ uses task-based API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp

class VideoAnnotationTool:
    def __init__(self):
        # Key landmarks we want to track (same indices as before)
        self.key_landmarks = {
            'nose': 0,
            'left_eye': 2,
            'right_eye': 5,
            'left_ear': 7,
            'right_ear': 8,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
        }
        
        self.frame_data = []
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def draw_landmarks(self, frame, landmarks):
        """Draw pose landmarks on frame using simple OpenCV drawing"""
        h, w = frame.shape[:2]
        
        # Define connections (body segments to draw)
        connections = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
            (11, 23), (12, 24), (23, 24),  # Torso
            (23, 25), (25, 27), (24, 26), (26, 28),  # Legs
            (0, 1), (0, 4), (1, 2), (2, 3), (3, 7), (4, 5), (5, 6), (6, 8)  # Face
        ]
        
        # Draw connections
        for connection in connections:
            try:
                point1 = landmarks[connection[0]]
                point2 = landmarks[connection[1]]
                
                if point1.visibility > 0.5 and point2.visibility > 0.5:
                    x1, y1 = int(point1.x * w), int(point1.y * h)
                    x2, y2 = int(point2.x * w), int(point2.y * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            except:
                pass
        
        # Draw landmarks
        for landmark in landmarks:
            if landmark.visibility > 0.5:
                x, y = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
    
    def extract_movement_signal(self, video_path, confidence_threshold=0.5):
        """
        Extract center of mass movement signal from video for synchronization
        
        Args:
            video_path: Path to video file
            confidence_threshold: Minimum confidence for pose detection
            
        Returns:
            dict: {'timestamps': [], 'com_x': [], 'com_y': [], 'velocity': []}
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Download model if needed
        model_path = '/tmp/pose_landmarker.task'
        if not os.path.exists(model_path):
            import urllib.request
            model_url = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task'
            print(f"Downloading pose model for sync...")
            urllib.request.urlretrieve(model_url, model_path)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=confidence_threshold,
            min_pose_presence_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold
        )
        
        signal = {'timestamps': [], 'com_x': [], 'com_y': [], 'velocity': []}
        frame_count = 0
        prev_com = None
        
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                timestamp_ms = int(frame_count * 1000000 / fps)
                results = landmarker.detect_for_video(mp_image, timestamp_ms)
                
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks[0]
                    
                    # Calculate center of mass (average of key body points)
                    key_points = [11, 12, 23, 24]  # shoulders and hips
                    com_x = np.mean([landmarks[i].x for i in key_points])
                    com_y = np.mean([landmarks[i].y for i in key_points])
                    
                    signal['timestamps'].append(frame_count / fps)
                    signal['com_x'].append(com_x)
                    signal['com_y'].append(com_y)
                    
                    # Calculate velocity
                    if prev_com is not None:
                        velocity = np.sqrt((com_x - prev_com[0])**2 + (com_y - prev_com[1])**2)
                        signal['velocity'].append(velocity)
                    else:
                        signal['velocity'].append(0)
                    
                    prev_com = (com_x, com_y)
        
        cap.release()
        return signal
    
    def detect_key_events(self, signal):
        """
        Detect key movement events (peaks, valleys) in movement signal
        
        Args:
            signal: Movement signal dict from extract_movement_signal
            
        Returns:
            list: Timestamps of key events
        """
        if not signal or len(signal['velocity']) < 10:
            return []
        
        velocity = np.array(signal['velocity'])
        timestamps = np.array(signal['timestamps'])
        
        # Smooth velocity signal
        window_size = min(5, len(velocity) // 10)
        if window_size >= 3:
            velocity = np.convolve(velocity, np.ones(window_size)/window_size, mode='same')
        
        # Find peaks (local maxima)
        events = []
        threshold = np.mean(velocity) + np.std(velocity) * 0.5
        
        for i in range(1, len(velocity) - 1):
            # Peak detection
            if velocity[i] > threshold and velocity[i] > velocity[i-1] and velocity[i] > velocity[i+1]:
                events.append(timestamps[i])
        
        return events
    
    def synchronize_videos(self, front_video_path, side_video_path, confidence_threshold=0.5):
        """
        Synchronize two videos using cross-correlation and key event detection
        
        Args:
            front_video_path: Path to front view video
            side_video_path: Path to side view video
            confidence_threshold: Detection confidence
            
        Returns:
            dict: {
                'offset_seconds': float,  # Positive = front starts first
                'confidence': float,      # 0-1
                'method': str,           # 'cross_correlation' or 'key_events'
                'front_events': list,
                'side_events': list
            }
        """
        print("\n🔄 Synchronizing videos...")
        
        # Extract movement signals from both videos
        print("  📊 Extracting movement signal from front view...")
        front_signal = self.extract_movement_signal(front_video_path, confidence_threshold)
        
        print("  📊 Extracting movement signal from side view...")
        side_signal = self.extract_movement_signal(side_video_path, confidence_threshold)
        
        if not front_signal or not side_signal:
            print("  ⚠️  Could not extract signals from one or both videos")
            return {'offset_seconds': 0, 'confidence': 0, 'method': 'none'}
        
        # Method 1: Cross-correlation of velocity signals
        front_vel = np.array(front_signal['velocity'])
        side_vel = np.array(side_signal['velocity'])
        
        # Normalize signals
        front_vel = (front_vel - np.mean(front_vel)) / (np.std(front_vel) + 1e-10)
        side_vel = (side_vel - np.mean(side_vel)) / (np.std(side_vel) + 1e-10)
        
        # Cross-correlate
        correlation = np.correlate(front_vel, side_vel, mode='full')
        lag = np.argmax(correlation) - (len(side_vel) - 1)
        
        # Convert lag to time offset
        front_fps = len(front_signal['timestamps']) / front_signal['timestamps'][-1] if front_signal['timestamps'] else 25
        offset_xcorr = lag / front_fps
        confidence_xcorr = correlation[np.argmax(correlation)] / (len(front_vel) * np.std(front_vel) * np.std(side_vel))
        confidence_xcorr = min(abs(confidence_xcorr), 1.0)
        
        print(f"  ✓ Cross-correlation: offset={offset_xcorr:.2f}s, confidence={confidence_xcorr:.2f}")
        
        # Method 2: Key event detection
        front_events = self.detect_key_events(front_signal)
        side_events = self.detect_key_events(side_signal)
        
        print(f"  ✓ Detected {len(front_events)} events in front, {len(side_events)} in side")
        
        # Match events and calculate average offset
        if len(front_events) >= 3 and len(side_events) >= 3:
            offsets = []
            for fe in front_events[:5]:  # Use first 5 events
                for se in side_events[:5]:
                    offset = fe - se
                    if abs(offset) < 10:  # Within 10 seconds
                        offsets.append(offset)
            
            if offsets:
                offset_events = np.median(offsets)
                confidence_events = 1.0 - (np.std(offsets) / (abs(np.mean(offsets)) + 1e-10))
                confidence_events = max(0, min(confidence_events, 1.0))
                print(f"  ✓ Event matching: offset={offset_events:.2f}s, confidence={confidence_events:.2f}")
            else:
                offset_events = offset_xcorr
                confidence_events = 0
        else:
            offset_events = offset_xcorr
            confidence_events = 0
        
        # Combine methods: weight by confidence
        if confidence_xcorr > 0.5 and confidence_events > 0.5:
            # Both methods reliable - average them
            final_offset = (offset_xcorr * confidence_xcorr + offset_events * confidence_events) / (confidence_xcorr + confidence_events)
            final_confidence = (confidence_xcorr + confidence_events) / 2
            method = 'combined'
        elif confidence_xcorr >= confidence_events:
            final_offset = offset_xcorr
            final_confidence = confidence_xcorr
            method = 'cross_correlation'
        else:
            final_offset = offset_events
            final_confidence = confidence_events
            method = 'key_events'
        
        print(f"  ✅ Final sync: offset={final_offset:.2f}s ({method}), confidence={final_confidence:.2f}")
        
        return {
            'offset_seconds': final_offset,
            'confidence': final_confidence,
            'method': method,
            'front_events': front_events,
            'side_events': side_events
        }
    
    def process_video(self, video_path, output_folder='output', confidence_threshold=0.5, 
                     athlete_height_cm=None, side_video_path=None):
        """
        Process video and extract pose landmarks frame by frame
        
        Args:
            video_path: Path to input video file (front view)
            output_folder: Folder to save outputs
            confidence_threshold: Minimum confidence for pose detection
            athlete_height_cm: Athlete's height in cm (optional, for better calibration)
            side_video_path: Path to side view video (optional, for better 3D analysis)
        """
        # Store athlete height for later use in analysis
        self.athlete_height_cm = athlete_height_cm
        self.side_video_path = side_video_path
        
        # Synchronize videos if side video is provided
        sync_info = None
        if side_video_path and os.path.exists(side_video_path):
            sync_info = self.synchronize_videos(video_path, side_video_path, confidence_threshold)
            self.sync_info = sync_info
            
            if sync_info['confidence'] < 0.4:
                print(f"  ⚠️  Low sync confidence ({sync_info['confidence']:.2f}). Results may not be perfectly aligned.")
        else:
            self.sync_info = None
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Cannot open video file {video_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video Info: {frame_width}x{frame_height} @ {fps}fps, Total frames: {total_frames}")
        
        # Initialize video writer for annotated output
        output_video_path = os.path.join(output_folder, f'annotated_video_{timestamp}.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
        
        # Create PoseLandmarker with task-based API
        # Download model if not exists
        model_path = '/tmp/pose_landmarker.task'
        if not os.path.exists(model_path):
            import urllib.request
            model_url = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task'
            print(f"Downloading pose model...")
            urllib.request.urlretrieve(model_url, model_path)
            print(f"Model downloaded to {model_path}")
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=confidence_threshold,
            min_pose_presence_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold
        )
        
        frame_count = 0
        
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Convert BGR to RGB for MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                
                # Process pose with timestamp in microseconds
                timestamp_ms = int(frame_count * 1000000 / fps)
                results = landmarker.detect_for_video(mp_image, timestamp_ms)
                
                # Extract landmarks if detected
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks[0]  # Get first pose
                    
                    # Create frame data dictionary
                    frame_dict = {
                        'frame': frame_count,
                        'timestamp_sec': frame_count / fps
                    }
                    
                    # Extract all landmark coordinates
                    for name, idx in self.key_landmarks.items():
                        lm = landmarks[idx]
                        frame_dict[f'{name}_x'] = lm.x
                        frame_dict[f'{name}_y'] = lm.y
                        frame_dict[f'{name}_z'] = lm.z
                        frame_dict[f'{name}_visibility'] = lm.visibility
                    
                    # Calculate key measurements and angles
                    # KNEE ANGLES (Hip-Knee-Ankle)
                    frame_dict['left_knee_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_hip']].x, landmarks[self.key_landmarks['left_hip']].y],
                        [landmarks[self.key_landmarks['left_knee']].x, landmarks[self.key_landmarks['left_knee']].y],
                        [landmarks[self.key_landmarks['left_ankle']].x, landmarks[self.key_landmarks['left_ankle']].y]
                    )
                    
                    frame_dict['right_knee_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_hip']].x, landmarks[self.key_landmarks['right_hip']].y],
                        [landmarks[self.key_landmarks['right_knee']].x, landmarks[self.key_landmarks['right_knee']].y],
                        [landmarks[self.key_landmarks['right_ankle']].x, landmarks[self.key_landmarks['right_ankle']].y]
                    )
                    
                    # ELBOW ANGLES (Shoulder-Elbow-Wrist)
                    frame_dict['left_elbow_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_shoulder']].x, landmarks[self.key_landmarks['left_shoulder']].y],
                        [landmarks[self.key_landmarks['left_elbow']].x, landmarks[self.key_landmarks['left_elbow']].y],
                        [landmarks[self.key_landmarks['left_wrist']].x, landmarks[self.key_landmarks['left_wrist']].y]
                    )
                    
                    frame_dict['right_elbow_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_shoulder']].x, landmarks[self.key_landmarks['right_shoulder']].y],
                        [landmarks[self.key_landmarks['right_elbow']].x, landmarks[self.key_landmarks['right_elbow']].y],
                        [landmarks[self.key_landmarks['right_wrist']].x, landmarks[self.key_landmarks['right_wrist']].y]
                    )
                    
                    # HIP ANGLES (Shoulder-Hip-Knee)
                    frame_dict['left_hip_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_shoulder']].x, landmarks[self.key_landmarks['left_shoulder']].y],
                        [landmarks[self.key_landmarks['left_hip']].x, landmarks[self.key_landmarks['left_hip']].y],
                        [landmarks[self.key_landmarks['left_knee']].x, landmarks[self.key_landmarks['left_knee']].y]
                    )
                    
                    frame_dict['right_hip_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_shoulder']].x, landmarks[self.key_landmarks['right_shoulder']].y],
                        [landmarks[self.key_landmarks['right_hip']].x, landmarks[self.key_landmarks['right_hip']].y],
                        [landmarks[self.key_landmarks['right_knee']].x, landmarks[self.key_landmarks['right_knee']].y]
                    )
                    
                    # SHOULDER ANGLES (Hip-Shoulder-Elbow)
                    frame_dict['left_shoulder_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_hip']].x, landmarks[self.key_landmarks['left_hip']].y],
                        [landmarks[self.key_landmarks['left_shoulder']].x, landmarks[self.key_landmarks['left_shoulder']].y],
                        [landmarks[self.key_landmarks['left_elbow']].x, landmarks[self.key_landmarks['left_elbow']].y]
                    )
                    
                    frame_dict['right_shoulder_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_hip']].x, landmarks[self.key_landmarks['right_hip']].y],
                        [landmarks[self.key_landmarks['right_shoulder']].x, landmarks[self.key_landmarks['right_shoulder']].y],
                        [landmarks[self.key_landmarks['right_elbow']].x, landmarks[self.key_landmarks['right_elbow']].y]
                    )
                    
                    # ANKLE ANGLES
                    ankle_vertical_point_left = [landmarks[self.key_landmarks['left_ankle']].x, 
                                                 landmarks[self.key_landmarks['left_ankle']].y + 0.1]
                    ankle_vertical_point_right = [landmarks[self.key_landmarks['right_ankle']].x, 
                                                  landmarks[self.key_landmarks['right_ankle']].y + 0.1]
                    
                    frame_dict['left_ankle_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_knee']].x, landmarks[self.key_landmarks['left_knee']].y],
                        [landmarks[self.key_landmarks['left_ankle']].x, landmarks[self.key_landmarks['left_ankle']].y],
                        ankle_vertical_point_left
                    )
                    
                    frame_dict['right_ankle_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_knee']].x, landmarks[self.key_landmarks['right_knee']].y],
                        [landmarks[self.key_landmarks['right_ankle']].x, landmarks[self.key_landmarks['right_ankle']].y],
                        ankle_vertical_point_right
                    )
                    
                    # NECK ANGLE
                    shoulder_midpoint = [
                        (landmarks[self.key_landmarks['left_shoulder']].x + landmarks[self.key_landmarks['right_shoulder']].x) / 2,
                        (landmarks[self.key_landmarks['left_shoulder']].y + landmarks[self.key_landmarks['right_shoulder']].y) / 2
                    ]
                    nose_vertical = [landmarks[self.key_landmarks['nose']].x, 
                                    landmarks[self.key_landmarks['nose']].y - 0.1]
                    
                    frame_dict['neck_angle'] = self.calculate_angle(
                        shoulder_midpoint,
                        [landmarks[self.key_landmarks['nose']].x, landmarks[self.key_landmarks['nose']].y],
                        nose_vertical
                    )
                    
                    # WRIST ANGLES
                    wrist_forward_point_left = [landmarks[self.key_landmarks['left_wrist']].x + 0.1, 
                                               landmarks[self.key_landmarks['left_wrist']].y]
                    wrist_forward_point_right = [landmarks[self.key_landmarks['right_wrist']].x - 0.1, 
                                                landmarks[self.key_landmarks['right_wrist']].y]
                    
                    frame_dict['left_wrist_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['left_elbow']].x, landmarks[self.key_landmarks['left_elbow']].y],
                        [landmarks[self.key_landmarks['left_wrist']].x, landmarks[self.key_landmarks['left_wrist']].y],
                        wrist_forward_point_left
                    )
                    
                    frame_dict['right_wrist_angle'] = self.calculate_angle(
                        [landmarks[self.key_landmarks['right_elbow']].x, landmarks[self.key_landmarks['right_elbow']].y],
                        [landmarks[self.key_landmarks['right_wrist']].x, landmarks[self.key_landmarks['right_wrist']].y],
                        wrist_forward_point_right
                    )
                    
                    # Additional measurements
                    frame_dict['left_knee_hip_distance'] = landmarks[self.key_landmarks['left_hip']].y - landmarks[self.key_landmarks['left_knee']].y
                    frame_dict['right_knee_hip_distance'] = landmarks[self.key_landmarks['right_hip']].y - landmarks[self.key_landmarks['right_knee']].y
                    frame_dict['shoulder_width'] = abs(landmarks[self.key_landmarks['left_shoulder']].x - landmarks[self.key_landmarks['right_shoulder']].x)
                    frame_dict['hip_width'] = abs(landmarks[self.key_landmarks['left_hip']].x - landmarks[self.key_landmarks['right_hip']].x)
                    
                    left_torso = abs(landmarks[self.key_landmarks['left_shoulder']].y - landmarks[self.key_landmarks['left_hip']].y)
                    right_torso = abs(landmarks[self.key_landmarks['right_shoulder']].y - landmarks[self.key_landmarks['right_hip']].y)
                    frame_dict['torso_height'] = (left_torso + right_torso) / 2
                    
                    self.frame_data.append(frame_dict)
                    
                    # Draw landmarks on frame
                    self.draw_landmarks(frame, landmarks)
                    
                    # Add frame number text
                    cv2.putText(frame, f'Frame: {frame_count}', (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Write annotated frame
                out.write(frame)
                
                # Progress update
                if frame_count % 30 == 0:
                    print(f"Processed {frame_count}/{total_frames} frames ({100*frame_count/total_frames:.1f}%)")
        
        cap.release()
        out.release()
        
        print(f"\n✓ Video processing complete!")
        print(f"✓ Annotated video saved: {output_video_path}")
        
        return timestamp
    
    def analyze_movements(self, output_folder='output', timestamp=None, athlete_height_cm=None):
        """
        Analyze movement data and identify key metrics
        
        Args:
            output_folder: Folder to save analysis results
            timestamp: Timestamp for filename
            athlete_height_cm: Actual athlete height in cm for accurate calibration
        """
        if not self.frame_data:
            print("No frame data to analyze!")
            return
        
        # Use athlete height if provided, otherwise use stored value or default
        if athlete_height_cm is None:
            athlete_height_cm = getattr(self, 'athlete_height_cm', None)
        
        # Convert to DataFrame
        df = pd.DataFrame(self.frame_data)
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw frame data
        raw_csv_path = os.path.join(output_folder, f'frame_data_{timestamp}.csv')
        df.to_csv(raw_csv_path, index=False)
        print(f"✓ Raw frame data saved: {raw_csv_path}")
        
        # Calculate movement statistics
        analysis = {}
        
        # Joint angle statistics
        angle_columns = [col for col in df.columns if 'angle' in col]
        for col in angle_columns:
            analysis[f'{col}_min'] = df[col].min()
            analysis[f'{col}_max'] = df[col].max()
            analysis[f'{col}_mean'] = df[col].mean()
            analysis[f'{col}_range'] = df[col].max() - df[col].min()
        
        # Distance measurements
        for side in ['left', 'right']:
            col = f'{side}_knee_hip_distance'
            if col in df.columns:
                analysis[f'{col}_min'] = df[col].min()
                analysis[f'{col}_max'] = df[col].max()
                analysis[f'{col}_mean'] = df[col].mean()
                analysis[f'{col}_range'] = df[col].max() - df[col].min()
        
        # Calculate velocity and real-world distance measurements
        # Use athlete's actual height for accurate scaling
        if athlete_height_cm and athlete_height_cm > 0:
            # Calculate full body height from landmarks (nose to average ankle)
            avg_body_height_normalized = df.apply(
                lambda row: abs(row['nose_y'] - (row['left_ankle_y'] + row['right_ankle_y']) / 2), 
                axis=1
            ).mean()
            
            # Scale factor: actual height / measured normalized height
            pixels_to_cm = athlete_height_cm / avg_body_height_normalized if avg_body_height_normalized > 0 else 1
            reference_height_cm = athlete_height_cm
            reference_description = f"Full body height (nose to ankles)"
        else:
            # Fallback to torso height method
            reference_height_cm = 50  # Average adult torso height in cm
            avg_torso_normalized = df['torso_height'].mean()
            pixels_to_cm = reference_height_cm / avg_torso_normalized if avg_torso_normalized > 0 else 1
            reference_description = "Torso height (shoulder to hip) - estimated"
        
        print(f"\n✓ Using reference: {reference_description} = {reference_height_cm} cm")
        print(f"✓ Scale factor: {pixels_to_cm:.2f} cm per normalized unit")
        
        velocity_data = []
        for name in ['left_knee', 'right_knee', 'left_hip', 'right_hip', 
                     'left_shoulder', 'right_shoulder', 'left_ankle', 'right_ankle',
                     'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']:
            if f'{name}_x' in df.columns:
                dx = df[f'{name}_x'].diff()
                dy = df[f'{name}_y'].diff()
                dz = df[f'{name}_z'].diff()
                velocity_normalized = np.sqrt(dx**2 + dy**2 + dz**2)
                
                # Convert to real-world measurements
                total_distance_cm = velocity_normalized.sum() * pixels_to_cm
                max_displacement_cm = velocity_normalized.max() * pixels_to_cm
                
                # Calculate movement range (max - min position)
                x_range = (df[f'{name}_x'].max() - df[f'{name}_x'].min()) * pixels_to_cm
                y_range = (df[f'{name}_y'].max() - df[f'{name}_y'].min()) * pixels_to_cm
                z_range = (df[f'{name}_z'].max() - df[f'{name}_z'].min()) * pixels_to_cm
                total_range_cm = np.sqrt(x_range**2 + y_range**2 + z_range**2)
                
                velocity_data.append({
                    'joint': name,
                    'max_velocity_normalized': velocity_normalized.max(),
                    'mean_velocity_normalized': velocity_normalized.mean(),
                    'total_movement_normalized': velocity_normalized.sum(),
                    'total_distance_cm': total_distance_cm,
                    'max_displacement_cm': max_displacement_cm,
                    'total_range_cm': total_range_cm,
                    'x_range_cm': x_range,
                    'y_range_cm': y_range,
                    'z_range_cm': z_range
                })
        
        velocity_df = pd.DataFrame(velocity_data)
        velocity_csv_path = os.path.join(output_folder, f'joint_movements_{timestamp}.csv')
        velocity_df.to_csv(velocity_csv_path, index=False)
        print(f"✓ Joint movement data (with distance in cm) saved: {velocity_csv_path}")
        
        # Add scaling info to analysis
        analysis['reference_height_cm'] = reference_height_cm
        analysis['reference_description'] = reference_description
        analysis['athlete_height_cm'] = athlete_height_cm if athlete_height_cm else None
        analysis['scale_factor_cm_per_unit'] = pixels_to_cm
        
        # Add synchronization info to analysis
        if hasattr(self, 'sync_info') and self.sync_info:
            analysis['sync_offset_seconds'] = self.sync_info['offset_seconds']
            analysis['sync_confidence'] = self.sync_info['confidence']
            analysis['sync_method'] = self.sync_info['method']
            analysis['has_side_video'] = True
        else:
            analysis['has_side_video'] = False
        
        # Create detailed joint angle analysis with min/max timestamps
        angle_analysis_data = []
        for col in angle_columns:
            min_idx = df[col].idxmin()
            max_idx = df[col].idxmax()
            
            angle_analysis_data.append({
                'joint_angle': col.replace('_angle', '').replace('_', ' ').title(),
                'minimum_angle_degrees': df[col].min(),
                'maximum_angle_degrees': df[col].max(),
                'range_degrees': df[col].max() - df[col].min(),
                'mean_angle_degrees': df[col].mean(),
                'std_dev_degrees': df[col].std(),
                'min_angle_frame': df.loc[min_idx, 'frame'],
                'min_angle_timestamp_sec': df.loc[min_idx, 'timestamp_sec'],
                'max_angle_frame': df.loc[max_idx, 'frame'],
                'max_angle_timestamp_sec': df.loc[max_idx, 'timestamp_sec']
            })
        
        angle_analysis_df = pd.DataFrame(angle_analysis_data)
        angle_csv_path = os.path.join(output_folder, f'joint_angles_minmax_{timestamp}.csv')
        angle_analysis_df.to_csv(angle_csv_path, index=False)
        print(f"✓ Joint angle min/max analysis saved: {angle_csv_path}")
        
        # Save analysis summary
        analysis_df = pd.DataFrame([analysis])
        analysis_csv_path = os.path.join(output_folder, f'movement_analysis_{timestamp}.csv')
        analysis_df.to_csv(analysis_csv_path, index=False)
        print(f"✓ Movement analysis saved: {analysis_csv_path}")
        
        # Generate summary report
        report_path = os.path.join(output_folder, f'summary_report_{timestamp}.txt')
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MOVEMENT ANALYSIS SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total frames analyzed: {len(df)}\n")
            f.write(f"Duration: {df['timestamp_sec'].max():.2f} seconds\n")
            f.write(f"Average FPS: {len(df) / df['timestamp_sec'].max():.1f}\n")
            
            # Add synchronization info if available
            if hasattr(self, 'sync_info') and self.sync_info:
                f.write("\n" + "=" * 80 + "\n")
                f.write("VIDEO SYNCHRONIZATION\n")
                f.write("=" * 80 + "\n")
                f.write(f"Side video: PROVIDED\n")
                f.write(f"Sync method: {self.sync_info['method']}\n")
                f.write(f"Time offset: {self.sync_info['offset_seconds']:.3f} seconds\n")
                f.write(f"Sync confidence: {self.sync_info['confidence']:.2f} (0=low, 1=high)\n")
                if abs(self.sync_info['offset_seconds']) > 0.1:
                    if self.sync_info['offset_seconds'] > 0:
                        f.write(f"Note: Front view starts {abs(self.sync_info['offset_seconds']):.2f}s before side view\n")
                    else:
                        f.write(f"Note: Side view starts {abs(self.sync_info['offset_seconds']):.2f}s before front view\n")
                f.write(f"Front view events detected: {len(self.sync_info.get('front_events', []))}\n")
                f.write(f"Side view events detected: {len(self.sync_info.get('side_events', []))}\n")
            
            f.write("\n")
            
            # Organize angles by joint type
            joint_types = {
                'KNEE': [col for col in angle_columns if 'knee' in col],
                'ELBOW': [col for col in angle_columns if 'elbow' in col],
                'HIP': [col for col in angle_columns if 'hip' in col],
                'SHOULDER': [col for col in angle_columns if 'shoulder' in col],
                'ANKLE': [col for col in angle_columns if 'ankle' in col],
                'WRIST': [col for col in angle_columns if 'wrist' in col],
                'NECK': [col for col in angle_columns if 'neck' in col]
            }
            
            for joint_type, cols in joint_types.items():
                if cols:
                    f.write("=" * 80 + "\n")
                    f.write(f"{joint_type} ANGLES\n")
                    f.write("=" * 80 + "\n")
                    for col in cols:
                        min_idx = df[col].idxmin()
                        max_idx = df[col].idxmax()
                        f.write(f"\n{col.replace('_', ' ').title()}:\n")
                        f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                        f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                        f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                        f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                    f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("REFERENCE SCALE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Reference measurement: {reference_description}\n")
            f.write(f"Reference height: {reference_height_cm} cm\n")
            if athlete_height_cm:
                f.write(f"Athlete height (provided): {athlete_height_cm} cm\n")
            f.write(f"Scale factor: {pixels_to_cm:.2f} cm per normalized unit\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("JOINT MOVEMENTS - DISTANCE TRAVELED (in centimeters)\n")
            f.write("=" * 80 + "\n")
            sorted_distance = velocity_df.sort_values('total_distance_cm', ascending=False)
            for idx, row in sorted_distance.head(10).iterrows():
                f.write(f"\n{row['joint'].replace('_', ' ').title()}:\n")
                f.write(f"  Total Distance Traveled: {row['total_distance_cm']:.2f} cm\n")
                f.write(f"  Movement Range (3D): {row['total_range_cm']:.2f} cm\n")
                f.write(f"  Range X-axis: {row['x_range_cm']:.2f} cm\n")
                f.write(f"  Range Y-axis: {row['y_range_cm']:.2f} cm\n")
                f.write(f"  Range Z-axis: {row['z_range_cm']:.2f} cm\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("MOST ACTIVE JOINTS (by normalized movement)\n")
            f.write("=" * 80 + "\n")
            sorted_velocity = velocity_df.sort_values('total_movement_normalized', ascending=False)
            for idx, row in sorted_velocity.head(10).iterrows():
                f.write(f"{row['joint'].replace('_', ' ').title()}: {row['total_movement_normalized']:.4f} (normalized) = {row['total_distance_cm']:.2f} cm\n")
            
        
        print(f"✓ Summary report saved (phase analysis will be appended): {report_path}")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualization_files = []
        
        try:
            # 1. Joint angle and range of motion visualizations
            angle_viz_files = self.create_joint_angle_visualization(df, output_folder, timestamp)
            visualization_files.extend(angle_viz_files)
            
            # 2. Gait analysis visualizations
            gait_viz_files = self.create_gait_analysis_visualization(df, output_folder, timestamp)
            visualization_files.extend(gait_viz_files)
            
            # 3. Add visualization paths to analysis
            analysis['visualizations'] = {
                'joint_angles': [os.path.basename(f) for f in angle_viz_files],
                'gait_analysis': [os.path.basename(f) for f in gait_viz_files],
                'all_files': [os.path.basename(f) for f in visualization_files]
            }
            
            # 4. Add reversal data to analysis
            reversal_summary = {}
            key_joints = ['left_knee', 'right_knee', 'left_elbow', 'right_elbow', 'left_ankle', 'right_ankle']
            for joint in key_joints:
                reversals = self.detect_movement_reversals(df, joint)
                reversal_summary[joint] = {
                    'count': len(reversals),
                    'timestamps': reversals
                }
            analysis['movement_reversals'] = reversal_summary
            
            print(f"✓ Generated {len(visualization_files)} visualization files")
            
        except Exception as e:
            print(f"⚠ Warning: Visualization generation failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            analysis['visualizations'] = {'error': str(e)}
        
        # 5. PHASE ANALYSIS - Run this independently from visualizations
        try:
            print("\n" + "=" * 70)
            print("DETECTING MOVEMENT PHASES (Landing, Mid-Stance, Push-Off)")
            print("=" * 70)
            
            left_phases = self.detect_movement_phases(df, side='left')
            right_phases = self.detect_movement_phases(df, side='right')
            
            print(f"✓ Left side: {len(left_phases['cycles'])} complete cycles detected")
            print(f"✓ Right side: {len(right_phases['cycles'])} complete cycles detected")
            
            # Analyze biomechanics for each phase
            left_phase_analysis = self.analyze_phase_biomechanics(df, left_phases, side='left')
            right_phase_analysis = self.analyze_phase_biomechanics(df, right_phases, side='right')
            
            # Save phase analysis data
            phase_analysis_data = {
                'left_side': {
                    'cycles_detected': len(left_phases['cycles']),
                    'cycles': left_phase_analysis
                },
                'right_side': {
                    'cycles_detected': len(right_phases['cycles']),
                    'cycles': right_phase_analysis
                }
            }
            
            # Save phase analysis as JSON
            phase_json_path = os.path.join(output_folder, f'phase_analysis_{timestamp}.json')
            with open(phase_json_path, 'w') as f:
                json.dump(phase_analysis_data, f, indent=2)
            print(f"✓ Phase analysis JSON saved: {phase_json_path}")
            
            # Save phase analysis as CSV for easy viewing
            phase_csv_path = os.path.join(output_folder, f'phase_analysis_{timestamp}.csv')
            phase_rows = []
            for side_name, side_data in [('left', left_phase_analysis), ('right', right_phase_analysis)]:
                for cycle in side_data:
                    for phase_name in ['landing', 'mid_stance', 'push_off']:
                        phase = cycle[phase_name]
                        row = {
                            'side': side_name,
                            'cycle': cycle['cycle_number'],
                            'phase': phase_name,
                            'frame': phase['frame'],
                            'timestamp_sec': phase['timestamp']
                        }
                        # Add all angles
                        for angle_name, angle_value in phase['angles'].items():
                            row[f'{angle_name}_angle_deg'] = angle_value
                        # Add all velocities
                        for joint_name, velocity_value in phase['velocities'].items():
                            row[f'{joint_name}_velocity'] = velocity_value
                        phase_rows.append(row)
            
            if phase_rows:
                phase_df = pd.DataFrame(phase_rows)
                phase_df.to_csv(phase_csv_path, index=False)
                print(f"✓ Phase analysis CSV saved: {phase_csv_path}")
                print(f"✓ Appending phase analysis to summary report...")
                
                # Append phase analysis to the summary report
                self.append_phase_analysis_to_report(report_path, left_phase_analysis, right_phase_analysis)
                print(f"✓ Phase analysis added to: {report_path}")
            else:
                print("⚠ No phase data to save (no cycles detected)")
            
            analysis['phase_analysis'] = {
                'left_cycles': len(left_phases['cycles']),
                'right_cycles': len(right_phases['cycles']),
                'json_file': os.path.basename(phase_json_path),
                'csv_file': os.path.basename(phase_csv_path) if phase_rows else None
            }
            
            # 6. Create phase-specific visualizations
            try:
                if phase_rows:  # Only create visualizations if we have phase data
                    print("\nGenerating phase visualizations...")
                    phase_viz_files = self.create_phase_analysis_visualization(df, left_phases, right_phases, 
                                                                               left_phase_analysis, right_phase_analysis,
                                                                               output_folder, timestamp)
                    visualization_files.extend(phase_viz_files)
                    
                    if 'visualizations' not in analysis:
                        analysis['visualizations'] = {}
                    analysis['visualizations']['phase_analysis'] = [os.path.basename(f) for f in phase_viz_files]
                    
                    print(f"✓ Generated {len(phase_viz_files)} phase visualization files")
            except Exception as viz_error:
                print(f"⚠ Warning: Phase visualization generation failed: {str(viz_error)}")
                import traceback
                print(traceback.format_exc())
            
        except Exception as e:
            print(f"⚠ Warning: Phase analysis failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            analysis['phase_analysis'] = {'error': str(e)}
        
        # Save analytics as JSON
        analytics_json_path = os.path.join(output_folder, f'analytics_{timestamp}.json')
        try:
            analytics_data = self.get_analytics_json()
            analytics_data['visualization_files'] = analysis.get('visualizations', {})
            
            with open(analytics_json_path, 'w') as json_file:
                json.dump(analytics_data, json_file, indent=2)
            
            print(f"✓ Analytics JSON saved: {analytics_json_path}")
            analysis['analytics_json'] = os.path.basename(analytics_json_path)
            
        except Exception as e:
            print(f"⚠ Warning: Analytics JSON generation failed: {str(e)}")
        
        return analysis
    
    def detect_movement_reversals(self, df, joint_name, threshold_percentile=75):
        """
        Detect points where joint movement direction reverses suddenly
        
        Args:
            df: DataFrame with joint position data
            joint_name: Name of joint (e.g., 'left_knee')
            threshold_percentile: Percentile threshold for detecting sudden changes
            
        Returns:
            list: Timestamps of reversal points
        """
        if f'{joint_name}_x' not in df.columns:
            return []
        
        # Calculate velocity
        dx = df[f'{joint_name}_x'].diff()
        dy = df[f'{joint_name}_y'].diff()
        velocity = np.sqrt(dx**2 + dy**2)
        
        # Calculate acceleration (change in velocity)
        acceleration = velocity.diff().abs()
        
        # Find sudden changes (high acceleration)
        threshold = np.percentile(acceleration.dropna(), threshold_percentile)
        reversal_indices = acceleration[acceleration > threshold].index
        
        reversal_times = df.loc[reversal_indices, 'timestamp_sec'].tolist()
        return reversal_times
    
    def detect_movement_phases(self, df, side='left', min_cycle_frames=15):
        """
        Detect key movement phases: landing, mid-stance, and push-off
        
        Args:
            df: DataFrame with movement data
            side: Which side to analyze ('left' or 'right')
            min_cycle_frames: Minimum frames between phases to avoid false detections
            
        Returns:
            dict: Dictionary containing phase information
                {
                    'landing': [list of frame indices],
                    'mid_stance': [list of frame indices],
                    'push_off': [list of frame indices],
                    'cycles': [list of cycle dictionaries]
                }
        """
        from scipy.signal import find_peaks
        
        ankle_col = f'{side}_ankle_y'
        knee_col = f'{side}_knee_y'
        hip_col = f'{side}_hip_y'
        
        if ankle_col not in df.columns or knee_col not in df.columns:
            return {'landing': [], 'mid_stance': [], 'push_off': [], 'cycles': []}
        
        # Get ankle vertical position (inverted because y increases downward in image coords)
        ankle_y = df[ankle_col].values
        knee_y = df[knee_col].values
        
        # Calculate ankle velocity
        ankle_velocity_y = np.diff(ankle_y, prepend=ankle_y[0])
        
        # Smooth the signal to reduce noise
        from scipy.ndimage import gaussian_filter1d
        ankle_y_smooth = gaussian_filter1d(ankle_y, sigma=2)
        ankle_velocity_smooth = gaussian_filter1d(ankle_velocity_y, sigma=2)
        
        # LANDING: Foot contacts ground (ankle reaches lowest point / local minimum in vertical pos)
        # In image coordinates, lower y = higher position, so we look for maxima
        landing_frames, _ = find_peaks(ankle_y_smooth, distance=min_cycle_frames, prominence=0.005)
        
        # PUSH OFF: Foot leaves ground (ankle reaches highest point before flight)
        # In image coordinates, higher y = lower position, so we look for minima
        push_off_frames, _ = find_peaks(-ankle_y_smooth, distance=min_cycle_frames, prominence=0.005)
        
        # MID STANCE: Point of maximum knee flexion during stance phase
        # This occurs between landing and push-off
        mid_stance_frames = []
        cycles = []
        
        # Match landing and push-off frames into cycles
        for landing_idx in landing_frames:
            # Find the next push-off after this landing
            next_push_offs = push_off_frames[push_off_frames > landing_idx]
            
            if len(next_push_offs) > 0:
                push_off_idx = next_push_offs[0]
                
                # Find mid-stance: minimum knee height (max knee_y in image coords) between landing and push-off
                stance_region = df.iloc[landing_idx:push_off_idx + 1]
                if len(stance_region) > 0 and knee_col in stance_region.columns:
                    mid_stance_idx = stance_region[knee_col].idxmax()
                    mid_stance_frames.append(mid_stance_idx)
                    
                    cycles.append({
                        'landing_frame': int(landing_idx),
                        'mid_stance_frame': int(mid_stance_idx),
                        'push_off_frame': int(push_off_idx),
                        'landing_time': float(df.iloc[landing_idx]['timestamp_sec']),
                        'mid_stance_time': float(df.iloc[mid_stance_idx]['timestamp_sec']),
                        'push_off_time': float(df.iloc[push_off_idx]['timestamp_sec']),
                        'cycle_duration': float(df.iloc[push_off_idx]['timestamp_sec'] - df.iloc[landing_idx]['timestamp_sec'])
                    })
        
        return {
            'landing': landing_frames.tolist(),
            'mid_stance': mid_stance_frames,
            'push_off': push_off_frames.tolist(),
            'cycles': cycles
        }
    
    def analyze_phase_biomechanics(self, df, phases, side='left'):
        """
        Extract angles and velocities for each movement phase
        
        Args:
            df: DataFrame with movement data
            phases: Dictionary from detect_movement_phases
            side: Which side to analyze ('left' or 'right')
            
        Returns:
            list: List of dictionaries containing phase analysis
        """
        phase_analysis = []
        
        # Define angle columns to track
        angle_columns = [
            f'{side}_knee_angle',
            f'{side}_hip_angle',
            f'{side}_ankle_angle',
            f'{side}_shoulder_angle',
            f'{side}_elbow_angle'
        ]
        
        # Define joints for velocity calculation
        joints = [f'{side}_knee', f'{side}_hip', f'{side}_ankle', f'{side}_shoulder', f'{side}_elbow']
        
        # Process each cycle
        for cycle_idx, cycle in enumerate(phases['cycles']):
            cycle_data = {
                'cycle_number': cycle_idx + 1,
                'side': side,
                'landing': {},
                'mid_stance': {},
                'push_off': {}
            }
            
            # Analyze each phase in the cycle
            for phase_name, frame_idx in [
                ('landing', cycle['landing_frame']),
                ('mid_stance', cycle['mid_stance_frame']),
                ('push_off', cycle['push_off_frame'])
            ]:
                phase_data = {
                    'frame': int(frame_idx),
                    'timestamp': float(df.iloc[frame_idx]['timestamp_sec']),
                    'angles': {},
                    'velocities': {}
                }
                
                # Extract angles at this phase
                for angle_col in angle_columns:
                    if angle_col in df.columns:
                        angle_name = angle_col.replace(f'{side}_', '').replace('_angle', '')
                        phase_data['angles'][angle_name] = float(df.iloc[frame_idx][angle_col])
                
                # Calculate velocities at this phase
                for joint in joints:
                    if f'{joint}_x' in df.columns and frame_idx > 0:
                        # Calculate velocity from previous frame
                        dx = df.iloc[frame_idx][f'{joint}_x'] - df.iloc[frame_idx - 1][f'{joint}_x']
                        dy = df.iloc[frame_idx][f'{joint}_y'] - df.iloc[frame_idx - 1][f'{joint}_y']
                        dz = df.iloc[frame_idx][f'{joint}_z'] - df.iloc[frame_idx - 1][f'{joint}_z']
                        
                        velocity = np.sqrt(dx**2 + dy**2 + dz**2)
                        joint_name = joint.replace(f'{side}_', '')
                        phase_data['velocities'][joint_name] = float(velocity)
                
                cycle_data[phase_name] = phase_data
            
            phase_analysis.append(cycle_data)
        
        return phase_analysis
    
    def append_phase_analysis_to_report(self, report_path, left_phase_analysis, right_phase_analysis):
        """
        Append detailed phase analysis to the summary report with comprehensive biomechanical breakdown
        
        Args:
            report_path: Path to the summary report file
            left_phase_analysis: Phase analysis for left side
            right_phase_analysis: Phase analysis for right side
        """
        with open(report_path, 'a') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("MOVEMENT PHASE ANALYSIS - LANDING, MID-STANCE, PUSH-OFF\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary statistics
            total_left = len(left_phase_analysis)
            total_right = len(right_phase_analysis)
            
            f.write("SUMMARY:\n")
            f.write(f"  Total Movement Cycles Detected: {total_left + total_right}\n")
            f.write(f"  Left Side Cycles: {total_left}\n")
            f.write(f"  Right Side Cycles: {total_right}\n\n")
            
            f.write("PHASE DEFINITIONS:\n")
            f.write("  • LANDING:     Initial foot contact - absorption phase begins\n")
            f.write("  • MID-STANCE:  Maximum knee flexion - peak loading\n")
            f.write("  • PUSH-OFF:    Toe-off - propulsion phase\n\n")
            
            if not left_phase_analysis and not right_phase_analysis:
                f.write("No movement cycles detected. This may occur if:\n")
                f.write("  - Movement is not cyclical (walking/running)\n")
                f.write("  - Video is too short\n")
                f.write("  - Foot contacts are not clearly visible\n")
                return
            
            # Create comprehensive phase table for each side
            for side_name, phase_data in [('LEFT SIDE', left_phase_analysis), ('RIGHT SIDE', right_phase_analysis)]:
                if not phase_data:
                    f.write(f"\n{side_name}: No cycles detected\n")
                    continue
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"{side_name} - DETAILED PHASE BREAKDOWN\n")
                f.write("=" * 80 + "\n\n")
                
                # Cycle-by-cycle breakdown
                for cycle in phase_data:
                    cycle_num = cycle['cycle_number']
                    duration = cycle['push_off']['timestamp'] - cycle['landing']['timestamp']
                    
                    f.write(f"CYCLE #{cycle_num}  |  Duration: {duration:.3f}s  |  Frequency: {1/duration if duration > 0 else 0:.2f} Hz\n")
                    f.write("-" * 80 + "\n")
                    
                    # Create a table header
                    f.write(f"{'JOINT':<15} | {'LANDING':>12} | {'MID-STANCE':>12} | {'PUSH-OFF':>12} | {'CHANGE':>12}\n")
                    f.write("-" * 80 + "\n")
                    
                    # Get all unique angle names
                    all_angles = set()
                    for phase_name in ['landing', 'mid_stance', 'push_off']:
                        all_angles.update(cycle[phase_name]['angles'].keys())
                    
                    # Display each angle across phases
                    for angle_name in sorted(all_angles):
                        landing_val = cycle['landing']['angles'].get(angle_name, 0)
                        mid_val = cycle['mid_stance']['angles'].get(angle_name, 0)
                        push_val = cycle['push_off']['angles'].get(angle_name, 0)
                        change = push_val - landing_val
                        
                        f.write(f"{angle_name.title():<15} | {landing_val:>10.1f}° | {mid_val:>10.1f}° | {push_val:>10.1f}° | {change:>+10.1f}°\n")
                    
                    f.write("\n")
                    
                    # Timing information
                    f.write(f"PHASE TIMING:\n")
                    f.write(f"  Landing:    Frame {cycle['landing']['frame']:>5} at {cycle['landing']['timestamp']:>6.2f}s\n")
                    f.write(f"  Mid-Stance: Frame {cycle['mid_stance']['frame']:>5} at {cycle['mid_stance']['timestamp']:>6.2f}s\n")
                    f.write(f"  Push-Off:   Frame {cycle['push_off']['frame']:>5} at {cycle['push_off']['timestamp']:>6.2f}s\n")
                    
                    stance_duration = cycle['push_off']['timestamp'] - cycle['landing']['timestamp']
                    landing_to_mid = cycle['mid_stance']['timestamp'] - cycle['landing']['timestamp']
                    mid_to_push = cycle['push_off']['timestamp'] - cycle['mid_stance']['timestamp']
                    
                    f.write(f"\n  Stance Duration: {stance_duration:.3f}s\n")
                    f.write(f"  Landing → Mid:   {landing_to_mid:.3f}s ({100*landing_to_mid/stance_duration:.1f}% of stance)\n")
                    f.write(f"  Mid → Push-Off:  {mid_to_push:.3f}s ({100*mid_to_push/stance_duration:.1f}% of stance)\n")
                    f.write("\n")
                    
                    # Key observations for this cycle
                    f.write(f"KEY OBSERVATIONS:\n")
                    
                    # Knee flexion analysis
                    if 'knee' in cycle['landing']['angles'] and 'knee' in cycle['mid_stance']['angles']:
                        knee_flexion = cycle['landing']['angles']['knee'] - cycle['mid_stance']['angles']['knee']
                        f.write(f"  • Knee Flexion (Landing→Mid): {knee_flexion:.1f}° ")
                        if knee_flexion > 25:
                            f.write("(Good shock absorption)\n")
                        elif knee_flexion > 15:
                            f.write("(Adequate shock absorption)\n")
                        else:
                            f.write("(Limited shock absorption - may increase impact)\n")
                    
                    # Ankle angle analysis
                    if 'ankle' in cycle['landing']['angles'] and 'ankle' in cycle['push_off']['angles']:
                        ankle_change = cycle['push_off']['angles']['ankle'] - cycle['landing']['angles']['ankle']
                        f.write(f"  • Ankle Plantarflexion (Landing→Push): {ankle_change:.1f}° ")
                        if ankle_change > 25:
                            f.write("(Strong propulsion)\n")
                        elif ankle_change > 15:
                            f.write("(Moderate propulsion)\n")
                        else:
                            f.write("(Limited propulsion power)\n")
                    
                    # Hip extension
                    if 'hip' in cycle['landing']['angles'] and 'hip' in cycle['push_off']['angles']:
                        hip_extension = cycle['push_off']['angles']['hip'] - cycle['landing']['angles']['hip']
                        f.write(f"  • Hip Extension (Landing→Push): {hip_extension:.1f}°\n")
                    
                    f.write("\n")
                
                # AVERAGE VALUES SECTION
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"{side_name} - AVERAGE VALUES ACROSS ALL CYCLES\n")
                f.write("=" * 80 + "\n\n")
                
                # Calculate averages
                phase_averages = {'landing': {}, 'mid_stance': {}, 'push_off': {}}
                
                for phase_name in ['landing', 'mid_stance', 'push_off']:
                    angle_sums = {}
                    angle_counts = {}
                    
                    for cycle in phase_data:
                        for angle_name, angle_value in cycle[phase_name]['angles'].items():
                            if angle_name not in angle_sums:
                                angle_sums[angle_name] = 0
                                angle_counts[angle_name] = 0
                            angle_sums[angle_name] += angle_value
                            angle_counts[angle_name] += 1
                    
                    for angle_name in angle_sums:
                        phase_averages[phase_name][angle_name] = angle_sums[angle_name] / angle_counts[angle_name]
                
                # Display average table
                f.write(f"{'JOINT':<15} | {'LANDING':>12} | {'MID-STANCE':>12} | {'PUSH-OFF':>12} | {'ROM':>12}\n")
                f.write("-" * 80 + "\n")
                
                all_angles = set()
                for phase_name in ['landing', 'mid_stance', 'push_off']:
                    all_angles.update(phase_averages[phase_name].keys())
                
                for angle_name in sorted(all_angles):
                    landing_avg = phase_averages['landing'].get(angle_name, 0)
                    mid_avg = phase_averages['mid_stance'].get(angle_name, 0)
                    push_avg = phase_averages['push_off'].get(angle_name, 0)
                    rom = max(landing_avg, mid_avg, push_avg) - min(landing_avg, mid_avg, push_avg)
                    
                    f.write(f"{angle_name.title():<15} | {landing_avg:>10.1f}° | {mid_avg:>10.1f}° | {push_avg:>10.1f}° | {rom:>10.1f}°\n")
                
                # Average timing
                avg_duration = sum(c['push_off']['timestamp'] - c['landing']['timestamp'] for c in phase_data) / len(phase_data)
                avg_frequency = 1 / avg_duration if avg_duration > 0 else 0
                
                f.write(f"\nAVERAGE CYCLE TIMING:\n")
                f.write(f"  • Stance Duration: {avg_duration:.3f}s\n")
                f.write(f"  • Cadence: {avg_frequency:.2f} Hz ({avg_frequency * 60:.1f} steps/min)\n")
                f.write("\n")
            
            # BILATERAL COMPARISON
            if left_phase_analysis and right_phase_analysis:
                f.write("\n" + "=" * 80 + "\n")
                f.write("BILATERAL COMPARISON (LEFT vs RIGHT)\n")
                f.write("=" * 80 + "\n\n")
                
                # Calculate average angles for each side
                left_avgs = {'landing': {}, 'mid_stance': {}, 'push_off': {}}
                right_avgs = {'landing': {}, 'mid_stance': {}, 'push_off': {}}
                
                for phase_name in ['landing', 'mid_stance', 'push_off']:
                    # Left side
                    for cycle in left_phase_analysis:
                        for angle_name, angle_value in cycle[phase_name]['angles'].items():
                            if angle_name not in left_avgs[phase_name]:
                                left_avgs[phase_name][angle_name] = []
                            left_avgs[phase_name][angle_name].append(angle_value)
                    
                    # Right side
                    for cycle in right_phase_analysis:
                        for angle_name, angle_value in cycle[phase_name]['angles'].items():
                            if angle_name not in right_avgs[phase_name]:
                                right_avgs[phase_name][angle_name] = []
                            right_avgs[phase_name][angle_name].append(angle_value)
                
                # Average the lists
                for phase_name in ['landing', 'mid_stance', 'push_off']:
                    for angle_name in left_avgs[phase_name]:
                        left_avgs[phase_name][angle_name] = sum(left_avgs[phase_name][angle_name]) / len(left_avgs[phase_name][angle_name])
                    for angle_name in right_avgs[phase_name]:
                        right_avgs[phase_name][angle_name] = sum(right_avgs[phase_name][angle_name]) / len(right_avgs[phase_name][angle_name])
                
                # Compare at each phase
                for phase_name, phase_display in [('landing', 'LANDING'), ('mid_stance', 'MID-STANCE'), ('push_off', 'PUSH-OFF')]:
                    f.write(f"\n{phase_display} PHASE:\n")
                    f.write(f"{'Joint':<15} | {'Left':>12} | {'Right':>12} | {'Difference':>12} | {'Symmetry':>10}\n")
                    f.write("-" * 80 + "\n")
                    
                    all_angles = set(left_avgs[phase_name].keys()) | set(right_avgs[phase_name].keys())
                    
                    for angle_name in sorted(all_angles):
                        left_val = left_avgs[phase_name].get(angle_name, 0)
                        right_val = right_avgs[phase_name].get(angle_name, 0)
                        diff = abs(left_val - right_val)
                        
                        # Symmetry assessment
                        if diff < 5:
                            symmetry = "Excellent"
                        elif diff < 10:
                            symmetry = "Good"
                        elif diff < 15:
                            symmetry = "Fair"
                        else:
                            symmetry = "Asymmetric"
                        
                        f.write(f"{angle_name.title():<15} | {left_val:>10.1f}° | {right_val:>10.1f}° | {diff:>10.1f}° | {symmetry:>10}\n")
                
                f.write("\n")
                f.write("SYMMETRY GUIDE:\n")
                f.write("  • Excellent  (<5°):   Highly symmetric, no concerns\n")
                f.write("  • Good       (5-10°): Normal variation, acceptable\n")
                f.write("  • Fair       (10-15°): Some asymmetry, monitor\n")
                f.write("  • Asymmetric (>15°):  Significant imbalance, address\n")
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF PHASE ANALYSIS\n")
            f.write("=" * 80 + "\n")
    
    def create_joint_angle_visualization(self, df, output_folder, timestamp):
        """
        Create comprehensive joint angle visualizations from multiple views
        
        Args:
            df: DataFrame with angle data
            output_folder: Where to save visualizations
            timestamp: Timestamp for filename
        """
        angle_columns = [col for col in df.columns if 'angle' in col and col != 'neck_angle']
        
        if not angle_columns:
            return []
        
        # Set style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        visualization_files = []
        
        # 1. Angle Range Overview (Anterior View)
        fig, axes = plt.subplots(4, 2, figsize=(16, 20))
        fig.suptitle('Joint Angle Analysis - Anterior/Posterior View', fontsize=20, fontweight='bold')
        
        joint_pairs = [
            ('left_knee_angle', 'right_knee_angle', 'Knee Angles'),
            ('left_elbow_angle', 'right_elbow_angle', 'Elbow Angles'),
            ('left_hip_angle', 'right_hip_angle', 'Hip Angles'),
            ('left_shoulder_angle', 'right_shoulder_angle', 'Shoulder Angles'),
            ('left_ankle_angle', 'right_ankle_angle', 'Ankle Angles'),
            ('left_wrist_angle', 'right_wrist_angle', 'Wrist Angles')
        ]
        
        for idx, (left_col, right_col, title) in enumerate(joint_pairs):
            if idx >= len(axes.flatten()) // 2:
                break
            
            ax_left = axes[idx, 0]
            ax_right = axes[idx, 1]
            
            if left_col in df.columns:
                ax_left.plot(df['timestamp_sec'], df[left_col], 'b-', linewidth=2, label='Left')
                ax_left.fill_between(df['timestamp_sec'], df[left_col].min(), df[left_col], 
                                     alpha=0.3, color='blue')
                ax_left.set_ylabel('Angle (degrees)', fontsize=12)
                ax_left.set_title(f'{title} - Left Side', fontsize=14, fontweight='bold')
                ax_left.grid(True, alpha=0.3)
                ax_left.set_xlabel('Time (seconds)', fontsize=10)
                
                # Mark min/max points
                min_idx = df[left_col].idxmin()
                max_idx = df[left_col].idxmax()
                ax_left.scatter(df.loc[min_idx, 'timestamp_sec'], df.loc[min_idx, left_col], 
                              c='red', s=100, zorder=5, label=f'Min: {df.loc[min_idx, left_col]:.1f}°')
                ax_left.scatter(df.loc[max_idx, 'timestamp_sec'], df.loc[max_idx, left_col], 
                              c='green', s=100, zorder=5, label=f'Max: {df.loc[max_idx, left_col]:.1f}°')
                ax_left.legend(fontsize=9)
            
            if right_col in df.columns:
                ax_right.plot(df['timestamp_sec'], df[right_col], 'r-', linewidth=2, label='Right')
                ax_right.fill_between(df['timestamp_sec'], df[right_col].min(), df[right_col], 
                                      alpha=0.3, color='red')
                ax_right.set_ylabel('Angle (degrees)', fontsize=12)
                ax_right.set_title(f'{title} - Right Side', fontsize=14, fontweight='bold')
                ax_right.grid(True, alpha=0.3)
                ax_right.set_xlabel('Time (seconds)', fontsize=10)
                
                # Mark min/max points
                min_idx = df[right_col].idxmin()
                max_idx = df[right_col].idxmax()
                ax_right.scatter(df.loc[min_idx, 'timestamp_sec'], df.loc[min_idx, right_col], 
                                c='red', s=100, zorder=5, label=f'Min: {df.loc[min_idx, right_col]:.1f}°')
                ax_right.scatter(df.loc[max_idx, 'timestamp_sec'], df.loc[max_idx, right_col], 
                                c='green', s=100, zorder=5, label=f'Max: {df.loc[max_idx, right_col]:.1f}°')
                ax_right.legend(fontsize=9)
        
        plt.tight_layout()
        angle_viz_path = os.path.join(output_folder, f'joint_angles_view_{timestamp}.png')
        plt.savefig(angle_viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(angle_viz_path)
        print(f"✓ Joint angle visualization saved: {angle_viz_path}")
        
        # 2. Range of Motion Comparison (Bar Chart)
        fig, ax = plt.subplots(figsize=(14, 8))
        
        joint_ranges = {}
        for col in angle_columns:
            if col in df.columns:
                range_val = df[col].max() - df[col].min()
                joint_name = col.replace('_angle', '').replace('_', ' ').title()
                joint_ranges[joint_name] = range_val
        
        if joint_ranges:
            joints = list(joint_ranges.keys())
            ranges = list(joint_ranges.values())
            colors = ['#3498db' if 'Left' in j else '#e74c3c' if 'Right' in j else '#95a5a6' for j in joints]
            
            bars = ax.barh(joints, ranges, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_xlabel('Range of Motion (degrees)', fontsize=14, fontweight='bold')
            ax.set_title('Joint Range of Motion Comparison', fontsize=16, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}°', ha='left', va='center', fontweight='bold')
            
            # Add legend
            left_patch = mpatches.Patch(color='#3498db', label='Left Side')
            right_patch = mpatches.Patch(color='#e74c3c', label='Right Side')
            ax.legend(handles=[left_patch, right_patch], fontsize=12)
        
        plt.tight_layout()
        rom_viz_path = os.path.join(output_folder, f'range_of_motion_{timestamp}.png')
        plt.savefig(rom_viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(rom_viz_path)
        print(f"✓ Range of motion visualization saved: {rom_viz_path}")
        
        # 3. Movement Reversal Visualization
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('Movement Reversal Points Detection', fontsize=20, fontweight='bold')
        
        key_joints = ['left_knee', 'right_knee', 'left_elbow', 'right_elbow', 'left_ankle', 'right_ankle']
        
        for idx, joint in enumerate(key_joints):
            if idx >= len(axes.flatten()):
                break
            
            ax = axes[idx // 2, idx % 2]
            
            if f'{joint}_x' in df.columns:
                # Plot trajectory
                ax.plot(df['timestamp_sec'], df[f'{joint}_y'], 'b-', linewidth=1.5, alpha=0.7, label='Y-position')
                
                # Detect and mark reversals
                reversals = self.detect_movement_reversals(df, joint)
                
                if reversals:
                    # Mark reversal points
                    for rev_time in reversals:
                        rev_idx = df[df['timestamp_sec'] >= rev_time].index[0] if any(df['timestamp_sec'] >= rev_time) else None
                        if rev_idx is not None:
                            ax.axvline(x=rev_time, color='red', linestyle='--', alpha=0.5, linewidth=1)
                            ax.scatter(df.loc[rev_idx, 'timestamp_sec'], df.loc[rev_idx, f'{joint}_y'], 
                                     c='red', s=80, zorder=5, marker='*')
                
                ax.set_title(f'{joint.replace("_", " ").title()} - {len(reversals)} Reversals', 
                           fontsize=12, fontweight='bold')
                ax.set_xlabel('Time (seconds)', fontsize=10)
                ax.set_ylabel('Vertical Position (normalized)', fontsize=10)
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=9)
        
        plt.tight_layout()
        reversal_viz_path = os.path.join(output_folder, f'movement_reversals_{timestamp}.png')
        plt.savefig(reversal_viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(reversal_viz_path)
        print(f"✓ Movement reversal visualization saved: {reversal_viz_path}")
        
        return visualization_files
    
    def create_gait_analysis_visualization(self, df, output_folder, timestamp):
        """
        Create running/gait-specific visualizations
        
        Args:
            df: DataFrame with movement data
            output_folder: Where to save visualizations
            timestamp: Timestamp for filename
        """
        visualization_files = []
        
        # 1. Gait Cycle Analysis
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Gait Analysis - Running Biomechanics', fontsize=20, fontweight='bold')
        
        # Knee angles over time (gait cycle indicator)
        ax1 = axes[0, 0]
        if 'left_knee_angle' in df.columns and 'right_knee_angle' in df.columns:
            ax1.plot(df['timestamp_sec'], df['left_knee_angle'], 'b-', linewidth=2, label='Left Knee')
            ax1.plot(df['timestamp_sec'], df['right_knee_angle'], 'r-', linewidth=2, label='Right Knee')
            ax1.set_ylabel('Knee Angle (degrees)', fontsize=12)
            ax1.set_xlabel('Time (seconds)', fontsize=12)
            ax1.set_title('Knee Angle Patterns (Stance & Swing Phases)', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3)
        
        # Hip-Knee coordination
        ax2 = axes[0, 1]
        if 'left_hip_angle' in df.columns and 'left_knee_angle' in df.columns:
            ax2.scatter(df['left_hip_angle'], df['left_knee_angle'], c=df['timestamp_sec'], 
                       cmap='viridis', s=30, alpha=0.6)
            ax2.set_xlabel('Hip Angle (degrees)', fontsize=12)
            ax2.set_ylabel('Knee Angle (degrees)', fontsize=12)
            ax2.set_title('Hip-Knee Coordination (Left)', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            cbar = plt.colorbar(ax2.collections[0], ax=ax2)
            cbar.set_label('Time (s)', fontsize=10)
        
        # Ankle angle patterns
        ax3 = axes[1, 0]
        if 'left_ankle_angle' in df.columns and 'right_ankle_angle' in df.columns:
            ax3.plot(df['timestamp_sec'], df['left_ankle_angle'], 'b-', linewidth=2, label='Left Ankle')
            ax3.plot(df['timestamp_sec'], df['right_ankle_angle'], 'r-', linewidth=2, label='Right Ankle')
            ax3.set_ylabel('Ankle Angle (degrees)', fontsize=12)
            ax3.set_xlabel('Time (seconds)', fontsize=12)
            ax3.set_title('Ankle Dorsiflexion/Plantarflexion', fontsize=14, fontweight='bold')
            ax3.legend(fontsize=11)
            ax3.grid(True, alpha=0.3)
        
        # Vertical displacement (bounce)
        ax4 = axes[1, 1]
        if 'left_knee_y' in df.columns and 'right_knee_y' in df.columns:
            avg_height = (df['left_knee_y'] + df['right_knee_y']) / 2
            ax4.plot(df['timestamp_sec'], avg_height, 'g-', linewidth=2)
            ax4.fill_between(df['timestamp_sec'], avg_height.min(), avg_height, alpha=0.3, color='green')
            ax4.set_ylabel('Average Knee Height (normalized)', fontsize=12)
            ax4.set_xlabel('Time (seconds)', fontsize=12)
            ax4.set_title('Vertical Oscillation (Body Bounce)', fontsize=14, fontweight='bold')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        gait_viz_path = os.path.join(output_folder, f'gait_analysis_{timestamp}.png')
        plt.savefig(gait_viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(gait_viz_path)
        print(f"✓ Gait analysis visualization saved: {gait_viz_path}")
        
        # 2. Stride Analysis
        fig, axes = plt.subplots(2, 1, figsize=(16, 10))
        fig.suptitle('Stride Analysis', fontsize=20, fontweight='bold')
        
        # Foot strike pattern (using ankle vertical position)
        ax1 = axes[0]
        if 'left_ankle_y' in df.columns and 'right_ankle_y' in df.columns:
            ax1.plot(df['timestamp_sec'], df['left_ankle_y'], 'b-', linewidth=2, label='Left Foot', marker='o', markersize=3)
            ax1.plot(df['timestamp_sec'], df['right_ankle_y'], 'r-', linewidth=2, label='Right Foot', marker='s', markersize=3)
            
            # Detect potential foot strikes (local minima in ankle height)
            from scipy.signal import find_peaks
            left_strikes, _ = find_peaks(-df['left_ankle_y'].values, distance=10)
            right_strikes, _ = find_peaks(-df['right_ankle_y'].values, distance=10)
            
            for strike in left_strikes:
                ax1.axvline(x=df.iloc[strike]['timestamp_sec'], color='blue', linestyle=':', alpha=0.3)
            for strike in right_strikes:
                ax1.axvline(x=df.iloc[strike]['timestamp_sec'], color='red', linestyle=':', alpha=0.3)
            
            ax1.set_ylabel('Ankle Height (normalized)', fontsize=12)
            ax1.set_xlabel('Time (seconds)', fontsize=12)
            ax1.set_title(f'Foot Strike Pattern (Left: {len(left_strikes)} strikes, Right: {len(right_strikes)} strikes)', 
                         fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()  # Lower values = foot closer to ground
        
        # Stride length estimation (hip horizontal displacement)
        ax2 = axes[1]
        if 'left_hip_x' in df.columns and 'right_hip_x' in df.columns:
            hip_center_x = (df['left_hip_x'] + df['right_hip_x']) / 2
            cumulative_displacement = (hip_center_x.diff().abs().cumsum()) * 100  # Scaled for visualization
            ax2.plot(df['timestamp_sec'], cumulative_displacement, 'purple', linewidth=2)
            ax2.fill_between(df['timestamp_sec'], 0, cumulative_displacement, alpha=0.3, color='purple')
            ax2.set_ylabel('Cumulative Forward Displacement', fontsize=12)
            ax2.set_xlabel('Time (seconds)', fontsize=12)
            ax2.set_title('Forward Progression', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        stride_viz_path = os.path.join(output_folder, f'stride_analysis_{timestamp}.png')
        plt.savefig(stride_viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(stride_viz_path)
        print(f"✓ Stride analysis visualization saved: {stride_viz_path}")
        
        return visualization_files
    
    def create_phase_analysis_visualization(self, df, left_phases, right_phases, 
                                           left_phase_analysis, right_phase_analysis, 
                                           output_folder, timestamp):
        """
        Create visualizations for movement phase analysis (landing, mid-stance, push-off)
        
        Args:
            df: DataFrame with movement data
            left_phases: Phase detection results for left side
            right_phases: Phase detection results for right side
            left_phase_analysis: Phase biomechanics for left side
            right_phase_analysis: Phase biomechanics for right side
            output_folder: Where to save visualizations
            timestamp: Timestamp for filename
        """
        visualization_files = []
        
        # 1. Phase Timeline Visualization
        fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
        fig.suptitle('Movement Phase Timeline - Landing, Mid-Stance, Push-Off', fontsize=20, fontweight='bold')
        
        # Left side
        ax1 = axes[0]
        if 'left_ankle_y' in df.columns:
            ax1.plot(df['timestamp_sec'], df['left_ankle_y'], 'b-', linewidth=2, alpha=0.6, label='Ankle Height')
            
            # Mark phases
            for cycle in left_phases['cycles']:
                # Landing (red circle)
                landing_time = df.iloc[cycle['landing_frame']]['timestamp_sec']
                landing_y = df.iloc[cycle['landing_frame']]['left_ankle_y']
                ax1.scatter(landing_time, landing_y, c='red', s=200, marker='o', 
                          edgecolors='darkred', linewidths=2, label='Landing' if cycle == left_phases['cycles'][0] else '', zorder=5)
                
                # Mid-stance (green square)
                mid_time = df.iloc[cycle['mid_stance_frame']]['timestamp_sec']
                mid_y = df.iloc[cycle['mid_stance_frame']]['left_ankle_y']
                ax1.scatter(mid_time, mid_y, c='green', s=200, marker='s', 
                          edgecolors='darkgreen', linewidths=2, label='Mid-Stance' if cycle == left_phases['cycles'][0] else '', zorder=5)
                
                # Push-off (blue triangle)
                push_time = df.iloc[cycle['push_off_frame']]['timestamp_sec']
                push_y = df.iloc[cycle['push_off_frame']]['left_ankle_y']
                ax1.scatter(push_time, push_y, c='blue', s=200, marker='^', 
                          edgecolors='darkblue', linewidths=2, label='Push-Off' if cycle == left_phases['cycles'][0] else '', zorder=5)
                
                # Shade the stance phase
                ax1.axvspan(landing_time, push_time, alpha=0.1, color='yellow')
            
            ax1.set_ylabel('Ankle Vertical Position', fontsize=12, fontweight='bold')
            ax1.set_title(f'Left Side - {len(left_phases["cycles"])} Gait Cycles Detected', fontsize=14, fontweight='bold')
            ax1.legend(loc='best', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()
        
        # Right side
        ax2 = axes[1]
        if 'right_ankle_y' in df.columns:
            ax2.plot(df['timestamp_sec'], df['right_ankle_y'], 'r-', linewidth=2, alpha=0.6, label='Ankle Height')
            
            # Mark phases
            for cycle in right_phases['cycles']:
                landing_time = df.iloc[cycle['landing_frame']]['timestamp_sec']
                landing_y = df.iloc[cycle['landing_frame']]['right_ankle_y']
                ax2.scatter(landing_time, landing_y, c='red', s=200, marker='o', 
                          edgecolors='darkred', linewidths=2, label='Landing' if cycle == right_phases['cycles'][0] else '', zorder=5)
                
                mid_time = df.iloc[cycle['mid_stance_frame']]['timestamp_sec']
                mid_y = df.iloc[cycle['mid_stance_frame']]['right_ankle_y']
                ax2.scatter(mid_time, mid_y, c='green', s=200, marker='s', 
                          edgecolors='darkgreen', linewidths=2, label='Mid-Stance' if cycle == right_phases['cycles'][0] else '', zorder=5)
                
                push_time = df.iloc[cycle['push_off_frame']]['timestamp_sec']
                push_y = df.iloc[cycle['push_off_frame']]['right_ankle_y']
                ax2.scatter(push_time, push_y, c='blue', s=200, marker='^', 
                          edgecolors='darkblue', linewidths=2, label='Push-Off' if cycle == right_phases['cycles'][0] else '', zorder=5)
                
                ax2.axvspan(landing_time, push_time, alpha=0.1, color='yellow')
            
            ax2.set_ylabel('Ankle Vertical Position', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
            ax2.set_title(f'Right Side - {len(right_phases["cycles"])} Gait Cycles Detected', fontsize=14, fontweight='bold')
            ax2.legend(loc='best', fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.invert_yaxis()
        
        plt.tight_layout()
        timeline_path = os.path.join(output_folder, f'phase_timeline_{timestamp}.png')
        plt.savefig(timeline_path, dpi=150, bbox_inches='tight')
        plt.close()
        visualization_files.append(timeline_path)
        print(f"✓ Phase timeline visualization saved: {timeline_path}")
        
        # 2. Phase-Specific Angle Comparison
        if left_phase_analysis or right_phase_analysis:
            fig, axes = plt.subplots(3, 2, figsize=(16, 18))
            fig.suptitle('Joint Angles at Each Movement Phase', fontsize=20, fontweight='bold')
            
            angles_to_plot = ['knee', 'hip', 'ankle']
            phase_names = ['landing', 'mid_stance', 'push_off']
            phase_colors = {'landing': 'red', 'mid_stance': 'green', 'push_off': 'blue'}
            phase_labels = {'landing': 'Landing', 'mid_stance': 'Mid-Stance', 'push_off': 'Push-Off'}
            
            for idx, angle_name in enumerate(angles_to_plot):
                # Left side
                ax_left = axes[idx, 0]
                if left_phase_analysis:
                    for phase_name in phase_names:
                        angles = [cycle[phase_name]['angles'].get(angle_name, None) 
                                for cycle in left_phase_analysis 
                                if angle_name in cycle[phase_name]['angles']]
                        
                        if angles:
                            cycles = list(range(1, len(angles) + 1))
                            ax_left.plot(cycles, angles, marker='o', linewidth=2, markersize=8,
                                       color=phase_colors[phase_name], label=phase_labels[phase_name])
                
                ax_left.set_xlabel('Cycle Number', fontsize=11, fontweight='bold')
                ax_left.set_ylabel(f'{angle_name.title()} Angle (degrees)', fontsize=11, fontweight='bold')
                ax_left.set_title(f'Left {angle_name.title()} Angle', fontsize=13, fontweight='bold')
                ax_left.legend(fontsize=10)
                ax_left.grid(True, alpha=0.3)
                
                # Right side
                ax_right = axes[idx, 1]
                if right_phase_analysis:
                    for phase_name in phase_names:
                        angles = [cycle[phase_name]['angles'].get(angle_name, None) 
                                for cycle in right_phase_analysis 
                                if angle_name in cycle[phase_name]['angles']]
                        
                        if angles:
                            cycles = list(range(1, len(angles) + 1))
                            ax_right.plot(cycles, angles, marker='o', linewidth=2, markersize=8,
                                        color=phase_colors[phase_name], label=phase_labels[phase_name])
                
                ax_right.set_xlabel('Cycle Number', fontsize=11, fontweight='bold')
                ax_right.set_ylabel(f'{angle_name.title()} Angle (degrees)', fontsize=11, fontweight='bold')
                ax_right.set_title(f'Right {angle_name.title()} Angle', fontsize=13, fontweight='bold')
                ax_right.legend(fontsize=10)
                ax_right.grid(True, alpha=0.3)
            
            plt.tight_layout()
            angles_path = os.path.join(output_folder, f'phase_angles_{timestamp}.png')
            plt.savefig(angles_path, dpi=150, bbox_inches='tight')
            plt.close()
            visualization_files.append(angles_path)
            print(f"✓ Phase angles visualization saved: {angles_path}")
            
            # 3. Average Phase Angles Comparison (Bar Chart)
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('Average Joint Angles by Phase', fontsize=20, fontweight='bold')
            
            for side_idx, (side_name, phase_analysis) in enumerate([('Left', left_phase_analysis), ('Right', right_phase_analysis)]):
                ax = axes[side_idx]
                
                if phase_analysis:
                    # Calculate averages
                    phase_averages = {phase: {} for phase in phase_names}
                    
                    for angle_name in angles_to_plot:
                        for phase_name in phase_names:
                            angles = [cycle[phase_name]['angles'].get(angle_name, None) 
                                    for cycle in phase_analysis 
                                    if angle_name in cycle[phase_name]['angles']]
                            if angles:
                                phase_averages[phase_name][angle_name] = np.mean(angles)
                    
                    # Plot grouped bar chart
                    x = np.arange(len(angles_to_plot))
                    width = 0.25
                    
                    for i, phase_name in enumerate(phase_names):
                        values = [phase_averages[phase_name].get(angle, 0) for angle in angles_to_plot]
                        ax.bar(x + i * width, values, width, label=phase_labels[phase_name], 
                             color=phase_colors[phase_name], alpha=0.8)
                    
                    ax.set_xlabel('Joint', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Average Angle (degrees)', fontsize=12, fontweight='bold')
                    ax.set_title(f'{side_name} Side', fontsize=14, fontweight='bold')
                    ax.set_xticks(x + width)
                    ax.set_xticklabels([a.title() for a in angles_to_plot])
                    ax.legend(fontsize=11)
                    ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            avg_angles_path = os.path.join(output_folder, f'phase_avg_angles_{timestamp}.png')
            plt.savefig(avg_angles_path, dpi=150, bbox_inches='tight')
            plt.close()
            visualization_files.append(avg_angles_path)
            print(f"✓ Phase average angles visualization saved: {avg_angles_path}")
        
        return visualization_files
    
    def get_analytics_json(self):
        """
        Prepare analytics data as JSON structure for API response
        
        Returns:
            dict: Complete analytics data
        """
        if not self.frame_data:
            return {}
        
        df = pd.DataFrame(self.frame_data)
        
        # Movement reversals for key joints
        reversal_data = {}
        key_joints = ['left_knee', 'right_knee', 'left_elbow', 'right_elbow', 'left_ankle', 'right_ankle']
        for joint in key_joints:
            reversals = self.detect_movement_reversals(df, joint)
            reversal_data[joint] = {
                'count': len(reversals),
                'timestamps': reversals
            }
        
        # Angle statistics
        angle_stats = {}
        angle_columns = [col for col in df.columns if 'angle' in col]
        for col in angle_columns:
            if col in df.columns:
                angle_stats[col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'range': float(df[col].max() - df[col].min()),
                    'std': float(df[col].std())
                }
        
        # Sync info (if available)
        sync_data = None
        if hasattr(self, 'sync_info') and self.sync_info:
            sync_data = {
                'offset_seconds': self.sync_info['offset_seconds'],
                'confidence': self.sync_info['confidence'],
                'method': self.sync_info['method'],
                'front_events_count': len(self.sync_info.get('front_events', [])),
                'side_events_count': len(self.sync_info.get('side_events', []))
            }
        
        return {
            'total_frames': len(df),
            'duration_seconds': float(df['timestamp_sec'].max()),
            'fps': len(df) / df['timestamp_sec'].max(),
            'angle_statistics': angle_stats,
            'movement_reversals': reversal_data,
            'synchronization': sync_data,
            'athlete_height_cm': getattr(self, 'athlete_height_cm', None),
            'has_side_video': hasattr(self, 'sync_info') and self.sync_info is not None
        }

def main():
    """Main function to run the video annotation tool"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_annotation_tool.py <video_path> [output_folder]")
        print("Example: python video_annotation_tool.py input_video.mp4 output")
        return
    
    video_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else 'output'
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return
    
    print("=" * 60)
    print("VIDEO ANNOTATION TOOL - MediaPipe Pose Analysis")
    print("=" * 60)
    print(f"\nInput video: {video_path}")
    print(f"Output folder: {output_folder}\n")
    
    # Create tool instance
    tool = VideoAnnotationTool()
    
    # Process video
    print("Processing video...")
    timestamp = tool.process_video(video_path, output_folder)
    
    # Analyze movements
    print("\nAnalyzing movements...")
    tool.analyze_movements(output_folder, timestamp)
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"\nAll outputs saved in: {output_folder}/")
    print("\nGenerated files:")
    print("  - annotated_video_*.mp4: Video with pose overlay")
    print("  - frame_data_*.csv: Raw landmark data for each frame")
    print("  - joint_angles_minmax_*.csv: Min/Max angles for all joints with timestamps")
    print("  - joint_movements_*.csv: Movement distances in cm and velocity for each joint")
    print("  - movement_analysis_*.csv: Statistical analysis")
    print("  - summary_report_*.txt: Human-readable summary with detailed angle and distance analysis")

if __name__ == "__main__":
    main()
