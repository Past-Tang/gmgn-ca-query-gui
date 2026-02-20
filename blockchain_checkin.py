import crypto
import csv
import os
import time
import random
import requests
from eth_account import Account
from web3 import Web3
import json

# 加载配置文件
with open('../../config/runner.json') as f:
    config = json.load(f)

# 设置请求头
headers = {
    'authority': 'interface.carv.io',
    'Accept': 'application/json, text/plain, */*',
    'Content-type': 'application/json',
    'Origin': 'https://protocol.carv.io',
    'Referer': 'https://protocol.carv.io/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'X-App-Id': 'carv',
}


def get_key_from_user():
    if 'SCRIPT_PASSWORD' in os.environ:
        key = os.environ['SCRIPT_PASSWORD']
    else:
        key = input('请输入你的密码: ')
    return crypto.sha256(key.encode()).digest()[:32]


def decrypt(text, secret_key):
    parts = text.split(':')
    iv = bytes.fromhex(parts[0])
    encrypted_text = bytes.fromhex(':'.join(parts[1:]))
    cipher = crypto.AES.new(secret_key, crypto.AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_text)
    return decrypted.rstrip(b'\0').decode()


def form_hex_data(string):
    if not isinstance(string, str):
        raise ValueError('Input must be a string.')
    if len(string) > 64:
        raise ValueError('String length exceeds 64 characters.')
    return '0' * (64 - len(string)) + string


def login(wallet):
    address = wallet.address
    url = 'https://interface.carv.io/protocol/login'
    msg = f"Hello! Please sign this message to confirm your ownership of the address. This action will not cost any gas fee. Here is a unique text: {int(time.time() * 1000)}"
    signature = wallet.sign_message(msg)
    data = {
        'wallet_addr': address,
        'text': msg,
        'signature': signature.signature.hex(),
    }

    for _ in range(4):
        try:
            response = requests.post(url, json=data, headers=headers, proxies=config['proxy'])
            response.raise_for_status()
            token = response.json()['data']['token']
            bearer = "bearer " + base64.b64encode(f"eoa:{token}".encode()).decode()
            headers['Authorization'] = bearer
            headers['Content-Type'] = 'application/json'
            return bearer
        except Exception as e:
            print(f'登录过程中发生错误: {e}')
            time.sleep(random.uniform(1, 5))
    return None


def roin_check_in():
    url = 'https://interface.carv.io/airdrop/mint/carv_soul'
    data = {'chain_id': 2020}

    for _ in range(4):
        try:
            response = requests.post(url, json=data, headers=headers, proxies=config['proxy'])
            response.raise_for_status()
            return
        except Exception as e:
            print(f'Roin签到过程中发生错误: {e}')
            time.sleep(random.uniform(1, 5))


def check_in_data():
    url = 'https://interface.carv.io/airdrop/mint/carv_soul'
    data = {'chain_id': 204}

    for _ in range(4):
        try:
            response = requests.post(url, json=data, headers=headers, proxies=config['proxy'])
            response.raise_for_status()
            if response.json()['code'] == 4500:
                return None
            else:
                return response.json()['data']
        except Exception as e:
            print(f'checkIndata 获取信息失败: {e}')
            time.sleep(random.uniform(1, 5))


def check_in(wallet, check_in_data):
    signature = check_in_data['signature']
    contract = check_in_data['contract']
    account = check_in_data['permit']['account']
    amount = check_in_data['permit']['amount']
    ymd = check_in_data['permit']['ymd']

    address_data = form_hex_data(account[2:])
    amount_data = form_hex_data(hex(amount)[2:])
    ymd_data = form_hex_data(hex(ymd)[2:])
    transaction_data = f"0xa2a9539c{address_data}{amount_data}{ymd_data}00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000041{signature[2:]}00000000000000000000000000000000000000000000000000000000000000"

    try:
        w3 = Web3(Web3.HTTPProvider(config['opbnb']))
        nonce = w3.eth.get_transaction_count(wallet.address)
        gas_price = w3.eth.gas_price
        tx = {
            'to': contract,
            'data': transaction_data,
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'value': 0,
        }
        signed_tx = wallet.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f'签到tx：{tx_hash.hex()}')
    except Exception as e:
        print(f'发送交易时出错: {e}')


def main():
    wallets = []
    with open(config['walletPath'], newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            private_key = row['privateKey']
            wallets.append(Account.from_key(private_key))

    for wallet in wallets:
        print(f"开始为 {wallet.address}签到")
        bearer = login(wallet)
        if bearer:
            roin_check_in()
            check_data = check_in_data()
            if check_data:
                check_in(wallet, check_data)
                print("签到成功🏅")

        pause_time = random.uniform(10, 30)
        print(f"{time.ctime()} 任务完成，线程暂停{pause_time:.2f}秒")
        time.sleep(pause_time)


if __name__ == "__main__":
    main()