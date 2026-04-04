import requests
import time
import datetime

# ================= 1. Telegram 即時通知模組 =================
class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_alert(self, message):
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        try:
            response = requests.post(self.base_url, data=payload)
            if response.status_code == 200:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 警報已發送！")
            else:
                print("警報發送失敗，請檢查 Token 或 Chat ID")
        except Exception as e:
            print(f"網路錯誤: {e}")

# ================= 2. 隔日沖監控策略模組（持續監控版） =================
class DayTradeSniper:
    def __init__(self, notifier):
        self.notifier = notifier
        # 監控清單（共 70 檔，可自行增減）
        self.watchlist = [
            {'stock_id': '2330', 'name': '台積電'},
            {'stock_id': '2317', 'name': '鴻海'},
            {'stock_id': '2454', 'name': '聯發科'},
            {'stock_id': '2303', 'name': '聯電'},
            {'stock_id': '2412', 'name': '中華電'},
            {'stock_id': '2881', 'name': '富邦金'},
            {'stock_id': '2882', 'name': '國泰金'},
            {'stock_id': '2891', 'name': '中信金'},
            {'stock_id': '2886', 'name': '兆豐金'},
            {'stock_id': '2884', 'name': '玉山金'},
            {'stock_id': '2885', 'name': '元大金'},
            {'stock_id': '2892', 'name': '第一金'},
            {'stock_id': '5880', 'name': '合庫金'},
            {'stock_id': '1303', 'name': '南亞'},
            {'stock_id': '1326', 'name': '台化'},
            {'stock_id': '1301', 'name': '台塑'},
            {'stock_id': '2002', 'name': '中鋼'},
            {'stock_id': '1216', 'name': '統一'},
            {'stock_id': '3045', 'name': '台灣大'},
            {'stock_id': '4904', 'name': '遠傳'},
            {'stock_id': '2308', 'name': '台達電'},
            {'stock_id': '2382', 'name': '廣達'},
            {'stock_id': '3231', 'name': '緯創'},
            {'stock_id': '2356', 'name': '英業達'},
            {'stock_id': '2357', 'name': '華碩'},
            {'stock_id': '2376', 'name': '技嘉'},
            {'stock_id': '2345', 'name': '智邦'},
            {'stock_id': '3034', 'name': '聯詠'},
            {'stock_id': '3037', 'name': '欣興'},
            {'stock_id': '8046', 'name': '南電'},
            {'stock_id': '3189', 'name': '景碩'},
            {'stock_id': '3481', 'name': '群創'},
            {'stock_id': '2409', 'name': '友達'},
            {'stock_id': '3711', 'name': '日月光投控'},
            {'stock_id': '6669', 'name': '緯穎'},
            {'stock_id': '3443', 'name': '創意'},
            {'stock_id': '6531', 'name': '愛普'},
            {'stock_id': '4968', 'name': '立積'},
            {'stock_id': '8016', 'name': '矽創'},
            {'stock_id': '6415', 'name': '矽力-KY'},
            {'stock_id': '5269', 'name': '祥碩'},
            {'stock_id': '3008', 'name': '大立光'},
            {'stock_id': '2498', 'name': '宏達電'},
            {'stock_id': '2912', 'name': '統一超'},
            {'stock_id': '2915', 'name': '潤泰全'},
            {'stock_id': '9945', 'name': '潤泰新'},
            {'stock_id': '1101', 'name': '台泥'},
            {'stock_id': '1102', 'name': '亞泥'},
            {'stock_id': '1402', 'name': '遠東新'},
            {'stock_id': '1476', 'name': '儒鴻'},
            {'stock_id': '2207', 'name': '和泰車'},
            {'stock_id': '2301', 'name': '光寶科'},
            {'stock_id': '2327', 'name': '國巨'},
            {'stock_id': '2379', 'name': '瑞昱'},
            {'stock_id': '2385', 'name': '群光'},
            {'stock_id': '2395', 'name': '研華'},
            {'stock_id': '2408', 'name': '南亞科'},
            {'stock_id': '2449', 'name': '京元電子'},
            {'stock_id': '3035', 'name': '智原'},
            {'stock_id': '3105', 'name': '穩懋'},
            {'stock_id': '3533', 'name': '嘉澤'},
            {'stock_id': '3653', 'name': '健策'},
            {'stock_id': '3661', 'name': '世芯-KY'},
            {'stock_id': '4763', 'name': '材料-KY'},
            {'stock_id': '5274', 'name': '信驊'},
            {'stock_id': '5483', 'name': '中美晶'},
            {'stock_id': '6176', 'name': '瑞儀'},
            {'stock_id': '6269', 'name': '台郡'},
            {'stock_id': '6271', 'name': '同欣電'},
            {'stock_id': '6789', 'name': '采鈺'},
        ]
        # 記錄已經觸發過的股票，避免重複發送
        self.triggered_stocks = set()

    def get_realtime_price(self, stock_id):
        """
        取得台股即時報價（證交所 API）
        """
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw&json=1&delay=0"
        try:
            # 加入時間戳避免快取
            res = requests.get(url + f"&_={int(time.time() * 1000)}", timeout=5)
            data = res.json()
            if data['msgArray']:
                info = data['msgArray'][0]
                return {
                    'current_price': float(info['z']) if info['z'] != '-' else None,
                    'open_price': float(info['o']) if info['o'] != '-' else None,
                    'yesterday_close': float(info['y'])
                }
        except Exception as e:
            print(f"API 錯誤 ({stock_id}): {e}")
        return None

    def check_and_alert(self):
        """
        單次檢查所有股票，若符合倒貨條件且尚未觸發過，則發送警報
        """
        for stock in self.watchlist:
            stock_id = stock['stock_id']
            stock_name = stock['name']

            # 如果這檔股票已經觸發過，不再檢查
            if stock_id in self.triggered_stocks:
                continue

            price_info = self.get_realtime_price(stock_id)
            if not price_info or price_info['current_price'] is None:
                continue

            current = price_info['current_price']
            open_p = price_info['open_price']
            y_close = price_info['yesterday_close']

            # 若開盤價或昨收價為 None 則跳過
            if open_p is None or y_close is None:
                continue

            change_percent = ((current - y_close) / y_close) * 100

            # 條件：開盤價 > 昨收（開紅） 且 現價 < 開盤價（跌破開盤）
            if open_p > y_close and current < open_p:
                msg = (
                    f"⚠️ *隔日沖倒貨警報* ⚠️\n"
                    f"標的：{stock_name} ({stock_id})\n"
                    f"狀態：*開高走低，跌破開盤價！*\n"
                    f"昨收：{y_close:.2f}\n"
                    f"開盤：{open_p:.2f}\n"
                    f"現價：{current:.2f} ({change_percent:.2f}%)\n"
                    f"👉 *動作建議*：主力可能正在倒貨，多單請注意避險，空手者可觀察放空時機。"
                )
                self.notifier.send_alert(msg)
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 已觸發 {stock_name} 的警報！")
                # 將此股票加入已觸發集合，之後不再重複發送
                self.triggered_stocks.add(stock_id)

    def run_continuous_monitor(self, interval_seconds=10):
        """
        持續監控，每隔 interval_seconds 秒檢查一次
        """
        print("🚀 開始持續監控（隔日沖倒貨警報）...")
        self.notifier.send_alert("🔔 *監控系統啟動*\n系統將每隔 10 秒檢查一次，每檔股票僅在首次觸發時發送警報。")

        while True:
            self.check_and_alert()
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 等待 {interval_seconds} 秒後再次檢查...")
            time.sleep(interval_seconds)

# ================= 3. 主程式執行區 =================
if __name__ == "__main__":
    # 請在這裡填入你的 Telegram Bot Token 和 Chat ID
    TOKEN = "8557890092:AAE99pDVzx3dPBiTN9h0LMHBQ9dhRKtuHAs" # 例如 "1234567890:ABCdefGHIjklmNOPqrsTUVwxyz"
    CHAT_ID = "6077073014" # 例如 "123456789"

    # 建立通知器與監控器
    tg_bot = TelegramNotifier(bot_token=TOKEN, chat_id=CHAT_ID)
    sniper = DayTradeSniper(notifier=tg_bot)

    # 開始持續監控（每 10 秒檢查一次）
    try:
        sniper.run_continuous_monitor(interval_seconds=10)
    except KeyboardInterrupt:
        print("\n使用者手動停止監控。")
        sniper.notifier.send_alert("🔴 *監控系統已關閉*")
