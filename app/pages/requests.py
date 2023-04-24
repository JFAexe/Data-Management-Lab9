import streamlit as st

from app.components import display_query, display_query_formated, display_sql

QUERY_PLAYER_COUNT = '''
SELECT COUNT(*) AS player_count
FROM Player;
'''

QUERY_REGISTRED_LAST_WEEK = '''
SELECT COUNT(*) AS player_count
FROM Player
WHERE register_stamp >= NOW() - INTERVAL '1 WEEK';
'''

QUERY_SERVER_MOST_PLAYERS = '''
SELECT server_id,
    COUNT(*) AS player_count
FROM Player
GROUP BY server_id
ORDER BY player_count DESC
LIMIT 1;
'''

QUERY_MOST_TIME_LOGIN = '''
SELECT EXTRACT(HOUR FROM login_stamp) AS active_hour,
    COUNT(*) AS login_count
FROM Player
GROUP BY active_hour
ORDER BY login_count DESC
LIMIT 1;
'''

QUERY_TIME = '''
SELECT EXTRACT(HOUR FROM login_stamp) AS active_hour,
    COUNT(*) AS login_count
FROM Player
GROUP BY active_hour
ORDER BY login_count DESC;
'''

QUERY_SERVER_MOST_TRADES = '''
SELECT Trade.server_id,
    COUNT(*) AS trade_count
FROM ItemTransfer
JOIN Trade ON ItemTransfer.trade_id = Trade.trade_id
WHERE ItemTransfer.purchase_id IS NULL
    AND ItemTransfer.initiator_id IS NOT NULL
GROUP BY Trade.server_id
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_SERVER_MOST_PURCHASES = '''
SELECT Purchase.server_id,
    COUNT(*) AS purchase_count
FROM ItemTransfer
JOIN Purchase ON ItemTransfer.purchase_id = Purchase.purchase_id
WHERE ItemTransfer.trade_id IS NULL
    AND ItemTransfer.initiator_id IS NULL
GROUP BY Purchase.server_id
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_PLAYER_MOST_TRADES = '''
SELECT initiator_id AS account_id,
    COUNT(*) AS trade_count
FROM Trade
GROUP BY initiator_id
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_PLAYER_MOST_PURCHASES = '''
SELECT receiver_id AS account_id,
    COUNT(*) AS purchase_count
FROM Purchase
GROUP BY receiver_id
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_PLAYER_MOST_ITEMS = '''
SELECT player_id AS account_id,
    COUNT(*) AS item_count
FROM Item
GROUP BY player_id
ORDER BY item_count DESC
LIMIT 1;
'''

QUERY_PLAYER_MOST_CURRENCY = '''
SELECT player_id AS account_id,
    SUM(Item.price) AS total_price
FROM Item
GROUP BY player_id
ORDER BY total_price DESC
LIMIT 1;
'''

QUERY_ITEM_MOST_TRADES = '''
SELECT ItemType.type_name,
    COUNT(*) AS trade_count
FROM Trade
JOIN ItemTransfer ON Trade.trade_id = ItemTransfer.trade_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.purchase_id IS NULL
    AND ItemTransfer.initiator_id IS NOT NULL
GROUP BY ItemType.type_name
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_ITEM_MOST_PURCHASES = '''
SELECT ItemType.type_name,
    COUNT(*) AS purchase_count
FROM Purchase
JOIN ItemTransfer ON Purchase.purchase_id = ItemTransfer.purchase_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.trade_id IS NULL
    AND ItemTransfer.initiator_id IS NULL
GROUP BY ItemType.type_name
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_ITEM_EXPIRE_WEEK = '''
SELECT item_id,
    player_id AS account_id,
    expiration_date
FROM Item
WHERE expiration_date >= NOW()
    AND expiration_date <= NOW() + INTERVAL '1 WEEK';
'''

