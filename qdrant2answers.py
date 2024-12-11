import random
import pandas as pd
import configparser
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from TWSC_embedding import get_embeddings_model
from ffm_model import tej_ai_service
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate

# Read config file Because the information are in config.ini
config = configparser.ConfigParser()
config.read("config.ini")

MODEL_NAME = config['embedding']['MODEL_NAME']
API_KEY = config['embedding']['API_KEY']
API_URL = config['embedding']['API_URL']

embeddings_model = get_embeddings_model(API_URL, API_KEY, MODEL_NAME)

collection_name = "TEJ_QA_Final"
collection_name_article = "TEJ_article"

def get_article_classes():
    output_parser = CommaSeparatedListOutputParser()
    client = QdrantClient("localhost", port=6333)
    count = int(str(client.count(collection_name_article, exact=True)).split("=")[-1])
    all_data = client.scroll(
        collection_name=collection_name_article,
        limit=count,
    )

    all_tags = []
    for article_data in all_data[0]:
        article_payload = article_data.payload
        for tag in article_payload['tag'].split(","):
            all_tags.append(tag.strip())

    unique_tags = list(set(all_tags))
    
    # format_instructions = output_parser.get_format_instructions()
    # LLM Model 的回覆速度太不一定，因為要設成預設的區域按鈕的概念，所以先不用這個方式
    # 未來若要使用這部分，若要掌握趨勢可搭配 tavily search 然後透過特定資料型態(ex:json)的 few-shot 和 output_parser 來使回覆型態趨於一致
    # prompt_template = """List three classes in [{classes}]. No prefix
    #                         {format_instructions}"""
    # prompt = PromptTemplate(
    #     template=prompt_template,
    #     input_variables=["classes"], 
    #     partial_variables={"format_instructions": format_instructions}
    # )
    # chain = prompt | tej_ai_service | output_parser
    # results = chain.invoke({"classes": unique_tags})
    # if len(results) == 3:
    #     return results
    # else:
    #     results = random.sample(unique_tags, 3)
    #     return results
    results = random.sample(unique_tags, 3)
    return results

def fetch_article_of_class(class_name):
    # 取出對應tag下的文章
    client = QdrantClient("localhost", port=6333)
    return client.scroll(
        collection_name=collection_name_article,
        scroll_filter=models.Filter(
            should=[
                models.FieldCondition(key=f"tag{i}", match=models.MatchValue(value=class_name)) for i in range(1, 7)
            ]
        )
    )

def filter_latest_articles(articles, dates):
    if len(articles) > 1:
        # 將日期字串轉換為datetime格式進行比較，並留下最新的
        date_objects = [datetime.strptime(date, '%Y/%m/%d %H:%M') for date in dates]
        latest_index = date_objects.index(max(date_objects))
        return articles[latest_index], dates[latest_index]
    elif articles:
        return articles[0], dates[0]
    return None, None

def get_article():
    classes = get_article_classes()
    class_1, class_2, class_3 = classes[0], classes[1], classes[2]
    article_of_class_1 = fetch_article_of_class(class_1)
    article_of_class_2 = fetch_article_of_class(class_2)
    article_of_class_3 = fetch_article_of_class(class_3)

    # if len(article_of_class_1[0]) > 0 and len(article_of_class_2[0]) > 0 and len(article_of_class_3[0]) > 0:
    class_1_article, class_2_article, class_3_article = [], [], []
    class_1_date, class_2_date, class_3_date = [], [], []
    for article_payload in article_of_class_1[0]:
        title = article_payload.payload['title']
        date = article_payload.payload['date']
        class_1_article.append(title)
        class_1_date.append(date)
    for article_payload in article_of_class_2[0]:
        title = article_payload.payload['title']
        date = article_payload.payload['date']
        class_2_article.append(title)
        class_2_date.append(date)
    for article_payload in article_of_class_3[0]:
        title = article_payload.payload['title']
        date = article_payload.payload['date']
        class_3_article.append(title)
        class_3_date.append(date)
        
    latest_class_1_article, latest_class_1_date = filter_latest_articles(class_1_article, class_1_date)
    latest_class_2_article, latest_class_2_date = filter_latest_articles(class_2_article, class_2_date)
    latest_class_3_article, latest_class_3_date = filter_latest_articles(class_3_article, class_3_date)

    recommend_article = {
        'messages':
        [
            {
                'class': class_1, 'article': latest_class_1_article, 'date': latest_class_1_date
            },
            {
                'class': class_2, 'article': latest_class_2_article, 'date': latest_class_2_date
            },
            {
                'class': class_3, 'article': latest_class_3_article, 'date': latest_class_3_date
            }
        ]
    }
    keyword = "公司介紹"
    return recommend_article, keyword


