from pyasn1.codec.ber import encoder
from pyasn1.type import tag
from scapy.layers.l2 import Ether
from scapy.layers.l2 import Dot1Q
from scapy.utils import hexdump

from goose.goose import GOOSE
from goose.goose_pdu import AllData
from goose.goose_pdu import Data
from goose.goose_pdu import IECGoosePDU
from scapy.sendrecv import sendp
from time import time


class GooseMessage:
    """  """
    def __init__(self,
                 goose_signals: list,
                 gocbRef: str,
                 sqNum: int,
                 dst_MAC: str,
                 vlan: int,
                 prio: int,
                 appid: hex,
                 stNum: int = None,
                 timeAllowedtoLive=4800,
                 test=False,
                 confRev=1,
                 ndsCom=False,
                 # sending_state=False,
                 ):
        # self.sending_state = sending_state
        self.length = len(goose_signals)
        self.g = IECGoosePDU().subtype(
            implicitTag=tag.Tag(
                tag.tagClassApplication,
                tag.tagFormatConstructed,
                1
            )
        )

        self.ether_part = Ether(dst=f'01:0c:cd:01:{dst_MAC}')
        self.dot1Q_part = Dot1Q(vlan=vlan, type=0x88b8, prio=prio)
        self.goose_part = GOOSE(appid=appid)

        self.g.setComponentByName('gocbRef', f'{gocbRef}__1LD/LLN0$GO$GSEOut')
        self.g.setComponentByName('timeAllowedtoLive', timeAllowedtoLive)
        self.g.setComponentByName('datSet', f'{gocbRef}__1LD/LLN0$GOOSEOut')
        self.g.setComponentByName('goID', f'{gocbRef}')
        self.g.setComponentByName('t', self.get_time())
        self.g.setComponentByName('stNum', stNum)
        self.g.setComponentByName('sqNum', sqNum)
        self.g.setComponentByName('test', test)
        self.g.setComponentByName('confRev', confRev)
        self.g.setComponentByName('ndsCom', ndsCom)
        self.g.setComponentByName('numDatSetEntries', self.length)

        self.d = AllData().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext,
                tag.tagFormatConstructed,
                11
            )
        )

        self.setComponentByName_boolean(goose_signals)
        self.g.setComponentByName('allData', self.d)

        self.packet = self.ether_part / self.dot1Q_part / self.goose_part / encoder.encode(self.g)

    def get_time(self):
        now = time()
        now_int = int(now)
        now_frac = int((now - now_int) * 10 ** 7)
        # print(f'now={now}')
        # print(f'    {now_int},{now_frac}')

        t1 = now_int.to_bytes(4, byteorder='big')
        t2 = now_frac.to_bytes(4, byteorder='big')
        # print([hex(i) for i in t1])
        # print([hex(i) for i in t2])
        # print([hex(i) for i in t1 + t2])
        return t1 + t2

    def hexdump(self, dump=True):
        """ :return dump """
        return hexdump(self.packet, dump)

    def __str__(self,
                dump=False
                ):
        """ :prints goose or dump """
        if dump:
            self.hexdump(dump=False)
        print(self.g)

    def setComponentByName_boolean(self, goose_signals):
        for i, signal in enumerate(goose_signals):
            d_i = Data()
            d_i.setComponentByName('boolean', signal)
            self.d.setComponentByPosition(i, d_i)

    def send_pack(self):
        sendp(self.packet)
        # sendpfast(self.packet, pps=1000, loop=10000, parse_results=1)  # todo: нагенерить на 1 период и повторять его по кругу


# if __name__ == '__main__':
#     goose = GooseModelCreator([1, 0, 1], 'gocb', 2, 3, '00:54', 3, 2, 4444, 4800, False, 1, False)
#     print(goose.length)
#     print(goose.hexdump)
