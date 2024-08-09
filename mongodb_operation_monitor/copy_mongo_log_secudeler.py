from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson.timestamp import Timestamp
from datetime import datetime, timedelta
import time


class ConnectionDb:
    def __init__(self):
        self.search_srv = "mongodb+srv://net/" # test detail
        self.master_srv = "mongodb+srv:b.net/" # test detail

        self.search_db = 'ubuy_onesearch_v1'
        self.master_db = 'ubuy_logs_v1'
        self.search_collection = 'ubuy_detail_products_us'
        self.insert_collection = "mongodb_operation_monitor"

    def get_search_connection(self):
        self.client = MongoClient(self.search_srv)
        return self.client
    def get_master_connection(self):
        self.client = MongoClient(self.master_srv)
        return self.client

    def get_connection_close(self,client):
        client.close()


def insert_data(): 
    print(" OneSerach Script Log Call " )
    timeCalc = time.time()
    start_time = datetime.now()   

    end_time = start_time.replace(hour=0, minute=0, second=0)
    start_time = end_time - timedelta(days=1)

    print(start_time , end_time)

    start_ts = Timestamp(int(start_time.timestamp()), 0)
    end_ts = Timestamp(int(end_time.timestamp()), 0)

    current_date = datetime.now()
    date_formate = current_date - timedelta(days=1)
    date_formate = date_formate.strftime('%Y-%m-%d')

    try:
        connection = ConnectionDb() 
        search_client = connection.get_search_connection()
        local_db = search_client.local

        master_client = connection.get_master_connection()

        masterdb = master_client[connection.master_db]
        master_obj = masterdb[connection.insert_collection]

        pipeline = [  {"$match": {"ts": {"$gt": start_ts, "$lt": end_ts}, "ns": f"{connection.search_db}.{connection.search_collection}"}},
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
            master_obj.insert_one(final_result)

    except (ServerSelectionTimeoutError, Exception ) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    insert_data()