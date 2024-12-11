import time
import warnings
import pandas as pd
import configparser
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import VectorParams, Distance
from TWSC_embedding import get_embeddings_model
warnings.filterwarnings("ignore")

# Read config file Because the information are in config.ini
config = configparser.ConfigParser()
config.read("config.ini")

MODEL_NAME = config['embedding']['MODEL_NAME']
API_KEY = config['embedding']['API_KEY']
API_URL = config['embedding']['API_URL']

# connect to embedding model
embeddings_model = get_embeddings_model(API_URL, API_KEY, MODEL_NAME)

# split the data for uploaded and not uploaded
data = pd.read_excel("RAG_智能客服文本.xlsx")
data_without_y = data[data['uploaded'] != 'y']
data_with_y = data[data['uploaded'] == 'y']

def data2qdrant():
    # connect to qdrant
    client = QdrantClient(url="http://localhost:6333")

    # check the database exist or not
    if client.collection_exists(collection_name="TEJ_QA_Final"):
        pass
    # if not exist, create the collection and two vector spaces
    else:
        client.create_collection(
            collection_name="TEJ_QA_Final",
            # The TWCC embedding model has 1536 dimensions
            vectors_config={
                "question": VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                ),
                "flag": VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                ),
            },
        )

    uploaded = []
    for index, row in data_without_y.iterrows():
        if str(row['flag']) == 'nan':
            # if the flag is nan, set the flag to [0] * 1536, represent no data available
            flag_list = [0] * 1536
        else:
            flag_list = embeddings_model.embed_query(row['flag'])
        time.sleep(1)
        q_list = embeddings_model.embed_query(row['Questions'])
        # put data into qdrant, and can see the data in payload
        client.upsert(
            collection_name="TEJ_QA_Final",
            points=[
                models.PointStruct(
                    id=row['序號'],
                    vector={
                        "question": q_list,
                        "flag": flag_list
                    },
                    payload={
                        "id": row['序號'],
                        "question": row['Questions'],
                        "answer": row['Answers'],
                        "keyword": row['問題分類'],
                        "flag": row['flag'],
                        "frequency": 0
                    },
                )
            ],
        )
        print(f"第{row['序號']}筆資料上傳成功！- Q:{row['Questions']}")
        uploaded.append('y')

    # get the collection information
    qdrant_info = client.get_collection(collection_name="TEJ_QA_Final")
    print(f"本次匯入{len(uploaded)}筆資料，現在資料庫共有{qdrant_info.points_count}筆資料！")
    # concat the dataframe with y and without y
    data_without_y['uploaded'] = uploaded
    data_to_excel = pd.concat([data_with_y, data_without_y])
    data_to_excel.to_excel("RAG_智能客服文本.xlsx", index=False)

# run this code to update dataframe
if __name__ == "__main__":
    
    start_time = time.time()

    data2qdrant()
    
    end_time = time.time()

    execution_time = end_time - start_time

    hours, rem = divmod(execution_time, 3600)

    minutes, seconds = divmod(rem, 60)

    print("Data to qdrant with execute time : {:0>2}:{:0>2}:{:05.2f} is successful !".format(int(hours),int(minutes),seconds))