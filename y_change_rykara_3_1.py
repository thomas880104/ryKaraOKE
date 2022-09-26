'''
原版本:
ryKaraOkeInPygame.py

2022/2/22
已處理：get_wav_mic_array()分離, freq_process()分離
2022/2/23
已處理：score system 問題：分數放入self, 分數一直閃爍, 分數計算方式
2022/2/24
已處理：所有模組化
需要處理： 按a後會卡住，收不到音(兩者)
2022/3/17
已處理：畫面速度
2022/3/31
需要處理：建database
2022/4/27
需要處理：背景播放mp4
2022/4/28
已處理：背景播放mp4
需要處理：localfile撥放mp4
2022/4/29
已處理：localfile撥放mp4
需要處理：沒影片的程式處理
2022/5/3
已處理：沒影片的程式處理
需要處理：pitch問題，訓練歌聲偵測
2022/6/3
需要處理：先讀取wav檔的pitch
2022/6/4
需要處理：讀取wav檔的pitch會比音樂慢，撥放音樂的地方
2022/6/7
已處理：先讀取wav檔的pitch，黃圈對齊音樂，影片太慢
需要處理：關閉程式

2022/7/13
需要處理：wav_pitch_array list out of range
2022/8/8
已增加：目前時間 / 總時長
2022/8/9
已處理：畫面配合影片縮放
2022/8/12
已處理：調整變數名稱，畫面
需處理：重寫output to screen部分
'''

import numpy        as np
import matplotlib.pyplot as plt

import colorsys
import time
from scipy.io import wavfile

import threading
import collections
import os
import sys
from scipy.io import wavfile
import evaluate
from tensorflow.keras import models
import tensorflow as tf

from ryMic      import *
from ryPitch__  import *
from myspleeter_ui  import *