QUERY_ITEM_TIME_TRADES = '''
SELECT EXTRACT(HOUR FROM time_stamp) AS active_hour,
    COUNT(*) AS trade_count
FROM Trade
GROUP BY active_hour
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_ITEM_TIME_PURCHASES = '''
SELECT EXTRACT(HOUR FROM time_stamp) AS active_hour,
    COUNT(*) AS purchase_count
FROM Purchase
GROUP BY active_hour
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_ITEM_AMOUNT_TRADES = '''
SELECT AVG(counter) AS item_count
FROM (
    SELECT COUNT(*) AS counter
    FROM Trade
    JOIN ItemTransfer ON Trade.trade_id = ItemTransfer.trade_id
    WHERE ItemTransfer.purchase_id IS NULL
        AND ItemTransfer.initiator_id IS NOT NULL
) sub_query;
'''

QUERY_ITEM_AMOUNT_PURCHASES = '''
SELECT AVG(counter) AS item_count
FROM (
    SELECT COUNT(*) AS counter
    FROM Purchase
    JOIN ItemTransfer ON Purchase.purchase_id = ItemTransfer.purchase_id
    WHERE ItemTransfer.trade_id IS NULL
        AND ItemTransfer.initiator_id IS NULL
) sub_query;
'''

QUERY_ITEM_LEVEL_TRADES = '''
SELECT ItemType.type_name,
    Item.minimum_level,
    COUNT(*) AS trade_count
FROM Trade
JOIN ItemTransfer ON Trade.trade_id = ItemTransfer.trade_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.purchase_id IS NULL
    AND ItemTransfer.initiator_id IS NOT NULL
GROUP BY ItemType.type_name, Item.minimum_level
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_ITEM_LEVEL_PURCHASES = '''
SELECT ItemType.type_name,
    Item.minimum_level,
    COUNT(*) AS purchase_count
FROM Purchase
JOIN ItemTransfer ON Purchase.purchase_id = ItemTransfer.purchase_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.trade_id IS NULL
    AND ItemTransfer.initiator_id IS NULL
GROUP BY ItemType.type_name, Item.minimum_level
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_ITEM_EXPIRE_TRADES = '''
SELECT ItemType.type_name,
    COUNT(*) AS trade_count
FROM Trade
JOIN ItemTransfer ON Trade.trade_id = ItemTransfer.trade_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.purchase_id IS NULL
    AND ItemTransfer.initiator_id IS NOT NULL
    AND Item.expiration_date IS NOT NULL
GROUP BY ItemType.type_name
ORDER BY trade_count DESC
LIMIT 1;
'''

QUERY_ITEM_EXPIRE_PURCHASES = '''
SELECT ItemType.type_name,
    COUNT(*) AS purchase_count
FROM Purchase
JOIN ItemTransfer ON Purchase.purchase_id = ItemTransfer.purchase_id
JOIN Item ON Item.item_id = ItemTransfer.item_id
JOIN ItemType ON Item.type_id = ItemType.type_id
WHERE ItemTransfer.trade_id IS NULL
    AND ItemTransfer.initiator_id IS NULL
    AND Item.expiration_date IS NOT NULL
GROUP BY ItemType.type_name
ORDER BY purchase_count DESC
LIMIT 1;
'''

QUERY_CONFIRMED_TRADES = '''
SELECT COUNT(*) AS confirmed_trades
FROM Trade
WHERE confirmation_status = true;
'''

QUERY_CONFIRMED_PURCHASES = '''
SELECT COUNT(*) AS confirmed_purchases
FROM Purchase
WHERE confirmation_status = true;
'''


def request_player_count(db):
    query = QUERY_PLAYER_COUNT
    display_sql(query)
    display_query(db, query)


def request_registrated_last_week(db):
    query = QUERY_REGISTRED_LAST_WEEK
    display_sql(query)
    display_query(db, query)


def request_most_players(db):
    query = QUERY_SERVER_MOST_PLAYERS
    display_sql(query)
    display_query(db, query)


