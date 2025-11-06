from flask import Flask
from threading import Thread
import os # 引入 os 模組來讀取環境變數

# Render 會將服務運行的 Port 號放入 PORT 環境變數中
# 如果環境變數不存在 (例如在本機測試時)，則預設使用 8080
PORT = os.environ.get('PORT', 8080)

app = Flask('')

# 1. 新增專門的健康檢查端點 (Health Check Endpoint)
# 這個端點是極簡的，不執行任何 I/O 或耗時操作
@app.route('/alive')
def alive_check():
    # 這是最可靠的回應，確保狀態碼是 200 OK
    return 'Service Alive', 200

# 原有的根路徑 /
@app.route('/')
def home():
    # 這裡可以保留您原有的複雜邏輯
    return "Alive!"

def run():
    # 使用讀取的 PORT 變數來啟動服務
    app.run(host='0.0.0.0', port=PORT)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 確保在主程式中啟動 keep_alive 函式
if __name__ == '__main__':
    keep_alive()