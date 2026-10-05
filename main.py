import sys
import av
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_mp4_to_mov(input_path, output_path, status_label):
    try:
        status_label.config(text=f"Opening file...", fg="blue")
        input_container = av.open(input_path)
        output_container = av.open(output_path, 'w', format='mov')
        
        in_video = input_container.streams.video[0]
        in_audio = input_container.streams.audio[0] if input_container.streams.audio else None
        
        out_video = output_container.add_stream('h264', rate=in_video.average_rate)
        out_video.width = in_video.width
        out_video.height = in_video.height
        out_video.pix_fmt = 'yuv420p'
        
        out_audio = None
        if in_audio:
            out_audio = output_container.add_stream('aac')
            
        status_label.config(text="Converting packets...", fg="orange")
        for packet in input_container.demux([in_video, in_audio] if in_audio else [in_video]):
            if packet.dts is None: continue
            if packet.stream == in_video:
                for frame in packet.decode():
                    for out_packet in out_video.encode(frame):
                        output_container.mux(out_packet)
            elif packet.stream == in_audio and out_audio:
                for frame in packet.decode():
                    for out_packet in out_audio.encode(frame):
                        output_container.mux(out_packet)
                        
        for out_packet in out_video.encode(): output_container.mux(out_packet)
        if out_audio:
            for out_packet in out_audio.encode(): output_container.mux(out_packet)
                
        output_container.close()
        input_container.close()
        status_label.config(text="Success! Saved to " + os.path.basename(output_path), fg="green")
        messagebox.showinfo("Success", f"Video successfully converted and saved to:\n{output_path}")
    except Exception as e:
        status_label.config(text="Error during conversion.", fg="red")
        messagebox.showerror("Error", str(e))

def select_file_and_convert(status_label):
    input_path = filedialog.askopenfilename(title="Select MP4 Video", filetypes=[("MP4 files", "*.mp4")])
    if not input_path: return
    output_path = input_path.rsplit('.', 1)[0] + '.mov'
    
    # Update UI to ensure it renders before the blocking conversion
    status_label.config(text="Starting conversion...", fg="black")
    status_label.update()
    
    convert_mp4_to_mov(input_path, output_path, status_label)

def run_app():
    root = tk.Tk()
    root.title("MP4 to QuickTime Converter")
    root.geometry("400x200")
    
    lbl = tk.Label(root, text="Select an MP4 file to convert to MOV (QuickTime)", pady=20)
    lbl.pack()
    
    status = tk.Label(root, text="Waiting for file...", fg="gray")
    
    btn = tk.Button(root, text="Select File & Convert", command=lambda: select_file_and_convert(status), height=2, width=20)
    btn.pack(pady=10)
    
    status.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    run_app()
