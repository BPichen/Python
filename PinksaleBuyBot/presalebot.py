from web3 import Web3
import json, telebot, requests, mysql.connector, time, constants
from telegram import ParseMode
from hexbytes import HexBytes
#from flaskext.mysql import MySQL

cc_url = constants.cc_url

telebot_key = constants.telebot_key
chat = constants.chat
admin_chat = constants.admin_chat
bot = telebot.TeleBot(telebot_key)

rpc = "https://mainnet.infura.io/v3/1ed399d5402048f4bc11240e9d552b9f"
web3 = Web3(Web3.HTTPProvider(rpc))
address = "0x06a34DE65130d950bc517aCe322ca1bC361a5b7C"
token_abi = [{"constant":"true","inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":"false","stateMutability":"view","type":"function"},{"constant":"false","inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":"false","stateMutability":"nonpayable","type":"function"},{"constant":"true","inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":"false","stateMutability":"view","type":"function"},{"constant":"false","inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":"false","stateMutability":"nonpayable","type":"function"},{"constant":"true","inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":"false","stateMutability":"view","type":"function"},{"constant":"true","inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":"false","stateMutability":"view","type":"function"},{"constant":"true","inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":"false","stateMutability":"view","type":"function"},{"constant":"false","inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":"false","stateMutability":"nonpayable","type":"function"},{"constant":"true","inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":"false","stateMutability":"view","type":"function"},{"payable":"true","stateMutability":"payable","type":"fallback"},{"anonymous":"false","inputs":[{"indexed":"true","name":"owner","type":"address"},{"indexed":"true","name":"spender","type":"address"},{"indexed":"false","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":"false","inputs":[{"indexed":"true","name":"from","type":"address"},{"indexed":"true","name":"to","type":"address"},{"indexed":"false","name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]

contract = web3.eth.contract(address=address,abi=token_abi)

list_of_entries = []

img = constants.img

def connectToDB():
    try:
        conn = mysql.connector.connect(user=constants.user,
                                password=constants.password,
                                host=constants.host,
                                database=constants.database)
    except:
        print("Error connecting to DB")
    return conn

def pushToDB(tx_id, block):
    conn = connectToDB()
    cursor = conn.cursor()
    try:
        query = 'INSERT INTO txs (tx_id, block) VALUES ("{}", "{}")'.format(tx_id, block)
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except:
        conn.rollback()
        cursor.close()
        conn.close()

def checkDB(tx_id):
    conn = connectToDB()
    cursor = conn.cursor()

    query = 'SELECT * FROM txs WHERE tx_id = "{}"'.format(tx_id)

    cursor.execute(query)
    data = cursor.fetchall()

    if data:
        return True   
    else:
        return False
    
def getLastRecord():
    conn = connectToDB()
    cursor = conn.cursor()

    query = 'select * from txs ORDER BY id DESC LIMIT 1;'

    cursor.execute(query)
    data = cursor.fetchall()
    
    return data

def selectAll():
    conn = connectToDB()
    cursor = conn.cursor()

    query = 'SELECT * FROM txs'
    cursor.execute(query)
    data = cursor.fetchall()
    
    return data

def main():

    fromBlock = 0
    
    while True:

        newestPost = getLastRecord()
        if newestPost:
            id, hash, fromBlock = newestPost[0]
        try:
            filter = web3.eth.filter({
                'fromBlock': fromBlock,
                'address': address          
            })

            entries = filter.get_all_entries()

            response = requests.get(cc_url)
            response_dict = json.loads(response.text)
            price = response_dict['USD']

            for entry in entries:
                if checkDB(entry['transactionHash'].hex()):
                    print("Found!")
                else:   
                    tx_hash = entry['transactionHash'].hex()           
                    tx = web3.eth.get_transaction(tx_hash)
                    wei = tx['value']
                    if wei != 0:
                        pushToDB(tx_hash, entry['blockNumber'])
                        data = selectAll()
                        
                        print("Not found! Adding!")                            
                        emoji_string = ''       
                        
                        value = wei / (10 ** 18)
                        spent = (value * price)
                        emoji_count = int((price * value) / 15)

                        for x in range(emoji_count):
                            emoji_string += ("🟢")

                        buyer_funds = ((web3.eth.get_balance(tx['from']) / 10 ** 18) * price)
                        contributors = len(data)
                        filled_balance = web3.eth.get_balance(address) / (10 ** 18)

                        msg_text = "<b>Denarius Presale Buy!</b>\n" + emoji_string + "\n<b>Spent</b>: {:.2f} WETH (${:.2f})\n<b>Buyer Funds</b>: ${:.2f}\n<b>Total Contributors</b>: {}\n<b>Filled: </b> {:.2f} WETH\n\n<a href='https://etherscan.io/tx/{}'>TX</a> | <a href='https://www.pinksale.finance/launchpad/0x8bccF40DB0154B24C382a5C43Cad100486d3be8a?chain=ETH'>Buy</a> | <a href='https://twitter.com/DenariusRoma'>Twitter</a>".format(value, spent, buyer_funds, contributors, filled_balance, tx_hash)

                        bot.send_photo(admin_chat, open(img,'rb'), caption=msg_text, parse_mode = ParseMode.HTML)
                        

        except Exception as e:
            print(e)
            continue
        time.sleep(30)
        print("Looping..")

if __name__ == "__main__":
   main()
