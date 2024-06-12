import datetime, os

def createLprPath(lpr_base_path, station_list):
    date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d')
    for station in station_list:
        lpr_path = lpr_base_path + '/' + date_str + '/' + str(station['station_id'])
        if not os.path.exists(lpr_path):
            try:
                os.makedirs(lpr_path)
            except Exception as e:
                print(f'create dir {lpr_path} fail with error {e}')
            else:
                print(f'create dir {lpr_path} successfully')
    
def createTailgatePath(tailgate_base_path, station_list):
    date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d')
    for station in station_list:
        tailgate_path = tailgate_base_path + '/' + date_str + '/' + str(station['station_id'])
        if not os.path.exists(tailgate_path+ '/image'):
            try:
                os.makedirs(tailgate_path + '/image')
            except Exception as e:
                print(f'create dir {tailgate_path}/image fail with error {e}')
            else:
                print(f'create dir {tailgate_path}/image successfully')
        if not os.path.exists(tailgate_path + '/video'):
            try:
                os.makedirs(tailgate_path + '/video')
            except Exception as e:
                print(f'create dir {tailgate_path}/video fail with error {e}')
            else:
                print(f'create dir {tailgate_path}/video successfully')

def checkLprPath(lpr_base_path, station_list):
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    for station in station_list:
        lpr_path = lpr_base_path + '/' + date_str + '/' + str(station['station_id'])
        if not os.path.exists(lpr_path):
            try:
                os.makedirs(lpr_path)
            except Exception as e:
                print(f'create dir {lpr_path} fail with error {e}')
            else:
                print(f'create dir {lpr_path} successfully')

def checkTailgatePath(tailgate_base_path, station_list):
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    for station in station_list:
        tailgate_path = tailgate_base_path + '/' + date_str + '/' + str(station['station_id'])
        if not os.path.exists(tailgate_path+ '/image'):
            try:
                os.makedirs(tailgate_path + '/image')
            except Exception as e:
                print(f'create dir {tailgate_path}/image fail with error {e}')
            else:
                print(f'create dir {tailgate_path}/image successfully')
        if not os.path.exists(tailgate_path + '/video'):
            try:
                os.makedirs(tailgate_path + '/video')
            except Exception as e:
                print(f'create dir {tailgate_path}/video fail with error {e}')
            else:
                print(f'create dir {tailgate_path}/video successfully')

if __name__ == '__main__':
    from config import ConfigData
    from db import LprTgDb
    config_data = ConfigData('./config.json')
    config_data.readConfigData()
    eps_db = LprTgDb(config_data.getDbParam())
    eps_db.openMySqlConn()
    stations = eps_db.select_sql('select station_id from station where station_type = 1')
    createLprPath(config_data.getLprBasePath(), stations)
    createTailgatePath(config_data.getTailgateBasePath(), stations)
    checkLprPath(config_data.getLprBasePath(), stations)
    checkTailgatePath(config_data.getTailgateBasePath(), stations)