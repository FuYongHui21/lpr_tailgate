def init():
    global config_data
    config_data = None

    global mysql_conn
    mysql_conn = None

    global udp_conn
    udp_conn = None
    
if __name__ == '__main__':
    init()
    print('mysql_conn = ', mysql_conn)
    print('config_data = ', config_data)