from random import choice

import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, bool_compare_box,
                            bool_update_box, date_time_box,
                            date_time_compare_box, default_or_value,
                            groupby_box, limitby_box, non_empty_button,
                            non_empty_dataframe, number_compare_box,
                            number_update_box, orderby_box, populate_elements,
                            text_compare_box)
from app.queries import QUERY_TYPE, query_accounts, query_servers
from app.utils import get_nanoid, time_now


def player_insert(db, query, table, fields, populate, append):
    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    server_ids = list(set(query_servers(db)))
    server = choice(server_ids)

    if len(server_ids) < 1:
        st.write('Не хватает типов предметов')
        return

    query = query.into(table)

    account_id = default_or_value(
        'account_id' in options,
        'account_' + get_nanoid(12),
        st.text_input,
        {
            'label': 'ID аккаунта',
            'max_chars': 20
        }
    )

    server_id = default_or_value(
        'server_id' in options,
        server,
        st.selectbox,
        {
            'label': 'ID сервера',
            'options': server_ids
        }
    )

    register_stamp = default_or_value(
        'register_stamp' in options,
        time_now(),
        date_time_box,
        {
            'label': 'регистрации'
        }
    )

    login_stamp = default_or_value(
        'login_stamp' in options,
        time_now(),
        date_time_box,
        {
            'label': 'логина'
        }
    )

    online_status = default_or_value(
        'online_status' in options,
        'DEFAULT',
        st.checkbox,
        {
            'label': 'Online'
        }
    )

    account_level = default_or_value(
        'account_level' in options,
        'DEFAULT',
        st.number_input,
        {
            'label': 'Уровень',
            'value': 1,
            'min_value': 1,
            'step': 1
        }
    )

    blank()

    non_empty_button(
        db,
        query.insert(
            account_id,
            server_id,
            register_stamp,
            login_stamp,
            online_status,
            account_level
        ),
        'Добавить'
    )


def player_select(db, query, table, fields, populate, append):
    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    query = query.from_(table).select(
        *options if len(options) > 0 else '*'
    )

    if st.checkbox('Уникальные'):
        query = query.distinct()

    blank()

    if st.checkbox('Критерии'):
        conditions = st.multiselect(
            label='Критерии',
            options=fields,
            default=None,
            label_visibility='collapsed'
        )

        query = populate_elements(query, conditions, populate)

    blank()

    if st.checkbox('Группировка'):
        query = groupby_box(query, fields)

    blank()

    if st.checkbox('Порядок'):
        query = orderby_box(query, fields)

    blank()

    if st.checkbox('Ограничить'):
        query = limitby_box(query)

    blank()

    non_empty_dataframe(db, query)


def player_update(db, query, table, fields, populate, append):
    conditions = st.multiselect(
        label='Критерии',
        options=fields,
        default=None
    )

    query = query.update(table)

    query = populate_elements(query, conditions, populate)

    blank()

    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    values = append_elements(options, append)

    blank()

    for value in values:
        query = query.set(*value)

    non_empty_button(db, query, 'Обновить')


def player_delete(db, query, table, fields, populate, append):
    conditions = st.multiselect(
        label='Критерии',
        options=fields,
        default=None
    )

    query = query.from_(table).delete()

    query = populate_elements(query, conditions, populate)

    blank()

    non_empty_button(db, query, 'Удалить')


QUERIES = {
    'INSERT': player_insert,
    'SELECT': player_select,
    'UPDATE': player_update,
    'DELETE': player_delete,
}


def tables_player(db):
    table = Table('Player')
    query = PostgreSQLQuery()

    fields = [
        'account_id',
        'server_id',
        'register_stamp',
        'login_stamp',
        'online_status',
        'account_level'
    ]

    populate = {
        'account_id': (
            text_compare_box,
            {
                'label': 'ID аккаунта',
                'compared': table.account_id,
                'options': query_accounts(db)
            }
        ),
        'online_status': (
            bool_compare_box,
            {
                'label': 'Online',
                'compared': table.online_status
            }
        ),
        'server_id': (
            number_compare_box,
            {
                'label': 'ID сервера',
                'compared': table.server_id
            }
        ),
        'account_level': (
            number_compare_box,
            {
                'label': 'Уровень',
                'compared': table.account_level
            }
        ),
        'register_stamp': (
            date_time_compare_box,
            {
                'label': 'регистрации',
                'compared': table.register_stamp
            }
        ),
        'login_stamp': (
            date_time_compare_box,
            {
                'label': 'логина',
                'compared': table.login_stamp
            }
        )
    }

    append = {
        'account_id': (
            table.account_id,
            st.text_input,
            {
                'label': 'ID аккаунта ',
                'max_chars': 20
            }
        ),
        'online_status': (
            table.online_status,
            bool_update_box,
            {
                'label': 'Online '
            }
        ),
        'server_id': (
            table.server_id,
            number_update_box,
            {
                'label': 'ID сервера '
            }
        ),
        'account_level': (
            table.account_level,
            number_update_box,
            {
                'label': 'Уровень '
            }
        ),
        'register_stamp': (
            table.register_stamp,
            date_time_box,
            {
                'label': 'регистрации '
            }
        ),
        'login_stamp': (
            table.login_stamp,
            date_time_box,
            {
                'label': 'логина '
            }
        )
    }

    query_type = st.radio(
        label='Тип',
        label_visibility='collapsed',
        options=QUERY_TYPE,
        horizontal=True
    )

    blank()

    QUERIES.get(query_type)(db, query, table, fields, populate, append)