def wav_pitch(wav):
    '''
    read wav's 3rd channel and get the singer's pitch 
    '''
    sr, data = wavfile.read(wav)   

    wavfile.write('output/ttmp.wav', sr, data[:, 2])   
    model = tf.keras.models.load_model('training_dsd100/vocal_model.h5')

    pred = evaluate.pred('output/ttmp.wav',model)

    target = data[:,2]
    time = len(target)/sr
    
    hz = []
    for i in range(int(time)*10):
        pitch = freq_from_autocorr(target[i*1600:(i+1)*1600], sr)
        if pitch > 2000:
            pitch = 0
        if pred[i//10]<0.5:
            hz.append(0)
        else:
            hz.append(pitch)

    os.remove('output/ttmp.wav')

    return hz

def note2freq(n=0):
    f0= 440 * (2**(n/12)) 
    return f0

def frequency_to_color(frequency, is_color= False):

    #frequency *= 倍數
    
    if is_color == True:
        r, g, b= colorsys.hsv_to_rgb(frequency, 1, .9)#.999)#.8)
        N= 256
        
        r = int(r*N)%N
        g = int(g*N)%N
        b = int(b*N)%N
        
    else: # 黑白
        r, g, b= frequency%1, frequency%1, frequency%1 #colorsys.hsv_to_rgb(frequency, 1, 1)#.999)#.8)   
        N= 128
    
        r = N-int(r*N)%N
        g = N-int(g*N)%N
        b = N-int(b*N)%N
    
    rgb_color= (r,g,b)

    return rgb_color

class RySpectrogram:

    def __init__(self, Mic= None,audio = None, video = None, pitch = None):

        self.width, self.height= self.width_height= size = (1024, 512) #512) #(512, 512) #( 640, 480 )

        if Mic is None:
            self.Mic= x.Mic
        else:
            self.Mic= Mic
        
        # for specgram, 頻譜， 調色盤，把 頻譜值 對應到顏色。
        self.i譜框= 0
        
        self.譜框數= self.Mic.框數 * 16 
        self.specgram= np.random.random([self.譜框數, self.Mic.frame_size//2])
        
        self.譜寬高= (self.譜框數, self.Mic.frame_size//2)    #specgram.shape

        self.depth= 8 
        
        self.palette= []  

        for n in range(int(2**self.depth)):
            k= n/2**self.depth
            bg_color= frequency_to_color(k)
            self.palette += [bg_color]
            
        self.main_loop=  False
        
        self.spectrum_line= threading.Thread(target= self.Spectrum_thread)
        
        
        self.時間點歌詞= dict()
        self.時間點們= []
        
        #self.Mic.等待第一圈錄音圓滿_wav()
        
        self.keyboard = None
        self.mouse_is_click = False
        self.mouse_x_axis = 0
        self.mouse_y_axis = 0

        self.wav_array = 0
        self.mic_array = 0
        
        self.pitchMatching = 0
        
        self.audio = audio
        self.video = video

        self.wav_pitch_array = pitch

        self.audio_start_time = 0
        self.audio_length = time.strftime('%M:%S', time.gmtime(len(self.wav_pitch_array)/10))

        
        
        self.score_times = 0

    def start(self):
            
        self.spectrum_line.start() # 用 thread 執行時，關不掉！！(quit 不了)

    def Spectrum_thread(self):


        def Cursor_display(self, mouse_x_axis, mouse_y_axis, keyboard= None):

            size=         10 #max(10, 音訊能量 )
            place_size=  (mouse_x_axis - size/2, mouse_y_axis - size/2, size, size)

            bg_color=      (255, 255, 255) #frequency_to_color(frequency)

            pg.draw.ellipse(self.screen, bg_color, place_size)
            pg.display.update()

        def keyboard_event():
            '''
            press the button on the keyboard and it will make output different
            '''
            events= pg.event.get() # 取得 使用者 輸入 事件
            mouse_is_click = False
            mouse_x_axis = mouse_y_axis=  0
            keyboard = None
            for e in events: # 處理 使用者 輸入 事件

                if e.type in [pg.QUIT]: # quit by closing window
                    self.main_loop= False
                elif e.type in [pg.KEYDOWN]: 
                    keyboard= e.key
                    self.keyboard = keyboard

                    if e.key in [pg.K_ESCAPE]: # quit by press Esc
                        self.main_loop= False

                    elif e.key in [pg.K_a]:
                        self.Mic.初框線程(source= 'wav')#會卡的原因，待解決
                        self.Mic.初框線程(source= 'mic')#
                        print('self.Mic.初框= {}'.format(self.Mic.初框))
                        print('self.Mic.wav初框= {}'.format(self.Mic.wav初框))

                    else:
                        pass
                        
                elif e.type in [pg.KEYUP]:
                    keyboard= None
                    self.keyboard = keyboard

                elif e.type in [pg.MOUSEBUTTONDOWN]:
                    self.mouse_is_click= True
                    mouse_x_axis, mouse_y_axis= x,y= e.pos

                elif e.type in [pg.MOUSEBUTTONUP]:
                    self.mouse_is_click= False 
                    

                elif e.type in [pg.MOUSEMOTION]:
                    if (self.mouse_is_click is True):
                        mouse_x_axis, mouse_y_axis= x,y= e.pos
                    else:
                        pass



        def get_wav_mic_array():
            '''
            get wav array and mic array from mic.frames and mic.wavframes
            '''

            #做成譜的音框數= 2
            # 這是 mic
            #b0= self.Mic.框們[-做成譜的音框數:]  
            # 連取 2音框，做成1譜框，譜看起來會更平滑吧
            #b0= b''.join(b0)
                
            #
            # 但 .框們 現在是一個 deque, 不能 用 x1:x2
            # 因此 簡單的改成如下
            #
            b0= b''
            b1= b''
            for k in range(-做成譜的音框數,0):
                b0 += self.Mic.框們[k]
                #b1 += self.Mic.wav框們[k]

            self.mic_array= np.frombuffer(b0,'int16')#x0
            #self.wav_array= np.fromstring(b1,'int16')#x1
            

        def freq_process():
            '''
            get vocal and wav array data and turn into freq
            '''
            frame = pg.time.get_ticks() - self.audio_start_time
            if frame//100 == len(self.wav_pitch_array):
                pg.quit()
                self.Mic.stop()
                sys.exit()

            #
            # 把 mic_freq 放在這裡。
            mic_freq= freq_from_autocorr(self.mic_array, self.Mic.sample_rate)#.frame_size) #self.Mic.sample_rate)
            
            wav_freq = self.wav_pitch_array[frame//100]

            en0= abs(self.mic_array).mean()
            #en1= abs(self.wav_array).mean()
                
            mic_not_noise= False
            wav_not_noise= False
            if en0 > self.Mic.初框['mean']    + self.Mic.初框['std']*3:   
                mic_not_noise= True
            '''
            if en1 > self.Mic.wav初框['mean'] + self.Mic.wav初框['std']*1: #原本為mean + std*3  
                wav_not_noise= True
            '''
            if mic_not_noise==False or mic_freq > 1000: #去掉雜音
                mic_freq=-20

            if wav_freq > 1000: 
                wav_freq=-10 
                
                
            #
            # 量化在半音內，觀看音符比較穩定。
            #
            mic_freq_Q, note0= pitchQuantization(mic_freq)
            wav_freq_Q, note1= pitchQuantization(wav_freq)
                
            #
            # 簡單的評分，調整八度後，相差 5 hz 以內 就算正確。
            #
            pitchHit= False
            if (abs(wav_freq - mic_freq) <= 5 or abs(wav_freq/2 - mic_freq) <= 5):       
                self.pitchMatching += 1
                pitchHit= True
                
            pg.draw.rect(self.screen, pg.Color('blue'),[(2, self.height-20),(80,20)])
            pg.draw.rect(self.screen, pg.Color('blue'),[(2, self.height-40),(80,20)])
            pg.draw.rect(self.screen, pg.Color('yellow'),[(2, self.height-60),(80,20)])
            pg.draw.rect(self.screen, pg.Color('blue'),[(self.width-140,self.height-20),(140,20)])
            
                

            aMsg= '{}, {:.0f}'.format(note0, mic_freq)
            aText= aFont.render(aMsg, True, pg.Color('white'))
                
            bMsg= '{}, {:.0f}'.format(note1, wav_freq)
            bText= aFont.render(bMsg, True, pg.Color('yellow'))
                
            cMsg= '{}'.format(self.pitchMatching)
            cText= aFont.render(cMsg, True, pg.Color('blue'))

            #length
            current_time = time.strftime('%M:%S', time.gmtime(frame//1000))

            dMsg= '{} / {}'.format(current_time,self.audio_length)
            dText= aFont.render(dMsg, True, pg.Color('white'))  

            self.screen.blit(aText, (2, self.height-20)) # 'while'
            self.screen.blit(bText, (2, self.height-40))    # 'yellow'
            self.screen.blit(cText, (2, self.height-60)) # 'blue'
            self.screen.blit(dText, (self.width-140,self.height-20))    
                
            #
            # 永遠把 mic_freq 限縮在 440 以內，以利畫圖於幕上
            #
            while mic_freq > 440: mic_freq = mic_freq/2
            while wav_freq > 440: wav_freq = wav_freq/2

            #將Voice跟Ans的frequency放入array(黃白圈圈)
            mic_freq_h= self.height - mic_freq/440 * self.height
            wav_freq_h= self.height - wav_freq/440 * self.height
            self.fQ += [(mic_freq_h, wav_freq_h)] 
                
            while len(self.fQ)>128: #128
                self.fQ.popleft()     # 保持 16 框就好
        
        def draw_pitch(x):
            '''
            get freq data from freq_process() "self.fQ" and output to screen
            ''' 

            for n in range(len(self.fQ)):
                mic_x_axis= x+ (n-len(self.fQ)+4) *8 #*16 # 橫軸 放大 16 倍 #辨識的要設70才會一樣
                mic_y_axis= self.fQ[n][0]
                    
                wav_x_axis= x+ (n-len(self.fQ)) *8 #不知為何它早出現約4框？只在前方4框先畫出
                wav_y_axis= self.fQ[n][1]
                    
                pg.draw.ellipse(self.screen, pg.Color('white'),  [(mic_x_axis, mic_y_axis), (16,16)],4)
                pg.draw.ellipse(self.screen, pg.Color('yellow'), [(wav_x_axis, wav_y_axis), (12,12)],4)     
            '''
            for n in range(self.width/8):
                wav_x_axis = n * 8
                wav_y_axis = 

                pg.draw.ellipse(self.screen, pg.Color('yellow'), [(wav_x_axis, wav_y_axis), (12,12)],4)
            '''
        def color_line(x):

            for n in range(-36,1):
                #f譜線= note2freq(n)
                y譜線= 2**(n/12)*self.height #h-f譜線/440*h
                                
                y譜線= self.height- y譜線
                                
                #color= pg.Color('cyan')
                                
                #color= frequency_to_color((n/12)%1, is_color= True) 
                                
                pg.draw.line(self.screen, pg.Color('black'),(0,y譜線),(self.width,y譜線) , 2)
                                
                if n%12 in [3,5,7,8,10,0,2]: # C 大調，通通沒升記號。
                                
                    color= frequency_to_color((n/12)%1, is_color= True)                 
                    pg.draw.line(self.screen, color,(0,y譜線),(self.width,y譜線) , 3)
                                    
                    noteName= noteNameL[n%len(noteNameL)] # noteNameL 在 ryPitch__ 裡面
                    noteMsg= '{}'.format(noteName)
                    noteText= aFont.render(noteMsg, True, color)#pg.Color('white'))
                    pg.draw.rect(self.screen, pg.Color('white'),[(x-20, y譜線-20),(20,20)])
                    self.screen.blit(noteText, (x-20, y譜線-20))

        def show_spectrum(self, keyboard= None):

        
            get_wav_mic_array()

            self.i譜框 += 1

            if self.video == None:
                aSurf= pg.transform.scale(self.bg, (self.width, self.height)) #//4))
                self.screen.blit(aSurf, (0,0))    
            #
            # 江永進的建議，在頻譜前畫一條白線，並把能量、frequency軌跡畫出。
            #
                
            if self.keyboard != pg.K_e:
                x= (self.i譜框 % self.譜框數)  * self.width / self.譜框數
            else:
                x= (self.譜框數-1)  * self.width / self.譜框數
                    
                
            
            pg.draw.line(self.screen, pg.Color('gray'),(x,self.height),(x,0) , 5)
                
            #
            # 把12平均律譜線在此跟江永進白線一起畫出。
            
            #color_line(x)     
            freq_process()
            draw_pitch(x)

            
            pg.display.flip()
            pg.display.update()

        
        
        def init_screen():
            '''
            畫面初始化
            '''
            self.screen= pg.display.set_mode( self.width_height, 0 )
        
            screen_title= '''cguKaraOkeScoring using Pyaudio, Pygame on Python 3, 
                by Renyuan Lyu (呂仁園), Chang Gung Univ (長庚大學), TAIWAN, modified by YCH'''
            pg.display.set_caption(screen_title)
            
            self.bg= pg.Surface(self.譜寬高, depth= self.depth) # for specgram

            self.bg.set_palette(self.palette)
            #'''
            self.fQ= collections.deque()

        def background_video(mp4):
            '''
            play mp4 at background
            need debug
            '''
            
            video = cv2.VideoCapture(mp4)
            success, video_image = video.read()
            fps = video.get(cv2.CAP_PROP_FPS)

            self.screen = pg.display.set_mode(video_image.shape[1::-1])
            self.width = pg.Surface.get_width(self.screen)
            self.height = pg.Surface.get_height(self.screen)
            clock = pg.time.Clock()

            pg.mixer.music.play()
            self.audio_start_time = pg.time.get_ticks()
            run = success
            while run:
                

                clock.tick(fps)
                #keyboard_event()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        run = False
                        self.main_loop = False
                success, video_image = video.read()
                if success:
                    video_surf = pg.image.frombuffer(
                        video_image.tobytes(), video_image.shape[1::-1], "BGR")
                else:
                    run = False
                    self.main_loop = False
                self.screen.blit(video_surf, (0, 0))

                show_spectrum(self, keyboard) 
                
                pg.display.flip()

        def play_audio():

            fs, data = wavfile.read(self.audio)           

            audio = np.vstack([data[:, 0],data[:, 1]])
            audio = audio.transpose()

            wavfile.write('output/tmp.wav', fs, audio)

            pg.mixer.music.load('output/tmp.wav')
            
            if self.video == None:
                pg.mixer.music.play()
                self.audio_start_time = pg.time.get_ticks()
            


        #   main()

        import cv2
        import pygame as pg # 把 import pygame 放在線程之內，用線程跑時，pygame display 才會正常運作 (GUI部分)
        
        做成譜的音框數= 2
        ham= np.hamming(做成譜的音框數 * self.Mic.frame_size) #len(x))

        pg.font.init()        
                
        font_path= '{}{}'.format( os.environ['SYSTEMROOT'], '\\Fonts\\mingliu.ttc')
                        
        aFont= pg.font.Font(font_path, 20, bold= True)
        

        pg.init()

        init_screen()
        
        print('頻譜主迴圈....')

        print(self.video)

        mouse_is_click=      False
        mouse_x_axis= mouse_y_axis=  0
        keyboard=          None

        i框= self.Mic.wav_i框
        

        #self.Mic.等待第一圈錄音圓滿(source='wav')
        self.Mic.等待第一圈錄音圓滿(source='mic')
        
        self.main_loop=  True

        print(len(self.wav_pitch_array))
        
        play_audio()


        while self.main_loop:
            
            '''
            if self.Mic.wav_record_thread_is_alive == False:
                self.main_loop = False
            '''
            if pg.mixer.music.get_busy() == False:
                self.main_loop = False

            
            
            keyboard_event()
        
            if self.video != None:
                background_video(self.video)
            elif self.video == None:
                show_spectrum(self, keyboard)
                pg.time.delay(25)
        
            # 滑鼠
            if (mouse_is_click is True):  # 用 K_ijk 來控制滑鼠處理
                Cursor_display(self, mouse_x_axis, mouse_y_axis, keyboard) 

            # 畫面更新
            pg.display.flip()
        
            
            #while (self.Mic.wav_i框 - i框 == 0 ): pass # .wav_i框 會在 ryMic reset 成 0




        if self.main_loop == False:
            pg.quit()
            self.Mic.stop()
            sys.exit()
            
                
    

if __name__=='__main__':   
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    app.exec_()
    if mainWin.allo ==True:
        if mainWin.NoNet ==True:
            pitch = wav_pitch(mainWin.filename)
            mic= RyMic(musicfile = mainWin.filename)
            mic.start(wav = False)
            
            Spectrogram = RySpectrogram(mic, pitch = pitch, audio=mainWin.filename)
            Spectrogram.start()
        else:
            pitch = wav_pitch('localfile/' + mainWin.mode + '/' + mainWin.filename + '.wav')
            mic= RyMic(musicfile = 'localfile/' + mainWin.mode + '/' + mainWin.filename + '.wav')
            mic.start(wav = False)
            if mainWin.video == True:
                Spectrogram = RySpectrogram(mic,video = 'localfile/mp4/' + mainWin.filename + '.mp4',pitch = pitch,audio='localfile/' + mainWin.mode + '/' + mainWin.filename + '.wav')
            elif mainWin.video == False:
                Spectrogram = RySpectrogram(mic,pitch = pitch,audio = mainWin.filename)
            Spectrogram.start()
    else:
        sys.exit()
