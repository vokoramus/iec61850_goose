import tkinter as tk
from configparser import ConfigParser
from scapy.utils import wrpcap
# from scapy.utils import wrpcapng


class GooseRepository(object):
    """ методы, обеспечивающие стыковку с БД (ini) """
    def __init__(self):
        pass

    #     запись в файл ini
    def save_to_file(self, filename, config):
        # save to a file
        with open(filename, 'w') as configfile:
            config.write(configfile)

    def open_file(self, filename):
        config = ConfigParser()
        config.read(filename)
        return config

    def save_to_pcap(self, filename='__new_goose'):
        """ save to pcap file """
        wrpcap(f'out/{filename}.pcap', self.packet)     # todo   self.packet

    # def save_to_pcapng(self, filename='__new_goose'):
    #     """ save to pcapng file
    #     https://scapy.readthedocs.io/en/latest/api/scapy.utils.html#scapy.utils.wrpcap
    #     """
    #     wrpcapng(f'out/{filename}.pcap', self.packet)


# if __name__ == "__main__":


