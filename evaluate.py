import os
import pathlib
import sys
from pydub import AudioSegment
from pydub.utils import make_chunks

import wave
from scipy.io import wavfile

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras import models
from IPython import display


from tensorflow import keras


def decode_audio(audio_binary):
  # Decode WAV-encoded audio files to `float32` tensors, normalized
  # to the [-1.0, 1.0] range. Return `float32` audio and a sample rate.
  audio, _ = tf.audio.decode_wav(contents=audio_binary)
  # Since all the data is single channel (mono), drop the `channels`
  # axis from the array.
  return tf.squeeze(audio, axis=-1)

def get_label(file_path):
  parts = tf.strings.split(
      input=file_path,
      sep=os.path.sep)
  # Note: You'll use indexing here instead of tuple unpacking to enable this
  # to work in a TensorFlow graph.
  return parts[-2]

def get_waveform_and_label(file_path):
  label = get_label(file_path)
  audio_binary = tf.io.read_file(file_path)
  waveform = decode_audio(audio_binary)
  return waveform, label

def get_spectrogram(waveform):
  # Zero-padding for an audio waveform with less than 16,000 samples.
  input_len = 16000
  waveform = waveform[:input_len]
  zero_padding = tf.zeros(
      [16000] - tf.shape(waveform),
      dtype=tf.float32)
  # Cast the waveform tensors' dtype to float32.
  waveform = tf.cast(waveform, dtype=tf.float32)
  # Concatenate the waveform with `zero_padding`, which ensures all audio
  # clips are of the same length.
  equal_length = tf.concat([waveform, zero_padding], 0)
  # Convert the waveform to a spectrogram via a STFT.
  spectrogram = tf.signal.stft(
      equal_length, frame_length=255, frame_step=128)
  # Obtain the magnitude of the STFT.
  spectrogram = tf.abs(spectrogram)
  # Add a `channels` dimension, so that the spectrogram can be used
  # as image-like input data with convolution layers (which expect
  # shape (`batch_size`, `height`, `width`, `channels`).
  spectrogram = spectrogram[..., tf.newaxis]
  return spectrogram

def get_spectrogram_and_label_id(audio, label):
  spectrogram = get_spectrogram(audio)
  label_id = tf.math.argmax(label == commands)
  return spectrogram, label_id

def preprocess_dataset(files):
  files_ds = tf.data.Dataset.from_tensor_slices(files)
  output_ds = files_ds.map(
      map_func=get_waveform_and_label,
      num_parallel_calls=AUTOTUNE)
  output_ds = output_ds.map(
      map_func=get_spectrogram_and_label_id,
      num_parallel_calls=AUTOTUNE)
  return output_ds

def get_all_spectrogram(waveform,model):
  # Zero-padding for an audio waveform with less than 16,000 samples.
  input_len = 16000
  waveform_all = waveform
  pred = []
  for i in range(0,len(waveform),input_len):
    waveform = waveform_all[i:i+input_len]
    zero_padding = tf.zeros(
        [16000] - tf.shape(waveform),
        dtype=tf.float32)
    # Cast the waveform tensors' dtype to float32.
    waveform = tf.cast(waveform, dtype=tf.float32)
    # Concatenate the waveform with `zero_padding`, which ensures all audio
    # clips are of the same length.
    equal_length = tf.concat([waveform, zero_padding], 0)
    # Convert the waveform to a spectrogram via a STFT.
    spectrogram = tf.signal.stft(
        equal_length, frame_length=255, frame_step=128)
    # Obtain the magnitude of the STFT.
    spectrogram = tf.abs(spectrogram)
    # Add a `channels` dimension, so that the spectrogram can be used
    # as image-like input data with convolution layers (which expect
    # shape (`batch_size`, `height`, `width`, `channels`).
    spectrogram = spectrogram[..., tf.newaxis]
    prediction = model.predict(spectrogram)
    p = tf.nn.softmax(prediction[0]).numpy()
    pred.append(p[1])
    
  
  return pred

def pred(wavfile,model):
  audio_binary = tf.io.read_file(wavfile)
  waveform = decode_audio(audio_binary) 
  pred = get_all_spectrogram(waveform,model)
  return pred

def show_result(pred):
  '''
  input: array
  output: singing or not in every second
  '''


  for i in range(len(pred)):
    print(pred[i])
    if pred[i] >= 0.5:
      print(str(i/10) +' s is singing')
    elif pred[i] < 0.5:
      print(str(i/10) +' s is not singing')

  plt.axhline(0.5, color= 'r')
  plt.plot(pred)
  plt.show()

def write_label(pred):
  '''
  input: array
  output: txt file for label
  '''
  f = open('label.txt','w')
  p = 0
  now_p = 0
  start_time = 0
  end_time = 0
  for i in range(len(pred)):
    now_p = 'not_singing' if pred[i] < 0.5 else 'singing'
    if i == 0:
      start_time = i
      p = now_p

    else:
      if i+1 == len(pred):
        f.write(str(start_time) + '\t' + str(i) + '\t' + p +'\n')
      elif p != now_p:
        f.write(str(start_time) + '\t' + str((i-1)) + '\t' + p+'\n')

        start_time = i
        p = now_p



if __name__ == '__main__':

  # Recreate the exact same model, including its weights and the optimizer
  model = tf.keras.models.load_model('training_dsd100/vocal_model.h5')

  commands = ['not_singing','singing']
  AUTOTUNE = tf.data.experimental.AUTOTUNE

  sample_file = './localfile/onvocal/《雲煙 Cloud of Smoke》Kimberley Chen 陳芳語 x Flesh Juicer 血肉果汁機｜Official Music Video.wav' 
  fs, data = wavfile.read(sample_file)           

  wavfile.write('tmp.wav', fs, data[:, 2])   


  audio_binary = tf.io.read_file('tmp.wav')
  waveform = decode_audio(audio_binary) 
  pred = get_all_spectrogram(waveform,model)

  #show_result(pred)
  write_label(pred)