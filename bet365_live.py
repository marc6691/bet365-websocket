import re
import sys
import time
import requests
from requests import request
from autobahn.twisted.websocket import connectWS, WebSocketClientFactory, WebSocketClientProtocol
from autobahn.websocket.compress import (
    PerMessageDeflateOffer,
    PerMessageDeflateResponse,
    PerMessageDeflateResponseAccept,
)
from autobahn.twisted.util import sleep

from twisted.python import log
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory

from txaio import start_logging, use_twisted
import subprocess

_MAP_LEN = 64
_charMap = [
    ["A", "d"], ["B", "e"], ["C", "f"], ["D", "g"], ["E", "h"], ["F", "i"], ["G", "j"], 
    ["H", "k"], ["I", "l"], ["J", "m"], ["K", "n"], ["L", "o"], ["M", "p"], ["N", "q"], ["O", "r"], 
    ["P", "s"], ["Q", "t"], ["R", "u"], ["S", "v"], ["T", "w"], ["U", "x"], ["V", "y"], ["W", "z"], 
    ["X", "a"], ["Y", "b"], ["Z", "c"], ["a", "Q"], ["b", "R"], ["c", "S"], ["d", "T"], ["e", "U"], 
    ["f", "V"], ["g", "W"], ["h", "X"], ["i", "Y"], ["j", "Z"], ["k", "A"], ["l", "B"], ["m", "C"], 
    ["n", "D"], ["o", "E"], ["p", "F"], ["q", "0"], ["r", "1"], ["s", "2"], ["t", "3"], ["u", "4"], 
    ["v", "5"], ["w", "6"], ["x", "7"], ["y", "8"], ["z", "9"], ["0", "G"], ["1", "H"], ["2", "I"], 
    ["3", "J"], ["4", "K"], ["5", "L"], ["6", "M"], ["7", "N"], ["8", "O"], ["9", "P"], 
    ["\n", ":|~"], ["\r", ""]
]


class MyClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      print("opened")      
      req = u'#\x03P\x01__time,S_{},D_{}\x00'.format(
            self.factory.session_id, self.factory.auth_token).encode('utf-8')
      print(req)
      self.sendMessage(req)
   
   def onMessage(self, payload, isBinary):
      print(payload)
      message = payload.decode('utf8')

      if message.startswith('100'):
      	# time.sleep(0.2)
      	req = u'\x16\x00CONFIG_3_0,OVInPlay_3_0,Media_L3_Z0,XL_L3_Z0_C1_W1\x01'.encode('utf-8')
      	self.sendMessage(req)


def _re_nst_token_feom_page_source(page_source) :      
        pattern1 = re.compile("d\[b\(\\'0x1\\\'\)\][\s]*=[\s]*\\\'.*?\\\'[\s]*;")
        pattern2 = re.compile("d\[b\(\\'0x0\\\'\)\][\s]*=[\s]*\\\'.*?\\\'[\s]*;")
        r1= pattern1.findall(page_source)
        r2= pattern2.findall(page_source)
        if len(r1) > 0 and len(r2) > 0:
            sr1 = r1[0].split('\'')[3]
            sr2 = r2[0].split('\'')[3]
            nst_token = '.'.join([sr1,sr2])
            print('nst token id'+nst_token)
            return nst_token
        return

def _gen_nst_auth_code_str(nst_token):
    D_str = _nst_decrypt(nst_token)
    print("nst auth str:" + D_str)
    return D_str

def _nst_encrypt(nst_token):
    
    ret = ""
    for r in range(len(nst_token)):
        n = nst_token[r]
        for s in range(_MAP_LEN):
            if n == _charMap[s][0]:
                n = _charMap[s][1]
                break
        ret += n
    return ret

def _nst_decrypt(nst_token):    

    ret = ""
    nst_token_len = len(nst_token)
    r= 0
    while nst_token_len>r:
        n = nst_token[r]
        for s in range(_MAP_LEN):
            if ":" == n and ":|~" == nst_token[r, r+3]:
                n = "\n"
                r += 2
                break
            if (n == _charMap[s][1]) :
                n = _charMap[s][0]
                break
        ret += n
        r +=1
    return ret

def get_session_id(response):
	return re.search(r'\"pstk\",\"value\":\"(.*?)\"', response).group(1)

class MyFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        self.retry(connector)

if __name__ == '__main__':
   
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    url = 'wss://premws-pt3.365lpodds.com/zap/'

    factory = MyFactory(
        url, useragent=USER_AGENT, protocols=['zap-protocol-v1'])
    factory.protocol = MyClientProtocol
    factory.headers = {}
    
    result = subprocess.run(["node", "bet365_nst.js"], capture_output=True)
    response = result.stdout.decode("utf-8").strip()
    print(response)
    factory.session_id = get_session_id(response)
    print(factory.session_id)

    nst_token = _re_nst_token_feom_page_source(response) 
    factory.auth_token = _gen_nst_auth_code_str(nst_token)

    def accept(response):
        if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)
    factory.setProtocolOptions(perMessageCompressionAccept=accept)
    factory.setProtocolOptions(perMessageCompressionOffers=[PerMessageDeflateOffer(
        accept_max_window_bits=True,
        accept_no_context_takeover=True,
        request_max_window_bits=0,
        request_no_context_takeover=True,
    )])

    if factory.isSecure:
         contextFactory = ssl.ClientContextFactory()
    else:
         contextFactory = None
 
    connectWS(factory, contextFactory)
    reactor.run()
 
