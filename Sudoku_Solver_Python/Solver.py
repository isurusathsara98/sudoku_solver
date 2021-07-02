import operator
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from Sudoku_Solver_Python.sudoku_solver import solver_algo

def preprocess_stage(img, skip_dilate=False):

    img_pro = cv2.GaussianBlur(img.copy(), (9, 9), 0)    #add blur to a copy of the image
    img_pro = cv2.adaptiveThreshold(img_pro, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    img_pro = cv2.bitwise_not(img_pro, img_pro)
    if not skip_dilate:
       kernel = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]],dtype=np.uint8)
       img_pro = cv2.dilate(img_pro, kernel)

    return img_pro

def rectangle(img, rect):
    #Obtain a rectangle from the image using the points
    return img[int(rect[0][1]):int(rect[1][1]),int(rect[0][0]):int(rect[1][0])]

def get_corners(img):
    #Function to obtain the corners of the biggest contour
    contours, h = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find contours in image
    contours = sorted(contours, key=cv2.contourArea, reverse=True)  # Sort the contours in the order of area
    img_cnt = None
    for c in contours: #Finding the biggest contour from the obtain contours
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) # approximated contour has four points to find the outline of puzzle
        if len(approx) == 4:
            img_cnt = approx
            polygon = c
            break
    if img_cnt is None:
        return "No Puzzle Found"

    bottom_right, _ = max(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    top_left, _ = min(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    bottom_left, _ = min(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    top_right, _ = max(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))

    return [polygon[top_left][0], polygon[top_right][0], polygon[bottom_right][0], polygon[bottom_left][0]]

def distance_cal(p1, p2):
    #get distance between two points
    a = p2[0] - p1[0]
    b = p2[1] - p1[1]
    return np.sqrt((a ** 2) + (b ** 2))

def crop_img(img, crop_rect):
    top_left, top_right, bottom_right, bottom_left = crop_rect[0], crop_rect[1], crop_rect[2], crop_rect[3] #rectangular shape given by 4 points
    src = np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')#set datatype
    side = max([#find the longest distance or side of the rectangle
        distance_cal(bottom_right, top_right),      
        distance_cal(top_left, bottom_left),
        distance_cal(bottom_right, bottom_left),
        distance_cal(top_left, top_right)
    ])

    dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype='float32') # define a square according to the side lenght to wrap 

    m = cv2.getPerspectiveTransform(src, dst) #Tranforming the indentified points to point of square

    return cv2.warpPerspective(img, m, (int(side), int(side))) #Wrap on original image

def cell_grids(img):
    #Gather the 81 cell grids from square image
    squares = []
    side = img.shape[:1]
    side = side[0] / 9
    for j in range(9):
        for i in range(9):
            p1 = (i * side, j * side)  # Top left point of the cell
            p2 = ((i + 1) * side, (j + 1) * side)  # Bottom right point of the cell
            squares.append((p1, p2))
    return squares

def Resize_and_center(img, size, margin=0, background=0):
    #Resize and center the image onto a new background
    h, w = img.shape[:2]

    def centre_len(length):
        #Centering of the length
        if length % 2 == 0:
            side1 = int((size - length) / 2)
            side2 = side1
        else:
            side1 = int((size - length) / 2)
            side2 = side1 + 1
        return side1, side2

    def scale(r, x):
        return int(r * x)

    if h > w:
        t_pad = int(margin / 2)
        b_pad = t_pad
        ratio = (size - margin) / h
        w, h = scale(ratio, w), scale(ratio, h)
        l_pad, r_pad = centre_len(w)
    else:
        l_pad = int(margin / 2)
        r_pad = l_pad
        ratio = (size - margin) / w
        w, h = scale(ratio, w), scale(ratio, h)
        t_pad, b_pad = centre_len(h)

    img = cv2.resize(img, (w, h))
    img = cv2.copyMakeBorder(img, t_pad, b_pad, l_pad, r_pad, cv2.BORDER_CONSTANT, None, background)
    return cv2.resize(img, (size, size))

def largest_sort(inp_img, scan_tl=None, scan_br=None):
    #Obtain the largest connected pixel structure in the image

    img = inp_img.copy()  # Take a copy of image
    height, width = img.shape[:2] #obtain width and height

    max_area = 0
    seed_point = (None, None)

    if scan_tl is None:
        scan_tl = [0, 0]

    if scan_br is None:
        scan_br = [width, height]

    for x in range(scan_tl[0], scan_br[0]): #Go throught the image
        for y in range(scan_tl[1], scan_br[1]):
            if img.item(y, x) == 255 and x < width and y < height:  #Sort only the white squares
                area = cv2.floodFill(img, None, (x, y), 64)
                if area[0] > max_area:  # Get the maximum bounded area
                    max_area = area[0]
                    seed_point = (x, y)

    for x in range(width):    # compensates for features outside of our middle scanning range
        for y in range(height):
            if img.item(y, x) == 255 and x < width and y < height:
                cv2.floodFill(img, None, (x, y), 64)  

    mask = np.zeros((height + 2, width + 2), np.uint8)  # mask of 2 pixel larger than image

    if all([p is not None for p in seed_point]): #highlight main features
        cv2.floodFill(img, mask, seed_point, 255)

    top, bottom, left, right = height, 0, width, 0

    for x in range(width):
        for y in range(height):
            if img.item(y, x) == 64: 
                cv2.floodFill(img, mask, (x, y), 0)

            if img.item(y, x) == 255: # Find the bounding parameters
                top = y if y < top else top
                bottom = y if y > bottom else bottom
                left = x if x < left else left
                right = x if x > right else right

    bbox = [[left, top], [right, bottom]]
    return img, np.array(bbox, dtype='float32'), seed_point

def digit_Extract(img, rect, size):
    #obtaining digits from squares

    digit = rectangle(img, rect)  # obtain the digit box

    h, w = digit.shape[:2] 
    margin = int(np.mean([h, w]) / 2.5) #Get the margin where the digit pixels are likely to be located
    _, bbox, seed = largest_sort(digit, [margin, margin], [w - margin, h - margin]) #obtain the largest feature of the square
    digit = rectangle(digit, bbox)

    w = bbox[1][0] - bbox[0][0]  #resize the scale of the square to fit the digit size of the digit classifier model
    h = bbox[1][1] - bbox[0][1]

    if w > 0 and h > 0 and (w * h) > 100 and len(digit) > 0:
        return Resize_and_center(digit, size, 4)
    else:
        return np.zeros((size, size), np.uint8)  #Ignore the small bounding boxes

def Puzzle_Digits(img,squares):
    labels = []
    model = load_model('./Sudoku_Solver_Python/digit_classifier.h5') #load the model
    img2 = cv2.medianBlur(img.copy(),5)    #Blur a copy of image
    img2 = cv2.adaptiveThreshold(img2,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2) #preprocessing 
    kernel = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]],dtype=np.uint8)
    img2 = cv2.dilate(img2, kernel)
    img2 = cv2.bitwise_not(img2, img2)
    for square in squares: #each each digit in the squares
        digit = digit_Extract(img2, square, 28)
        numPixels = cv2.countNonZero(digit)
        if numPixels<80:
            labels.append(0) 
        else:
            kernel = np.array([[2., 2., 2.], [2., 2., 2.], [2., 2., 2.]],dtype=np.uint8)
            digit = cv2.dilate(digit, kernel)
            digit = digit/255            
            digit = np.argmax(model.predict(digit.reshape(-1,28,28,1))[0])    
            labels.append(1+ digit)
    return Grid_conversion(labels)

