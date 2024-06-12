from socket import *
import struct

class LprTgUdp():
    def __init__(self, udp_ip_address, udp_port):
        self.udp_ip_address = udp_ip_address
        self.udp_port = udp_port

    def openUdpConn(self):
        try:
            self.lpr_tg_udp_conn = socket(AF_INET, SOCK_DGRAM)
            self.lpr_tg_udp_conn.bind((self.udp_ip_address, self.udp_port))
        except Exception as e:
            print(f'bind UDP socket failure with error {e}, ip_address = {self.udp_ip_address}, port = {self.udp_port}')
        else:
            print(f'UDP socket created successfully, ip_address = {self.udp_ip_address}, port = {self.udp_port}')

    def recvUdpPkt(self):
        return self.lpr_tg_udp_conn.recvfrom(256)

if __name__ == '__main__':
    from config import ConfigData
    from db import LprTgDb
    import tools
    config_data = ConfigData('./config.json')
    config_data.readConfigData()
    eps_db = LprTgDb(config_data.getDbParam())
    eps_db.openMySqlConn()
    lpr_tg_udp = LprTgUdp(config_data.getUdpIpAddress(), config_data.getUdpPort())
    lpr_tg_udp.openUdpConn()

    while True:
        try:
            pass
            recv_pkt, addr = lpr_tg_udp.recvUdpPkt()
            pkg_type, src_sid, dest_sid, data_len = struct.unpack(">BBBB", recv_pkt[0:4])
            recv_data = recv_pkt[4:4 + data_len]
            recv_data = recv_data.decode('ascii')
            recv_crc = struct.unpack(">H", recv_pkt[4 + data_len: 6 + data_len])
            print('pkg_type =', pkg_type, ',src_sid =', src_sid, ',dest_sid = ',dest_sid, ',data_len =', data_len, ',data = ', recv_data, ',crc = ', recv_crc[0])
            # print('pkg_type =', pkg_type, ',src_sid =', src_sid, ',dest_sid = ',dest_sid, ',data_len =', data_len)
            if pkg_type == config_data.getUdpPkgLpr():
                eps_db.createLpr(recv_data)
            elif pkg_type == config_data.getUdpPkgTg():
                eps_db.createTailgate(recv_data)
                
        except Exception as e:
            print(f'Exception {e} happened')
