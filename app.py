import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def call_spam_api(uid, action):
    """استدعاء API البريد العشوائي"""
    url = f"https://spam-masjon-2.onrender.com/masjon/{action}?uid={uid}"
    try:
        response = requests.get(url, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}

def call_friend_api(uid):
    """استدعاء API الأصدقاء"""
    try:
        url = f"https://masjon-frend.vercel.app/rizer?uid={uid}"
        response = requests.get(url, timeout=30)
        return {"success": True, "data": response.text}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}

@app.route('/start', methods=['GET'])
def start_all():
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({"error": "UID مطلوب! استخدم ?uid=القيمة"}), 400
    
    # استدعاء كلا الـ APIs
    spam_result = call_spam_api(uid, 'start')
    friend_result = call_friend_api(uid)
    
    return jsonify({
        "status": "تم بدء العمليات",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": friend_result
    })

@app.route('/stop', methods=['GET'])
def stop_all():
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({"error": "UID مطلوب! استخدم ?uid=القيمة"}), 400
    
    # إيقاف API البريد العشوائي فقط (API الأصدقاء لا يدعم الإيقاف)
    spam_result = call_spam_api(uid, 'stop')
    
    return jsonify({
        "status": "تم إيقاف العمليات",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": {
            "success": True,
            "message": "API الأصدقاء لا يدعم الإيقاف، تم إيقاف البريد العشوائي فقط"
        }
    })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "API يعمل",
        "note": "استخدم /start?uid=ID لبدء الإرسال، /stop?uid=ID للإيقاف"
    })

@app.route('/')
def home():
    return jsonify({
        "message": "✅ API يعمل بنجاح على Render",
        "endpoints": {
            "بدء الإرسال": "/start?uid=YOUR_UID",
            "إيقاف الإرسال": "/stop?uid=YOUR_UID",
            "الحالة": "/status"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 التشغيل على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port)
