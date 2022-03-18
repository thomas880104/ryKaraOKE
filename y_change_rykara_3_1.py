'''
原版本:
ryKaraOkeInPygame.py



2022/2/22
已處理：get_wav_mic_array()分離, point_system()分離


2022/2/23
已處理：point system 問題：分數放入self, 分數一直閃爍, 分數計算方式
2022/2/24
已處理：所有模組化
需要處理： 按a後會卡住，收不到音(兩者)
2022/3/17
已處理：畫面速度
'''

import numpy        as np


import colorsys
import time

import threading
import collections
import os
import sys

from ryMic      import *
from ryPitch__  import *
from myspleeter_ui  import *



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

    def __init__(self, Mic= None):

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
        
        self.Mic.等待第一圈錄音圓滿_wav()
        
        self.keyboard = None
        self.mouse_is_click = False
        self.mouse_x_axis = 0
        self.mouse_y_axis = 0

        self.wav_array = 0
        self.mic_array = 0
        
        self.pitchMatching = 0
        
    

    

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

        def point_system():
            '''
            how this program get your score with your voice
            '''
                
            # 把 f0 放在這裡。
            f0= freq_from_autocorr(self.wav_array, self.Mic.sample_rate)#.frame_size) #self.Mic.sample_rate)
            f1= freq_from_autocorr(self.mic_array, self.Mic.sample_rate)#.frame_size) #self.Mic.sample_rate)
                
            en0= abs(self.wav_array).mean()
            en1= abs(self.mic_array).mean()
                
            mic_not_noice= False
            wav_not_noice= False
            if en0 > self.Mic.初框['mean']    + self.Mic.初框['std']*3:   
                mic_not_noice= True
            if en1 > self.Mic.wav初框['mean'] + self.Mic.wav初框['std']*1: #原本為mean + std*3  
                wav_not_noice= True
                
            if mic_not_noice==False or f0 > 1000: #去掉雜音
                f0=-20
            if wav_not_noice==False or f1 > 1000: 
                f1=-10 
                
                
            #
            # 量化在半音內，觀看音符比較穩定。
            #
            f0_Q, note0= pitchQuantization(f0)
            f1_Q, note1= pitchQuantization(f1)
                
            #
            # 簡單的評分，調整八度後，相差 5 hz 以內 就算正確。
            #
            pitchHit= False
            if (abs(f1 - f0) <= 5 or abs(f1/2 - f0) <= 5):       
                self.pitchMatching += 1
                pitchHit= True
            else: pass
                
            pitchScore_y= (self.height - self.pitchMatching) % self.height - 20# for y axis
            pitchScore_x= ((self.pitchMatching // self.height + 1) * 16) % self.width # for x axis
                
            pg.draw.rect(self.screen, pg.Color('blue'),[(pitchScore_x, pitchScore_y+20),(60,20)])
            pg.draw.rect(self.screen, pg.Color('blue'),[(pitchScore_x, pitchScore_y),(60,20)])
            pg.draw.rect(self.screen, pg.Color('yellow'),[(pitchScore_x, pitchScore_y-20),(60,20)])
            pg.draw.line(self.screen, pg.Color('blue'),(0, self.height),(0, pitchScore_y), pitchScore_x*2)
                

            aMsg= '{}, {:.0f}'.format(note0, f0)
            aText= aFont.render(aMsg, True, pg.Color('white'))
                
            bMsg= '{}, {:.0f}'.format(note1, f1)
            bText= aFont.render(bMsg, True, pg.Color('yellow'))
                
            cMsg= '{}'.format(self.pitchMatching)
            cText= aFont.render(cMsg, True, pg.Color('blue'))
                
            self.screen.blit(aText, (pitchScore_x, pitchScore_y+20)) # 'while'
            self.screen.blit(bText, (pitchScore_x, pitchScore_y))    # 'yellow'
            self.screen.blit(cText, (pitchScore_x, pitchScore_y-20)) # 'blue'
                
                
            #
            # 永遠把 f0 限縮在 440 以內，以利畫圖於幕上
            #
            while f0>440: f0=f0/2
            while f1>440: f1=f1/2

            #將Voice跟Ans的frequency放入array(黃白圈圈)
            f0_h= self.height - f0/440 * self.height
            f1_h= self.height - f1/440 * self.height
            self.fQ += [(f0_h, f1_h)] 
                
            while len(self.fQ)>128: 
                self.fQ.popleft()     # 保持 16 框就好
        
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
                b1 += self.Mic.wav框們[k]

            self.wav_array= np.fromstring(b0,'int16')#x0
            self.mic_array= np.fromstring(b1,'int16')#x1

        def show_spectrum(self, keyboard= None):

            get_wav_mic_array()


            # 這是 wav 檔
            #b= self.Mic.wav框們[-做成譜的音框數:]  
            # 連取 2音框，做成1譜框，譜看起來會更平滑吧       
            #b= b''.join(b)
            '''
            b1= b''
            for k in range(-做成譜的音框數,0):
                b1 += self.Mic.wav框們[k]
      
            x1= np.fromstring(b1,'int16')
            '''
                    
            # mic + wav 檔
            x2ch= self.mic_array + self.wav_array
            
            # 以下轉頻譜
            
            x2ch= x2ch * ham  #np.hamming(len(x)) # 拿出去，改善速度
            
            xFFT= np.fft.fft(x2ch)[0:self.Mic.frame_size//2] # 這時，僅剩 Fs/4 的frequency範圍了，解析度更高了吧。
                
            xP=   np.absolute(xFFT*xFFT.conj())
                
            #self.i譜框= self.Mic.i框  # 框同步
                
            self.specgram[self.i譜框%self.譜框數]= xP
                
            self.i譜框 += 1
            
            Specgram= self.specgram #.copy()

            # up_down flip, 頻譜上下對調，讓低頻在下，高頻在上，比較符合直覺。
            Specgram= Specgram[:,-1::-1]

            # 這個 頻譜 大小要如何自動調整才能恰當的呈現在螢幕上，還有待研究一下。
            Specgram= (np.log(Specgram)+10)*10

      
                
            # 錦上添花
            #
            # 加這行讓頻譜會轉，有趣！！
            #
            if self.keyboard == pg.K_e:
                Specgram= np.roll(Specgram, -int(self.i譜框 % self.譜框數), axis=0)
                
                x= (self.譜框數-1)  * self.width / self.譜框數
                pg.draw.line(self.screen, pg.Color('white'),(x,self.height),(x,0) , 10)
                    
                pg.display.update()
            #
            # pygame 的 主要貢獻:  頻譜 ---> 音幕
            #
            pg.surfarray.blit_array(self.音幕, Specgram.astype('int'))
            #
            # pygame 的 次要貢獻: 調整一下 self.譜寬高 音幕 ---> aSurf
            #
            aSurf= pg.transform.scale(self.音幕, (self.width, self.height)) #//4))

            #
            # 黏上幕  aSurf ---> display
            #

            #aSurf= pg.transform.average_surfaces([aSurf, self.攝影畫面])
            self.screen.blit(aSurf, (0,0))


                
            #
            # 江永進的建議，在頻譜前畫一條白線，並把能量、frequency軌跡畫出。
            #
                
            if self.keyboard != pg.K_e:
                x= (self.i譜框 % self.譜框數)  * self.width / self.譜框數
            else:
                x= (self.譜框數-1)  * self.width / self.譜框數
                    
                
            w= self.width
            pg.draw.line(self.screen, pg.Color('gray'),(x,self.height),(x,0) , 10)
                
            #
            # 把12平均律譜線在此跟江永進白線一起畫出。
            # 直的白線
            '''
            for xx in range(16):
                xxx= xx*w//16
                color= 255-(xx*256*4//16)%256
                pg.draw.line(self.screen, (color,color,color),(xxx,0),(xxx,self.height) , 1)
            '''    
            
            #彩色線
            for n in range(-36,1):
                #f譜線= note2freq(n)
                y譜線= 2**(n/12)*self.height #h-f譜線/440*h
                    
                y譜線= self.height- y譜線
                    
                #color= pg.Color('cyan')
                    
                #color= frequency_to_color((n/12)%1, is_color= True) 
                    
                pg.draw.line(self.screen, pg.Color('black'),(0,y譜線),(w,y譜線) , 2)
                    
                if n%12 in [3,5,7,8,10,0,2]: # C 大調，通通沒升記號。
                    
                    color= frequency_to_color((n/12)%1, is_color= True)                 
                    pg.draw.line(self.screen, color,(0,y譜線),(w,y譜線) , 3)
                        
                    noteName= noteNameL[n%len(noteNameL)] # noteNameL 在 ryPitch__ 裡面
                    noteMsg= '{}'.format(noteName)
                    noteText= aFont.render(noteMsg, True, color)#pg.Color('white'))
                    pg.draw.rect(self.screen, pg.Color('white'),[(x-20, y譜線-20),(20,20)])
                    self.screen.blit(noteText, (x-20, y譜線-20))
                    
                
            point_system()
            
            #畫黃白圈圈        
            for n in range(len(self.fQ)):
                x00= x+ (n-len(self.fQ)) *8 #*16 # 橫軸 放大 16 倍
                y00= self.fQ[n][0]
                    
                x01= x+ (n-len(self.fQ)+4) *8 #不知為何它早出現約4框？只在前方4框先畫出
                y01= self.fQ[n][1]
                    
                pg.draw.ellipse(self.screen, pg.Color('white'), [(x00, y00), (16, 16)],4)
                pg.draw.ellipse(self.screen, pg.Color('yellow'), [(x01, y01), (12,12)])
            pg.display.update()

        def lyrics():
            '''
            Output lyrics on the screen.
            Need lyrics file.
            '''

            aLyric= bLyric= cLyric= ''
            iLyric= 0
            
            wav_i框_0, wav_i框_1, wav_i框_2= 0,0,0
            
            if self.時間點歌詞!={}:
                wav_i框_0= wav_i框_1= wav_i框_2= list(self.時間點歌詞.keys())[0]
                
            i歌詞時間點們= []
            i框= self.Mic.wav_i框

            #lyrics
            #But I think most of time won't have the lyric.
            if i框==0:
                print('{}'.format(i歌詞時間點們))
                
                xL= i歌詞時間點們
                yL= sorted(xL, key= lambda xL: xL[2])
                yD= dict([(x1,x3) for (x0, x1, x2,x3) in yL])
                
                print('{}'.format(yD))
                
                #self.時間點歌詞= yD
                
                
                i歌詞時間點們= []
                iLyric= 0
                
                
                if self.Mic.音檔名 in LrcDic.keys():
                    self.時間點歌詞= LrcDic[self.Mic.音檔名]
                    self.時間點們=   sorted(list(self.時間點歌詞.keys()))
                else:
                    self.時間點歌詞= {}
                    self.時間點們= []
                    
                self.Mic.初框線程(source= 'wav')
                self.Mic.初框線程(source= 'mic')
        
        def init_screen():
            '''
            畫面初始化
            '''
            self.screen= pg.display.set_mode( self.width_height, 0 )
        
            screen_title= '''cguKaraOkeScoring using Pyaudio, Pygame on Python 3, 
                by Renyuan Lyu (呂仁園), Chang Gung Univ (長庚大學), TAIWAN, modified by YCH'''
            pg.display.set_caption(screen_title)
            
            self.音幕= pg.Surface(self.譜寬高, depth= self.depth) # for specgram

            self.音幕.set_palette(self.palette)
            #'''
            self.fQ= collections.deque()


        import  pygame  as pg # 把 import pygame 放在線程之內，用線程跑時，pygame display 才會正常運作 (GUI部分)
        
        做成譜的音框數= 2
        ham= np.hamming(做成譜的音框數 * self.Mic.frame_size) #len(x))
              
        pg.font.init()        
                
        font_path= '{}{}'.format( os.environ['SYSTEMROOT'], '\\Fonts\\mingliu.ttc')
                        
        aFont= pg.font.Font(font_path, 20, bold= True)
        

        pg.init()

        init_screen()
        
        print('頻譜主迴圈....')

        mouse_is_click=      False
        mouse_x_axis= mouse_y_axis=  0
        keyboard=          None

        i框= self.Mic.wav_i框
        

        self.Mic.等待第一圈錄音圓滿(source='wav')
        self.Mic.等待第一圈錄音圓滿(source='mic')
        
        self.main_loop=  True
        
        while self.main_loop:
            
            if self.Mic.wav_record_thread_is_alive == False:
                self.main_loop = False

            lyrics()
            
            keyboard_event()

            # 音訊
            show_spectrum(self, keyboard) # 用 K_efgh 來控制音訊處理

            
            
            # 滑鼠
            if (mouse_is_click is True):  # 用 K_ijk 來控制滑鼠處理
                Cursor_display(self, mouse_x_axis, mouse_y_axis, keyboard) 

            # 畫面更新
            pg.display.flip()
            pg.time.delay(25)
            
            while (self.Mic.wav_i框 - i框 == 0 ): pass # .wav_i框 會在 ryMic reset 成 0
        if self.main_loop == False:
            pg.quit()
            self.Mic.stop()
            sys.exit()
     
                
    def start(self):
            
        self.spectrum_line.start() # 用 thread 執行時，關不掉！！(quit 不了)

if __name__=='__main__':   
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    app.exec_()
    if mainWin.allo ==True:
        if mainWin.NoNet ==True:
            mic= RyMic(musicfile = mainWin.filename)
            mic.start()
            
            Spectrogram= RySpectrogram(mic)
            Spectrogram.start()
        else:
            mic= RyMic(musicfile = r'output/tmp/KaraOKE.wav')
            mic.start()
            
            Spectrogram= RySpectrogram(mic)
            Spectrogram.start()
    else:
        sys.exit()
