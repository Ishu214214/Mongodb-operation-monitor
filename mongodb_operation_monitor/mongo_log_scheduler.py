from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson.timestamp import Timestamp
from datetime import datetime, timedelta
import schedule
import time
import threading
from pytz import timezone

class ConnectionDb:
    def __init__(self):
        self.CONNECTION_STRING = "mongodb+srv.net/"
        self.database_name = 'ubuy_onesearch_v1'
        self.collection_name = 'mongodb_operation_monitor'
        self.insert_collection_name = "mongodb_operation_monitor"

    def get_connection(self):
        self.client = MongoClient(self.CONNECTION_STRING)
        return self.client
    def get_connection_close(self,client):
        client.close()


def quary_status_scheduler(): 
    print(f"\033[42m" + "*" * 10 + " OneSerach Script Log Call " + "*" * 10 + "\033[0m")
    timeCalc = time.time()
    start_time = datetime.now()   

    ist_timezone = timezone('Asia/Kolkata')
    current_date = datetime.now(ist_timezone)
    date_formate = current_date.replace(day=7)
    date_formate = date_formate.strftime('%Y-%m-%d %H:%M:%S')

    print(date_formate)

    end_time = start_time.replace(hour=0, minute=0, second=0)
    end_time = end_time.replace(day=7)

    start_time = end_time - timedelta(days=1)
    print(start_time , end_time)

    start_ts = Timestamp(int(start_time.timestamp()), 0)
    end_ts = Timestamp(int(end_time.timestamp()), 0)
    
    try:
        connection = ConnectionDb() 
        client = connection.get_connection()
        local_db = client.local

        db = client[connection.database_name]
        collection = db[connection.insert_collection_name]

        pipeline = [  {"$match": {"ts": {"$gt": start_ts, "$lt": end_ts}, "ns": f"{connection.database_name}.{connection.collection_name}"}},
                        {"$group": {"_id": "$op", "count": {"$sum": 1}}}     ]
        
        result = local_db.oplog.rs.aggregate(pipeline)
        print("Time Taken in query:", (time.time()- timeCalc))

        final_result = {"date":date_formate,"insert_query":0,"delete_query":0,"update_query":0}

        if result:
            for doc in result:
                if doc['_id'] == 'i':
                    final_result['insert_query'] = doc['count']
                elif doc['_id'] == 'd':
                    final_result['delete_query'] = doc['count']
                elif doc['_id'] == 'u':
                    final_result['update_query'] = doc['count']

            print(final_result)
            collection.insert_one(final_result)

    except (ServerSelectionTimeoutError, Exception ) as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.get_connection_close(client)


def schedule_task():
    schedule.every().day.at("17:10").do(quary_status_scheduler)
    print("function call")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # scheduler_thread = threading.Thread(target=schedule_task)
    # scheduler_thread.daemon = True
    # scheduler_thread.start()
    # while True:
    #     time.sleep(1)
    quary_status_scheduler()