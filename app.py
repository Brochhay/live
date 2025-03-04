from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import subprocess
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class StreamManager:
    def __init__(self):
        self.process = None
        self.is_streaming = False
        self.loop_enabled = False
        self.loop_count = 1
        self.current_loop = 0
        self.debug_messages = []
        self.source_type = "file"  # Set default source type to "file"

    def debug(self, message):
        """Store debug message"""
        self.debug_messages.append(message)

    def get_debug_messages(self):
        """Get and clear debug messages"""
        messages = self.debug_messages[:]
        self.debug_messages.clear()
        return messages

    def start_stream(self, source, stream_key, video_size):
        if self.is_streaming:
            return False
            
        if not all([source, stream_key, video_size]):
            flash("Please enter all required fields.", "warning")
            return False

        try:
            self.is_streaming = True
            threading.Thread(target=self._stream_thread, 
                           args=(source, stream_key, video_size),
                           daemon=True).start()
            return True

        except Exception as e:
            flash(f"Live streaming failed: {e}", "danger")
            return False

    def _stream_thread(self, source, stream_key, video_size):
        """Handle streaming in a separate thread with loop support"""
        while self.is_streaming and (not self.loop_enabled or self.current_loop < self.loop_count):
            try:
                if self.source_type == "file":
                    # Direct FFmpeg command for local file
                    ffmpeg_command = [
                        "ffmpeg",
                        "-re",  # Read input at native framerate
                        "-stream_loop", "-1" if self.loop_enabled else "0",  # Loop setting
                        "-i", source,  # Input file
                        "-filter_complex", "[0:v]format=yuv420p,fps=30",
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-maxrate", "4000k",
                        "-bufsize", "8000k",
                        "-g", "60",
                        "-c:a", "aac",
                        "-b:a", "160k",
                        "-ar", "44100",
                        "-f", "flv",
                        "-s", video_size,
                        f"rtmps://live-api-s.facebook.com:443/rtmp/{stream_key}"
                    ]
                    self.debug(f"Starting file stream: {' '.join(ffmpeg_command)}")
                    self.ffmpeg_process = subprocess.Popen(
                        ffmpeg_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        bufsize=1
                    )
                    
                    # Read FFmpeg output
                    for line in self.ffmpeg_process.stderr:
                        self.debug(line.strip())
                    
                    self.ffmpeg_process.wait()

                if self.loop_enabled:
                    self.current_loop += 1
                    self.debug(f"Loop {self.current_loop}/{self.loop_count} completed")
                    if self.current_loop >= self.loop_count:
                        break
                else:
                    break

            except Exception as e:
                self.debug(f"Error: {str(e)}")
                break

        self.debug("Stream stopped")
        self.is_streaming = False

    def stop_stream(self):
        """Stop the streaming process and clean up"""
        if self.is_streaming:
            try:
                self.is_streaming = False  # Set this first to stop loops
                
                if hasattr(self, 'ffmpeg_process'):
                    try:
                        self.ffmpeg_process.terminate()
                        self.ffmpeg_process.wait(timeout=5)
                    except Exception as e:
                        self.debug(f"Error stopping FFmpeg: {e}")
                        self.ffmpeg_process.kill()
                    finally:
                        self.debug("FFmpeg process stopped")
                
                self.ffmpeg_process = None
                self.current_loop = 0
                
                self.debug("Stream ended successfully")
                return True
                
            except Exception as e:
                self.debug(f"Error during stream stop: {e}")
                
        return False

stream_manager = StreamManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_stream', methods=['POST'])
def start_stream():
    file = request.files['source']
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        source = filename
    else:
        flash("Please select a video file.", "warning")
        return redirect(url_for('index'))

    stream_key = request.form['stream_key']
    video_size = request.form['video_size']
    loop_enabled = 'loop_enabled' in request.form
    loop_count = request.form.get('loop_count', 1, type=int)

    stream_manager.loop_enabled = loop_enabled
    stream_manager.loop_count = loop_count

    if stream_manager.start_stream(source, stream_key, video_size):
        flash("Stream started successfully!", "success")
    else:
        flash("Failed to start stream.", "danger")

    return redirect(url_for('index'))

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    if stream_manager.stop_stream():
        flash("Stream stopped successfully!", "success")
    else:
        flash("Failed to stop stream.", "danger")

    return redirect(url_for('index'))

@app.route('/debug', methods=['GET'])
def debug():
    messages = stream_manager.get_debug_messages()
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True)