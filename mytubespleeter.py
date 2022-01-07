
from pytube import YouTube
import ffmpeg
import shlex, subprocess,os
from pydub import AudioSegment 



def Splitting_stereo_audio(file):
    # Import stereo audio file and check channels
    stereo_audio = AudioSegment.from_file(file,format="wav")
    
    # Split stereo phone call and check channels
    channels = stereo_audio.split_to_mono()
    channel_1 = channels[0]
    channel_2 = channels[1]
    return channel_1,channel_2

def Downloading_music(link):
    song_there = os.path.isfile("tmp.wav")
    if song_there:
        try:
            os.remove("tmp.mp4")
            os.remove("tmp.wav")
            os.remove(r'output\tmp\accompaniment.wav')
            os.remove(r"output\tmp\vocals.wav")
        except:
            pass
    yt=YouTube(link)
    t=yt.streams.filter(only_audio=True, file_extension='mp4')
    name= 'tmp.mp4'
    t[0].download(filename=name)
    video = ffmpeg.input("tmp.mp4")
    audio = video.audio
    stream = ffmpeg.output(audio, "tmp.wav")
    ffmpeg.run(stream)
def myspleeterrun():
    command_line = "spleeter separate -o output/ tmp.wav"
    args = shlex.split(command_line)
    p = subprocess.Popen(args)
    p.wait()  
    accompaniment_channel_1,accompaniment_channel_2 =Splitting_stereo_audio(r'output\tmp\accompaniment.wav')
    vocal_channel_1,vocal_channel_2 =Splitting_stereo_audio(r"output\tmp\vocals.wav")
    mutli_channel = AudioSegment.from_mono_audiosegments(accompaniment_channel_1,accompaniment_channel_2,vocal_channel_1)
    mutli_channel.export(r"output\tmp\KaraOKE.wav",format="wav")
    sound = AudioSegment.from_file(r"output\tmp\KaraOKE.wav")
    sound = sound.set_frame_rate(16000)
    sound.export(r"output\tmp\KaraOKE.wav",format="wav")
