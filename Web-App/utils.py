import os
import settings

import cv2

def save_up_img(fileObj):
    filename = fileObj.filename
    
    name, ext = filename.split('.')
    
    save_filename = 'uploade.' + ext
    
    upload_image_path = settings.join_path(settings.SAVE_DIR, save_filename)
    
    fileObj.save(upload_image_path)
    
    return upload_image_path