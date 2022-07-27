'''
2022/3/8
修改Downloading_music,myspleeterrun內容
可將下載過的音樂存入localfile資料夾
2022/3/11
修正onvocal，Downloading_music功能
2022/3/15
增加folder selecter for local file
2022/3/31
分別將onvocal & offvocal 版本放入相對應的folder
2022/4/22
處理檔名問題與下載影片
'''
from pytube import YouTube
import ffmpeg
import shlex, subprocess,os,shutil,time
from pydub import AudioSegment 



def Splitting_stereo_audio(file):
    # Import stereo audio file and check channels
    stereo_audio = AudioSegment.from_file(file,format="wav")
    
    # Split stereo phone call and check channels
    channels = stereo_audio.split_to_mono()
    channel_1 = channels[0]
    channel_2 = channels[1]
    return channel_1,channel_2

def Downloading_music(link,video):
    '''
    input:youtube link
    output:song title
    '''
    song_there = os.path.isfile("tmp.wav")
    if song_there:
        try:
            os.remove("tmp.mp4")
            os.remove("tmp.wav")
            os.remove('output/tmp/accompaniment.wav')
            os.remove("output/tmp/vocals.wav")
        except:
            pass
    yt=YouTube(link)
    if video == True:
        t=yt.streams.get_highest_resolution()
        v = t
    elif video == False:
        t=yt.streams.filter(only_audio=True, file_extension='mp4')
        v = t[0]
    v.download(filename='tmp.mp4')
    name= v.title
    symbol = [':','/','\\']
    for s in symbol: 
        if name.find(s) >= 0:
            name = name.replace(s,' ')
    print(name+'.mp4')
    video = ffmpeg.input('./tmp.mp4')
    audio = video.audio
    stream = ffmpeg.output(audio, "tmp.wav")
    ffmpeg.run(stream)
    shutil.move('tmp.mp4', 'localfile/mp4/' + name + '.mp4')
    return name
def myspleeterrun(song_name = 'KaraOKE',mode = 'offvocal'):
    command_line = "spleeter separate -o output/ tmp.wav"
    args = shlex.split(command_line)
    p = subprocess.Popen(args)
    p.wait()  
    if mode == 'offvocal':
        accompaniment_channel_1,accompaniment_channel_2 = Splitting_stereo_audio('output/tmp/accompaniment.wav')
    elif mode == 'onvocal':
        accompaniment_channel_1,accompaniment_channel_2 = Splitting_stereo_audio('./tmp.wav')
    vocal_channel_1,vocal_channel_2 = Splitting_stereo_audio(r"output/tmp/vocals.wav")
    mutli_channel = AudioSegment.from_mono_audiosegments(accompaniment_channel_1,accompaniment_channel_2,vocal_channel_1)
    mutli_channel.export("output/tmp/KaraOKE.wav",format="wav")
    sound = AudioSegment.from_file("output/tmp/KaraOKE.wav")
    sound = sound.set_frame_rate(16000)
    sound.export("output/tmp/KaraOKE.wav",format="wav")
    shutil.copyfile('./output/tmp/KaraOKE.wav', './localfile/KaraOKE.wav')
    print(song_name)
    if mode == 'offvocal':
        shutil.move('./localfile/KaraOKE.wav', './localfile/offvocal/' + song_name + '.wav')
    elif mode == 'onvocal':
        shutil.move('./localfile/KaraOKE.wav', './localfile/onvocal/' + song_name + '.wav')
    os.remove('./tmp.wav')

def localfile_spleeter(song_name):
    video = ffmpeg.input(song_name)
    audio = video.audio
    stream = ffmpeg.output(audio, "tmp.wav")
    ffmpeg.run(stream)
    command_line = "spleeter separate -o output/ tmp.wav"
    args = shlex.split(command_line)
    p = subprocess.Popen(args)
    p.wait()  
    accompaniment_channel_1,accompaniment_channel_2 = Splitting_stereo_audio('./tmp.wav')
    vocal_channel_1,vocal_channel_2 = Splitting_stereo_audio("output/tmp/vocals.wav")
    mutli_channel = AudioSegment.from_mono_audiosegments(accompaniment_channel_1,accompaniment_channel_2,vocal_channel_1)
    mutli_channel.export("output/tmp/KaraOKE.wav",format="wav")
    sound = AudioSegment.from_file("output/tmp/KaraOKE.wav")
    sound = sound.set_frame_rate(16000)
    sound.export(r"output/tmp/KaraOKE.wav",format="wav")
    shutil.copyfile('./output/tmp/KaraOKE.wav', './localfile/KaraOKE.wav')
    print(song_name)
    song_name = song_name.split('/')[-1][:-4]
    
    shutil.move('./localfile/KaraOKE.wav', './localfile/onvocal/' + song_name + '.wav')
    os.remove('./tmp.wav')
    return song_name