from flask import Flask, render_template ,request
from pymongo import MongoClient, ReadPreference

class ConnectionDb:
    def __init__(self):
        self.CONNECTION_STRING = "mongodb+srv:/et/"
        self.database_name = 'ubuy_logs_v1' 
        self.insert_collection_name = "mongodb_operation_monitor"


    def get_connection(self):
        self.client = MongoClient(self.CONNECTION_STRING, read_preference=ReadPreference.PRIMARY)
        return self.client
    def get_connection_close(self,client):
        client.close()


onesearch_scrip_log = Flask(__name__)
@onesearch_scrip_log.route('/', methods=['GET', 'POST'])
def index():
    try:
        fetch_limit = 20
        connection = ConnectionDb()
        client = connection.get_connection()

        if request.method == 'POST':
            input_limit = request.form.get('count_limit', 0)
            if input_limit:
                fetch_limit = int(input_limit)
                print(fetch_limit)

        db = client[connection.database_name]
        collection = db[connection.insert_collection_name]

        items = list(collection.find().sort({'date':-1}).limit(fetch_limit))
    except Exception as e:
        return render_template('index.html', error_message=e)

    finally:
        if client:
            connection.get_connection_close(client)

    return render_template("index.html", items=items)


if __name__=="__main__":
    onesearch_scrip_log.run(host='0.0.0.0' ,debug=True,port= 5007)