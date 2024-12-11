import os
import time
import threading
from flask import Flask, render_template, jsonify, make_response, request, session
from intelligent_customer_service import customer_system
from point_out_function import point_out_keyword
from TEJ_text import TEJ_3D_text
from chat_history import connect_sql

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
reset_topics = True

def execute_time(start_time, end_time, string):
    execution_time = end_time - start_time
    hours, rem = divmod(execution_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("{}耗時：{:0>2}時{:0>2}分{:05.2f}秒".format(string, int(hours), int(minutes), seconds))

def SaveTopicsPosts(msg, response):
    global reset_topics, topic_id
    # member_id = request.values['member_id']
    member_id = 1
    if reset_topics:
        if msg == "請給我一些推薦的主題以及該主題下的幾篇文章":
            classes_response = [class_['class'] for class_ in response['messages']]
            title = f"推薦{str(classes_response)}以上三類的文章"
            chat_memory = connect_sql()
            chat_memory.topic_create(member_id, title)
        else:
            title = customer_system(str(msg).upper()).AI_topic_create(response=response)
            chat_memory = connect_sql()
            chat_memory.topic_create(member_id, title)

        chat_memory = connect_sql()
        particular_topic_result = chat_memory.topic_particular(member_id, title)
        topic_id = particular_topic_result['topic_id']

    chat_memory = connect_sql()
    chat_memory.posts_create(member_id, topic_id, msg.strip())
    chat_memory = connect_sql()
    chat_memory.posts_create(member_id, topic_id, str(response['messages']))
    reset_topics = False

@app.route("/")
def index():
    response = make_response(render_template('chat.html'))
    return response

# chat api connect to intellegent_customer_service.py 
@app.route("/get", methods=["POST"])
def chat():
    start_time = time.time()
    msg = request.form["msg"]
    response, keyword = customer_system(str(msg).upper()).system()
    session['keyword'] = keyword
    print(response)
    threading.Thread(target=SaveTopicsPosts, args=(msg, response)).start()
    end_time = time.time()
    execute_time(start_time, end_time, "回答")
    # return jsonify(response)
    return response['messages']

# get sidebar recommend api
@app.route('/recommend', methods=['POST'])
def get_endpoint():
    try:
        keyword = session.get('keyword')
    except:
        keyword = "公司介紹"
    print(keyword)
    response = {}
    out = []
    try:
        out = point_out_keyword(keyword)
    except:
        if out == None:
            return jsonify(response)

    if len(out) < 5:
        for i in range(1, 6):
            if i-1 >= len(out):
                out.append('')
                response[f'recommend_{i}'] = out[i-1]
            else:
                response[f'recommend_{i}'] = out[i-1]
    else:
        for i in range(1, 6):
            response[f'recommend_{i}'] = out[i-1]
    
    print(response)
    return jsonify(response)

@app.route('/update', methods=['POST'])
def get_topic_update():
    new_topic = request.values['new_topic']
    origin_topic = request.values['origin_topic']
    member_id = request.values['member_id']
    chat_memory = connect_sql()
    particular_topic_result = chat_memory.topic_particular(member_id, origin_topic)
    topic_id = particular_topic_result['topic_id']
    chat_memory = connect_sql()
    update_data = chat_memory.topic_update(member_id, topic_id, new_topic)
    # print(jsonify(update_data))
    return jsonify(update_data)

if __name__ == '__main__':
    TEJ_3D_text()
    app.run(debug=True)
