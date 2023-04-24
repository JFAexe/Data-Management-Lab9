from copy import deepcopy

import streamlit as st

from app.components import display_sql
from app.queries import query_accounts, query_items, query_servers

QUERY_PLAYER_BY_ID = '''
SELECT account_id,
    account_level
FROM Player
WHERE account_id = '\
'''


def construct_call(func, players, amount, proc=True):
    call = 'CALL ' if proc else 'SELECT '
    player = ',\n    '.join(['\'' + str(p).strip() + '\'' for p in players])

    call += func\
        + '(\n    '\
        + player

    if proc:
        call += ',\n    CAST('\
            + str(amount)\
            + ' AS INT2)\n);'
    else:
        call += '\n)'\
            + ' FROM GENERATE_SERIES(1, '\
            + str(amount)\
            + ');'

    return call


def _procedure_account_level(db, procedure_name):
    accounts = query_accounts(db)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    player = st.selectbox(
        label='ID аккаунта',
        options=accounts
    )

    amount = st.slider(
        label='Количество',
        min_value=1,
        max_value=255,
        value=1
    )

    query = construct_call(procedure_name, [player], amount)
    display_sql(query)

    def call():
        db.call_proc(query)

    if st.button(
        label='Выполнить процедуру',
        on_click=call
    ) or True:
        subquery = QUERY_PLAYER_BY_ID + str(player) + '\';'
        display_sql(subquery)

        st.json(db.run_query_uncached(subquery)[0])


def procedure_increase_account_level(db):
    return _procedure_account_level(db, 'increase_account_level')


def procedure_decrease_account_level(db):
    return _procedure_account_level(db, 'decrease_account_level')


def procedure_make_random_trade(db):
    server_ids = list(set(query_servers(db)))

    if len(server_ids) < 1:
        st.write('Не хватает типов предметов')
        return

    server = st.selectbox(
        label='ID сервера',
        options=server_ids
    )

    accounts = query_accounts(db, server)

    if len(accounts) < 2:
        st.write('Не хватает игроков')
        return

    initiator = st.selectbox(
        label='ID инициатора',
        options=accounts
    )

    accounts_receiver = deepcopy(accounts)
    accounts_receiver.remove(initiator)

    receiver = st.selectbox(
        label='ID получателя',
        options=accounts_receiver
    )

    max_amount = len(query_items(db, initiator))

    if max_amount < 1:
        st.write('Не хватает предметов')
        return

    amount = st.slider(
        label='Количество',
        min_value=1,
        max_value=max_amount,
        value=1
    )

    query = construct_call('make_random_trade', [initiator, receiver], amount)
    display_sql(query)

    if st.button('Выполнить процедуру'):
        db.call_proc(query)


def procedure_make_random_purchase(db):
    accounts = query_accounts(db)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    player = st.selectbox(
        label='ID аккаунта',
        options=accounts
    )

    amount = st.slider(
        label='Количество',
        min_value=1,
        max_value=50,
        value=1
    )

    query = construct_call('make_random_purchase', [player], amount)
    display_sql(query)

    if st.button('Выполнить процедуру'):
        db.call_proc(query)


def function_give_random_item(db):
    accounts = query_accounts(db)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    player = st.selectbox(
        label='ID аккаунта',
        options=accounts
    )

    amount = st.slider(
        label='Количество',
        min_value=1,
        max_value=50,
        value=1
    )

    query = construct_call('give_random_item', [player], amount, False)
    display_sql(query)

    if st.button('Вызвать функцию'):
        st.dataframe(
            data=db.run_query_uncached(query),
            use_container_width=True
        )


PROCEDURES = {
    'Увеличить уровень': procedure_increase_account_level,
    'Уменьшить уровень': procedure_decrease_account_level,
    'Провести случайный обмен': procedure_make_random_trade,
    'Провести случайную покупку': procedure_make_random_purchase,
    'Выдать случайные предметы': function_give_random_item
}


def page_procedures():
    option = st.selectbox(
        label='Процедура',
        options=PROCEDURES.keys()
    )

    PROCEDURES.get(option)(st.session_state.db)
