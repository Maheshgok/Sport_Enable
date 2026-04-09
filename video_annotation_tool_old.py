"""
Video Annotation Tool using Google MediaPipe
Captures movement characteristics and analyzes key joint movements
Uses MediaPipe 0.10.30+ task-based API with Python 3.13
"""

import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime

# MediaPipe 0.10.30+ uses task-based API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

class VideoAnnotationTool:
    def __init__(self):
        # Initialize MediaPipe Pose Landmarker with task-based API
        self.pose_landmarker = None
        
        # Key landmarks we want to track
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
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two 3D points"""
        return np.sqrt(
            (point1[0] - point2[0])**2 + 
            (point1[1] - point2[1])**2 + 
            (point1[2] - point2[2])**2
        )
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def process_video(self, video_path, output_folder='output', confidence_threshold=0.5):
        """
        Process video and extract pose landmarks frame by frame
        
        Args:
            video_path: Path to input video file
            output_folder: Folder to save outputs
            confidence_threshold: Minimum confidence for pose detection
        """
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
        
        frame_count = 0
        
        with self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold
        ) as pose:
            
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Convert BGR to RGB
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose
                results = pose.process(image_rgb)
                
                # Extract landmarks if detected
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    
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
                    
                    # HIP ANGLES (Shoulder-Hip-Knee) - measures torso-leg angle
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
                    
                    # SHOULDER ANGLES (Hip-Shoulder-Elbow) - measures arm position relative to torso
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
                    
                    # ANKLE ANGLES (Knee-Ankle-Foot approximation using vertical reference)
                    # Note: MediaPipe doesn't track toes, so we approximate using vertical
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
                    
                    # NECK ANGLE (between shoulders midpoint - nose - vertical)
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
                    
                    # WRIST ANGLES (Elbow-Wrist and forward direction approximation)
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
                    
                    # Calculate relative distances (normalized)
                    # Knee to hip vertical distance
                    frame_dict['left_knee_hip_distance'] = landmarks[self.key_landmarks['left_hip']].y - landmarks[self.key_landmarks['left_knee']].y
                    frame_dict['right_knee_hip_distance'] = landmarks[self.key_landmarks['right_hip']].y - landmarks[self.key_landmarks['right_knee']].y
                    
                    # Shoulder width for normalization
                    frame_dict['shoulder_width'] = abs(landmarks[self.key_landmarks['left_shoulder']].x - landmarks[self.key_landmarks['right_shoulder']].x)
                    
                    # Hip width
                    frame_dict['hip_width'] = abs(landmarks[self.key_landmarks['left_hip']].x - landmarks[self.key_landmarks['right_hip']].x)
                    
                    # Torso height (shoulder to hip)
                    left_torso = abs(landmarks[self.key_landmarks['left_shoulder']].y - landmarks[self.key_landmarks['left_hip']].y)
                    right_torso = abs(landmarks[self.key_landmarks['right_shoulder']].y - landmarks[self.key_landmarks['right_hip']].y)
                    frame_dict['torso_height'] = (left_torso + right_torso) / 2
                    
                    self.frame_data.append(frame_dict)
                    
                    # Draw pose landmarks on frame
                    self.mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
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
    
    def analyze_movements(self, output_folder='output', timestamp=None):
        """Analyze movement data and identify key metrics"""
        if not self.frame_data:
            print("No frame data to analyze!")
            return
        
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
        
        # Distance measurements (knee-hip)
        for side in ['left', 'right']:
            col = f'{side}_knee_hip_distance'
            if col in df.columns:
                analysis[f'{col}_min'] = df[col].min()
                analysis[f'{col}_max'] = df[col].max()
                analysis[f'{col}_mean'] = df[col].mean()
                analysis[f'{col}_range'] = df[col].max() - df[col].min()
        
        # Calculate movement velocity (change between frames)
        velocity_data = []
        for name in ['left_knee', 'right_knee', 'left_hip', 'right_hip', 
                     'left_shoulder', 'right_shoulder', 'left_ankle', 'right_ankle',
                     'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']:
            if f'{name}_x' in df.columns:
                dx = df[f'{name}_x'].diff()
                dy = df[f'{name}_y'].diff()
                dz = df[f'{name}_z'].diff()
                velocity = np.sqrt(dx**2 + dy**2 + dz**2)
                
                velocity_data.append({
                    'joint': name,
                    'max_velocity': velocity.max(),
                    'mean_velocity': velocity.mean(),
                    'total_movement': velocity.sum()
                })
        
        velocity_df = pd.DataFrame(velocity_data)
        velocity_csv_path = os.path.join(output_folder, f'joint_velocities_{timestamp}.csv')
        velocity_df.to_csv(velocity_csv_path, index=False)
        print(f"✓ Joint velocity data saved: {velocity_csv_path}")
        
        # Create detailed joint angle analysis
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
            f.write(f"Average FPS: {len(df) / df['timestamp_sec'].max():.1f}\n\n")
            
            # Organize angles by joint type
            knee_angles = [col for col in angle_columns if 'knee' in col]
            elbow_angles = [col for col in angle_columns if 'elbow' in col]
            hip_angles = [col for col in angle_columns if 'hip' in col]
            shoulder_angles = [col for col in angle_columns if 'shoulder' in col]
            ankle_angles = [col for col in angle_columns if 'ankle' in col]
            wrist_angles = [col for col in angle_columns if 'wrist' in col]
            neck_angles = [col for col in angle_columns if 'neck' in col]
            
            # KNEE ANALYSIS
            if knee_angles:
                f.write("=" * 80 + "\n")
                f.write("KNEE ANGLES (Hip-Knee-Ankle)\n")
                f.write("=" * 80 + "\n")
                for col in knee_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum (most bent): {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum (most straight): {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # ELBOW ANALYSIS
            if elbow_angles:
                f.write("=" * 80 + "\n")
                f.write("ELBOW ANGLES (Shoulder-Elbow-Wrist)\n")
                f.write("=" * 80 + "\n")
                for col in elbow_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum (most bent): {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum (most straight): {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # HIP ANALYSIS
            if hip_angles:
                f.write("=" * 80 + "\n")
                f.write("HIP ANGLES (Shoulder-Hip-Knee)\n")
                f.write("=" * 80 + "\n")
                for col in hip_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # SHOULDER ANALYSIS
            if shoulder_angles:
                f.write("=" * 80 + "\n")
                f.write("SHOULDER ANGLES (Hip-Shoulder-Elbow)\n")
                f.write("=" * 80 + "\n")
                for col in shoulder_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # ANKLE ANALYSIS
            if ankle_angles:
                f.write("=" * 80 + "\n")
                f.write("ANKLE ANGLES (Knee-Ankle-Vertical)\n")
                f.write("=" * 80 + "\n")
                for col in ankle_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # WRIST ANALYSIS
            if wrist_angles:
                f.write("=" * 80 + "\n")
                f.write("WRIST ANGLES (Elbow-Wrist-Forward)\n")
                f.write("=" * 80 + "\n")
                for col in wrist_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            # NECK ANALYSIS
            if neck_angles:
                f.write("=" * 80 + "\n")
                f.write("NECK ANGLE (Head Position)\n")
                f.write("=" * 80 + "\n")
                for col in neck_angles:
                    min_idx = df[col].idxmin()
                    max_idx = df[col].idxmax()
                    f.write(f"\n{col.replace('_', ' ').title()}:\n")
                    f.write(f"  Minimum: {df[col].min():.2f}° at frame {df.loc[min_idx, 'frame']} ({df.loc[min_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Maximum: {df[col].max():.2f}° at frame {df.loc[max_idx, 'frame']} ({df.loc[max_idx, 'timestamp_sec']:.2f}s)\n")
                    f.write(f"  Range of Motion: {df[col].max() - df[col].min():.2f}°\n")
                    f.write(f"  Mean Angle: {df[col].mean():.2f}°\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("MOST ACTIVE JOINTS (by total movement)\n")
            f.write("=" * 80 + "\n")
            sorted_velocity = velocity_df.sort_values('total_movement', ascending=False)
            for idx, row in sorted_velocity.head(10).iterrows():
                f.write(f"{row['joint'].replace('_', ' ').title()}: {row['total_movement']:.4f}\n")
        
        print(f"✓ Summary report saved: {report_path}")
        
        return analysis

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
    print("  - joint_velocities_*.csv: Movement velocity for each joint")
    print("  - movement_analysis_*.csv: Statistical analysis")
    print("  - summary_report_*.txt: Human-readable summary with detailed angle analysis")

if __name__ == "__main__":
    main()
