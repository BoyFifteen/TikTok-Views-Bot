from utils.signer import Argus, Ladon, Gorgon, md5
from urllib.parse import urlencode
import requests, time, random, string, os, json, threading
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
success_count = 0
failed_count = 0
lock = threading.Lock()
class TikTokUltimate:
    def __init__(self):
        self.host = "api31-core-alisg.tiktokv.com"
        self.device_pool = [
            {"model": "SM-S9260", "brand": "Samsung", "api": "32", "ver": "12", "ua": "com.zhiliaoapp.musically/2024306030 (Linux; U; Android 12; en; SM-S9260; Build/V417IR;tt-ok/3.12.13.21)"},
            {"model": "Pixel 8 Pro", "brand": "Google", "api": "34", "ver": "14", "ua": "com.zhiliaoapp.musically/2024306030 (Linux; U; Android 14; en; Pixel 8 Pro; Build/UQ1A.231205.015;tt-ok/3.12.13.21)"},
            {"model": "Xiaomi 14", "brand": "Xiaomi", "api": "34", "ver": "14", "ua": "com.zhiliaoapp.musically/2024306030 (Linux; U; Android 14; en; Xiaomi 14; Build/UKQ1.230804.001;tt-ok/3.12.13.21)"},
            {"model": "CPH2551", "brand": "OPPO", "api": "33", "ver": "13", "ua": "com.zhiliaoapp.musically/2024306030 (Linux; U; Android 13; en; CPH2551; Build/TP1A.220905.001;tt-ok/3.12.13.21)"}
        ]
        self.countries = ["DZ", "US", "EG", "SA", "GB", "FR", "IQ", "TR"]
        self.proxies = self.load_proxies()
    def load_proxies(self):
        if os.path.exists("proxies.txt"):
            with open("proxies.txt", "r") as f:
                px = [line.strip() for line in f if line.strip()]
                print(f"[*] Loaded {len(px)} proxies.")
                return px
        print("[!] No proxies.txt found. Running without proxy.")
        return []
    def hex_gen(self, length):
        return "".join(random.choices(string.hexdigits.lower(), k=length))
    def sign(self, query, payload=None):
        unix = int(time.time())
        x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload else None
        return Gorgon(query, unix, payload, None).get_value() | {
            "x-ladon": Ladon.encrypt(unix, 1611921764, 1233),
            "x-argus": Argus.get_sign(query, x_ss_stub, unix, aid=1233)
        }
    def boost(self, video_id):
        global success_count, failed_count
        device = random.choice(self.device_pool)
        country = random.choice(self.countries)
        did = "759" + "".join(random.choices(string.digits, k=16))
        iid = "759" + "".join(random.choices(string.digits, k=16))
        ts = int(time.time())
        params = {
            "device_platform": "android",
            "os": "android",
            "aid": "1233",
            "version_code": "430603",
            "version_name": "43.6.3",
            "device_type": device["model"],
            "device_brand": device["brand"],
            "os_api": device["api"],
            "os_version": device["ver"],
            "current_region": country,
            "sys_region": country,
            "region": "US",
            "language": "en",
            "timezone_name": "Africa/Lagos",
            "ts": ts,
            "iid": iid,
            "device_id": did,
            "_rticket": int(ts * 1000)
        }
        data = {
            "item_id": video_id,
            "play_delta": "1",
            "first_install_time": "-1",
            "action_time": ts,
            "session_id": int(ts * 1000) - 15000,
            "enter_from": "homepage_hot",
            "item_distribute_source": "for_you_page_1"
        }
        q_str = urlencode(params)
        p_str = urlencode(data)
        cookies = {
            "sessionid": self.hex_gen(32),
            "install_id": iid,
            "device_id": did,
            "odin_tt": self.hex_gen(120),
            "msToken": self.hex_gen(128),
            "tt_chain_token": self.hex_gen(40),
            "d_ticket": self.hex_gen(40)
        }
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

        headers = {
            "user-agent": device["ua"],
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": cookie_str,
            "x-tt-dm-status": "login=0;ct=0;rt=1"
        }
        headers.update(self.sign(q_str, p_str))
        proxy = None
        if self.proxies:
            px = random.choice(self.proxies)
            proxy = {"http": px, "https": px}
        try:
            url = f"https://{self.host}/aweme/v1/aweme/stats/?{q_str}"
            r = requests.post(url, data=data, headers=headers, proxies=proxy, timeout=5)
            resp_data = r.text
            
            if r.status_code == 200 and '"status_code":0' in resp_data:
                with lock:
                    success_count += 1
                print(f"{GREEN}[SUCCESS]{RESET} | DID: {did[:8]} | Country: {country} | Resp: {resp_data}")
            else:
                with lock:
                    failed_count += 1
                print(f"{RED}[FAILED]{RESET} | Status: {r.status_code} | Resp: {resp_data}")
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} | Connection Failed: {str(e)[:50]}")
def worker(bot, v_id):
    while True:
        bot.boost(v_id)
if __name__ == "__main__":
    bot = TikTokUltimate()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"--- TikTok Booster Pro | @WHI3PER ---")
    video_id = input("Video ID: ")
    threads = int(input("Threads: "))
    print(f"\n[🚀] Attack Started on {video_id}...\n")
    for _ in range(threads):
        threading.Thread(target=worker, args=(bot, video_id), daemon=True).start()
    try:
        while True:
            time.sleep(1)
            print(f"\r{GREEN}Successful: {success_count}{RESET} | {RED}Failed: {failed_count}{RESET}", end="")
    except KeyboardInterrupt:
        print("\n[!] Exit.")