"""
Batch Video Processing Script
Process multiple videos at once with the Video Annotation Tool
"""

import os
import glob
from video_annotation_tool import VideoAnnotationTool

def batch_process_videos(video_folder, output_folder='batch_output', file_pattern='*.mp4'):
    """
    Process all videos in a folder
    
    Args:
        video_folder: Folder containing video files
        output_folder: Root output folder
        file_pattern: Pattern to match video files (*.mp4, *.avi, etc.)
    """
    # Find all video files
    search_pattern = os.path.join(video_folder, file_pattern)
    video_files = glob.glob(search_pattern)
    
    if not video_files:
        print(f"No video files found matching pattern: {search_pattern}")
        return
    
    print("=" * 70)
    print(f"BATCH VIDEO PROCESSING")
    print("=" * 70)
    print(f"Found {len(video_files)} video(s) to process\n")
    
    results = []
    
    for idx, video_path in enumerate(video_files, 1):
        video_name = os.path.basename(video_path)
        print(f"\n{'=' * 70}")
        print(f"Processing {idx}/{len(video_files)}: {video_name}")
        print("=" * 70)
        
        # Create separate output folder for each video
        video_output_folder = os.path.join(output_folder, os.path.splitext(video_name)[0])
        
        try:
            # Create tool instance for this video
            tool = VideoAnnotationTool()
            
            # Process video
            timestamp = tool.process_video(video_path, video_output_folder)
            
            # Analyze movements
            print("\nAnalyzing movements...")
            tool.analyze_movements(video_output_folder, timestamp)
            
            results.append({
                'video': video_name,
                'status': 'SUCCESS',
                'output_folder': video_output_folder
            })
            
            print(f"\n✓ Successfully processed: {video_name}")
            
        except Exception as e:
            print(f"\n✗ Error processing {video_name}: {str(e)}")
            results.append({
                'video': video_name,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"\nTotal videos: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print(f"\nOutputs saved in: {output_folder}/")
    
    if failed > 0:
        print("\nFailed videos:")
        for result in results:
            if result['status'] == 'ERROR':
                print(f"  - {result['video']}: {result.get('error', 'Unknown error')}")
    
    return results

def main():
    """Main function for batch processing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <video_folder> [output_folder] [file_pattern]")
        print("\nExamples:")
        print("  python batch_process.py videos/")
        print("  python batch_process.py videos/ batch_results/")
        print("  python batch_process.py videos/ batch_results/ *.avi")
        print("\nThis will process all matching videos in the folder and create")
        print("separate output folders for each video.")
        return
    
    video_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else 'batch_output'
    file_pattern = sys.argv[3] if len(sys.argv) > 3 else '*.mp4'
    
    if not os.path.exists(video_folder):
        print(f"Error: Video folder not found: {video_folder}")
        return
    
    batch_process_videos(video_folder, output_folder, file_pattern)

if __name__ == "__main__":
    main()
