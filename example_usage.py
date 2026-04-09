"""
Simple example showing how to use the Video Annotation Tool programmatically
"""

from video_annotation_tool import VideoAnnotationTool
import pandas as pd

def simple_example():
    """Simple example: Process one video and get basic stats"""
    
    # Step 1: Create tool instance
    tool = VideoAnnotationTool()
    
    # Step 2: Process video
    print("Processing video...")
    video_path = "your_video.mp4"  # Change this to your video file
    timestamp = tool.process_video(video_path, output_folder='my_analysis')
    
    # Step 3: Analyze movements
    print("\nAnalyzing movements...")
    analysis = tool.analyze_movements('my_analysis', timestamp)
    
    print("\n✓ Processing complete!")
    print(f"Check 'my_analysis/' folder for outputs")
    
    # Step 4: Load and examine the data
    df = pd.DataFrame(tool.frame_data)
    
    print(f"\nCaptured {len(df)} frames")
    print(f"Duration: {df['timestamp_sec'].max():.2f} seconds")
    
    # Print some interesting stats
    print(f"\nLeft knee angle range: {df['left_knee_angle'].min():.1f}° to {df['left_knee_angle'].max():.1f}°")
    print(f"Right knee angle range: {df['right_knee_angle'].min():.1f}° to {df['right_knee_angle'].max():.1f}°")

def custom_analysis_example():
    """Example: Process video and do custom analysis"""
    
    tool = VideoAnnotationTool()
    
    # Process video
    video_path = "your_video.mp4"
    timestamp = tool.process_video(video_path, output_folder='custom_output')
    
    # Get the data as DataFrame
    df = pd.DataFrame(tool.frame_data)
    
    # Custom analysis: Find when knee angle is smallest (deepest squat)
    deepest_squat_frame = df['left_knee_angle'].idxmin()
    deepest_squat_angle = df.loc[deepest_squat_frame, 'left_knee_angle']
    deepest_squat_time = df.loc[deepest_squat_frame, 'timestamp_sec']
    
    print(f"\nDeepest squat:")
    print(f"  Frame: {df.loc[deepest_squat_frame, 'frame']}")
    print(f"  Time: {deepest_squat_time:.2f} seconds")
    print(f"  Angle: {deepest_squat_angle:.1f}°")
    
    # Find highest jump (lowest hip position)
    highest_jump_frame = df['left_hip_y'].idxmin()
    highest_jump_time = df.loc[highest_jump_frame, 'timestamp_sec']
    
    print(f"\nHighest jump:")
    print(f"  Frame: {df.loc[highest_jump_frame, 'frame']}")
    print(f"  Time: {highest_jump_time:.2f} seconds")
    
    # Calculate average shoulder width
    avg_shoulder_width = df['shoulder_width'].mean()
    print(f"\nAverage shoulder width: {avg_shoulder_width:.4f} (normalized units)")

def compare_two_videos_example():
    """Example: Compare movement between two videos"""
    
    videos = [
        ("athlete1.mp4", "athlete1_output"),
        ("athlete2.mp4", "athlete2_output")
    ]
    
    results = []
    
    for video_path, output_folder in videos:
        print(f"\nProcessing {video_path}...")
        
        tool = VideoAnnotationTool()
        timestamp = tool.process_video(video_path, output_folder)
        
        df = pd.DataFrame(tool.frame_data)
        
        # Calculate key metrics
        results.append({
            'video': video_path,
            'max_knee_bend': df['left_knee_angle'].min(),
            'avg_knee_angle': df['left_knee_angle'].mean(),
            'knee_range_of_motion': df['left_knee_angle'].max() - df['left_knee_angle'].min()
        })
    
    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    for result in results:
        print(f"\n{result['video']}:")
        print(f"  Max knee bend: {result['max_knee_bend']:.1f}°")
        print(f"  Average knee angle: {result['avg_knee_angle']:.1f}°")
        print(f"  Range of motion: {result['knee_range_of_motion']:.1f}°")

def export_specific_joints_example():
    """Example: Export only specific joints to CSV"""
    
    tool = VideoAnnotationTool()
    
    # Process video
    video_path = "your_video.mp4"
    tool.process_video(video_path, output_folder='selective_output')
    
    # Get full data
    df = pd.DataFrame(tool.frame_data)
    
    # Select only knee and hip data
    knee_hip_columns = ['frame', 'timestamp_sec'] + [
        col for col in df.columns 
        if 'knee' in col or 'hip' in col
    ]
    
    knee_hip_df = df[knee_hip_columns]
    
    # Save to custom CSV
    knee_hip_df.to_csv('selective_output/knee_hip_only.csv', index=False)
    print("✓ Saved knee and hip data only")

def find_specific_movements_example():
    """Example: Find specific movement patterns"""
    
    tool = VideoAnnotationTool()
    
    # Process video
    video_path = "your_video.mp4"
    tool.process_video(video_path, output_folder='pattern_output')
    
    df = pd.DataFrame(tool.frame_data)
    
    # Find all frames where knee angle is less than 90° (deep bend)
    deep_bend_frames = df[df['left_knee_angle'] < 90]
    
    print(f"\nFound {len(deep_bend_frames)} frames with deep knee bend (<90°)")
    print("\nDeep bend moments:")
    for idx, row in deep_bend_frames.iterrows():
        print(f"  Frame {row['frame']} at {row['timestamp_sec']:.2f}s: {row['left_knee_angle']:.1f}°")
    
    # Find when wrist is above shoulder (arm raised)
    arm_raised_frames = df[df['left_wrist_y'] < df['left_shoulder_y']]
    
    print(f"\n\nFound {len(arm_raised_frames)} frames with left arm raised")

# Uncomment the example you want to run:
if __name__ == "__main__":
    print("Video Annotation Tool - Usage Examples")
    print("=" * 60)
    print("\nEdit this file and uncomment the example you want to run:\n")
    print("1. simple_example() - Basic usage")
    print("2. custom_analysis_example() - Custom metrics")
    print("3. compare_two_videos_example() - Compare multiple videos")
    print("4. export_specific_joints_example() - Export selective data")
    print("5. find_specific_movements_example() - Pattern detection")
    print("\n" + "=" * 60)
    
    # Uncomment one of these to run:
    # simple_example()
    # custom_analysis_example()
    # compare_two_videos_example()
    # export_specific_joints_example()
    # find_specific_movements_example()
