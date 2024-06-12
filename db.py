import pymysql.cursors
from datetime import datetime, timedelta
from log import *

logger = logging.getLogger('log')
class LprTgDb():
    def __init__(self, config_data):
        self.dbParam = config_data
        self.whatsapp_group = {}
        self.stations = {}
 
    def openMySqlConn(self):
        try:
            self.mysql_conn = pymysql.connect(host=self.dbParam['host'],
                                                database=self.dbParam['database'],
                                                user=self.dbParam['user'],
                                                password=self.dbParam['password'],
                                                charset=self.dbParam['charset'],
                                                autocommit=True)
                                                # cursorclass=pymysql.cursors.DictCursor)
            self.getImagePathPrefix()
        except Exception as e:
            print(f'Exception {e} fired during connecting to database')
        else:
            print('connect to database successfully')

    def insert_sql(self, sql):
        # print('sql = ', sql)
        try:
            with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
            self.mysql_conn.commit()
        except pymysql.Error as e:
            print(f"mysql insert error: {e}")

    def select_sql(self, sql):
        # print('sql = ', sql)
        try:
            with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
        except pymysql.Error as e:
            print(f"mysql selct error: {e}")
        return results

    def update_sql(self, sql):
        # print('sql = ', sql)
        affected_rows = 0
        try:
            with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                affected_rows = cursor.execute(sql)
            self.mysql_conn.commit()
        except pymysql.Error as e:
            print(f"mysql update error: {e}")
        return affected_rows

    def delete_sql(self, sql):
        # print('sql = ', sql)
        try:
            with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
            self.mysql_conn.commit()
        except pymysql.Error as e:
            print(f"mysql delete error: {e}")

    def closeMySqlConn(self):
        self.mysql_conn.close()
    
    def get_settings(self):
            try:
                if len(self.whatsapp_group):
                    return
                setting_resp = self.select_sql('select * from setting')
                print('jasper setting_resp = ', setting_resp)
                for item in setting_resp:
                    if item['setting_type'] == 'WHATSAPP_GROUP':
                        self.whatsapp_group[item['setting_value'].split('|')[1]] = item['setting_value'].split('|')[0]
                if len(self.stations):
                    return
                station_resp = self.select_sql('select station_id, station_name, CASE WHEN in_out_state = 1 THEN "EXIT" ELSE "ENTRY" END AS station_role from station where station_type = 1')
                for item in station_resp:
                    self.stations[str(item['station_id'])] = item
            except Exception as e:
                print(f'update lpr failure with error {e}')
            # else:
            #     print('whatsapp_group = ', self.whatsapp_group)
            #     print('stations = ', self.stations)
                
    
    def updatelpr(self, data):
        # data="%d:%d:%s:%d:%s:", station_id, trans_id, trans_time, card_number, vehicle_number,image_path
        try:
            items = data.split(':')
            station_id = items[0]
            trans_id = items[1]
            trans_time = items[2]
            card_number = items[3]
            vehicle_number = items[4]
            image_path = items[5]
            print('station_id=', station_id, 'trans_id=', trans_id, 'trans_time=', trans_time, 'card_number=', card_number, 'vehicle_number=', vehicle_number, 'image_path=', image_path)
            trans_datetime = datetime.strptime(trans_time, '%Y%m%d%H%M%S')
            conv_trans_time = trans_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print('conv_trans_time = ', conv_trans_time)
            upd_rows = self.update_sql(f'update movement set vehicle_number = "{vehicle_number}", image_path = "{image_path}" where station_id = {station_id} and trans_id = {trans_id} and trans_time = "{conv_trans_time}"')
            print('result = ', upd_rows)
        except Exception as e:
            print(f'update lpr failure with error {e}')

    def createLpr(self, data):
        # data="%d:%d:%s:%d:%s:", station_id, trans_id, trans_time, card_number, vehicle_number,image_path
        try:
            items = data.split(':')
            station_id = items[0]
            trans_id = items[1]
            trans_time = items[2]
            card_number = items[3]
            vehicle_number = items[4]
            image_path = items[5]
            print('station_id=', station_id, 'trans_id=', trans_id, 'trans_time=', trans_time, 'card_number=', card_number, 'vehicle_number=', vehicle_number, 'image_path=', image_path)
            trans_datetime = datetime.strptime(trans_time, '%Y%m%d%H%M%S')
            conv_trans_time = trans_datetime.strftime('%Y-%m-%d %H:%M:%S')
            conv_trans_date = trans_datetime.strftime('%Y-%m-%d')
            # print('conv_trans_time = ', conv_trans_time)
            image_path = self.img_path_prefix + image_path
            self.insert_sql(f'insert into lpr_data (station_id, trans_id, trans_time, vehicle_number, image_path) values ({station_id}, {trans_id}, "{conv_trans_time}", "{vehicle_number}", "{image_path}")')
            # search vip table, insert a record into table whatsapp_notification if it is a VIP
            vip_resp = self.select_sql(f'select * from vip where card_number is NULL and vehicle_number = "{vehicle_number}" and start_datetime <= "{conv_trans_date}" and end_datetime >= "{conv_trans_date}" order by vip_id desc limit 1')
            if vip_resp:
                cur_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vip = vip_resp[0]
                whatsapp_group = self.whatsapp_group[str(vip['whatsapp_group'])]
                message = f'{card_number} {vehicle_number} {self.stations[station_id]["station_role"]}: {self.stations[station_id]["station_name"]} at {conv_trans_time}'
                self.insert_sql(f'insert into whatsapp_notification (created_at, whatsapp_group, message, send, remarks) values ("{cur_time}", "{whatsapp_group}", "{message}", 0, "{vip["remarks"]}")')
        except Exception as e:
            print(f'update lpr failure with error {e}')

    def createTailgate(self, data):
        # data="%d:%s:%s:%d:%s:", station_id, vehicle_number, tailgate_timestamp, tailgate_img_path, tailgate_video_path
        try:
            items = data.split(':')
            station_id = items[0]
            vehicle_number = items[1]
            tailgate_timestamp = items[2]
            tailgate_img_pathname = items[3]
            tailgate_video_pathname = items[4]
            print('station_id=', station_id, 'vehicle_number=', vehicle_number, 'tailgate_timestamp=', tailgate_timestamp, 'tailgate_img_pathname=', tailgate_img_pathname, 'tailgate_video_pathname=', tailgate_video_pathname)
            logger.info(f'Tailgate received - station_id = {station_id}, vehicle_number = {vehicle_number}, tailgate_timestamp = {tailgate_timestamp}, tailgate_img_pathname = {tailgate_img_pathname}, tailgate_video_pathname = {tailgate_video_pathname}')
            tailgate_datetime = datetime.strptime(tailgate_timestamp[0:14], '%Y%m%d%H%M%S')
            exit_time = tailgate_datetime.strftime('%Y-%m-%d %H:%M:%S')
            tailgate_img_pathname = self.img_path_prefix + tailgate_img_pathname
            tailgate_video_pathname = self.img_path_prefix + tailgate_video_pathname
            # print('exit_time = ', exit_time)
            # search movement table with vehicle_number to get the latest record
            # if in_out_state is 0 or 2, get station_id -> entry_station_id, trans_time -> entry_time, card_number, card_type, vehicle_type and write the tailgate table
            # else, only input info from UDP into tailgate table
            results = self.select_sql(f'select station_id, trans_time, card_number, vehicle_type, in_out_state, card_type from movement where vehicle_number = "{vehicle_number}" order by movement_id desc limit 1')
            # print('result = ', results)
            # print('in_out_state = ', results[0]["in_out_state"])
            if results and ( results[0]["in_out_state"] == 0 or results[0]["in_out_state"] == 2 ):
                result = results[0]
                self.insert_sql(f'insert into tailgate (entry_station_id, exit_station_id, entry_time, exit_time, card_number, vehicle_number, card_type, vehicle_type, image, video, status) values ({result["station_id"]}, {station_id}, "{result["trans_time"]}", "{exit_time}", "{result["card_number"]}", "{vehicle_number}", {result["card_type"]}, {result["vehicle_type"]}, "{tailgate_img_pathname}", "{tailgate_video_pathname}", 0)')
            else:
                self.insert_sql(f'insert into tailgate (exit_station_id, exit_time, vehicle_number, image, video, status) values ({station_id}, "{exit_time}", "{vehicle_number}", "{tailgate_img_pathname}", "{tailgate_video_pathname}", 0)')
        except Exception as e:
            print(f'update tailgate failure with error {e}')

    def syncLprToMovement(self):
        try:
            print('---- start to sync lpr info from lpr_data to movement ---')
            lpr_rec = self.select_sql('select * from lpr_data')
            for lpr in lpr_rec:
                lpr_id = lpr['lpr_id']
                station_id = lpr['station_id']
                trans_id = lpr['trans_id']
                trans_time = lpr['trans_time']
                vehicle_number = lpr['vehicle_number']
                image_path = lpr['image_path']
                upd_row = self.update_sql(f'update movement set vehicle_number = "{vehicle_number}", image_path = "{image_path}" where station_id = {station_id} and trans_id = {trans_id} and trans_time = "{trans_time}"')
                if upd_row == 1:
                    self.delete_sql(f'delete from lpr_data where lpr_id = {lpr_id}')
                    print(f'sync record from lpr to movement with station_id = {station_id}, trans_id = {trans_id}, trans_time = {trans_time}, vehicle_number = {vehicle_number}, image_path = {image_path}')
        except Exception as e:
            print(f'sync info from lpr to movement failure with error {e}')

    def rmvUselessLpr(self):
        try:
            print('---- start to remove useless lpr from table lpr_data ----')
            date_str = (datetime.now() + timedelta(hours=-1)).strftime('%Y-%m-%d %H:%M:%S')
            self.delete_sql(f'delete from lpr_data where trans_time < "{date_str}"')
        except Exception as e:
            print(f'remove useless lpr data failure with error {e}')

    def getImagePathPrefix(self):
        try:
            img_path_setting = self.select_sql('select * from setting where setting_type = "IMAGE_PATH_PREFIX"')
            self.img_path_prefix = img_path_setting[0]['setting_value']
        except Exception as e:
            print(f'get IMAGE_PATH_PREFIX fail with error {e}')

if __name__ == '__main__':
    from config import ConfigData
    config_data = ConfigData('enc_config.json')
    config_data.readConfigData()
    eps_db = LprTgDb(config_data.getDbParam())
    eps_db.openMySqlConn()
    # result = eps_db.select_sql('select trans_time, in_out_state, vehicle_type, card_type from latest_trans where vehicle_number = "111111" limit 1')
    result = eps_db.select_sql('select * from lpr_data')
    print('query result = ', result)
    for item in result:
        # print('item = ', item)
        print('station_id = ', item['station_id'])
        print('trans_id = ', item['trans_id'])
        print('trans_time = ', item['trans_time'])
        print('vehicle_number = ', item['vehicle_number'])
        print('image_path = ', item['image_path'])
    eps_db.rmvUselessLpr()
    eps_db.get_settings()
