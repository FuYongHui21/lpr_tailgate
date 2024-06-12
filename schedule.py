from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers import interval, cron
import tzlocal
import tools

class LprTgPathSchedule():
    def __init__(self, lpr_base_path, tailgate_base_path, stations, sched_db_conn):
        self.lpr_base_path = lpr_base_path
        self.tailgate_base_path = tailgate_base_path
        self.stations = stations
        self.sched_db_conn = sched_db_conn
    
    def init_scheduler(self):
        self.sched = BackgroundScheduler(daemon=True, timezone=str(tzlocal.get_localzone()))
        self.sched.add_job(tools.createLprPath, 'cron',args = (self.lpr_base_path, self.stations),  hour = '23', minute = '59', second = '0')
        self.sched.add_job(tools.checkTailgatePath, 'cron', args = (self.tailgate_base_path, self.stations),  hour = '23', minute = '59', second = '10')
        self.sched.add_job(self.sched_db_conn.rmvUselessLpr, 'cron', hour = '23', minute = '59', second = '0')
        notifytrigger = interval.IntervalTrigger(seconds = 30)
        self.sched.add_job(tools.checkLprPath, args = (self.lpr_base_path, self.stations), trigger = notifytrigger)
        self.sched.add_job(tools.checkTailgatePath, args = (self.tailgate_base_path, self.stations), trigger = notifytrigger)
        notifytrigger_lpr = interval.IntervalTrigger(minutes = 5)
        self.sched.add_job(self.sched_db_conn.syncLprToMovement, trigger = notifytrigger_lpr)
        self.sched.start()

    def shutdown(self):
        print('shut down the schedule')
        self.sched.remove_all_jobs()
        self.sched.shutdown()
        
if __name__ == '__main__':
    from config import ConfigData
    from db import LprTgDb
    config_data = ConfigData('./config.json')
    config_data.readConfigData()
    eps_db_conn = LprTgDb(config_data.getDbParam())
    eps_db_conn.openMySqlConn()
    stations = eps_db_conn.select_sql('select station_id from station where station_type = 1')
    path_sched = LprTgPathSchedule(config_data.getLprBasePath(), config_data.getTailgateBasePath(), stations, eps_db_conn)
    path_sched.init_scheduler()

    while True:
        pass