import subprocess
import re
import sys
import os
import time

def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    cloudflared_path = os.path.join(app_dir, "cloudflared.exe")

    if not os.path.exists(cloudflared_path):
        print(f"❌ Không tìm thấy cloudflared.exe tại {cloudflared_path}", flush=True)
        return

    print("================================================================", flush=True)
    print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG NẾP NHỎ D2C VÀ MỞ MẠNG PUBLIC...", flush=True)
    print("================================================================", flush=True)

    # 1. Khởi động Flask server (ghi log ra file để không tắc buffer)
    flask_log_path = os.path.join(app_dir, "flask.log")
    flask_log = open(flask_log_path, "w", encoding='utf-8')
    flask_proc = subprocess.Popen(
        [sys.executable, "-u", "app1.py"],
        cwd=app_dir,
        stdout=flask_log,
        stderr=subprocess.STDOUT
    )

    time.sleep(2)

    # 2. Khởi động Cloudflare Tunnel (Ghi thẳng vào file log để không bao giờ bị nghẽn buffer!)
    tunnel_log_path = os.path.join(app_dir, "cloudflared.log")
    tunnel_log = open(tunnel_log_path, "w", encoding='utf-8')
    tunnel_proc = subprocess.Popen(
        [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:5000"],
        cwd=app_dir,
        stdout=tunnel_log,
        stderr=subprocess.STDOUT
    )

    public_url = None
    print("⏳ Đang kết nối đường truyền Cloudflare toàn cầu...", flush=True)

    start_time = time.time()
    while time.time() - start_time < 25:
        time.sleep(0.5)
        if os.path.exists(tunnel_log_path):
            try:
                with open(tunnel_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    match = re.search(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', content)
                    if match:
                        public_url = match.group(0)
                        break
            except Exception:
                pass

    if public_url:
        print("\n" + "="*68, flush=True)
        print("🎉 CHÚC MỪNG! HỆ THỐNG ĐÃ MỞ MẠNG PUBLIC THÀNH CÔNG!", flush=True)
        print("="*68, flush=True)
        print("🌍 ĐƯỜNG LINK ONLINE TOÀN CẦU (4G, 5G, KHÁC WI-FI ĐỀU VÀO ĐƯỢC):", flush=True)
        print(f"👉 Trang chủ:      {public_url}", flush=True)
        print(f"👉 Giao diện App:  {public_url}/mobile", flush=True)
        print(f"👉 Giỏ hàng/Mua:   {public_url}/cart", flush=True)
        print(f"👉 Mô phỏng 3 máy: {public_url}/demo", flush=True)
        print("="*68, flush=True)
        print("💡 Bạn có thể gửi đường link này cho thầy cô, bạn bè hoặc mở trên", flush=True)
        print("   điện thoại dùng 4G/5G ở bất kỳ đâu cũng vào được 100%!", flush=True)
        print("⚠️ GIỮ NGUYÊN CỬA SỔ NÀY ĐỂ DUY TRÌ WEB. Bấm Ctrl + C để dừng.", flush=True)
        print("="*68 + "\n", flush=True)
    else:
        print("❌ Chưa lấy được đường link. Kiểm tra cloudflared.log", flush=True)

    try:
        while True:
            time.sleep(2)
            if flask_proc.poll() is not None or tunnel_proc.poll() is not None:
                print("⚠️ Server hoặc Tunnel bị ngắt, đang dừng...", flush=True)
                break
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng hệ thống...", flush=True)
    finally:
        try:
            flask_proc.terminate()
            tunnel_proc.terminate()
            flask_log.close()
            tunnel_log.close()
        except Exception:
            pass
        print("✓ Đã dừng hoàn toàn.", flush=True)

if __name__ == '__main__':
    main()
