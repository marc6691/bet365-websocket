import websockets
import asyncio
import collections
import json
import re
from websockets.extensions import permessage_deflate
import traceback
import execjs
import requests


def decryptToken(t):
    n = ""
    i = ""
    o = len(t)
    r = 0
    s = 0
    MAP_LEN = 64
    charMap = [["A", "d"], ["B", "e"], ["C", "f"], ["D", "g"], ["E", "h"], ["F", "i"], ["G", "j"], ["H", "k"], ["I", "l"], ["J", "m"], ["K", "n"], ["L", "o"], ["M", "p"], ["N", "q"], ["O", "r"], ["P", "s"], ["Q", "t"], ["R", "u"], ["S", "v"], ["T", "w"], ["U", "x"], ["V", "y"], ["W", "z"], ["X", "a"], ["Y", "b"], ["Z", "c"], ["a", "Q"], ["b", "R"], ["c", "S"], ["d", "T"], ["e", "U"], ["f", "V"], [
        "g", "W"], ["h", "X"], ["i", "Y"], ["j", "Z"], ["k", "A"], ["l", "B"], ["m", "C"], ["n", "D"], ["o", "E"], ["p", "F"], ["q", "0"], ["r", "1"], ["s", "2"], ["t", "3"], ["u", "4"], ["v", "5"], ["w", "6"], ["x", "7"], ["y", "8"], ["z", "9"], ["0", "G"], ["1", "H"], ["2", "I"], ["3", "J"], ["4", "K"], ["5", "L"], ["6", "M"], ["7", "N"], ["8", "O"], ["9", "P"], ["\n", ":|~"], ["\r", ""]]
    for r in range(0, o):
        n = t[r]
        for s in range(0, MAP_LEN):
            if ":" == n and ":|~" == t[r:3]:
                n = "\n"
                r = r + 2
                break
            if n == charMap[s][1]:
                n = charMap[s][0]
                break
        i = i+n
    return i

async def get_token():
    head = """
       function aaa () {
           const jsdom = require("jsdom");
           const { JSDOM } = jsdom;
           const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
           window = dom.window;
           document = window.document;
           XMLHttpRequest = window.XMLHttpRequest;
           location=window.Location;
           navigator=window.navigator;
           var ue=[];
           var de=[];
           var gh=(function() {
                           var e = 0
                             , t = 0
                             , n = 0;
                           return function(o) {
                               e > 0 && e % 2 == 0 && (2 > t ? ue[t++] = o : 3 > n && (de[n++] = o)),
                               e++
                           }
                       })();
       """
    tail = 'return [ue,de];}'
    a = requests.get("https://www.bet365.es")
    # print(a.text)
    js = head + a.text.split("(boot||(boot={}));(function(){")[1].split('''</script>''')[0][:-6] + tail
    # print(js)
    e = execjs.compile(js.replace("boot['gh']", 'gh'), cwd=r'/home/dume/')
    res = e.call('aaa')
    res[0].append('.')
    token1 = ''
    for i in res:
        for j in i:
            token1 += j

    return decryptToken(token1)

async def get_session_id():
    headers = {
        'Host': 'www.bet365.es',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.bet365.es/',
        'Connection': 'keep-alive',
        'Cookie': 'aps03=ct=171&lng=3',
        'DNT': '1'
    }
       
    response = requests.get('https://www.bet365.es/defaultapi/sports-configuration', headers=headers)
    return response.cookies['pstk']

async def on_message(message):
    print(message)

if __name__ == "__main__":
    global websocket

    async def async_processing():
      _REQ_EXTENSIONS = [permessage_deflate.ClientPerMessageDeflateFactory(
                server_max_window_bits=15,
                client_max_window_bits=15,
                compress_settings={'memLevel': 4},
            )]
      _REQ_PROTOCOLS = ['zap-protocol-v1']

      R_HEADER = collections.namedtuple('Header','name value')
      _REQ_HEADERS = [
            R_HEADER('Sec-WebSocket-Version', '13'),
            R_HEADER('Accept-Encoding', 'gzip, deflate, br'),
            R_HEADER('Pragma', 'no-cache'),
            R_HEADER('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36')
      ]

      
      session_id = await get_session_id()
      token = await get_token()
  
      print(session_id)
      print(token)
      initial_msg = '\x23\x03P\x01__time,S_{},D_{}\x00'.format(session_id, token)

      async with websockets.connect('wss://premws-pt3.365lpodds.com/zap/', extra_headers=_REQ_HEADERS,
                                        extensions=_REQ_EXTENSIONS, subprotocols=_REQ_PROTOCOLS, ping_interval=None) as websocket:
        print("opened")
        await websocket.send(initial_msg)
        await websocket.send('\x16\x00CONFIG_3_0,OVInPlay_3_0,Media_L3_Z0\x01')

        while True:
          try:
              message = await websocket.recv()
              await on_message(message)
      
          except Exception as e:
              print(traceback.format_exc())
              print('Connection Closed')
              raise

    asyncio.get_event_loop().run_until_complete(async_processing())