import os
import settings
import numpy as np
import cv2
from imutils.perspective import four_point_transform

def save_up_img(fileObj):
    filename = fileObj.filename
    
    name, ext = filename.split('.')
    
    save_filename = 'uploade.' + ext
    
    upload_image_path = settings.join_path(settings.SAVE_DIR, save_filename)
    
    fileObj.save(upload_image_path)
    
    return upload_image_path

def array2json(np_array):
    points =[]
    for point in np_array.tolist():
        points.append({'x':point[0], 'y':point[1]})
    return points
    

class BillScan():
    def __init__(self):
        pass
    
    @staticmethod
    def resize_func(image, width=590):
        h,w,c = image.shape
        height = int((h/w)* width)
        size= (width,height)
        image = cv2.resize(image,(width,height))
        return image, size
    
    @staticmethod
    def bright_cont(input_img , brightness = 0, contrast=0):
        if brightness != 0:
            if brightness> 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255+ brightness
            alpha_b =(highlight - shadow)/ 255
            gamma_b = shadow
            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()
        if contrast != 0:
            f =131*(contrast+127)/(127*(131-contrast))
            alpha_c = f
            gamma_c = 127*(1-f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
            
        return buf
    
    
    def bill_scanner(self, image_path):
        self.image = cv2.imread(image_path)
        img_resize, self.size = self.resize_func(self.image)
        filename = 'resize_image.jpg'
        RESIZE_IMAGE_PATH = settings.join_path(settings.MEDIA_DIR, filename)
        
        cv2.imwrite(RESIZE_IMAGE_PATH, img_resize)
        
        try:
            hsv = cv2.cvtColor(img_resize, cv2.COLOR_BGR2HSV)
            lower_white = np.array([0, 0, 170])
            upper_white = np.array([180, 50, 255])
            mask = cv2.inRange(hsv, lower_white, upper_white)
            kernel_big = np.ones((20, 20), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_big)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_big)

            
            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            for contour in contours:
                hull = cv2.convexHull(contour)
                prei = cv2.arcLength(hull, True)
                approx = cv2.approxPolyDP(hull, 0.02 * prei, True)
                if len(approx) == 4:
                    four_pts = np.squeeze(approx)
                    break
            return four_pts, self.size
        except:
            return None, self.size
        
    
    def calibrate(self, four_pts):
        
        multiplier = self.image.shape[1] / self.size[0]
        four_pts = four_pts * multiplier
        four_pts = four_pts.astype(int)
        
        
        
        img_wrap = four_point_transform(self.image, four_pts)
        
        fixed_image = self.bright_cont(img_wrap, brightness=60, contrast=35)
        
        return fixed_image
        