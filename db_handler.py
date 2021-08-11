import mysql.connector
import hashlib
import uuid

from account import Account
from validator import error_window

__db_server = '52.50.23.197'
__db_port = '3306'
__db_username = 'Felipe_2019405'
__db_password = '2019405'
__database = 'Felipe_2019405'

# returns connection
def __start_connection():
    try:
        conn = mysql.connector.connect(user=__db_username, password=__db_password, host=__db_server, port=__db_port, database=__database)
    except mysql.connector.Error:
        error_window('Connection error', 'Please check your connection and try again.')
        return None
    return conn

# base for any SELECT queries
def __select_query(select_rows, select_table, args=''):
    results = []
    query = 'SELECT ' + select_rows + ' FROM ' + select_table
    if args != '': query += ' ' + args
    query += ';'
    conn = __start_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except mysql.connector.Error as error:
        conn.rollback()
    conn.close()
    return results

# base for any INSERT queries
def __insert_query(insert_table, insert_array, conn=None):
    result = False
    if conn is None: conn = __start_connection()
    cursor = conn.cursor()
    query = 'INSERT INTO ' + insert_table + ' VALUES '
    for i, values in enumerate(insert_array):
        query += '(' + values + ')'
        if i < len(insert_array) - 1:
            query += ', '
    query += ';'
    try:
        cursor.execute(query)
        conn.commit()
        result = True
    except mysql.connector.Error as error:
        conn.rollback()
        result = False
        error_window('Error ' + str(error.errno), 'SQL error.')
    conn.close()
    return result

# base for any UPDATE queries
def __update_query(update_table, update_columns, args):
    query = 'UPDATE ' + update_table + ' SET ' + update_columns + ' ' + args + ';'
    conn = __start_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except mysql.connector.Error as error:
        conn.rollback()
        error_window('Error ' + error.errno, error.msg)
    conn.close()

# base for any DELETE queries
def __delete_query(delete_table, args, conn=None):
    query = 'DELETE FROM ' + delete_table + ' ' + args
    if conn is None: conn = __start_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except mysql.connector.Error as error:
        conn.rollback()
        error_window('Error ' + error.errno, error.msg)
    conn.close()

# returns salt
def __create_salt():
    return uuid.uuid4().hex

# returns hashed password based on password and salt
def __get_hashed_password(plain_text_password, salt):
    salt = salt.encode('utf-8')
    plain_text_password = plain_text_password.encode('utf-8')
    return hashlib.sha256(plain_text_password + salt).hexdigest()

# checks inserted password and salt hashed password against an already hashed password
def check_password(salt, password, plain_text_password):
    return __get_hashed_password(plain_text_password, salt) == password

# creates new account
def create_account(name, surname, email, password, country, language, category):
    salt = __create_salt()
    hashed_password = __get_hashed_password(password, salt)
    __insert_query('newsfeed_accounts(name, surname, email, password, salt, country, language, category)', ['\"' + name + '\", \"' + surname + '\", \"' + email + '\", \"' + hashed_password + '\", \"' + salt + '\", \"' + country + '\", \"' + language + '\", \"' + category + '\"'])

# returns account if login information is correct, None otherwise
def get_account(email, password):
    acc = __select_query('*', 'newsfeed_accounts', 'WHERE email=\"' + email + '\"')[0]
    plain_text_password = acc[4]
    salt = acc[5]
    acc = Account(acc[1] + ' ' + acc[2], acc[0], acc[3], [], {'country': acc[6], 'language': acc[7], 'category': acc[8]})

    if not check_password(salt, plain_text_password, password):
        return None

    faves = __select_query('article', 'news_articles', 'WHERE account_id=' + str(acc.get_id()))
    if faves is not None:
        for fav in faves:
            acc.add_favourite(fav[0])
    return acc

# adds a favourite article to an account
def add_favourite(account: Account, article):
    conn = __start_connection()
    __insert_query('news_articles(account_id, article)', [str(account.get_id()) + ', \"' + conn.converter.escape(str(article)) + '\"'], conn=conn)

# deletes a favourite article from an account
def remove_favourite(account: Account, article):
    conn = __start_connection()
    __delete_query('news_articles', 'WHERE account_id=' + str(account.get_id()) + ' AND article=\"' + conn.converter.escape(str(article)) + '\"', conn=conn)

# updates account's settings on database
def update_settings(account: Account, settings):
    __update_query('newsfeed_accounts', 'country=\"' + settings['country'] + '\", language=\"' + settings['language'] + '\", category=\"' + settings['category'] + '\"', 'WHERE id=' + str(account.get_id()))

# returns a mysql.connector escaped string
def escape_string(string):
    conn = __start_connection()
    s = conn.converter.escape(string)
    conn.close()
    return s
