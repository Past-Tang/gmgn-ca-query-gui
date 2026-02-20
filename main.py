import threading
import time
import uuid
from datetime import datetime, timezone
from tkinter import ttk, Menu, messagebox
import http.client
import json

import customtkinter as ctk
import websocket
import wx
import wx.html2

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def fetch_api_data(query):
    conn = http.client.HTTPSConnection("gmgn.ai")
    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "deflate, br",
        'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
        'Connection': "keep-alive"
    }
    conn.request("GET", f"/defi/quotation/v1/tokens/sol/search?q={query}", "", headers)
    try:
        response = conn.getresponse().read().decode("utf-8")
    except:
        return "Error"
    if "success" in response:
        return json.loads(response)


class CADataWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CA 数据查询")
        self.geometry("1300x650")

        self.ws = None
        self.ca_value = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.create_input_area(main_frame)
        self.create_data_overview_area(main_frame)
        self.create_data_list_area(main_frame)

    def create_input_area(self, parent):
        ctk.CTkLabel(parent, text="CA 输入", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(input_frame, text="请输入 CA:", font=("Arial", 14)).pack(side="left", padx=5)
        self.textbox = ctk.CTkEntry(input_frame, placeholder_text="请输入 CA", font=("Arial", 14))
        self.textbox.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkButton(input_frame, text="查询", command=self.on_button_click, font=("Arial", 14)).pack(side="left",
                                                                                                       padx=5)

    def create_data_overview_area(self, parent):
        ctk.CTkLabel(parent, text="数据概览", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        data_frame = ctk.CTkFrame(parent)
        data_frame.pack(fill="x", padx=10, pady=5)

        self.data_labels = {
            "总市值": ctk.CTkLabel(data_frame, text="总市值: N/A", font=("Arial", 14)),
            "流通市值": ctk.CTkLabel(data_frame, text="流通市值: N/A", font=("Arial", 14)),
            "成交额": ctk.CTkLabel(data_frame, text="成交额: N/A", font=("Arial", 14)),
            "24小时成交额": ctk.CTkLabel(data_frame, text="24小时成交额: N/A", font=("Arial", 14)),
            "黑名单": ctk.CTkLabel(data_frame, text="黑名单: N/A", font=("Arial", 14)),
            "烧池子": ctk.CTkLabel(data_frame, text="烧池子: N/A", font=("Arial", 14)),
            "老鼠仓百分比": ctk.CTkLabel(data_frame, text="老鼠仓百分比: N/A", font=("Arial", 14)),
            "mint丢弃": ctk.CTkLabel(data_frame, text="mint丢弃: N/A", font=("Arial", 14)),
            "DEV状态": ctk.CTkLabel(data_frame, text="DEV状态: N/A", font=("Arial", 14)),
            "跑路概率": ctk.CTkLabel(data_frame, text="跑路概率: N/A", font=("Arial", 14))
        }

        for i, (key, label) in enumerate(self.data_labels.items()):
            row, col = divmod(i, 5)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")

        for i in range(5):
            data_frame.grid_columnconfigure(i, weight=1)

    def create_data_list_area(self, parent):
        ctk.CTkLabel(parent, text="详细数据[实时更新]", font=("Arial", 16, "bold")).pack(anchor="w", padx=10,
                                                                                         pady=(10, 0))

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 14), rowheight=40)
        style.configure("Treeview.Heading", font=('Arial', 14, 'bold'))

        self.data_list = ttk.Treeview(tree_frame,
                                      columns=("time", "type", "usd_amount", "quantity", "price", "wallet", "trader"),
                                      show="headings", style="Treeview",
                                      yscrollcommand=tree_scroll.set)
        self.data_list.pack(side="left", fill="both", expand=True)

        tree_scroll.config(command=self.data_list.yview)

        columns = ["时间", "类型", "交易额USD", "数量", "成交价格", "交易钱包", "交易者类型"]
        widths = [150, 80, 100, 100, 100, 300, 150]
        for col, text, width in zip(self.data_list["columns"], columns, widths):
            self.data_list.heading(col, text=text, anchor="center")
            self.data_list.column(col, width=width, anchor="center")

        self.data_list.bind("<Button-3>", self.show_context_menu)

    def on_button_click(self):
        self.ca_value = self.textbox.get().strip()
        if not self.ca_value:
            self.show_error("请输入CA值")
            return
        print(f'输入的 CA 值为: {self.ca_value}')
        self.fetch_data(self.ca_value)
        self.start_websocket()
        self.show_kline_window(self.ca_value)

    def show_kline_window(self, ca_value):
        threading.Thread(target=self.start_wxpython, args=(ca_value,)).start()

    def start_wxpython(self, ca_value):
        app = wx.App(False)

        loading_frame = wx.Frame(None, wx.ID_ANY, "加载中", size=(400, 200))
        loading_panel = wx.Panel(loading_frame)
        wx.StaticText(loading_panel, label="正在加载K线图，请稍候...", pos=(100, 80))
        loading_frame.Show()

        frame = wx.Frame(None, wx.ID_ANY, "K线图", size=(1000, 800))
        browser = wx.html2.WebView.New(frame)

        def on_page_loaded(event):
            js_code = """
            setTimeout(function() {
                var link = document.querySelector('a[href="https://gmgn.ai//sol/token/ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"]');
                if (link) {
                    link.style.display = 'none';
                }
            }, 1000);
            """
            browser.RunScript(js_code)
            time.sleep(3)
            loading_frame.Destroy()
            frame.Show()

        browser.Bind(wx.html2.EVT_WEBVIEW_LOADED, on_page_loaded)
        browser.LoadURL("https://gmgn.ai/sol/token/ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82?embled=1")

        app.MainLoop()

    def fetch_data(self, ca_value):
        try:
            result = fetch_api_data(ca_value)
            if result['code'] == 0 and result['msg'] == 'success':
                self.update_overview_data(result['data']['tokens'][0])
            else:
                self.show_error(f"API返回错误: {result.get('msg', '未知错误')}")
        except Exception as e:
            self.show_error(f"获取数据时发生错误: {str(e)}")

    def start_websocket(self):
        if self.ws:
            self.ws.close()

        def on_message(ws, message):
            data = json.loads(message)
            self.update_data_from_ws(data)

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")

        def on_open(ws):
            print("WebSocket connection opened")
            self.subscribe_to_token()

        self.ws = websocket.WebSocketApp("wss://ws.gmgn.ai/stream?_t=true",
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close,
                                         on_open=on_open,
                                         header={
                                             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
                                         })

        websocket_thread = threading.Thread(target=self.ws.run_forever)
        websocket_thread.daemon = True
        websocket_thread.start()

    def subscribe_to_token(self):
        if not self.ws or not self.ca_value:
            return

        kline_subscribe_message = {
            "action": "subscribe",
            "id": str(uuid.uuid4()),
            "channel": "token_kline",
            "data": {
                "chain": "sol",
                "address": self.ca_value,
                "interval": "1m"
            }
        }
        self.ws.send(json.dumps(kline_subscribe_message))

        activity_subscribe_message = {
            "action": "subscribe",
            "id": str(uuid.uuid4()),
            "channel": "token_activity",
            "data": {
                "chain": "sol",
                "address": self.ca_value
            }
        }
        self.ws.send(json.dumps(activity_subscribe_message))

    def update_data_from_ws(self, data):
        if 'channel' in data:
            if data['channel'] == 'token_kline' and 'data' in data:
                self.update_kline_data(data['data'])
            elif data['channel'] == 'token_activity' and 'data' in data:
                for activity in data['data']:
                    if float(activity['amount_usd']) >= 0.01:
                        self.update_activity_data(activity)

    def update_kline_data(self, kline_data):
        if isinstance(kline_data, list) and len(kline_data) > 0:
            kline_data = kline_data[0]
        self.data_labels["24小时成交额"].configure(text=f"24小时成交额: {float(kline_data['volume']):.2f} U")

    def update_activity_data(self, activity_data):
        usd_amount = float(activity_data['amount_usd'])
        if usd_amount < 0.01:
            return

        timestamp = activity_data['timestamp'] / (1000 if len(str(activity_data['timestamp'])) > 10 else 1)
        formatted_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

        transaction_type = "买入" if activity_data['event'] == 'buy' else "卖出"

        trader_tags = {
            'top_holder': '顶级持仓',
            'rat_trader': '老鼠仓',
            'pump_smart': '聪明钱',
            'sniper': '狙击手',
            'dev_team': '创建者小号',
            'creator': '创建者'
        }

        maker_tags = activity_data.get('maker_tags', []) + activity_data.get('maker_token_tags', [])
        trader_type = next((trader_tags[tag] for tag in maker_tags if tag in trader_tags), '散户')

        self.insert_transaction(
            formatted_time,
            transaction_type,
            usd_amount,
            float(activity_data['base_amount']),
            float(activity_data['price_usd']),
            activity_data['maker'],
            trader_type
        )

    def insert_transaction(self, time, type, usd_amount, quantity, price, wallet, trader):
        self.data_list.insert("", 0, values=(
            time,
            type,
            f"{usd_amount:.2f}",
            f"{quantity:.2f}",
            f"{price:.8f}",
            wallet,
            trader
        ))

        if len(self.data_list.get_children()) > 100:
            self.data_list.delete(self.data_list.get_children()[-1])

    def update_overview_data(self, token_data):
        def format_amount(amount):
            if amount >= 1_000_000:
                return f"{amount / 1_000_000:.2f}M U"
            elif amount >= 1_000:
                return f"{amount / 1_000:.2f}K U"
            else:
                return f"{amount:.2f} U"

        total_market_cap = token_data['price'] * token_data['total_supply']
        circulating_market_cap = total_market_cap * (1 - token_data['top_10_holder_rate'])

        self.data_labels["总市值"].configure(text=f"总市值: {format_amount(total_market_cap)}")
        self.data_labels["流通市值"].configure(text=f"流通市值: {format_amount(circulating_market_cap)}")
        self.data_labels["成交额"].configure(text=f"成交额: {format_amount(token_data['volume_24h'])}")
        self.data_labels["24小时成交额"].configure(text=f"24小时成交额: {format_amount(token_data['volume_24h'])}")
        self.data_labels["黑名单"].configure(text=f"黑名单: {'是' if token_data['is_show_alert'] else '否'}")
        self.data_labels["烧池子"].configure(text=f"烧池子: {token_data['burn_status']}")
        self.data_labels["老鼠仓百分比"].configure(text=f"老鼠仓百分比: {token_data['top_10_holder_rate'] * 100:.2f}%")
        self.data_labels["mint丢弃"].configure(text=f"mint丢弃: {'是' if token_data['renounced_mint'] == 1 else '否'}")
        self.data_labels["DEV状态"].configure(
            text=f"DEV状态: {'已放弃' if token_data['renounced_freeze_account'] == 1 else '未放弃'}")

        run_risk_factors = [
            not token_data['is_show_alert'],
            token_data['renounced_mint'] == 1,
            token_data['renounced_freeze_account'] == 1,
            token_data['burn_ratio'] == '1.0000'
        ]
        run_risk = "低" if all(run_risk_factors) else "中" if sum(run_risk_factors) >= 2 else "高"
        self.data_labels["跑路概率"].configure(text=f"跑路概率: {run_risk}")

    def show_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="复制", command=self.copy_selected)
        context_menu.tk_popup(event.x_root, event.y_root)

    def copy_selected(self):
        selected_items = self.data_list.selection()
        if not selected_items:
            return
        item_text = self.data_list.item(selected_items[0])['values']
        self.clipboard_clear()
        self.clipboard_append("\t".join(map(str, item_text)))

    def show_error(self, message):
        messagebox.showerror("错误", message)

    def on_closing(self):
        if self.ws:
            self.ws.close()
        self.destroy()

if __name__ == "__main__":
    app = CADataWidget()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # Properly handle window close
    app.mainloop()