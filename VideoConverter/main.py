#!/usr/bin/env python3
"""
Video to Hex Converter
Converts video files to hex byte arrays with customizable resolution, framerate, and grayscale options.
Useful for embedded systems like ESP32 projects.
"""

import cv2
import numpy as np
import argparse
import os
import sys
from pathlib import Path


class VideoToHexConverter:
    def __init__(self, input_path, output_path=None, width=128, height=64, fps=10, grayscale=True):
        """
        Initialize the video converter
        
        Args:
            input_path (str): Path to input video file
            output_path (str): Path to output file (optional)
            width (int): Target width for frames
            height (int): Target height for frames
            fps (int): Target framerate
            grayscale (bool): Convert to grayscale
        """
        self.input_path = input_path
        self.width = width
        self.height = height
        self.target_fps = fps
        self.grayscale = grayscale
        self.output_path = output_path or self._generate_output_path()
        self.frames_data = []
        
    def _generate_output_path(self):
        """Generate output filename based on input filename"""
        input_file = Path(self.input_path)
        suffix = f"_{self.width}x{self.height}_{self.target_fps}fps"
        if self.grayscale:
            suffix += "_grayscale"
        return input_file.parent / f"{input_file.stem}{suffix}_hex.txt"
    
    def load_video(self):
        """Load and validate the video file"""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Video file not found: {self.input_path}")
        
        self.cap = cv2.VideoCapture(self.input_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {self.input_path}")
        
        # Get original video properties
        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Original video: {self.original_width}x{self.original_height} @ {self.original_fps:.2f} FPS")
        print(f"Total frames: {self.total_frames}")
        print(f"Target: {self.width}x{self.height} @ {self.target_fps} FPS")
    
    def process_frames(self):
        """Process video frames according to specified parameters"""
        frame_skip = max(1, int(self.original_fps / self.target_fps))
        frame_count = 0
        processed_count = 0
        
        print(f"Processing every {frame_skip} frame(s)...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Skip frames to achieve target FPS
            if frame_count % frame_skip == 0:
                processed_frame = self._process_single_frame(frame)
                self.frames_data.append(processed_frame)
                processed_count += 1
                
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count} frames...")
            
            frame_count += 1
        
        self.cap.release()
        print(f"Total processed frames: {processed_count}")
    
    def _process_single_frame(self, frame):
        """Process a single frame: resize, convert to grayscale if needed, and convert to hex"""
        # Resize frame
        resized = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        
        # Convert to grayscale if requested
        if self.grayscale:
            if len(resized.shape) == 3:
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            else:
                gray = resized
            
            # Convert to hex bytes
            hex_data = []
            for row in gray:
                for pixel in row:
                    hex_data.append(f"0x{pixel:02X}")
            
            return hex_data
        else:
            # Keep color (BGR format)
            hex_data = []
            for row in resized:
                for pixel in row:
                    # BGR format
                    b, g, r = pixel
                    hex_data.extend([f"0x{b:02X}", f"0x{g:02X}", f"0x{r:02X}"])
            
            return hex_data
    
    def save_hex_data(self, format_type="c_array"):
        """
        Save hex data to file in specified format
        
        Args:
            format_type (str): Output format - 'c_array', 'plain_hex', or 'python_list'
        """
        with open(self.output_path, 'w') as f:
            if format_type == "c_array":
                self._write_c_array_format(f)
            elif format_type == "plain_hex":
                self._write_plain_hex_format(f)
            elif format_type == "python_list":
                self._write_python_list_format(f)
            else:
                raise ValueError(f"Unknown format type: {format_type}")
        
        print(f"Hex data saved to: {self.output_path}")
    
    def _write_c_array_format(self, file):
        """Write data in C array format"""
        channels = 1 if self.grayscale else 3
        file.write(f"// Video data: {len(self.frames_data)} frames, {self.width}x{self.height}, {channels} channel(s)\n")
        file.write(f"// Generated from: {self.input_path}\n\n")
        
        file.write(f"const unsigned char video_data[{len(self.frames_data)}][{self.width * self.height * channels}] = {{\n")
        
        for i, frame in enumerate(self.frames_data):
            file.write(f"  // Frame {i}\n  {{")
            
            for j, hex_byte in enumerate(frame):
                if j % 16 == 0:
                    file.write("\n    ")
                file.write(f"{hex_byte}")
                if j < len(frame) - 1:
                    file.write(", ")
            
            file.write("\n  }")
            if i < len(self.frames_data) - 1:
                file.write(",")
            file.write("\n")
        
        file.write("};\n\n")
        file.write(f"#define FRAME_COUNT {len(self.frames_data)}\n")
        file.write(f"#define FRAME_WIDTH {self.width}\n")
        file.write(f"#define FRAME_HEIGHT {self.height}\n")
        file.write(f"#define FRAME_CHANNELS {channels}\n")
    
    def _write_plain_hex_format(self, file):
        """Write data as plain hex values"""
        file.write(f"# Video data: {len(self.frames_data)} frames, {self.width}x{self.height}\n")
        file.write(f"# Generated from: {self.input_path}\n\n")
        
        for i, frame in enumerate(self.frames_data):
            file.write(f"# Frame {i}\n")
            for j, hex_byte in enumerate(frame):
                if j % 16 == 0 and j > 0:
                    file.write("\n")
                file.write(f"{hex_byte[2:]} ")  # Remove 0x prefix
            file.write("\n\n")
    
    def _write_python_list_format(self, file):
        """Write data as Python list"""
        file.write(f"# Video data: {len(self.frames_data)} frames, {self.width}x{self.height}\n")
        file.write(f"# Generated from: {self.input_path}\n\n")
        
        file.write("video_data = [\n")
        for i, frame in enumerate(self.frames_data):
            file.write(f"    # Frame {i}\n    [")
            for j, hex_byte in enumerate(frame):
                if j % 16 == 0 and j > 0:
                    file.write("\n     ")
                file.write(f"{hex_byte}")
                if j < len(frame) - 1:
                    file.write(", ")
            file.write("]")
            if i < len(self.frames_data) - 1:
                file.write(",")
            file.write("\n")
        file.write("]\n")
    
    def get_stats(self):
        """Get conversion statistics"""
        if not self.frames_data:
            return "No data processed yet"
        
        channels = 1 if self.grayscale else 3
        bytes_per_frame = self.width * self.height * channels
        total_bytes = len(self.frames_data) * bytes_per_frame
        
        return f"""
Conversion Statistics:
- Frames: {len(self.frames_data)}
- Resolution: {self.width}x{self.height}
- Channels: {channels} ({'Grayscale' if self.grayscale else 'Color'})
- Bytes per frame: {bytes_per_frame}
- Total bytes: {total_bytes}
- File size estimate: {total_bytes / 1024:.2f} KB
"""


def main():
    parser = argparse.ArgumentParser(description="Convert video to hex bytes for embedded systems")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-w", "--width", type=int, default=128, help="Target width (default: 128)")
    parser.add_argument("-H", "--height", type=int, default=64, help="Target height (default: 64)")
    parser.add_argument("-f", "--fps", type=int, default=10, help="Target framerate (default: 10)")
    parser.add_argument("--color", action="store_true", help="Keep color (default is grayscale)")
    parser.add_argument("--format", choices=["c_array", "plain_hex", "python_list"], 
                       default="c_array", help="Output format (default: c_array)")
    
    args = parser.parse_args()
    # Create converter
    converter = VideoToHexConverter(
        input_path=args.input,
        output_path=args.output,
        width=args.width,
        height=args.height,
        fps=args.fps,
        grayscale=not args.color
    )
    
    # Process video
    print("Loading video...")
    converter.load_video()
    
    print("Processing frames...")
    converter.process_frames()
    
    print("Saving hex data...")
    converter.save_hex_data(args.format)
    
    print(converter.get_stats())
    print("Conversion completed successfully!")
    


if __name__ == "__main__":
    main()