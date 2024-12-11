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

data = pd.read_csv("官方網站文章清單.csv")
data_notna = data.dropna()
data_notna = data_notna.reset_index(drop=True)
data_notna['標籤分類'] = data_notna['標籤'].apply(lambda x: x.split(','))
max_tags = data_notna['標籤分類'].apply(len).max()
tags_df = pd.DataFrame(data_notna['標籤分類'].to_list(), columns=[f'標籤{i+1}' for i in range(max_tags)])
data_notna = data_notna.join(tags_df)

def article2qdrant():
    # connect to qdrant
    client = QdrantClient(url="http://localhost:6333")

    # check the database exist or not
    if client.collection_exists(collection_name="TEJ_article"):
        client.delete_collection(collection_name="TEJ_article")
    client.create_collection(
        collection_name="TEJ_article",
        # The TWCC embedding model has 1536 dimensions
        vectors_config={
            "title": VectorParams(
                size=1536,
                distance=Distance.COSINE,
            )
        },
    )

    for index, row in data_notna.iterrows():
        # tag_list = embeddings_model.embed_query(row['標籤'])
        # time.sleep(1)
        title_list = embeddings_model.embed_query(row['內容標題'])
        tags = {f"tag{i+1}": row[f"標籤{i+1}"].strip() if pd.notna(row[f"標籤{i+1}"]) else None for i in range(max_tags)}
        # put data into qdrant, and can see the data in payload
        client.upsert(
            collection_name="TEJ_article",
            points=[
                models.PointStruct(
                    id=index+1,
                    vector={
                        "title": title_list,
                    },
                    payload={
                        "id": index+1,
                        "title": row['內容標題'],
                        "class": row['分類'],
                        "tag": row['標籤'],
                        "date": row['日期'],
                        **tags
                    },
                )
            ],
        )
        print(f"第{index+1}筆資料上傳成功！- Q:{row['內容標題']}")

    qdrant_info = client.get_collection(collection_name="TEJ_article")
    print(f"現在資料庫共有{qdrant_info.points_count}筆資料！")

# run this code to update dataframe
if __name__ == "__main__":
    
    start_time = time.time()

    article2qdrant()
    
    end_time = time.time()

    execution_time = end_time - start_time

    hours, rem = divmod(execution_time, 3600)

    minutes, seconds = divmod(rem, 60)

    print("Article to qdrant with execute time : {:0>2}:{:0>2}:{:05.2f} is successful !".format(int(hours),int(minutes),seconds))