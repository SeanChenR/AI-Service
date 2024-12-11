import time
import random
from ffm_model import tej_ai_service
from qdrant2answers import get_answers, get_article, overwrite_frequency
from qdrant_client import QdrantClient
from langchain_core.prompts import PromptTemplate
from default_response import default_response

client = QdrantClient("localhost", port=6333)
collection_name = "TEJ_QA_Final"

class customer_system():

    def __init__(self, text):
        self.text = text
        self.assistant_message = '\n\n若您對使用TEJ有其他問題或需要進一步說明，請至TEJ台灣經濟新報官方網站https://www.tejwin.com/點選「聯絡我們」，我們非常樂意為您解答。'

    # search answers match in qdrant database
    def search(self):
        
        qa = get_answers(self.text)['qdrant_search_result']
        qa_unique = qa.drop_duplicates(subset=['question'])
        Pass_LLM = qa_unique['Pass_LLM'].iloc[0]
        replace_question = qa_unique['replace_question'].iloc[0]
        score = qa_unique['score'].iloc[0]

        try:
            qa_dict = {'question' : [quq for quq in qa_unique['question']], 
                        'answer' : [qua for qua in qa_unique['answer']]}
            keyword = [quk for quk in qa_unique['keyword']][0]
        except:
            qa_dict = {'question' : '', 'answer' : '', 'score' : ''}
            keyword = "公司介紹"
            
        return qa_dict, self.text, keyword, Pass_LLM, replace_question, score

    # tide the dataset in qdrant database
    def tide_dataset(self, qa_dict):
        test_qa, q_list = "", []
        for qq, aa in zip(qa_dict['question'], qa_dict['answer']):
            if len(qq) == 0:
                test_qa = ""
            else:
                rag_qa = f"Q:{qq} \nA:{aa}\n"
                test_qa += rag_qa
                q_list.append(qq)
        return test_qa, q_list

    # Combining prompt and answer for FFM-Llama-chat
    # Get the RAG result and count frequency for each question. Overwrite payload, finally.
    def chat(self, test_qa, q_list, text, replace_question, score):
        if len(q_list) == 0:
            pass
        else:
            for qq in q_list:
                overwrite_frequency(qq, collection_name, client)

        # add customer service official response for user to contact with TEJ
        # system prompt for basic rules
        # short answer only 
        # use tranditional chinese only
        prompt_template = """你是一位樂於助人的台灣經濟新報(TEJ)客服人員，請務必盡可能回答有幫助的答案。你的答案不應包含任何有害、不道德、種族主義、性別歧視、危險或非法內容。
                            請僅根據<context>中的Q&A回答問題，不要回答多餘的東西，也不要用你的想法加油添醋，也不要任何歡迎詞或問候語。
                            <context>{testqa}</context>
                            No prefix
                            使用者問題：{question}"""
        system_prompt = PromptTemplate(input_variables=["testqa", "question"], template=prompt_template)
        chain = system_prompt | tej_ai_service
        if replace_question:
            if score < 0.3:
                print("default_response", score)
                return_text = random.choice(default_response)
            else:
                print("replace_question", score)
                question = q_list[0]
                response = chain.invoke({"testqa": test_qa, "question": question})
                return_text = response.content + self.assistant_message
        else:
            question = text.strip()
            response = chain.invoke({"testqa": test_qa, "question": question})
            return_text = response.content + self.assistant_message
        # If there is no data in the RAG result, the following message is displayed
        # else:
        #     return_text = '我目前還在學習中，請您提供進一步說明或相關資訊給我們，或參考左側精選提問，謝謝！' + self.assistant_message
        
        return {'messages': return_text}

    # 如果按下推薦文章的那個 block，會利用 get_article 取得文章；其餘會透過 LLM
    def system(self):
        if self.text == "請給我一些推薦的主題以及該主題下的幾篇文章":
            article, keyword = get_article()
            return article, keyword
        else:
            qa, text, keyword, Pass_LLM, replace_question, score = self.search()
            if not Pass_LLM:
                return {'messages': qa['answer'][0] + self.assistant_message}, keyword
            else:
                test_qa ,q_list = self.tide_dataset(qa)
                return self.chat(test_qa, q_list, text, replace_question, score), keyword

    def AI_topic_create(self, response):
        prompt_template = "Please think of a topic based on {query} and {response}. The word count is limited to 10 words.\
                            Please make sure the topic content is relevant. If any offensive words appear, please ignore them and do not display them in the topic."
        system_prompt = PromptTemplate(input_variables=["query", "response"], template=prompt_template)
        chain = system_prompt | tej_ai_service
        title = chain.invoke({"query": self.text, "response": response}).content
        return title

if __name__ == '__main__':

    start_time = time.time()

    response, keyword = customer_system('請給我一些推薦的主題以及該主題下的幾篇文章').system()
    response, keyword = customer_system('TCRI是什麼?').system()
    print(response, '\n關鍵字分類：', keyword)

    end_time = time.time()

    execution_time = end_time - start_time

    print('execute time:', str(float(end_time-start_time))+' s')

