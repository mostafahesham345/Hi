import pyaudio
import numpy as np
import wave
import threading
import speech_recognition as sr
import noisereduce as nr

class AudioRecorder:
    def __init__(self, output_filename="output.wav", audio_level_callback=None):
        self.FORMAT = pyaudio.paInt16  # 16-bit resolution
        self.CHANNELS = 1  # Mono audio
        self.RATE = 44100  # 44.1kHz sampling rate
        self.CHUNK = 1024  # 2^10 samples for buffer
        self.output_filename = output_filename
        self.frames = []
        self.recording = False
        self.audio_level_callback = audio_level_callback

        self.audio = pyaudio.PyAudio()

    def start_recording(self):
        self.recording = True
        self.frames = []
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK)
        threading.Thread(target=self._record).start()

    def _record(self):
        while self.recording:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
            if self.audio_level_callback:
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.abs(audio_data).mean()
                self.audio_level_callback(level)

    def stop_recording(self):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # Save the recorded data as a WAV file
        with wave.open(self.output_filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))

        # Apply noise reduction
        self.reduce_noise()

    def reduce_noise(self):
        with wave.open(self.output_filename, 'rb') as wf:
            rate = wf.getframerate()
            frames = wf.getnframes()
            audio = wf.readframes(frames)
            audio = np.frombuffer(audio, dtype=np.int16)

        reduced_noise_audio = nr.reduce_noise(y=audio, sr=rate)
        reduced_noise_audio = reduced_noise_audio.astype(np.int16)

        with wave.open(self.output_filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(reduced_noise_audio.tobytes())

    def get_audio_data_as_text(self):
        recognizer = sr.Recognizer()
        audio_data = sr.AudioFile(self.output_filename)
        with audio_data as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

if __name__ == "__main__":
    def print_audio_level(level):
        print(f"Audio Level: {level}")

    recorder = AudioRecorder(audio_level_callback=print_audio_level)
    recorder.start_recording()
    input("Press Enter to stop recording...")
    recorder.stop_recording()
    print(f"Recording saved to {recorder.output_filename}")
    audio_data_text = recorder.get_audio_data_as_text()
    print(audio_data_text)