def get_answers(question : str):

    client = QdrantClient("localhost", port=6333)

    qdrant_search_df = pd.DataFrame(columns=['question', 'answer', 'keyword', 'score', 'Pass_LLM', 'replace_question'])

    substr_delete = {'我想要', '我需要', '我想找', '請告訴我', '請跟我說', '請說明', '請給我', '我想要找', '我要'}
    # delete prefix  
    for i in substr_delete:
        index = question.find(i)
        if index != -1:
            question = question.replace(i, '')

    # 第一輪是如果與資料庫的問題完全符合，就會不經過LLM，直接回傳答案，這種情況通常會是按下精選提問
    first_search = client.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="question", match=models.MatchValue(value=question)),
            ]
        ),
        with_payload=True,
        with_vectors=False,
        )
    # 如果第一輪搜尋沒有數據，則進行第二輪搜尋
    if len(first_search[0]) == 0:
        question_vector=embeddings_model.embed_query(question)
        # 第二輪，取出得分最高的5條訊息，分數需要高於0.6
        second_search = client.search(
                collection_name=collection_name,
                query_vector=models.NamedVector(
                    name="question",
                    vector=question_vector,
                ),
                limit=5,
                with_vectors=False,
                with_payload=True,
                score_threshold=0.6
            )
        # 如果第二輪搜尋沒有數據，則進行第三輪搜尋
        if len(second_search) == 0:
            # 第三輪，取出「flag」欄位中得分最高的數據
            third_search = client.search(
                collection_name=collection_name,
                query_vector=models.NamedVector(
                    name="flag",
                    vector=question_vector,
                ),
                limit=1,
                with_vectors=False,
                with_payload=True,
                # score_threshold=0.6
            )
            # 如果第三輪搜尋沒有數據，則傳回空dataframe
            if len(third_search) == 0:
                qdrant_search_df['Pass_LLM'] = True
                print("沒有符合的搜尋結果！")
            else:
                print("第三層篩選！")
                qdrant_search_df['question'] = [third_search[0].payload['question']]
                qdrant_search_df['answer'] = [third_search[0].payload['answer']]
                qdrant_search_df['keyword'] = [third_search[0].payload['keyword']]
                qdrant_search_df['score'] = [third_search[0].score]
                qdrant_search_df['Pass_LLM'] = True
                qdrant_search_df['replace_question'] = True
        else:
            print("第二層篩選！")
            Q, A, keyword, score = [], [], [], []
            for search in second_search:
                Q.append(search.payload['question'])
                A.append(search.payload['answer'])
                keyword.append(search.payload['keyword'])
                score.append(search.score)
            qdrant_search_df['question'] = Q
            qdrant_search_df['answer'] = A
            qdrant_search_df['keyword'] = keyword
            qdrant_search_df['score'] = score
            qdrant_search_df['Pass_LLM'] = True
            qdrant_search_df['replace_question'] = False
    else:
        print("第一層篩選！")
        qdrant_search_df['question'] = [first_search[0][0].payload['question']]
        qdrant_search_df['answer'] = [first_search[0][0].payload['answer']]
        qdrant_search_df['keyword'] = [first_search[0][0].payload['keyword']]
        qdrant_search_df['score'] = [first_search[0][0].score]
        qdrant_search_df['Pass_LLM'] = False
        qdrant_search_df['replace_question'] = False

    return {'qdrant_search_result': qdrant_search_df}

def overwrite_frequency(question : str, collection_name : str, client):
    # 將 Qdrant RAG 到的結果複寫一次，並且 freqency 欄位 +1
    search = client.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="question", match=models.MatchValue(value=question)),
            ]
        ),
        with_payload=True,
        with_vectors=False,
        )
    
    points = [(search[0][0].id)]
    payload = search[0][0].payload
    answer, flag, frequency, Id, keyword, question = payload['answer'], payload['flag'], payload['frequency'], payload['id'], payload['keyword'], payload['question']
    frequency += 1
    client.overwrite_payload(
        collection_name=collection_name,
        payload={
            "answer": answer,
            "flag": flag,
            "frequency": frequency,
            "id": Id,
            "keyword": keyword,
            "question": question,
        },
        points=points,
    )

# if __name__  == "__main__":
#     while True:
#         text = input('search: ')
#         if text == 'exit':
#             break
#         else:
#             result = get_article()
#             print(result)
    # get_article_classes()
    # wanna_know = "TEJ介紹" #input('search: ')
    # start_time = time.time()
    # # tej_answers = get_answers(wanna_know)
    # # print(tej_answers)
    # tej_recommend = get_recommend(wanna_know)
    # print(tej_recommend)
    # end_time = time.time()

    # execution_time = end_time - start_time

    # hours, rem = divmod(execution_time, 3600)

    # minutes, seconds = divmod(rem, 60)

    # print("Get answer with execute time : {:0>2}:{:0>2}:{:05.2f} is successful !".format(int(hours),int(minutes),seconds))