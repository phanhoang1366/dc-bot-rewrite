import sqlite3

database = "database.db"

def insert_remind(server, channel, message, author, time):
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        insert_with_param = """INSERT INTO REMINDME
                              (ServerID, ChannelID, MessageID, AuthorID, UnixRemindTimestamp) 
                               VALUES 
                              (?, ?, ?, ?, ?)"""
        data = (server, channel, message, author, time)
        cursor.execute(insert_with_param, data)
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert variable", error)
        raise Exception
        
def delete_remind(time):
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        sql_update_query = """DELETE from REMINDME where UnixRemindTimestamp = ?"""
        cursor.execute(sql_update_query, (time,))
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete record", error)
        raise Exception
        
def insert_warn(author, warned, timestamp, reason):
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        insert_with_param = """INSERT INTO WARN
                              (AuthorID, WarnedID, Timestamp, Reason) 
                               VALUES 
                              (?, ?, ?, ?)"""
        
        data = (author, warned, timestamp, reason)
        cursor.execute(insert_with_param, data)
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert variable", error)
        raise Exception
        
def delete_warn(caseid):
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        sql_update_query = """DELETE from WARN where CaseID = ?"""
        cursor.execute(sql_update_query, (caseid,))
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete record", error)
        raise Exception