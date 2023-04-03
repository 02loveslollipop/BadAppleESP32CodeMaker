import sys
import cv2
import numpy as np
from PIL import Image
import os
import optFunc

threshold = 60
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
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', 'test.mp4', '-r', '120x80', '-lc','-a']
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
        elif args[i] == "-lc" and resize == False:
            resample = cv2.INTER_LANCZOS4
            resize = True
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-nr" and resize == False:
            resample = cv2.INTER_NEAREST
            resize = True
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bc" and resize == False:
            resample = cv2.INTER_CUBIC
            resize = True
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bl" and resize == False:
            resample = cv2.INTER_LINEAR
            resize = True
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-b2" and resize == False:
            resample = cv2.INTER_BITS2
            resize = True
        elif args[i] == "-b2" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-ar" and resize == False:
            resample = cv2.INTER_AREA
            resize = True
        elif args[i] == "-ar" and resize == True:
            print("You can only use 1 resize algoritm")
        elif nex_i:
            nex_i = False
        elif args[i] == "-a":
            batch=True
        elif custom_res:
            path = args[i]
        elif not custom_res and not ready:
            path = args[i]
            vid = cv2.VideoCapture(path)
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            ready = True
        elif not ready:
            path = args[i]
            vid = cv2.VideoCapture(path)
            ready = True
        else: 
            print(f"{args[i]} has not been recognize as a valid argument")
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

l_subframes = []
l_frames_compress = []
sub_frame_finded = 0
sub_frame_not_finded = 0
total_frames = 0
clear()
print("Creating and assigning subframe table")
for frame in lFrames:
    subframe_map = np.zeros(shape=(int(width/l_pattern),int(height/l_pattern)),dtype=int)
    for i in range(len(subframe_map)):
        for j in range(len(subframe_map[0])):
            subframe = np.zeros(shape=(l_pattern,l_pattern),dtype=bool)
            for subframe_i in range(l_pattern):
                for subframe_j in range(l_pattern):
                    subframe[subframe_i][subframe_j] = frame[(i*l_pattern)+(subframe_i)][(j*l_pattern)+(subframe_j)]
            try:
                val = optFunc.findSubFrame(list_buffer=l_subframes,subframe=subframe)
                sub_frame_finded += 1
            except Exception as e:
                l_subframes.append(subframe)
                val = int(len(l_subframes)-1)
                sub_frame_not_finded += 1
            finally:
                subframe_map[i][j] = val
                total_frames += 1
    l_frames_compress.append(subframe_map)
    
clear()
print(f"Total subframes: {total_frames}\nSubframes not compress: {sub_frame_not_finded}\nsubframes compress: {sub_frame_finded}")

if batch:
    SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)
elif input() == "1":
    print("Press 1 to save result as Photo list\nPress anything else to exit the program")
    SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)
    

    
                        

                
                    
                    
                        
                        
                        



                   
                        
                    
                
            
        
    