def Grid_conversion(label): #obtain a sudoku grid matrix to solve
    a=0
    matrix=[]
    for i in range(0,9):
        matrix.append(label[a:a+9])
        a=a+9
    return matrix

def Image_Overlay(solved,org_crop,img,squares): #Write the digits on the original image 
    font  = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.022*squares[0][1][0]
    color  = ( 29, 184, 69)
    org = (50, 50)    
    thickness = 2   
    img2 = cv2.medianBlur(img.copy(),5)
    img2 = cv2.adaptiveThreshold(img2,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY,11,2)

    img2 = cv2.bitwise_not(img2, img2)
    for square in squares:
        write_digit = digit_Extract(img2, square, 28) 
        numPixels = cv2.countNonZero(write_digit)
        tp = (int(square[0][0]+(squares[0][1][0]/3)),int(square[0][1]+(squares[0][1][0]/1.3)))
        if numPixels<80:        
            cv2.putText(org_crop,str(solved[round(square[0][1]/squares[0][1][0])][round(square[0][0]/squares[0][1][0])]),tp, font,  fontScale,color, thickness, cv2.LINE_AA)
    return org_crop

def solver(img):
    fitSize = False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert the image to gray scale
    processed_img = preprocess_stage(gray)
    corners = get_corners(processed_img) #obtain corners
    if corners == 'No Puzzle Found': 
        return 'No Puzzle Found'
    cropped = crop_img(gray, corners)
    org_crop = crop_img(img, corners)
    h,w = cropped.shape
    if h<600 or w<600:  #resize to the model image size
        cropped = cv2.resize(cropped,(600,600),interpolation = cv2.INTER_LINEAR)
        org_crop = cv2.resize(org_crop,(600,600),interpolation = cv2.INTER_LINEAR)
        fitSize = True
    squares = cell_grids(cropped)
    digits = Puzzle_Digits(cropped, squares) #get digits as predicted
    if(np.count_nonzero(digits)<17):
        return 'No Solution Found'

    solution=solver_algo(digits)

    if(len(solution) < 2):
        return 'No Solution Found'
    result_img = Image_Overlay(solution,org_crop,cropped,squares) #PLacing digits of solution on image
    if fitSize:
        result_img = cv2.resize(result_img,(w,h),interpolation = cv2.INTER_AREA) #resize resultant image
    return result_img

