from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import pyautogui
import os
import json
import queue
import threading
import time
import base64
import cv2
import numpy as np
import mss
import io
import ctypes
import socket

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

pyautogui.FAILSAFE = False

STREAM_QUALITY = 50
STREAM_FPS = 30

screen_share_active = False
capture_thread = None
thread_lock = threading.Lock()

def get_screen_resolution():
    user32 = ctypes.windll.user32
    return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

def capture_screen(quality=STREAM_QUALITY, resolution=get_screen_resolution()):
    try:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_LANCZOS4)
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buffer.tobytes()
    except Exception as e:
        print(f"Screen capture error: {e}")
        return None

def screen_share_loop():
    global screen_share_active
    
    try:
        while screen_share_active:
            frame = capture_screen()
            if frame:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                socketio.emit('screen_frame', encoded_frame)
                socketio.sleep(1 / STREAM_FPS)
            else:
                socketio.sleep(1)
    except Exception as e:
        print(f"Screen share loop error: {e}")
    finally:
        with thread_lock:
            screen_share_active = False

@socketio.on('connect')
def handle_connect():
    resolution = get_screen_resolution()
    socketio.emit('screen_resolution', resolution)
    print(f"Client connected. Screen resolution: {resolution}")

@socketio.on('start_screen_share')
def handle_start_screen_share():
    global screen_share_active, capture_thread
    
    with thread_lock:
        if screen_share_active:
            return
        screen_share_active = True
    
    capture_thread = socketio.start_background_task(screen_share_loop)

@socketio.on('adjust_quality')
def handle_quality_adjustment(data):
    global STREAM_QUALITY
    
    try:
        quality = int(data.get('quality', STREAM_QUALITY))
        
        STREAM_QUALITY = max(10, min(quality, 100))
    except Exception as e:
        print(f"Quality adjustment error: {e}")

@socketio.on('offer')
def handle_offer(offer):
    socketio.emit('offer', offer, broadcast=True, include_self=False)

@socketio.on('answer')
def handle_answer(answer):
    socketio.emit('answer', answer, broadcast=True, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(candidate):
    socketio.emit('ice_candidate', candidate)

@socketio.on('launch_app')
def handle_launch_app(data):
    path = data.get('path')
    if path and os.path.exists(path):
        try:
            os.startfile(path)
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    return {'status': 'error', 'message': 'Invalid path'}

@socketio.on('mouse_move')
def handle_mouse_move(data):
    try:
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        movement_type = str(data.get('type', 'relative')).lower()
        
        if movement_type == 'absolute':
            current_x, current_y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            
            safe_x = max(0, min(x, screen_width - 1))
            safe_y = max(0, min(y, screen_height - 1))
            
            pyautogui.moveTo(safe_x, safe_y, _pause=False)
        
        elif movement_type == 'relative':
            current_x, current_y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            
            new_x = max(0, min(current_x + x, screen_width - 1))
            new_y = max(0, min(current_y + y, screen_height - 1))
            
            pyautogui.moveTo(new_x, new_y, _pause=False)
        
        current_pos = pyautogui.position()
        socketio.emit('mouse_position', {
            'x': current_pos[0], 
            'y': current_pos[1]
        })
    
    except Exception as e:
        print(f"Mouse movement error: {e}")
        socketio.emit('mouse_move_error', {'message': str(e)})

@socketio.on('mouse_click')
def handle_mouse_click(data):
    try:
        button = data.get('button', 'left')
        click_type = data.get('type', 'single')
        
        button_map = {
            'left': 'leftClick',
            'right': 'rightClick',
            'middle': 'middleClick'
        }
        
        if click_type == 'single':
            getattr(pyautogui, f'{button_map[button]}')()
        elif click_type == 'double':
            getattr(pyautogui, f'{button_map[button]}')(clicks=2)
    except Exception as e:
        print(f"Mouse click error: {e}")

@socketio.on('mouse_scroll')
def handle_mouse_scroll(data):
    try:
        scroll_amount = int(data.get('amount', 0))
        pyautogui.scroll(scroll_amount)
    except Exception as e:
        print(f"Mouse scroll error: {e}")

@app.route('/')
def index():
    return render_template('panel.html')

@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/apps')
def apps():
    return render_template('apps.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/camera/view')
def camera_view():
    return render_template('camera_view.html')

@app.route('/screen_share')
def screen_share():
    return render_template('screen_share.html')

@app.route('/get_apps')
def get_apps():
    start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    apps_list = []
    
    for root, dirs, files in os.walk(start_menu):
        for file in files:
            if file.endswith('.lnk'):
                full_path = os.path.join(root, file)
                name = os.path.splitext(file)[0]
                apps_list.append({
                    'name': name,
                    'path': full_path
                })
    
    return jsonify(apps_list)

@app.route('/stop_screen_share')
def stop_screen_share():
    global screen_share_active, capture_thread
    
    with thread_lock:
        screen_share_active = False
    
    if capture_thread:
        capture_thread.join(timeout=2)
    
    return jsonify({"status": "Screen sharing stopped"})

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return '127.0.0.1'

LOCAL_IP = get_local_ip()
PORT = 5000

if __name__ == '__main__':
    print(f"Server starting on {LOCAL_IP}:{PORT}")
    print(f"Access from phone: http://{LOCAL_IP}:{PORT}")
    
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        print("\nAvailable Network Interfaces:")
        for interface in interfaces:
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip = addrs[netifaces.AF_INET][0]['addr']
                    print(f"- {interface}: {ip}")
            except Exception:
                pass
    except ImportError:
        print("(Install 'netifaces' for detailed network info)")

    socketio.run(
        app, 
        host=LOCAL_IP, 
        port=PORT, 
        debug=False,  
        allow_unsafe_werkzeug=True  
    )
