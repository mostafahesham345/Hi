import tkinter as tk
from tkinter import messagebox
from audio_recorder import AudioRecorder
import os
import platform

def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder")

        self.recorder = AudioRecorder(audio_level_callback=self.update_audio_level)

        self.record_button = tk.Button(root, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.canvas = tk.Canvas(root, width=200, height=100, bg='white')
        self.canvas.pack(pady=20)
        self.audio_level_bar = self.canvas.create_rectangle(0, 100, 200, 100, fill="green")

        self.audio_text = tk.Text(root, height=10, width=50)
        self.audio_text.pack(pady=20)

    def start_recording(self):
        try:
            self.record_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.recorder.start_recording()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while starting recording: {e}")
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_recording(self):
        try:
            self.recorder.stop_recording()
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            audio_data_text = self.recorder.get_audio_data_as_text()
            self.audio_text.delete(1.0, tk.END)
            self.audio_text.insert(tk.END, audio_data_text)
            messagebox.showinfo("Recording", f"Recording saved to {self.recorder.output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while stopping recording: {e}")
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def update_audio_level(self, level):
        try:
            # Normalize level to fit within the canvas height
            normalized_level = min(max(level / 30000, 0), 1)  # Adjust normalization as needed
            height = 100 - (normalized_level * 100)
            self.canvas.coords(self.audio_level_bar, 0, height, 200, 100)
            self.canvas.itemconfig(self.audio_level_bar, fill="green" if height > 20 else "red")
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error in update_audio_level: {e}")

if __name__ == "__main__":
    try:
        clear_terminal()
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
