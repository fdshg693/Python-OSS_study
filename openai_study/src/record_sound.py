import sounddevice as sd
import soundfile as sf

duration = 20  # 秒
samplerate = 44100

print("録音開始...")
audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
sd.wait()
print("録音終了")

sf.write("output.wav", audio, samplerate)