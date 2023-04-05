import sys
import cv2
import numpy as np
from PIL import Image
import os
import optFunc
import csv
import pandas as pd
import struct

threshold = 60

def count_frames(path: str):
    try:
        return int(cv2.VideoCapture(path).get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    except:
        return int(count_frames_manual(cv2.VideoCapture(path)))

def count_frames_manual(video):
	# initialize the total number of frames read
	total = 0
	# loop over the frames of the video
	while True:
		(grabbed, frame) = video.read()
		if not grabbed:
			break
		total += 1
	return total

def clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def SaveResultAsPhotoList(patternList,frameList,width,height,patternSize):
    frameCount = 1
    frameBuffer = np.zeros((width,height,3),dtype=float)
    for frame in frameList:
        for i in range(int(width/l_pattern)):
            for j in range(int(height/l_pattern)):
                bufferSubframe = patternList[frame[i][j]]  
                for subframe_i in range(patternSize):
                    for subframe_j in range(patternSize):
                        if bufferSubframe[subframe_i][subframe_j]:
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][0] = 0
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][1] = 0
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][2] = 0
                        else:
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][0] = 255
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][1] = 255
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][2] = 255
        cv2.imwrite(filename=f"{frameCount:05d}.png",img=frameBuffer)
        frameCount += 1

args = sys.argv
#print(args)
args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', './media/320x240.mp4', '-r', '32x16', '-lc']
if len(args) <= 1:
    print("You must give at least the video path")
    exit()
else:
    l_pattern = 8
    dither = False
    nex_i = False
    custom_res = False
    ready = False
    resize = False
    resample = Image.LANCZOS
    batch = False
    save_photo = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif(args[i] == "-r"):
            height = int(args[i+1].split("x")[0])
            width = int(args[i+1].split("x")[1])
            custom_res = True
            nex_i = True
        elif args[i] == "-d":
            dither = True
        elif args[i] == "-sv":
            dither = True
        elif args[i] == "-lc" and resize == False:
            resample = cv2.INTER_LANCZOS4
            resize = True
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-nr" and resize == False:
            resample = cv2.INTER_NEAREST
            resize = True
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bc" and resize == False:
            resample = cv2.INTER_CUBIC
            resize = True
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bl" and resize == False:
            resample = cv2.INTER_LINEAR
            resize = True
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-b2" and resize == False:
            resample = cv2.INTER_BITS2
            resize = True
        elif args[i] == "-b2" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-ar" and resize == False:
            resample = cv2.INTER_AREA
            resize = True
        elif args[i] == "-ar" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif nex_i:
            nex_i = False
        elif args[i] == "-bt":
            batch=True
        elif custom_res:
            path = args[i]
        elif not custom_res and not ready:
            path = args[i]
            try:
                vid = cv2.VideoCapture(path)
            except FileNotFoundError:
                print("cv2 could not open the video file, please check the path or if the file is in use")
                exit()
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            ready = True
        elif not ready:
            path = args[i]
            try:
                vid = cv2.VideoCapture(path)
            except FileNotFoundError:
                print("cv2 could not open the video file, please check the path or if the file is in use")
                exit()
            ready = True
        else: 
            print(f"{args[i]} has not been recognize as a valid argument")

totalFrames = count_frames(path)

if not batch:
    clear()
    print(f"----SUMMARY----\nFile path: {path}\nDither: {dither}\nResample algoritm: {resample}\nHeight: {height}\nWidth: {width}\nPress 1 to make a test of the algoritm method\nPress any other button to start the convertion")
    sel = input()
    if sel == "1":
        clear()
        print("Frame to test: ")
        frame = int(input())
        sus = True
        con = 0
        while sus and frame != con:
            sus,img = vid.read()
            con += 1
        imgTest = cv2.resize(src=img,dsize=(height,width),interpolation=resample)
        cv2.imwrite(filename="test.png",img=imgTest)
        clear()
        print("File save as test.png, press any button to start convertion\n\nDuring convertion press ESC to cancel the process")
        input()
    else:     
        clear()
        print("Press any button to start convertion\n\nDuring convertion press ESC to cancel the process")

if resize:
    lFrames = optFunc.convertionWithResize(width=width,height=height,video=vid,resample=resample,threshold=threshold)
else:
    lFrames = optFunc.convertion(width=width,height=height,video=vid,threshold=threshold)

l_subframes, l_frames_compress, total, sub_frame_not_finded, numberSubframes = optFunc.solveSubframe(frameBuffer=lFrames,totalFrames=totalFrames,width=width,height=height,l_pattern = l_pattern)

if batch:
    print(f"Total subframes: {total}\nCompress subframes: {numberSubframes}\nNot compress subframes: {sub_frame_not_finded}")
else:
    clear()
    print(f"Total subframes: {total}\nCompress subframes: {numberSubframes}\nNot compress subframes: {sub_frame_not_finded}\nPress any button to save the result")
    input()
    
while True: #Save "binarySubframeList.bin"
    try:
        # 1 is white, 0 is black 
        with open ('binarySubframeList.bin','wb') as f:
            binaryListBuffer = []
            byteBuffer = 0
            k = 0
            for subframe in l_subframes:
                for i in range(len(subframe)):
                    for j in range(len(subframe[0])):
                        if k == 8:
                            binaryListBuffer.append(byteBuffer)
                            byteBuffer = 0
                            k = 0
                        if subframe[i][j]:
                            byteBuffer+=(1*(2**k))
                        k+=1
            
            f.write(bytearray(binaryListBuffer))
            f.close()
            break    
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()
        
while True: #Save "binaryCompressFrame.bin"
    try:
        # 1 is white, 0 is black 
        with open ('binaryCompressFrame.bin','wb') as f:
            binaryCompressFrame = []

            for frame in l_frames_compress:
                for line in frame:
                    for dot in line:
                        f.write(int(dot).to_bytes(8,"big"))
            
            f.close()
            break    
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()

while True: #Save "l_frames_compressed.ztfl"
    try: 
        with open ('l_frames_compressed.ztfl','w') as f:
            write = csv.writer(f)
            write.writerows(l_frames_compress)
        break
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()

while True: #Save "l_subframes.ztsl"
    try:
        with open ('l_subframes.ztsl','w') as f:
            write = csv.writer(f)
            write.writerows(l_subframes)
        break
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()
        
if save_photo:
    SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)
else:
    clear()
    print("Press 1 to save result as Photo list\nPress anything else to exit the program")
    if input() == "1":
        SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)