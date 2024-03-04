# Bad Apple ESP32 Code Maker
> A Python utility to convert a video into a C array for the ESP32.

## Intro
This is a Python based utility to convert a video into a C array for the ESP32. The video is converted into a 1bit np array that is delta encoded and RLE compressed. The output is a C char array that can be used in the ESP32 code, to display the video on a composite video output.

## Requirements
- [anaconda](https://www.anaconda.com/download) or [miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) for managing the python environment

- a C compiler (gcc, clang, etc.) as Cython requires a C compiler to build the extension

- [ffmpeg](https://ffmpeg.org/download.html) for video processing (optional)

- [Arduino IDE](https://www.arduino.cc/en/software) for ESP32 development

## Setup
1. download the repository:
```bash
git clone https://github.com/02loveslollipop/BadAppleESP32CodeMaker.git
```
2. (Windows) execute setup.ps1 script:
```powershell
.\setup.ps1
```
2. (Linux) execute setup.sh script:
```bash
./setup.sh
```
3. Execute the utility:
```bash
