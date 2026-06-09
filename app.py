from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# تخزين الجلسات (سيتم مسحها عند إعادة النشر)
friend_sessions = {}

def simulate_friend_spam(uid):
    """محاكاة الإرسال المستمر"""
    while friend_sessions.get(uid, {}).get('active', False):
        try:
            url = f"https://masjon-frend.vercel.app/rizer?uid={uid}"
            response = requests.get(url, timeout=5)
            print(f"[الأصدقاء] تم الإرسال إلى {uid}: {response.status_code}")
        except Exception as e:
            print(f"[الأصدقاء] خطأ: {e}")
        time.sleep(1)

def call_spam_api(uid, action):
    url = f"https://spam-masjon-2.onrender.com/masjon/{action}?uid={uid}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}

def call_friend_api(uid, action):
    if action == 'stop':
        if uid in friend_sessions and friend_sessions[uid].get('active'):
            friend_sessions[uid]['active'] = False
            return {"success": True, "message": f"✅ تم إيقاف إرسال الأصدقاء لـ {uid}"}
        return {"success": False, "message": f"❌ لا توجد جلسة نشطة"}
    
    elif action == 'start':
        if uid in friend_sessions and friend_sessions[uid].get('active'):
            return {"success": False, "message": f"⚠️ الجلسة نشطة بالفعل"}
        
        friend_sessions[uid] = {'active': True, 'thread': None}
        thread = threading.Thread(target=simulate_friend_spam, args=(uid,))
        thread.daemon = True
        thread.start()
        friend_sessions[uid]['thread'] = thread
        
        try:
            url = f"https://masjon-frend.vercel.app/rizer?uid={uid}"
            response = requests.get(url, timeout=10)
            return {"success": True, "message": f"✅ بدأ الإرسال", "api_response": response.text}
        except Exception as e:
            return {"success": True, "message": f"✅ بدأ (تحذير: {str(e)})"}

@app.route('/start', methods=['GET'])
def start_all():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "UID مطلوب"}), 400
    
    spam_result = call_spam_api(uid, 'start')
    friend_result = call_friend_api(uid, 'start')
    
    return jsonify({
        "status": "تم البدء",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": friend_result
    })

@app.route('/stop', methods=['GET'])
def stop_all():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "UID مطلوب"}), 400
    
    spam_result = call_spam_api(uid, 'stop')
    friend_result = call_friend_api(uid, 'stop')
    
    return jsonify({
        "status": "تم الإيقاف",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": friend_result
    })

@app.route('/status', methods=['GET'])
def get_status():
    active = [uid for uid, s in friend_sessions.items() if s.get('active')]
    return jsonify({"active_sessions": active, "count": len(active)})

@app.route('/')
def home():
    return jsonify({
        "message": "API يعمل ✅",
        "endpoints": {
            "start": "/start?uid=YOUR_UID",
            "stop": "/stop?uid=YOUR_UID",
            "status": "/status"
        }
    })

# لـ Vercel
handler = app
