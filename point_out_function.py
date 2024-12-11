from qdrant_client import QdrantClient, models


def point_out_keyword(keyword : str):
    # get the recommend keyword from the users input messages

    client = QdrantClient("localhost", port=6333)

    collection_name = "TEJ_QA_Final"
    # get the same class of the keyword in qdrant
    search = client.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="keyword", match=models.MatchValue(value=keyword)),
            ]
        ),
        with_payload=True,
        with_vectors=False,
        )
    
    # take out the question and frequency from the filter result
    row = {sr.payload['question']: sr.payload['frequency'] for sr in sorted(search[0], key=lambda x: x.payload['frequency'], reverse=True)}
    # sort questions by frequency
    recommend_dict = dict(sorted(row.items(), key=lambda item: item[1], reverse=True))
    
    if len(recommend_dict) > 5:
        recommend_list = list(recommend_dict.keys())[:5]
    else:
        recommend_list = list(recommend_dict.keys())

    # print(f"{qdrant_result_keyword}分類下的推薦問題 : {recommend_dict}")
    return recommend_list

if __name__ == '__main__':
    recommend_list = point_out_keyword("TEJ介紹")
    # recommend_list = point_out_keyword(input('search: '))
    print(recommend_list)