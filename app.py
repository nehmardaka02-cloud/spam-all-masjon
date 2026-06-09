from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# تخزين مؤقت لحالة جلسات الأصدقاء
friend_sessions = {}

# دالة لمحاكاة الإرسال المستمر للأصدقاء (لأن API الأصلي لا يدعم stop)
def simulate_friend_spam(uid):
    """محاكاة إرسال مستمر للأصدقاء (يعمل في خلفية)"""
    while friend_sessions.get(uid, {}).get('active', False):
        try:
            # استدعاء API الأصدقاء بشكل متكرر
            url = f"https://masjon-frend.vercel.app/rizer?uid={uid}"
            response = requests.get(url, timeout=5)
            print(f"[الأصدقاء] تم الإرسال إلى {uid}: {response.status_code}")
        except Exception as e:
            print(f"[الأصدقاء] خطأ لـ {uid}: {e}")
        
        time.sleep(1)  # انتظر ثانية بين كل إرسال

# دالة للاتصال بـ API الأول (spam-masjon)
def call_spam_api(uid, action):
    """استدعاء API البريد العشوائي الرئيسي"""
    url = f"https://spam-masjon-2.onrender.com/masjon/{action}?uid={uid}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}

# دالة للاتصال بـ API الأصدقاء
def call_friend_api(uid, action):
    """استدعاء API الأصدقاء (مع دعم stop محاكى)"""
    if action == 'stop':
        # إيقاف جلسة الأصدقاء
        if uid in friend_sessions and friend_sessions[uid].get('active'):
            friend_sessions[uid]['active'] = False
            return {"success": True, "message": f"✅ تم إيقاف إرسال الأصدقاء لـ {uid}"}
        return {"success": False, "message": f"❌ لا توجد جلسة نشطة لـ {uid}"}
    
    elif action == 'start':
        # بدء جلسة الأصدقاء
        if uid in friend_sessions and friend_sessions[uid].get('active'):
            return {"success": False, "message": f"⚠️ جلسة الأصدقاء لـ {uid} نشطة بالفعل"}
        
        # بدء جلسة جديدة
        friend_sessions[uid] = {'active': True, 'thread': None}
        
        # تشغيل الإرسال في خيط منفصل
        thread = threading.Thread(target=simulate_friend_spam, args=(uid,))
        thread.daemon = True
        thread.start()
        friend_sessions[uid]['thread'] = thread
        
        # محاولة الاتصال الأولية بـ API الأصدقاء
        try:
            url = f"https://masjon-frend.vercel.app/rizer?uid={uid}"
            response = requests.get(url, timeout=10)
            return {
                "success": True,
                "message": f"✅ بدأ إرسال الأصدقاء لـ {uid}",
                "api_response": response.json() if response.text else {"status": "started"}
            }
        except Exception as e:
            return {
                "success": True,
                "message": f"✅ بدأ إرسال الأصدقاء لـ {uid} (لكن حدث خطأ: {str(e)})"
            }

# نقطة النهاية الرئيسية لبدء الكل
@app.route('/start', methods=['GET'])
def start_all():
    """بدء جميع APIs"""
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({"error": "UID مطلوب! استخدم ?uid=القيمة"}), 400
    
    # 1. استدعاء API البريد العشوائي الأول
    spam_result = call_spam_api(uid, 'start')
    
    # 2. استدعاء API الأصدقاء
    friend_result = call_friend_api(uid, 'start')
    
    # إرجاع النتيجة المجمعة
    return jsonify({
        "status": "🟢 تم بدء جميع العمليات",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": friend_result
    })

# نقطة النهاية الرئيسية لإيقاف الكل
@app.route('/stop', methods=['GET'])
def stop_all():
    """إيقاف جميع APIs"""
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({"error": "UID مطلوب! استخدم ?uid=القيمة"}), 400
    
    # 1. إيقاف API البريد العشوائي الأول
    spam_result = call_spam_api(uid, 'stop')
    
    # 2. إيقاف API الأصدقاء (محاكاة)
    friend_result = call_friend_api(uid, 'stop')
    
    # إرجاع النتيجة المجمعة
    return jsonify({
        "status": "🔴 تم إيقاف جميع العمليات",
        "uid": uid,
        "spam_masjon": spam_result,
        "friend_rizer": friend_result
    })

# نقطة حالة لعرض الجلسات النشطة
@app.route('/status', methods=['GET'])
def get_status():
    """عرض حالة الجلسات النشطة"""
    active_sessions = []
    for uid, session in friend_sessions.items():
        if session.get('active'):
            active_sessions.append(uid)
    
    return jsonify({
        "active_friend_sessions": active_sessions,
        "total_active": len(active_sessions)
    })

# تشغيل الخادم
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║   🚀 تشغيل الخادم على المنفذ 5000     ║
    ║                                       ║
    ║   للاستخدام:                          ║
    ║   - بدء الكل: /start?uid=123          ║
    ║   - إيقاف الكل: /stop?uid=123         ║
    ║   - الحالة: /status                   ║
    ╚═══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
