import json, os
from cryptography.fernet import Fernet

class ConfigData:
    def __init__(self, file_name):
        self.config_file_name = file_name

    def readConfigData(self):
        # config_file = open(self.config_file_name)
        # self.config_data = json.load(config_file)
        # config_file.close()

        key = '7YvFbC0uPNUuZX5DE2ClqTjaShTJBKaxI6OEMOdJYaA='
        key_f = Fernet(key)
        with open(self.config_file_name, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        encrypted_file.close()

        decrypted_data = key_f.decrypt(encrypted_data).decode('utf-8')
        self.config_data = json.loads(decrypted_data)

    def getDbParam(self):
        return self.config_data['db']

    def getUdpPort(self):
        return self.config_data['upd_port']

    def getUdpIpAddress(self):
        return self.config_data['udp_ip_address']

    def getUdpPkgLpr(self):
        return self.config_data['udp_pkg_lpr']

    def getUdpPkgTg(self):
        return self.config_data['upd_pkg_tg']

    def getLprBasePath(self):
        return self.config_data['lpr_base_path']

    def getTailgateBasePath(self):
        return self.config_data['tailgate_base_path']
    
    def getLogPath(self):
        return self.config_data['log_lpr_tailgate']['log_path']
    
    def getMainLogFile(self):
        return self.config_data['log_lpr_tailgate']['main_log_name']
    
    def getLogFileSize(self):
        return self.config_data['log_lpr_tailgate']['log_file_size']
    
    def getLogFileCount(self):
        return self.config_data['log_lpr_tailgate']['log_file_count']
    
if __name__ == '__main__':
    lpr_config_data = ConfigData('./config.json')
    lpr_config_data.readConfigData()
    print('config_data = ', lpr_config_data.config_data)
    print('dbinfo = ', lpr_config_data.getDbParam())
    print('UDP ip address = ', lpr_config_data.getUdpIpAddress())
    print('UDP port = ', lpr_config_data.getUdpPort())
    print('UDP package LPR = ', lpr_config_data.getUdpPkgLpr())
    print('UDP package TG = ', lpr_config_data.getUdpPkgTg())
    print('LPR base path = ', lpr_config_data.getLprBasePath())
    print('Tailgate base path = ', lpr_config_data.getTailgateBasePath())