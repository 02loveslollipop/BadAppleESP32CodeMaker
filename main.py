import sys
import cv2
import numpy as np
from PIL import Image

def count_frames(path: str, manual:str=False):
    if manual:
        return int(count_frames_manual(cv2.VideoCapture(path)))
    else:
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

def convertionWithResize(height: int,width: int,video,resample):
    count = 0
    success = True
    l_vectors = []
    while True:
        vector = np.zeros(shape=(width,height),dtype=bool)
        success,image = video.read()
        if not success:
            break
        imgArray = np.asarray(cv2.resize(src=image,dsize=(height,width),interpolation=resample))
        for j in range(len(imgArray[1])-1):
            for i in range(len(imgArray)-1):
                if imgArray[i][j][0] >= 128 and imgArray[i][j][1] >= 128 and imgArray[i][j][2] >= 128:
                    vector[i][j] = True
                else:
                    vector[i][j] = False
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector)           
        count += 1
    return l_vectors

def convertion(height: int,width: int,video):
    count = 0
    success = True
    l_vectors = []
    while True:
        vector = np.zeros(shape=(height,width),dtype=bool)
        success,image = video.read()
        if not success:
            break
        imgArray = np.asarray(image)
        for i in range(height-1):
            for j in range(width-1):
                if imgArray[i][j][0] >= 128 and imgArray[i][j][1] >= 128 and imgArray[i][j][2] >= 128:
                    vector[i][j] = False
                else:
                    vector[i][j] = True
        print(f"Cached frame: {count+1}")
        l_vectors.append(vector) 
        count += 1
    return l_vectors

def findSubFrame(list_buffer,subframe):
    val = 0
    for listed_subframes in list_buffer:
        
        if np.array_equal(listed_subframes,subframe):
            return int(val)
        else:
            val += 1
            
    raise Exception("subFrame not found")

args = sys.argv
#print(args)
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', '1.mp4', '-r', '16x8', '-lc']
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
if not batch:
    print(f"----SUMMARY----\nFile path: {path}\nDither: {dither}\nResample algoritm: {resample}\nHeight: {height}\nWidth: {width}\nThe convertion will start, Press 1 to make a test of the resample algoritm\npress anything else to start the convertion.")
    sel = input()
    if sel == "1":
        print("Frame for testing: ")
        frame = int(input())
        sus = True
        con = 0
        while sus and frame != con:
            sus,img = vid.read()
            con += 1
        imgTest = cv2.resize(src=img,dsize=(height,width),interpolation=resample)
        cv2.imwrite(filename="test.png",img=imgTest)
        print("File save as test.png, press any button to start convertion\n\nDuring convertion press ESC to cancel the process")
        input()
    else:     
        print("Press any button to start convertion\n\nDuring convertion press ESC to cancel the process")

if resize:
    lFrames = convertionWithResize(width=width,height=height,video=vid,resample=resample)
else:
    lFrames = convertion(width=width,height=height,video=vid)

l_subframes = []
l_frames_compress = []

i = 0
j = 0
k = 0
h_sprite = 0
w_sprite = 0

# de cada fotograma se coge sub fotogramas cuadrados de orden l_pattern x l_pattern, 
# entonce hay que hacer que el programa coja desde 0 hasta 8 y lo meta en un vector, 
# ahora mismo mi idea es que vaya sean 5 for (si, extremadamente eficiente),entonces 
# el primero es el de los frames, luego el otro es el de los subframes horizontales y 
# el otro los subframes verticales, el siguiente lo que hace es llenar los subframes 
# entonces deben ser desde 0 hasta l_pattern, y yo creeria que deberia ser desde 1, 
# porque hay que ver como solucionar lo de 0, porque eso me puede tirar problemas aunque 
# creo que podria ser ((sprite_actual)*l_pattern)+(p_actual)) YO CREO Y ESPERO QUE SIRVA
for frame in lFrames:
    subframe_map = np.zeros(shape=(int(width/l_pattern),int(height/l_pattern)),dtype=int)
    for i in range(len(subframe_map)):
        for j in range(len(subframe_map[0])):
            subframe = np.zeros(shape=(l_pattern,l_pattern),dtype=bool)
            for subframe_i in range(l_pattern-1):
                for subframe_j in range(l_pattern-1):
                    subframe[subframe_i][subframe_j] = frame[(i*l_pattern)+(subframe_i)][(j*l_pattern)+(subframe_j)]
            try:
                val = findSubFrame(list=l_subframes,subframe=subframe)
            except:
                l_subframes.append(subframe)
                val = int(len(l_subframes)-1)
                print("new subframe created")
            finally:
                subframe_map[i][j] = val
                print("subframe calculated")
                
    l_frames_compress.append(subframe_map)
    print(l_subframes)                  
                        
                    
                
            
        
    

