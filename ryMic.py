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

    def __init__(self,musicfile = None, sample_rate= 16000,  frame_size= 1024, 框數= 32):#16):
    
        self.audio=  pyaudio.PyAudio()
        self.musicfile = musicfile
        self.sample_rate= self.point_per_sec=  sample_rate #16000 # 10240 #10000
        self.frame_size=            frame_size #1024  # 1000
        self.byte_per_point= byte_per_point= 2

        self.音流=  self.audio.open(
                    rate=     self.sample_rate, 
                    channels= 1, # 麥克風鎖定 1 聲道，若是 wav file，則可處理多聲道。
                    format=   self.audio.get_format_from_width(
                                        byte_per_point, 
                                        unsigned= 'False'), #8,
                    
                    frames_per_buffer= self.frame_size, 
                    
                    input= True, 
                    output=True
                    )
        
        #主要　語音資料在此！！　將維持　.框數　個框
        self.框們=  deque() #[] # 據說用 deque 比用 list 快很多 leftpop() vs pop(0) ，練習看看。
        self.i框=   0        
        
        '''         
        self.秒數= 秒數 #1
        self.點數= self.秒數 * self.point_per_sec
        self.框數= self.點數 // self.frame_size 
        '''
        self.框數= 框數
        self.點數= self.框數 * self.frame_size
        self.秒數= self.點數 / self.point_per_sec # 秒數非整數，在此預設值計算為 1.024
        
        # 由於這裡會無條件捨去小數點，
        # 故實際秒數會變小一點。 
        

        # 計算初始環境雜訊之資訊，可模仿之來撰寫其他演算法
        self.初框= {'mean':0, 'std':1, 'fmean':0, 'fstd':1}
        
        #
        # 用多線程
        #
        self.record=  threading.Thread(target= self.record_thread )
        self.放音線=  threading.Thread(target= self.放音線程 )       
        self.初框線=  threading.Thread(target= self.初框線程)
        self.wav初框線=  threading.Thread(target= self.初框線程,kwargs={'source':'wav'})
        
        #
        # 加入 wav 檔 當作 麥 來用，可同時使用。
        #
        
        self.wav錄放音線=  threading.Thread(target= self.wav錄放音線程)
        
        self.wavsample_rate= self.wav每秒點數=  self.sample_rate #16000 # 10240 #10000
        self.wavframe_size=                self.frame_size #1024  # 1000
        self.wavbyte_per_point=              self.byte_per_point=           2
        
        self.wav框們=  deque() #[]
        self.wav_i框=   0        
        
        '''         
        self.秒數= 秒數 #1
        self.點數= self.秒數 * self.point_per_sec
        self.框數= self.點數 // self.frame_size 
        '''
        self.wav框數= self.框數
        self.wav點數= self.框數 * self.frame_size
        self.wav秒數= self.點數 / self.point_per_sec # 秒數非整數，在此預設值計算為 1.024

    def record_thread(self):
        '''
        讀檔並以每個frame_size大小放入 框們 且 i框++
        框們為queue
        '''
    
        # 最初 決定 框數= 10，frame_size= 1000， frame_size應小於 y.get_read_available()
        #
        #
        #框數     = 10
        #frame_size = 1024
        #
        print('record_thread()....')
        
        self.i框= 0
        self.框們=  deque() #[]
        for i in range(self.框數):
            z= self.音流.read(self.frame_size) #, exception_on_overflow= False )
            
            #self.音流.write(z) ## 即時放音
            
            self.框們 += [z]
            self.i框  += 1
            

        #
        # 往後一直維持 相同框數(=10)，讀進 最新 @10 (末端)，丟棄 最舊 @0 (前端)
        # 框們[0 .. -1]
        #
        
 
        self.record_thread_is_alive= True
        while self.record_thread_is_alive: #True:
            
            z= self.音流.read(self.frame_size)
            
            self.框們 += [z]  # 新框加在尾端
            self.i框  += 1
            
            self.框們.popleft()#pop(0)  # 舊框彈出
        
        # 如此，框們[:] ==框們[0,...,(N-1)] == 框們[-N,...,-1]

    def 等待第一圈錄音圓滿(self):
        while (len(self.框們) < self.框數): time.sleep(.01)
        return True
        
    def 放音線程(self):
        
        print('放音線程()....')
        self.等待第一圈錄音圓滿()
        
        self.放音線程活著= True
        while self.放音線程活著: #True:
            z= self.框們[0] # [0..-1] # 錄音進 框們[-1] 之後，放音與其相距 (框數-1) 個框
            self.音流.write(z)
           
        '''
        Good....
        錄音從最右邊進來
        到達最左邊才放音
        '''


    def start(self, 錄= True, 放= False, 初= True, wav= True):

        if 錄:   self.record.start()
        if 放:   self.放音線.start()
        if 初:   
            self.初框線.start()
            self.wav初框線.start()
            
        if wav:  self.wav錄放音線.start()

    def stop(self):
        '''
        結束錄放音線程
        '''
        self.record_thread_is_alive= False
        self.放音線程活著= False
        self.wav_record_thread_is_alive= False
        
        time.sleep(.1) # 等一下，讓錄放音線程停車
        
        
        self.音流.close()
        self.audio.terminate()
    
       
    def 初框線程(self, source= 'mic'):
        

        #取 最初框、算振幅平均mean、振幅標準差std
        
        print('{}, source= {}\n'.format('初框線程()....', source))
        
        if source == 'mic':
            self.等待第一圈錄音圓滿()
            x= self.框們 #.copy()
        else: #source == 'wav': # source= 'wav'
            self.等待第一圈錄音圓滿_wav()
            x= self.wav框們 #.copy()
        
        x= b''.join(x) # 二進位數字串 b'...'
        x= np.fromstring(x, dtype= np.int16) # 須轉為 int

        m= abs(x).mean()
        s= abs(x).std()
        
          
        #
        # 把頻譜當作 機率分布，算 平均頻率
        #
        N= self.frame_size
        k= np.arange(N//2)
        
        平均頻率=0
        平均平方頻率=0
        for i in range(self.框數):
            X= np.fft.fft(x[(0+i*N):(N+i*N)])
            X= abs(X)
            X= X[0:N//2]
            
            #防止X.sum()==0 但不知會不會影響其他地方
            if X.sum() == 0:
                continue
            else:   
                平均頻率 += (k*X).sum()/X.sum() 
                
                平均平方頻率 += (k*k*X).sum()/X.sum() 
        
        平均頻率 /= self.框數
        平均平方頻率 /= self.框數
        
        頻率var= 平均平方頻率-平均頻率**2
        頻率std= 頻率var**.5
        
        平均頻率 *= self.sample_rate/self.frame_size
        頻率std *= self.sample_rate/self.frame_size
        
        if source=='mic':
            self.初框=    {'mean':m, 'std':s, 'fmean':平均頻率, 'fstd':頻率std}
        else:  #source=='wav':
            self.wav初框= {'mean':m, 'std':s, 'fmean':平均頻率, 'fstd':頻率std}

        
        #self.重新計算初框活著= False
        #print('初框= ',self.初框)
        
        
        #重新計算初框活著= False

    def 等待第一圈錄音圓滿_wav(self):
        while (len(self.wav框們) < self.wav框數): time.sleep(.01)
        return True
        
    def wav錄放音線程(self):
        
        p= self.audio
        音檔名 = self.musicfile
        self.wav_record_thread_is_alive= True
        
        self.wav_i框= 0 
        self.wav框們=  deque() #[]
        while self.wav_record_thread_is_alive:
        
            self.音檔名 = 音檔名
            
            
            with wave.open(音檔名,'rb') as f:
                   
                fm= p.get_format_from_width(f.getsampwidth())
                ch= f.getnchannels()
                self.wavsample_rate= rt= f.getframerate()
                
                print('音檔名={}, fm= {}, ch= {}, rt= {}'.format(音檔名, fm, ch, rt))

                self.w音流= p.open(
                                format=   fm,
                                channels= max(ch-1,1),  #1,  #ch, 永遠只放音單聲道
                                rate=     rt,
                                output= True)
                                           
                self.wav_i框= 0 #self.i框 #0 # 用 來同步，起初同步，運作過程未知。待研究！！
                
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

                    
                    self.w音流.write(z0)
                    
                    self.wav框們 += [z1]  # 新框加在尾端
                    
                    self.wav_i框  += 1
                    #self.wav_i框= self.i框 #0 # 用 來同步
                    self.i框=  self.wav_i框
                    
                    
                    while len(self.wav框們) > self.wav框數:
                        self.wav框們.popleft()#pop(0)  # 舊框彈出
                self.wav_record_thread_is_alive= False
                self.w音流.stop_stream()
                self.w音流.close()
                        

if __name__=='__main__':        
    x= RyMic(musicfile = 'output/tmp/KaraOKE.wav')
    x.start()
    print('ryEnjoy.....! 記得　x.stop()')
     
