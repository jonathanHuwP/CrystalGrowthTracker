
def save_region_video(self):
    """
    demo of how to save images to an avi file using cv2 
    """
    import numpy as np
    import cv2
        
    writer = cv2.VideoWriter("output.avi",cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))
    for frame in range(1000):
        random_dots = np.random.randint(0, 255, (480,640,3)).astype('uint8')
        writer.write(random_dots)
            
    writer.release()