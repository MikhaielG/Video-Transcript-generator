import subprocess
import os
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from my_functions import *
import os.path
from os import path
import time


''' Shows welcome message'''
def welcome_message():
    print("Welcome!\n")
    print("Place your video file in the same directory as the the program!")
    print('Your file will be transcripted and exported to a text file!\n\n')

def get_target_file_name():
    print("Type 'exit' or 'quit' to terminate the program!\n")
    file_name = input("Please type the file name with proper file extension!\n")

    if file_name.lower() == 'exit' or  file_name.lower() == 'quit':
        quit()

    if path.exists(file_name):
        return file_name
    
    else:
        print('Make sure if the file is in the directory or spelling is correct!')
        get_target_file_name()

def extract_audio_from_video(target_file_name, audio_output):
    print("Please wait while the audio is extracted!")
    print("Audio extraction has begun, please wait a while!")  
    command = f"ffmpeg -i {target_file_name} -ab 160k -ar 44100 -vn {audio_output}"
    subprocess.call(command, shell=True)
    print('Audio extracted successfully!\n')


def compress_and_split_audio(audio_output):
    #Compress and Split Audio
    print('Compressing the audio...')
    command = f"ffmpeg -i {audio_output} -vn -ar 44100 -ac 2 -b:a 192k audio.mp3"
    subprocess.call(command, shell=True)
    print('Audio compressed successfully!\n')

    print('Making segments of the audio file to minimize time...')
    command = 'ffmpeg -i audio.mp3 -f segment -segment_time 360 -c copy %03d.mp3'
    subprocess.call(command, shell=True)
    print('Segments created successfully!\n')


def get_segment_names():
    files = []
    for filename in os.listdir('.'):
        if filename.endswith(".mp3") and filename !='audio.mp3':
            files.append(filename)
    files.sort()

    return files

def set_up_api():
    '''
    Set up API for Speech To Text
    '''
    #https://cloud.ibm.com/catalog?category=ai#services
    apikey = ''
    url = ''
    # Setup service
    print('Setting up connection with IBM Cloud...')
    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)
    print('Connection successful!\n\n')
    return stt

def get_results(stt, files):
    results = []
    length = len(files)
    print('Begun transcripting...')
    print('This may take a while!')
    for filename in files:
        print(f"Transcripting...{length - 1} segments remaining...")
        with open(filename, 'rb') as f:
            res = stt.recognize(audio=f, content_type='audio/mp3', model='en-US_NarrowbandModel', continuous=True, \
                           inactivity_timeout=360).get_result()
        results.append(res)
    
    print('Transcripting complete!\n\n')
    return results

def parse_text(results):
    text = []
    print("Parsing text...")
    for file in results:
        for result in file['results']:
            text.append(result['alternatives'][0]['transcript'].rstrip() + '.\n')
    
    print('Parsing done!\n\n')
    return text


def free_up_the_segments(audio_output,files):
    #delete unnecessary files
    print('Freeing up the segments')
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
        
    if os.path.exists(audio_output):
        os.remove(audio_output)

    for file in files:
        if os.path.exists(file):
            os.remove(file)

    print('Cleaned up the unnecessary files')


def write_to_txt(text,audio_output,files):
    output_file_name = input('Type the name of your output file without the extention:')

    if path.exists(f"{output_file_name}.txt"):
        print('File name already in use, choose a different name')
        write_to_txt(text)
    
    else:
        with open(f"{output_file_name}.txt", 'w') as out:
            out.writelines(text)

        free_up_the_segments(audio_output,files)
        print(f"Text file created! Your Transcription is in {output_file_name}.txt file! Thanks for using the program!")
