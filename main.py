from my_functions import *

welcome_message()
target_file_name = get_target_file_name()
audio_output = "default.wav"

extract_audio_from_video(target_file_name, audio_output)

compress_and_split_audio(audio_output)

segments = get_segment_names()

stt = set_up_api()

results = get_results(stt, segments)

text = parse_text(results)

write_to_txt(text,audio_output,segments)

time.sleep(5)
quit()