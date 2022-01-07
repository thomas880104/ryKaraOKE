'''
ryKaraOkeInPygame.py

此版本 把畫圖的工作交給 Pygame。
Vpython 與 tk 可暫時退位。
2016/08/28


rySpecgram001.py
rySpecgram.py
2016/08/16
'''




import numpy        as np


import colorsys
import time

import threading
import collections
import os
import sys

#from ryMic002_wavFile   import *
#from ryMic003_deque   import *

from ryMic      import *
from ryPitch__  import *
from myspleeter_ui  import *

#from ryASR              import *

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

class Ry頻譜類:



    def __init__(self, 麥= None):



        self.幕寬, self.幕高= self.幕寬高= size = (1024, 512) #512) #(512, 512) #( 640, 480 )


        if 麥 is None:
            x= Ry辨類()
            self.麥= x.麥
        else:
            self.麥= 麥
        


        #
        # for specgram, 頻譜， 調色盤，把 頻譜值 對應到顏色。
        #
        self.i譜框= 0
        
        self.譜框數= self.麥.框數 * 16 #8  ## 把譜留在畫面上多一點時間
        self.specgram= np.random.random([self.譜框數, self.麥.frame_size//2])
        
        self.譜寬高= (self.譜框數, self.麥.frame_size//2)    #specgram.shape

        self.深度= 8 # 試過 10, 16 都不行
        
        self.調色盤= []  # 這個調色盤的原理還有待研究！
        for n in range(int(2**self.深度)):

            k= n/2**self.深度
            色= frequency_to_color(k)

            self.調色盤 += [色]
            
        
        self.main_loop_running=  False
        
        self.頻譜線= threading.Thread(target= self.頻譜線程)
        
        
        self.時間點歌詞= dict()
        self.時間點們= []
        
        '''
        if LrcGeau != {}: #LrcToki != {}:
            self.時間點歌詞= LrcGeau #LrcToki
            self.時間點們= sorted(list(self.時間點歌詞.keys()))
        '''
        
        self.麥.等待第一圈錄音圓滿_wav()
        
    
        


    
    def 頻譜線程(self):
        

        import  pygame  as pg
        
        # 把 import pygame 放在線程之內，用線程跑時，pygame display 才會正常運作 (GUI部分)

        ###############################
        做成譜的音框數= 2
        ham= np.hamming(做成譜的音框數 * self.麥.frame_size) #len(x))
        
        
        pg.font.init()        
        
        #aFont= pg.font.SysFont('Times', 20)
        
        font_path= '{}{}'.format( os.environ['SYSTEMROOT'], 
                            '\\Fonts\\mingliu.ttc')
        aFont= pg.font.Font(font_path, 20, bold= True)
        
        pitchMatching= 0
        
        aLyric= bLyric= cLyric= ''
        iLyric= 0
        
        wav_i框_0, wav_i框_1, wav_i框_2= 0,0,0
        曾來過= False
        
        if self.時間點歌詞!={}:
            wav_i框_0= wav_i框_1= wav_i框_2= list(self.時間點歌詞.keys())[0]
            
        def 取音訊且顯示頻譜於幕(self, keyboard= None):
            nonlocal pitchMatching, aLyric, bLyric, cLyric, iLyric
            nonlocal wav_i框_0, wav_i框_1, wav_i框_2, 曾來過

            #做成譜的音框數= 2
            # 這是 mic
            #b0= self.麥.框們[-做成譜的音框數:]  
            # 連取 2音框，做成1譜框，譜看起來會更平滑吧
            #b0= b''.join(b0)
            
            #
            # 但 .框們 現在是一個 deque, 不能 用 x1:x2
            # 因此 簡單的改成如下
            #
            b0= b''
            b1= b''
            for k in range(-做成譜的音框數,0):
                b0 += self.麥.框們[k]
                b1 += self.麥.wav框們[k]
            
            x0= np.fromstring(b0,'int16')
            x1= np.fromstring(b1,'int16')
                               
            # 這是 wav 檔
            #b= self.麥.wav框們[-做成譜的音框數:]  
            # 連取 2音框，做成1譜框，譜看起來會更平滑吧       
            #b= b''.join(b)
            '''
            b1= b''
            for k in range(-做成譜的音框數,0):
                b1 += self.麥.wav框們[k]

            
            x1= np.fromstring(b1,'int16')
            '''
                
            # mic + wav 檔
            x2ch= x1 + x0
            
            # 以下轉頻譜
            
            x2ch= x2ch * ham  #np.hamming(len(x)) # 拿出去，改善速度
            
            xFFT= np.fft.fft(x2ch)[0:self.麥.frame_size//2] # 這時，僅剩 Fs/4 的frequency範圍了，解析度更高了吧。
            
            xP=   np.absolute(xFFT*xFFT.conj())
            
            #self.i譜框= self.麥.i框  # 框同步
            
            self.specgram[self.i譜框%self.譜框數]= xP
            
            self.i譜框 += 1
            
            頻譜= self.specgram #.copy()

            #
            # up_down flip, 頻譜上下對調，讓低頻在下，高頻在上，比較符合直覺。
            #
            頻譜= 頻譜[:,-1::-1]

            #
            # 這個 頻譜 大小要如何自動調整才能恰當的呈現在螢幕上，還有待研究一下。
            #
            頻譜= (np.log(頻譜)+10)*10

            
            
       
            
            
            
            #
            # 錦上添花
            #
            # 加這行讓頻譜會轉，有趣！！
            #
            if keyboard == pg.K_e:
                頻譜= np.roll(頻譜, -int(self.i譜框 % self.譜框數), axis=0)
                
                x= (self.譜框數-1)  * self.幕寬 / self.譜框數
                h= self.幕高
                pg.draw.line(self.幕, pg.Color('white'),(x,h),(x,0) , 10)
                

                pg.display.update()


            #
            # pygame 的 主要貢獻:  頻譜 ---> 音幕
            #
            pg.surfarray.blit_array(self.音幕, 頻譜.astype('int'))

            #
            # pygame 的 次要貢獻: 調整一下 self.譜寬高 音幕 ---> aSurf
            #
            aSurf= pg.transform.scale(self.音幕, (self.幕寬, self.幕高)) #//4))

            #
            # 黏上幕  aSurf ---> display
            #

            #aSurf= pg.transform.average_surfaces([aSurf, self.攝影畫面])
            self.幕.blit(aSurf, (0,0))


            
            #
            # 江永進的建議，在頻譜前畫一條白線，並把能量、frequency軌跡畫出。
            #
            
            if keyboard != pg.K_e:
                x= (self.i譜框 % self.譜框數)  * self.幕寬 / self.譜框數
            else:
                x= (self.譜框數-1)  * self.幕寬 / self.譜框數
                
            h= self.幕高
            w= self.幕寬
            pg.draw.line(self.幕, pg.Color('gray'),(x,h),(x,0) , 10)
            
            #
            # 把12平均律譜線在此跟江永進白線一起畫出。
            #
            for xx in range(16):
                xxx= xx*w//16
                c= 255-(xx*256*4//16)%256
                pg.draw.line(self.幕, (c,c,c),(xxx,0),(xxx,h) , 1)
            
            for n in range(-36,1):
                #f譜線= note2freq(n)
                y譜線= 2**(n/12)*h #h-f譜線/440*h
                
                y譜線= h- y譜線
                
                #c= pg.Color('cyan')
                
                #c= frequency_to_color((n/12)%1, is_color= True) 
                
                pg.draw.line(self.幕, pg.Color('black'),(0,y譜線),(w,y譜線) , 2)
                
                if n%12 in [3,5,7,8,10,0,2]: # C 大調，通通沒升記號。
                
                    c= frequency_to_color((n/12)%1, is_color= True)                 
                    pg.draw.line(self.幕, c,(0,y譜線),(w,y譜線) , 3)
                    
                    noteName= noteNameL[n%len(noteNameL)] # noteNameL 在 ryPitch__ 裡面
                    noteMsg= '{}'.format(noteName)
                    noteText= aFont.render(noteMsg, True, c)#pg.Color('white'))
                    pg.draw.rect(self.幕, pg.Color('white'),[(x-20, y譜線-20),(20,20)])
                    self.幕.blit(noteText, (x-20, y譜線-20))
                
            

            # 把 f0 放在這裡。
            f0= freq_from_autocorr(x0, self.麥.sample_rate)#.frame_size) #self.麥.sample_rate)
            f1= freq_from_autocorr(x1, self.麥.sample_rate)#.frame_size) #self.麥.sample_rate)
            
            en0= abs(x0).mean()
            en1= abs(x1).mean()
            
            x0聲音夠大= False
            x1聲音夠大= False
            if en0 > self.麥.初框['mean']    + self.麥.初框['std']*3:    x0聲音夠大= True
            if en1 > self.麥.wav初框['mean'] + self.麥.wav初框['std']*3: x1聲音夠大= True
            
            if x0聲音夠大==False: f0=1.0
            if x1聲音夠大==False: f1=1.5 # 避開2倍 那會當作正確
            #s= abs(x).std()
            
            #
            # 永遠把 f0 限縮在 440 以內，以利畫圖於幕上
            #
            while f0>440: f0=f0/2
            while f1>440: f1=f1/2
            
            #
            # 量化在半音內，觀看音符比較穩定。
            #
            f0_Q, note0= pitchQuantization(f0)
            f1_Q, note1= pitchQuantization(f1)
            
            #
            # 簡單的評分，調整八度後，相差 1 semitone 以內 就算正確。
            #
            pitchHit= False
            if (f0/f1 < 1.06 and f0/f1 > 1/1.06):       pitchMatching += 1; pitchHit= True
            elif (f0/2/f1 < 1.06 and f0/2/f1 > 1/1.06): pitchMatching += 1; pitchHit= True
            elif (f0/4/f1 < 1.06 and f0/4/f1 > 1/1.06): pitchMatching += 1; pitchHit= True
            elif (f0*2/f1 < 1.06 and f0*2/f1 > 1/1.06): pitchMatching += 1; pitchHit= True
            else: pass
            
            pitchScore_y= (h - pitchMatching)%h  # for y axis
            pitchScore_x= ((pitchMatching//h+1)*16) % w # for x axis
            
            pg.draw.rect(self.幕, pg.Color('blue'),[(pitchScore_x, pitchScore_y+20),(60,20)])
            pg.draw.rect(self.幕, pg.Color('blue'),[(pitchScore_x, pitchScore_y),(60,20)])
            pg.draw.rect(self.幕, pg.Color('yellow'),[(pitchScore_x, pitchScore_y-20),(60,20)])
            #pg.draw.line(self.幕, pg.Color('blue'),(0, pitchScore_y),(pitchScore_x, pitchScore_y), 2)
            pg.draw.line(self.幕, pg.Color('blue'),(0, h),(0, pitchScore_y), pitchScore_x*2) #2)
            
            aMsg= '{}, {:.0f}'.format(note0, f0)
            aText= aFont.render(aMsg, True, pg.Color('white'))
            
            bMsg= '{}, {:.0f}'.format(note1, f1)
            bText= aFont.render(bMsg, True, pg.Color('yellow'))
            
            cMsg= '{}'.format(pitchMatching)
            cText= aFont.render(cMsg, True, pg.Color('blue'))
            
            self.幕.blit(aText, (pitchScore_x, pitchScore_y+20)) # 'while'
            self.幕.blit(bText, (pitchScore_x, pitchScore_y))    # 'yellow'
            self.幕.blit(cText, (pitchScore_x, pitchScore_y-20)) # 'blue'
            
            # 把 f0 放在這裡。
            #x= (self.i譜框 % self.譜框數)  * self.幕寬 / self.譜框數
            #h= self.幕高
            
            #f0 = f0/440*h # f0 先放大16倍，
            #f1 = f1/440*h
            
            f0_h= h - f0/440*h
            f1_h= h - f1/440*h
            self.fQ += [(f0_h, f1_h)] 
            
            while len(self.fQ)>128: self.fQ.popleft()     # 保持 16 框就好
            
            for n in range(len(self.fQ)):
                x00= x+ (n-len(self.fQ)) *8 #*16 # 橫軸 放大 16 倍
                y00= self.fQ[n][0]
                
                x01= x+ (n-len(self.fQ)+4) *8 #不知為何它早出現約4框？只在前方4框先畫出
                y01= self.fQ[n][1]
                
                pg.draw.ellipse(self.幕, pg.Color('white'), [(x00, y00), (16, 16)],4)
                pg.draw.ellipse(self.幕, pg.Color('yellow'), [(x01, y01), (12,12)])
                
                #self.幕.blit(bText, ((x00, y00)))
                #self.幕.blit(aText, ((x00, y01)))
                
                '''
                if (n==len(self.fQ)-1):# and (pitchHit == True):
                    
                    pg.draw.rect(self.幕, pg.Color('blue'),[(x00, y01),(60,20)]) 
                    pg.draw.rect(self.幕, pg.Color('blue'),[(x00, y00),(60,20)]) 
                
                    self.幕.blit(aText, ((x00, y01)))
                    self.幕.blit(bText, ((x00, y00)))
                '''
                
            
            #aLyric= '.wav_i框= {:10d}, aLyric......, '.format(self.麥.wav_i框)#i譜框) # wav_i框
            '''
            if keyboard == pg.K_UP:
                iLyric -= 1
                iLyric = iLyric%len(LyricToki)
                aLyric= LyricToki[iLyric-2]
                bLyric= LyricToki[iLyric-1]
                cLyric= LyricToki[iLyric]
                
            elif keyboard == pg.K_DOWN:
                iLyric += 1
                iLyric = iLyric%len(LyricToki)
                aLyric= LyricToki[iLyric-2]
                bLyric= LyricToki[iLyric-1]
                cLyric= LyricToki[iLyric]
            '''
            #
            # 把歌詞之時間文字插在這裡，但資料結構沒有細想，
            # 結果就有點紊亂，應重新構思改寫。
            #
            pg.display.update()

           
        def 滑鼠游標顯示(self, mouse_x_axis, mouse_y_axis, keyboard= None):

            大小=         10 #max(10, 音訊能量 )
            位置及大小=  (mouse_x_axis - 大小/2, mouse_y_axis - 大小/2, 大小, 大小)

 
            色=      (255, 255, 255) #frequency_to_color(frequency)

            pg.draw.ellipse(self.幕, 色, 位置及大小)
            pg.display.update()

        ###############################

        #'''
        pg.init()

        self.幕= pg.display.set_mode( self.幕寬高, 0 )
        
        screen_title= '''cguKaraOkeScoring using Pyaudio, Pygame on Python 3, 
            by Renyuan Lyu (呂仁園), Chang Gung Univ (長庚大學), TAIWAN, modified by YCH'''
        pg.display.set_caption(screen_title)
        
        self.音幕= pg.Surface( self.譜寬高, depth= self.深度) # for specgram

        self.音幕.set_palette(self.調色盤)
        #'''
        self.fQ= collections.deque()
        
        print('頻譜主迴圈....')

        mouse_is_click=      False
        mouse_x_axis= mouse_y_axis=  0
        keyboard=          None

        i歌詞時間點們= []
        i歌詞= 0

        self.麥.等待第一圈錄音圓滿_wav()
        self.麥.等待第一圈錄音圓滿()
        
        self.main_loop_running=  True
        
        while self.main_loop_running:
            
            if self.麥.wav錄音線程活著==False:
                self.main_loop_running =  False
                pg.quit()
                self.麥.stop()
                sys.exit()
                break
            i框= self.麥.wav_i框
            if i框==0:
                print('{}'.format(i歌詞時間點們))
                
                xL= i歌詞時間點們
                yL= sorted(xL, key= lambda xL: xL[2])
                yD= dict([(x1,x3) for (x0, x1, x2,x3) in yL])
                
                print('{}'.format(yD))
                
                #self.時間點歌詞= yD
                
                
                i歌詞時間點們= []
                iLyric= 0
                曾來過= False
                
                if self.麥.音檔名 in LrcDic.keys():
                    self.時間點歌詞= LrcDic[self.麥.音檔名]
                    self.時間點們=   sorted(list(self.時間點歌詞.keys()))
                else:
                    self.時間點歌詞= {}
                    self.時間點們= []
                    
                self.麥.初框線程(source= 'wav')
                self.麥.初框線程(source= 'mic')
            
            #
            # 取得 使用者 輸入 事件
            #
            事件群= pg.event.get()

            #
            # 處理 使用者 輸入 事件
            #
            for e in 事件群:
                #
                # 首先 優先處理 如何結束，優雅的結束！
                #
                # 用滑鼠點擊 X (在 視窗 右上角) 結束！
                #
                if e.type in [pg.QUIT]:
                    self.main_loop_running= False
                    pg.quit()
                    self.麥.stop()
                    sys.exit()
                    break
                #
                # 用keyboard 按 Esc (在 keyboard 左上角) 結束！
                #
                elif e.type in [pg.KEYDOWN]:
                    keyboard= e.key
                    if e.key in [pg.K_ESCAPE]:
                        self.main_loop_running= False
                        pg.quit()
                        self.麥.stop()
                        sys.exit()
                        break
                    
                    
                    elif e.key in [pg.K_SPACE]:
                        
                        pass
                    
                    elif e.key in [pg.K_a]:
                        self.麥.初框線程(source= 'wav')
                        self.麥.初框線程(source= 'mic')
                        print('self.麥.初框= {}'.format(self.麥.初框))
                        print('self.麥.wav初框= {}'.format(self.麥.wav初框))
                    
                    else:
                        pass
                        
                elif e.type in [pg.KEYUP]:
                    keyboard= None
                #
                # 以下 3 個 if , 用來 處理 滑鼠
                #
                elif e.type in [pg.MOUSEBUTTONDOWN]:
                    mouse_is_click= True
                    mouse_x_axis, mouse_y_axis= x,y= e.pos

                elif e.type in [pg.MOUSEBUTTONUP]:
                    mouse_is_click= False
                    mouse_x_axis, mouse_y_axis= x,y= e.pos

                elif e.type in [pg.MOUSEMOTION]:
                    if (mouse_is_click is True):
                        mouse_x_axis, mouse_y_axis= x,y= e.pos
                else:
                    pass

            #
            # 音訊
            #
            取音訊且顯示頻譜於幕(self, keyboard) # 用 K_efgh 來控制音訊處理

            #
            # 滑鼠
            #
            if (mouse_is_click is True):  # 用 K_ijk 來控制滑鼠處理
                滑鼠游標顯示(self, mouse_x_axis, mouse_y_axis, keyboard) 
            #
            # 畫面更新
            #
            pg.display.flip()
            while (self.麥.wav_i框 - i框 == 0 ): pass # .wav_i框 會在 ryMic reset 成 0
            #clk.tick(10) # 類似 vpython 之 rate
        if self.main_loop_running == False:
            pg.quit()
            self.麥.stop()
            sys.exit()
        #
        # 跳出主迴圈了
        #
        #self.攝影機.stop()
        #self.麥.結束()
        
        #self.麥.stop()
            
        
    
    
    def start(self):
            
        self.頻譜線.start() # 用 thread 執行時，關不掉！！(quit 不了)

if __name__=='__main__':   
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    app.exec_()
    if mainWin.allo ==True:
        if mainWin.NoNet ==True:
            麥= RyMic(musicfile = r'NoNetSongs/'+str(mainWin.filename)+r'.wav')
            麥.start()
            
            頻譜= Ry頻譜類(麥)
            頻譜.start()
        else:
            麥= RyMic(musicfile = r'output/tmp/KaraOKE.wav')
            麥.start()
            
            頻譜= Ry頻譜類(麥)
            頻譜.start()
    else:
        sys.exit()

    
    
    
    