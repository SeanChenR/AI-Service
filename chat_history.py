import pymysql

class AI_Service_Memory:
    def __init__(self, host, user, password, database):
        self.connection = pymysql.connect(host=host,
                                            user=user,
                                            password=password,
                                            database=database,
                                            cursorclass=pymysql.cursors.DictCursor)

    def members_register(self, username:str, email:str, password:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO `Members` (`username`, `email`, `password`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (username, email, password))

                self.connection.commit()
                print("Register Successful!")
            except:
                print(f"Duplicate entry {username} for key 'username' or {email} for key 'email'")

    def members_login(self, email:str, password:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "SELECT * FROM `Members` WHERE `email`=%s AND `password`=%s"
                    cursor.execute(sql, (email, password))
                    result = cursor.fetchone()
                    if result:
                        print("Login successful!")
                        return result
                    else:
                        print("Email or Password is not correct!")
            except:
                print("Email or Password is not correct!")

    def topic_create(self, member_id:int, title:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO `Topics` (`member_id`, `title`) VALUES (%s, %s)"
                    cursor.execute(sql, (member_id, title))

                self.connection.commit()
                # time.sleep(2)
                # with self.connection.cursor() as cursor:
                #     sql = "SELECT * FROM `Topics` WHERE `member_id`=%s ORDER BY `created_at` ASC"
                #     cursor.execute(sql, (member_id))
            except Exception as e:
                print(f"Topics create error: {e}")
    
    def topic_search(self, member_id:int):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "SELECT * FROM `Topics` WHERE `member_id`=%s ORDER BY `created_at` ASC"
                    cursor.execute(sql, (member_id))
                    result = cursor.fetchall()
                    return result
            except Exception as e:
                print(f"Topics search error: {e}")

    def topic_particular(self, member_id:int, title:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "SELECT * FROM `Topics` WHERE `member_id`=%s AND `title`=%s ORDER BY `created_at` ASC"
                    cursor.execute(sql, (member_id, title))
                    result = cursor.fetchall()
                    return result[0] if result else None
            except Exception as e:
                print(f"Particular topics search error: {e}")

    def topic_delete(self, member_id:int, title:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "DELETE FROM `Topics` WHERE `member_id`=%s AND `title`=%s"
                    cursor.execute(sql, (member_id, title))
                    result = cursor.fetchall()
                    return result[0] if result else None
            except Exception as e:
                print(f"Delete topics error: {e}")

    def topic_update(self, member_id: int, topic_id: int, new_title: str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "UPDATE `Topics` SET `title`=%s WHERE `member_id`=%s AND `topic_id`=%s"
                    cursor.execute(sql, (new_title, member_id, topic_id))
                    self.connection.commit()
                    return {"messages": "Update successful!"}
            except Exception as e:
                print(f"Update topics error: {e}")
                return None

    def posts_create(self, member_id:int, topic_id:int, content:str):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) AS count_posts FROM `Posts` WHERE `topic_id` = %s", (topic_id,))
                    result = cursor.fetchone()
                    count_posts = result['count_posts']

                    if (count_posts % 2) == 0:
                        # Create a new record
                        sql = "INSERT INTO `Posts` (`topic_id`, `member_id`, `content`) VALUES (%s, %s, %s)"
                        cursor.execute(sql, (topic_id, member_id, content))
                    else:
                        get_parent_post_id = "SELECT * FROM `Posts` WHERE `member_id`=%s AND `topic_id`=%s ORDER BY `created_at` DESC"
                        cursor.execute(get_parent_post_id, (member_id, topic_id))
                        parent_post_id = cursor.fetchone()['post_id']
                        sql = "INSERT INTO `Posts` (`topic_id`, `member_id`, `content`, `parent_post_id`) VALUES (%s, %s, %s, %s)"
                        cursor.execute(sql, (topic_id, member_id, content, parent_post_id))

                self.connection.commit()
                # time.sleep(2)
                # with self.connection.cursor() as cursor:
                #     sql = "SELECT * FROM `Posts` WHERE `member_id`=%s AND `topic_id`=%s ORDER BY `created_at` ASC"
                #     cursor.execute(sql, (member_id, topic_id))
                #     result = cursor.fetchall()
            except Exception as e:
                print(f"Posts create error: {e}")

    def posts_search(self, member_id: int, topic_id: int):
        with self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = "SELECT * FROM `Posts` WHERE `member_id`=%s AND `topic_id`=%s ORDER BY `created_at` ASC"
                    cursor.execute(sql, (member_id, topic_id))
                    result = cursor.fetchall()
                    return result
            except Exception as e:
                print(f"Posts search error: {e}")

def connect_sql():
    chat_memory = AI_Service_Memory(
        host="localhost",
        user="root",
        password="123456",
        database="TEJ_AI_Service_Chat_Memory"
    )
    return chat_memory

# chat_memory.members_register('sean', 'sean@tej.com.tw', '123456')
# time.sleep(1)
# member_info = chat_memory.members_login('sean@tej.com.tw', '123456')
# if member_info:
#     member_id = member_info['member_id']
# else:
#     print('Login failed')

# time.sleep(1)
# chat_memory.topic_create(member_id, "詢問TEJ的相關資訊")
# chat_memory.topic_search(member_id)

# particular_topic_result = chat_memory.topic_particular(member_id, "詢問TEJ的相關資訊")
# topic_id = particular_topic_result['topic_id']
# member_id = particular_topic_result['member_id']

# time.sleep(1)
# chat_memory.posts_create(member_id, topic_id, "TEJ是什麼？")
# time.sleep(0.5)
# chat_memory.posts_create(member_id, topic_id, "TEJ 為台灣本土第一大財經資訊公司，成立於 1990 年，專門提供金融市場基本分析所需資訊，以及信用風險、法遵科技、資產評價、量化分析及 ESG 等解決方案及顧問服務。")
# time.sleep(0.5)
# chat_memory.posts_create(member_id, topic_id, "TQuant LAB 量化分析資料集是什麼？")
# time.sleep(0.5)
# chat_memory.posts_create(member_id, topic_id, "主要提供台股在過去每個時點的資料，避免使用到未來資料進行回測，可有效避免前視偏誤問題。")

# time.sleep(1)
# chat_memory.posts_search(member_id, topic_id)