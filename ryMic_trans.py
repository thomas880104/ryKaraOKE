'''
ryMic.py

ryMic003_deque.py
ryMic002_waveFile.py

ryMic.py
ry重寫錄放音.py

Renyuan Lyu
2016/08/03, 08/06, 08/15, 08/21

'''
import threading
import time
import pyaudio
import numpy as np
import wave
import struct

from collections import deque

#
# 語音的時間單位要精細劃分，
# 點 < 框 < 秒 < 段
#
# 點 即是 樣本點，為最小的時間單位
#
# 點、秒 可透過 sample_rate 來設定
# point_per_sec 即為 sample_rate， 
# 習慣上可設為 44100, 16000
#
# 在此：
# 1 框 = 1024 點 (取 2**10 ，適合後面的 FFT 運算)
#

class RyMic:

    def __init__(self,musicfile = None, sample_rate= 16000,  frame_size= 1024, n_frame= 32):#16):
    
        self.audio=  pyaudio.PyAudio()
        self.musicfile = musicfile
        self.sample_rate= self.point_per_sec=  sample_rate #16000 # 10240 #10000
        self.frame_size=            frame_size #1024  # 1000
        self.byte_per_point= byte_per_point= 2

        self.stream=  self.audio.open(
                    rate=     self.sample_rate, 
                    channels= 1, # 麥克風鎖定 1 聲道，若是 wav file，則可處理多聲道。
                    format=   self.audio.get_format_from_width(
                                        byte_per_point, 
                                        unsigned= 'False'), #8,
                    
                    frames_per_buffer= self.frame_size, 
                    
                    input= True, 
                    output=True
                    )
        
        #主要　語音資料在此！！　將維持　.n_frame　個框
        self.frame_array=  deque() #[] # 據說用 deque 比用 list 快很多 leftpop() vs pop(0) ，練習看看。
        self.frame_counter=   0        
        
        '''         
        self.sec= sec #1
        self.point= self.sec * self.point_per_sec
        self.n_frame= self.point // self.frame_size 
        '''
        self.n_frame= n_frame
        self.point= self.n_frame * self.frame_size
        self.sec= self.point / self.point_per_sec # sec非整數，在此預設值計算為 1.024
        
        # 由於這裡會無條件捨去小數點，
        # 故實際sec會變小一點。 
        

        # 計算初始環境雜訊之資訊，可模仿之來撰寫其他演算法
        self.first_frame= {'mean':0, 'std':1, 'fmean':0, 'fstd':1}
        
        #
        # 用多線程
        #
        self.record=  threading.Thread(target= self.record_thread )
        self.play=  threading.Thread(target= self.play_thread )       
        self.first_frame_thread=  threading.Thread(target= self.first_frame_thread)
        self.wav_first_frame_thread=  threading.Thread(target= self.first_frame_thread,kwargs={'source':'wav'})
        
        #
        # 加入 wav 檔 當作 麥 來用，可同時使用。
        #
        
        self.wav_record_and_play=  threading.Thread(target= self.wav_record_and_play_thread)
        
        self.byte_per_point = 2
        
        self.wav_frame_array=  deque() #[]
        self.wav_frame_counter=   0        
        
        '''         
        self.sec= sec #1
        self.point= self.sec * self.point_per_sec
        self.n_frame= self.point // self.frame_size 
        '''

    def record_thread(self):
        '''
        讀檔並以每個frame_size大小放入 frame_array 且 frame_counter++
        frame_array為queue
        '''
    
        # 最初 決定 n_frame= 10，frame_size= 1000， frame_size應小於 y.get_read_available()
        #
        #
        #n_frame     = 10
        #frame_size = 1024
        #
        print('record_thread()....')
        
        self.frame_counter= 0
        self.frame_array=  deque() #[]
        for i in range(self.n_frame):
            z= self.stream.read(self.frame_size) #, exception_on_overflow= False )
            
            #self.stream.write(z) ## 即時放音
            
            self.frame_array += [z]
            self.frame_counter  += 1
            

        #
        # 往後一直維持 相同n_frame(=10)，讀進 最新 @10 (末端)，丟棄 最舊 @0 (前端)
        # frame_array[0 .. -1]
        #
        
 
        self.record_thread_is_alive= True
        while self.record_thread_is_alive: 
            
            z= self.stream.read(self.frame_size)
            
            self.frame_array += [z]  # 新框加在尾端
            self.frame_counter  += 1
            
            self.frame_array.popleft()#pop(0)  # 舊框彈出
        
        # 如此，frame_array[:] ==frame_array[0,...,(N-1)] == frame_array[-N,...,-1]

    def frame_array_is_full(self, source = 'mic'):
        if source == 'mic':
            while (len(self.frame_array) < self.n_frame): 
                time.sleep(.01)
            return True
        elif source == 'wav':
            while (len(self.wav_frame_array) < self.n_frame): 
                time.sleep(.01)
            return True
        
    def play_thread(self):
        
        print('play_thread()....')
        self.frame_array_is_full()
        
        self.play_thread_is_alive= True
        while self.play_thread_is_alive: #True:
            z= self.frame_array[0] # [0..-1] # 錄音進 frame_array[-1] 之後，放音與其相距 (n_frame-1) 個框
            self.stream.write(z)
           
        '''
        Good....
        錄音從最右邊進來
        到達最左邊才放音
        '''


    def start(self, record= True, play= False, first= True, wav= True):

        if record:   self.record.start()
        if play:   self.play.start()
        if first:   
            self.first_frame_thread.start()
            self.wav_first_frame_thread.start()
            
        if wav:  self.wav_record_and_play.start()

    def stop(self):
        '''
        結束record_and_play_thread
        '''
        self.record_thread_is_alive= False
        self.play_thread_is_alive= False
        self.wav_record_thread_is_alive= False
        
        time.sleep(.1) # 等一下，讓record_and_play_thread停車
        
        
        self.stream.close()
        self.audio.terminate()
    
       
    def first_frame_thread(self, source= 'mic'):
        '''
        取 最first_frame、算振幅平均mean、振幅標準差std
        '''

        
        print('{}, source= {}\n'.format('first_frame_thread()....', source))
        
        if source == 'mic':
            self.frame_array_is_full(source = 'mic')
            x= self.frame_array #.copy()
        else: #source == 'wav': # source= 'wav'
            self.frame_array_is_full(source = 'wav')
            x= self.wav_frame_array #.copy()
        
        x= b''.join(x) # 二進位數字串 b'...'
        x= np.fromstring(x, dtype= np.int16) # 須轉為 int

        m= abs(x).mean()
        s= abs(x).std()
        
     
        if source=='mic':
            self.first_frame=    {'mean':m, 'std':s}#, 'fmean':平均頻率, 'fstd':頻率std}
        else:  #source=='wav':
            self.wav_first_frame= {'mean':m, 'std':s}#, 'fmean':平均頻率, 'fstd':頻率std}

        
        #self.重新計算first_frame活著= False
        #print('first_frame= ',self.first_frame)
        
        
        #重新計算first_frame活著= False

    def frame_array_is_full_wav(self):
        while (len(self.wav_frame_array) < self.n_frame): time.sleep(.01)
        return True
        
    def wav_record_and_play_thread(self):
        
        p= self.audio
        wav_name = self.musicfile
        self.wav_record_thread_is_alive= True
        
        self.wav_frame_counter= 0 
        self.wav_frame_array=  deque() #[]
        while self.wav_record_thread_is_alive:
        
            self.wav_name = wav_name
            
            
            with wave.open(wav_name,'rb') as f:
                   
                fm= p.get_format_from_width(f.getsampwidth())
                ch= f.getnchannels()
                self.sample_rate= rt= f.getframerate()
                
                print('wav_name={}, fm= {}, ch= {}, rt= {}'.format(wav_name, fm, ch, rt))

                self.w_stream= p.open(
                                format=   fm,
                                channels= max(ch-1,1),  #1,  #ch, 永遠只放音單聲道
                                rate=     rt,
                                output= True)
                                           
                self.wav_frame_counter= 0 #self.frame_counter #0 # 用 來同步，起初同步，運作過程未知。待研究！！
                
                self.wav_record_thread_is_alive= True
                while self.wav_record_thread_is_alive: #True:
                    
                    z= f.readframes(self.frame_size)
                    
                    if z==b'' or len(z)<self.frame_size*self.byte_per_point*ch: break #f.rewind() # 重複
                    
                    
                    if ch==1:
                        z0= z1= z
                        
                    elif ch==2:
                        #
                        # 1 sterio ==> 2 mono , for short int
                        #
                        nFrames= self.frame_size #4
                        x= z #f.readframes(nFrames)
                        
                        xx= struct.unpack('<'+'hh'*nFrames,x)
                        
                        x0= xx[0::2]
                        x1= xx[1::2]
                        
                        z0= struct.pack('<'+'h'*nFrames, *x0)
                        z1= struct.pack('<'+'h'*nFrames, *x1)
                    
                    elif ch==3:
                        #
                        # 1 sterio ==> listening 
                        # 1 mono ==> analysis and processing, teacher's voice
                        #
                        nFrames= self.frame_size #4
                        x= z #f.readframes(nFrames)
                        
                        xx= struct.unpack('<'+'lh'*nFrames,x) # 'l'== 4 bytes, 'h'== 2 bytes
                        
                        x0= xx[0::2] # 左右放音, 4 bytes = 2 bytes + 2 bytes
                        x1= xx[1::2] # 分析,     2 bytes
                        
                        z0= struct.pack('<'+'l'*nFrames, *x0)
                        z1= struct.pack('<'+'h'*nFrames,  *x1)
                   
                    else: 
                        z0= z1= b''
                        print('ch= {}, not processed'.format(ch))
                        break

                    
                    self.w_stream.write(z0)
                    
                    self.wav_frame_array += [z1]  # 新框加在尾端
                    
                    self.wav_frame_counter  += 1
                    #self.wav_frame_counter= self.frame_counter #0 # 用 來同步
                    self.frame_counter=  self.wav_frame_counter
                    
                    
                    while len(self.wav_frame_array) > self.n_frame:
                        self.wav_frame_array.popleft()#pop(0)  # 舊框彈出
                self.wav_record_thread_is_alive= False
                self.w_stream.stop_stream()
                self.w_stream.close()
                        

if __name__=='__main__':        
    x= RyMic(musicfile = 'output/tmp/KaraOKE.wav')
    x.start()
    print('ryEnjoy.....! 記得　x.stop()')
     