def request_most_time_login(db):
    query = QUERY_MOST_TIME_LOGIN
    display_sql(query)
    display_query_formated(db, query, 'active_hour', int)


def request_time(db):
    query = QUERY_TIME
    display_sql(query)

    result = db.run_query(query)
    for i in result:
        i['active_hour'] = int(i.get('active_hour'))

    st.dataframe(
        data=result,
        use_container_width=True
    )


def request_server_most_actions(db):
    queries = {
        'Обменов': QUERY_SERVER_MOST_TRADES,
        'Покупок': QUERY_SERVER_MOST_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


def request_player_most_actions(db):
    queries = {
        'Обменивается': QUERY_PLAYER_MOST_TRADES,
        'Покупает': QUERY_PLAYER_MOST_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


def request_player_most_items(db):
    queries = {
        'Предметов': QUERY_PLAYER_MOST_ITEMS,
        'Валюты в предметах': QUERY_PLAYER_MOST_CURRENCY,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query_formated(db, query, 'total_price', int)


def request_item_most_actions(db):
    queries = {
        'Обменивают': QUERY_ITEM_MOST_TRADES,
        'Покупают': QUERY_ITEM_MOST_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


def request_item_expire_week(db):
    query = QUERY_ITEM_EXPIRE_WEEK
    display_sql(query)
    st.dataframe(
        data=db.run_query(query),
        use_container_width=True
    )


def request_item_time_actions(db):
    queries = {
        'Обменивают': QUERY_ITEM_TIME_TRADES,
        'Покупают': QUERY_ITEM_TIME_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query_formated(db, query, 'active_hour', int)


def request_amount_actions(db):
    queries = {
        'Обменивают': QUERY_ITEM_AMOUNT_TRADES,
        'Покупают': QUERY_ITEM_AMOUNT_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query_formated(db, query, 'item_count', float)


def request_item_level_actions(db):
    queries = {
        'Обменивают': QUERY_ITEM_LEVEL_TRADES,
        'Покупают': QUERY_ITEM_LEVEL_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


def request_item_expire_actions(db):
    queries = {
        'Обменивают': QUERY_ITEM_EXPIRE_TRADES,
        'Покупают': QUERY_ITEM_EXPIRE_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


def request_confirmed_actions(db):
    queries = {
        'Обменов': QUERY_CONFIRMED_TRADES,
        'Покупок': QUERY_CONFIRMED_PURCHASES,
    }

    option = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=queries.keys(),
        horizontal=True
    )

    query = queries.get(option)
    display_sql(query)
    display_query(db, query)


REQUESTS = {
    'Сколько игроков на данный момент?':
        request_player_count,
    'Сколько новых игроков зарегистрировались за последнюю неделю?':
        request_registrated_last_week,
    'На каком сервере наибольшее количество игроков?':
        request_most_players,
    'В какое время играют чаще всего?':
        request_most_time_login,
    'Активность по часам?':
        request_time,
    'На каком сервере больше всего ...?':
        request_server_most_actions,
    'Какой игрок больше всего ...?':
        request_player_most_actions,
    'Какой игрок имеет больше всего ...?':
        request_player_most_items,
    'Какие предметы ... чаще всего?':
        request_item_most_actions,
    'Какие предметы истекут на следующей неделе?':
        request_item_expire_week,
    'В какое время чаще всего ... предметы?':
        request_item_time_actions,
    'Какое количество предметов в среднем ...?':
        request_amount_actions,
    'Предметы какого минимального уровня ... больше всего?':
        request_item_level_actions,
    'Какие предметы с ограничением по времени ... чаще всего?':
        request_item_expire_actions,
    'Каково количество подтвержденных ...?':
        request_confirmed_actions,
}


def page_requests():
    option = st.selectbox(
        label='Запрос',
        options=REQUESTS.keys()
    )

    REQUESTS.get(option)(st.session_state.db)
