
import cv2
import time
import mediapipe as mp
import vlc
import argparse


parser = argparse.ArgumentParser()
color = ()
parser.add_argument("-p", "--path", default='cv2/Video.avi', 
                    required = False, type = str, help='Give path of video file')
args = parser.parse_args()
vid_path = ''
for i in list(args.path):
    vid_path += i


vlc_player = vlc.MediaPlayer()
media = vlc.Media(vid_path)
vlc_player.set_media(media)
vlc_player.video_set_scale(0.25)
vlc_player.play()
time.sleep(5)

    
x, y = 0.0, 0.0
pos = 0.0
vol = 0
a = [0.0, 0.0]
flag = 0


class HandsDetection():
    
    def __init__(self, num_hands = 1, detection_confidence = 0.7, 
                 static_mode = False, tracking_confidence = 0.7,):
        self.num_hands = num_hands
        self.detection_confidence = detection_confidence
        self.static_mode = static_mode
        self.tracking_confidence = tracking_confidence
        
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(max_num_hands = self.num_hands, 
                                        min_detection_confidence = self.detection_confidence, 
                                        static_image_mode = self.static_mode, 
                                        min_tracking_confidence = self.tracking_confidence)
        
    
    def DrawHandsLandmarks(self, frame):
        
        for i in self.results.multi_hand_landmarks:    
            self.mpDraw.draw_landmarks(frame, i, self.mpHands.HAND_CONNECTIONS)
        
        return frame
    
    
    def dist(self, x1, y1, x2, y2):
        '''
        To calculate distance between 2 points
        '''
        
        return int(((y2-y1)**2+(x2-x1)**2)**0.5)


    def magic(self, x1, y1, x2, y2):
        '''
        To show magic
        '''
        
        global flag, k
    
        if ((self.dist(x1, y1, x2, y2) <= 30) and (self.dist(x1, y1, x2, y2) >= 5)):
                
            if k == 2:
            
                if flag:
                    flag = False
                
                else:
                    flag = True
                print('Snap detected')
                
                k = 0
                
            k += 1
        
        return None
    
    
    def Landmarks(self, frame, draw = True):
        
        self.results = self.hands.process(frame)
        
        if self.results.multi_hand_landmarks: 
        
            h, w = frame.shape[0], frame.shape[1]    
            x1, y1 = self.results.multi_hand_landmarks[0].landmark[4].x*w, self.results.multi_hand_landmarks[0].landmark[4].y*h
            x2, y2 = self.results.multi_hand_landmarks[0].landmark[8].x*w, self.results.multi_hand_landmarks[0].landmark[8].y*h

            self.magic(x1, y1, x2, y2)
            
            if draw:
                frame = self.DrawHandsLandmarks(frame)
            
        return frame
    

    def handsFuncs(frame, draw = True):
        '''
        Returns the co-ordinates (x, y) for tip of index finger
        '''
    
        global x, y
        
        results = hands.process(frame)
        
        if results.multi_hand_landmarks:
            h, w, c = frame.shape       
            # Co-ordinates of index finger:
            x, y = results.multi_hand_landmarks[0].landmark[8].x*w, results.multi_hand_landmarks[0].landmark[8].y*h
        
            if draw:
                for i in results.multi_hand_landmarks:    
                    mpDraw.draw_landmarks(frame, i, mpHands.HAND_CONNECTIONS)
            
            x, y = int(x), int(y)
            return frame
        
        else:
            x, y = 0, 0
            return frame
    
    
    def CheckSeekBarConditions(frame):
        '''
        To check seek bar conditions
        '''
        
        global pos, a, x, y
        
        if ((50 < x < 1050) and (25 < y < 85)):
            cv2.circle(frame, (x, 55), 15, (255, 0, 0), -1)
            pos = int((x - 50)/10)
            a.append(pos)
            cv2.putText(frame, 'Seek Position (%):', (250, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.putText(frame, str(pos) + '%', (550, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        return frame
    
    
    def SetSeekPosition(frame):
        '''
        To set volume bar conditions
        '''
        
        global flag, pos, a
        
        if pos != a[-2]:   
            vlc_player.set_position(pos/100) 
            vlc_player.play()
        
        elif vlc_player.get_position() >= 1.0:
            pos = 0.0
            vlc_player.set_position(pos/100) 
            vlc_player.play()
            a.append(pos)
            a.append(pos)
            flag = 25
        
        if flag > 0:
            cv2.putText(frame, 'Video Restarted!!!', (300, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            flag -= 1
        
        return frame
    
    
    def CheckVolumeBarConditions(frame):
        '''
        To check volume bar conditions
        '''
        
        global vol, x, y
        
        if ((25 < x < 85) and (100 < y < 400)):
            cv2.circle(frame, (55, y), 15, (255, 0, 0), -1)
            vol = int((y - 100)/3)
            
            if vol > 100:
                vol = 100
            
            elif vol < 0:
                vol = 0
                
            cv2.putText(frame, 'Vol:', (30, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.putText(frame, str(vol), (30, 480), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        return frame
    
    
    def SetVolumePosition():
        '''
        To set volume position
        '''
        
        global vol
        
        vlc_player.audio_set_volume(vol)
       
        return None
    
    
    def DoNothing(emp):
    	pass
    
    
    def SetRealTrackBar():
        '''
        To set real track bar position for Seek and Volume
        '''
        
        cv2.setTrackbarPos('Seek', 'RealTrackBar', int(vlc_player.get_position()*100))
        cv2.setTrackbarPos('Volume', 'RealTrackBar', vlc_player.audio_get_volume())
        
        return None
          

                
def main():
    
    global pos, vol, a, x, y
    
    t, count_frames = 0, 0
    
    cv2.namedWindow('RealTrackBar')
    cv2.resizeWindow('RealTrackBar', 1000, 80)
    cv2.moveWindow('RealTrackBar', 50, 600)
    cv2.createTrackbar('Seek', 'RealTrackBar', 0, 100, DoNothing)
    cv2.createTrackbar('Volume', 'RealTrackBar', 0, 100, DoNothing)
    
    video = cv2.VideoCapture(0) 
    # If dimensions of the frame are changed, scales of seek and volume bar will also have to be modified!!! 
    video.set(3, 1280) # width
    video.set(4, 720)  # height
    
    # frame_width = int(video.get(3)) 
    # frame_height = int(video.get(4)) 
    # vid_fps = int(video.get(5)) 
    # code_of_codec = int(video.get(6))
    # No_of_frames = int(video.get(7))  
    # size = (frame_width, frame_height) 
    # result = cv2.VideoWriter('cv2/pose_detection_openpose_output.avi',  
    #                          cv2.VideoWriter_fourcc(*'MJPG'), 
    #                          10, size) 

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
      
        frame = handsFuncs(cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB), draw = False)
        
        s = time.time()
        fps = int(1/(s-t))
        t = s
        cv2.putText(frame, 'FPS: '+str(fps), (30, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
        cv2.rectangle(frame, (50, 50), (1050, 60), (0, 0, 255), -1) # For seek bar
        
        cv2.rectangle(frame, (50, 100), (60, 400), (0, 0, 255), -1) # For volume

        if (x, y) != (0, 0): # and (a[-1] != [0,0])):    
            cv2.circle(frame, (x, y), 15, (200, 255, 200), -1)
            
            frame = CheckSeekBarConditions(frame)   # for video seek bar
            frame = CheckVolumeBarConditions(frame)   # for video volume bar
            
        # for video seek bar    
        frame = SetSeekPosition(frame)
        
        # for volume bar  
        SetVolumePosition()
        
        # for real track bar position for Seek and Volume
        SetRealTrackBar()
        
        cv2.imshow('frame', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  
          
        count_frames += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            vlc_player.stop()
            # result.write(output)
            break
        
    # result.release()    
    video.release() 
    
    cv2.destroyAllWindows()
    print("Done processing video")
    
    return None
    


if __name__ == '__main__':
    main()