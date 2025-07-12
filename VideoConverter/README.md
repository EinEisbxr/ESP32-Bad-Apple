# Video to Hex Converter

A Python script that converts video files to hex byte arrays, perfect for embedded systems projects like ESP32 displays.

## Features

-   **Customizable Resolution**: Specify target width and height for frames
-   **Adjustable Framerate**: Control the output framerate to match your display needs
-   **Grayscale/Color Options**: Choose between grayscale (1 byte per pixel) or color (3 bytes per pixel)
-   **Multiple Output Formats**: C arrays, plain hex, or Python lists
-   **Optimized Processing**: Automatically skips frames to achieve target framerate

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py input_video.mp4
```

This will create a hex file with default settings:

-   Resolution: 128x64 pixels
-   Framerate: 10 FPS
-   Grayscale output
-   C array format

### Advanced Usage

```bash
python main.py input_video.mp4 -w 64 -H 32 -f 15 --color --format python_list -o output.txt
```

### Command Line Options

-   `input`: Input video file path (required)
-   `-o, --output`: Output file path (optional, auto-generated if not specified)
-   `-w, --width`: Target width in pixels (default: 128)
-   `-H, --height`: Target height in pixels (default: 64)
-   `-f, --fps`: Target framerate (default: 10)
-   `--color`: Keep color information (default is grayscale)
-   `--format`: Output format - `c_array`, `plain_hex`, or `python_list` (default: c_array)

### Examples

#### For ESP32 OLED Display (128x64 monochrome)

```bash
python main.py badapple.mp4 -w 128 -H 64 -f 10
```

#### For Small Color Display (64x32)

```bash
python main.py video.mp4 -w 64 -H 32 -f 8 --color
```

#### High Framerate Grayscale

```bash
python main.py input.mp4 -w 96 -H 48 -f 20
```

## Output Formats

### C Array Format (default)

Generates a C-compatible array with frame data and helpful defines:

```c
const unsigned char video_data[FRAMES][WIDTH*HEIGHT] = {
  // Frame 0
  {0x00, 0x15, 0x2A, ...},
  // Frame 1
  {0x11, 0x26, 0x3B, ...}
};
```

### Plain Hex Format

Simple hex values without formatting:

```
# Frame 0
00 15 2A FF 88 CC
# Frame 1
11 26 3B EE 99 DD
```

### Python List Format

Python-compatible list format:

```python
video_data = [
    # Frame 0
    [0x00, 0x15, 0x2A, ...],
    # Frame 1
    [0x11, 0x26, 0x3B, ...]
]
```

## Technical Details

-   **Grayscale**: Each pixel is represented as 1 byte (0x00-0xFF)
-   **Color**: Each pixel uses 3 bytes in BGR format (Blue, Green, Red)
-   **Frame Skipping**: Automatically calculated based on original FPS and target FPS
-   **Interpolation**: Uses area-based interpolation for high-quality resizing

## Tips for ESP32 Projects

1. **Memory Management**: Keep resolution and frame count reasonable for your ESP32's memory
2. **Storage**: Consider using PROGMEM for storing large arrays in flash memory
3. **Streaming**: For long videos, consider splitting into chunks or streaming from SD card
4. **Display Timing**: Match your target FPS to your display's refresh capabilities

## Example ESP32 Integration

```c
#include "video_data.h"  // Generated hex file

void displayFrame(int frameIndex) {
    const unsigned char* frame = video_data[frameIndex];
    // Display frame on your screen
    display.drawBitmap(0, 0, frame, FRAME_WIDTH, FRAME_HEIGHT, WHITE);
    display.display();
}

void playVideo() {
    for (int i = 0; i < FRAME_COUNT; i++) {
        displayFrame(i);
        delay(1000 / TARGET_FPS);  // Adjust timing as needed
    }
}
```

## Supported Video Formats

The converter supports any video format that OpenCV can read:

-   MP4, AVI, MOV, MKV
-   WebM, FLV, WMV
-   And many more

## Performance Notes

-   Processing time depends on video length, resolution, and target settings
-   Larger resolutions and higher framerates will create larger output files
-   Consider your ESP32's memory limitations when choosing settings
