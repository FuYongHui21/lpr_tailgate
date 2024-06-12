import struct, sys
from config import ConfigData
from db import LprTgDb
from schedule import LprTgPathSchedule
from udp import LprTgUdp
from log import *

# get encrypted config file
enc_config_file_name = 'enc_config.json'
if len(sys.argv) > 1:
    enc_config_file_name = sys.argv[1]

# read config data from ./config.json
# lpr_tg_config_data = ConfigData('./config.json')
lpr_tg_config_data = ConfigData(enc_config_file_name)
lpr_tg_config_data.readConfigData()

# init log file
init_rotating_log(lpr_tg_config_data.getLogPath() + lpr_tg_config_data.getMainLogFile(),lpr_tg_config_data.getLogFileSize(), lpr_tg_config_data.getLogFileCount())
logger = logging.getLogger('log')
# connect to the database
lpr_tg_db_conn = LprTgDb(lpr_tg_config_data.getDbParam())
lpr_tg_db_conn.openMySqlConn()
lpr_tg_db_conn.get_settings()
sched_db_conn = LprTgDb(lpr_tg_config_data.getDbParam())
sched_db_conn.openMySqlConn()

# get all configured stations
stations = lpr_tg_db_conn.select_sql('select station_id from station where station_type = 1')
# start background schedule, add 4 jobs
# job 1 - create lpr/tailgate directory at 23:59:00 for tomorrow
# job 2 - check whether today's lpr/tailgate directory exists every 30 seconds, create them if not
# job 3 - remove useless lpr (1 hour ago) from lpr_data at 23:59:00
# job 4 - sync lpr info from lpr_data to movement table every 5 minutes 
path_sched = LprTgPathSchedule(lpr_tg_config_data.getLprBasePath(), lpr_tg_config_data.getTailgateBasePath(), stations, sched_db_conn)
path_sched.init_scheduler()

# start UDP client socket
lpr_tg_udp_conn = LprTgUdp(lpr_tg_config_data.getUdpIpAddress(), lpr_tg_config_data.getUdpPort())
lpr_tg_udp_conn.openUdpConn()
while True:
    try:
        recv_pkt, addr = lpr_tg_udp_conn.recvUdpPkt()
        print('recv_pkt = ', recv_pkt)
        print('addr = ', addr)
        pkg_type, src_sid, dest_sid, data_len = struct.unpack(">BBBB", recv_pkt[0:4])
        recv_data = recv_pkt[4:4 + data_len]
        recv_data = recv_data.decode('ascii')
        recv_crc = struct.unpack(">H", recv_pkt[4 + data_len: 6 + data_len])
        print('pkg_type =', pkg_type, ',src_sid =', src_sid, ',dest_sid = ',dest_sid, ',data_len =', data_len, ',data = ', recv_data, ',crc = ', recv_crc[0])
        logger.info(f'pkg_type = {pkg_type}, src_sid = {src_sid}, dest_sid = {dest_sid}, data_len = {data_len}, data = {recv_data}, crc = {recv_crc[0]}')
        if pkg_type == lpr_tg_config_data.getUdpPkgLpr():
            lpr_tg_db_conn.createLpr(recv_data)
        elif pkg_type == lpr_tg_config_data.getUdpPkgTg():
            lpr_tg_db_conn.createTailgate(recv_data)
    except Exception as e:
        print(f'Exception {e} happened')