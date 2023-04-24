from copy import deepcopy
from random import choice

import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, bool_compare_box,
                            bool_update_box, date_time_box,
                            date_time_compare_box, default_or_value,
                            groupby_box, limitby_box, non_empty_button,
                            non_empty_dataframe, number_compare_box,
                            number_update_box, orderby_box, populate_elements,
                            text_compare_box, warning)
from app.queries import (QUERY_TYPE, query_accounts, query_purchases,
                         query_servers)
from app.utils import time_now


def purchase_insert(db, query, table, fields, populate, append):
    if not warning():
        blank()
    else:
        return

    fields_noids = deepcopy(fields)
    fields_noids.remove('purchase_id')

    options = st.multiselect(
        label='Поля',
        options=fields_noids,
        default=None
    )

    server_ids = list(set(query_servers(db)))
    server = choice(server_ids)

    if len(server_ids) < 1:
        st.write('Не хватает типов предметов')
        return

    query = query.into(table)

    server_id = default_or_value(
        'server_id' in options,
        server,
        st.selectbox,
        {
            'label': 'ID Сервера',
            'options': server_ids
        }
    )

    accounts = query_accounts(db, server_id)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    time_stamp = default_or_value(
        'time_stamp' in options,
        time_now(),
        date_time_box,
        {
            'label': 'покупки'
        }
    )

    confirmation_status = default_or_value(
        'confirmation_status' in options,
        'DEFAULT',
        st.checkbox,
        {
            'label': 'Подтвержден'
        }
    )

    pending = default_or_value(
        'pending' in options,
        'DEFAULT',
        st.checkbox,
        {
            'label': 'В обработке'
        }
    )

    receiver_id = default_or_value(
        'receiver_id' in options,
        choice(accounts),
        st.selectbox,
        {
            'label': 'ID получателя',
            'options': accounts
        }
    )

    blank()

    non_empty_button(
        db,
        query.insert(
            'DEFAULT',
            server_id,
            time_stamp,
            confirmation_status,
            pending,
            receiver_id
        ),
        'Добавить'
    )


def purchase_select(db, query, table, fields, populate, append):
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


def purchase_update(db, query, table, fields, populate, append):
    if not warning():
        blank()
    else:
        return

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


def purchase_delete(db, query, table, fields, populate, append):
    if not warning():
        blank()
    else:
        return

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
    'INSERT': purchase_insert,
    'SELECT': purchase_select,
    'UPDATE': purchase_update,
    'DELETE': purchase_delete,
}


def tables_purchase(db):
    table = Table('Purchase')
    query = PostgreSQLQuery()

    fields = [
        'purchase_id',
        'server_id',
        'time_stamp',
        'confirmation_status',
        'pending',
        'receiver_id'
    ]

    populate = {
        'purchase_id': (
            text_compare_box,
            {
                'label': 'ID покупки',
                'compared': table.purchase_id,
                'options': query_purchases(db),
                'uid': True
            }
        ),
        'server_id': (
            number_compare_box,
            {
                'label': 'ID сервера',
                'compared': table.server_id
            }
        ),
        'time_stamp': (
            date_time_compare_box,
            {
                'label': 'обмена',
                'compared': table.time_stamp
            }
        ),
        'confirmation_status': (
            bool_compare_box,
            {
                'label': 'Подтвержден',
                'compared': table.confirmation_status
            }
        ),
        'pending': (
            bool_compare_box,
            {
                'label': 'В обработке',
                'compared': table.pending
            }
        ),
        'receiver_id': (
            text_compare_box,
            {
                'label': 'ID получателя',
                'compared': table.receiver_id,
                'options': query_accounts(db)
            }
        )
    }

    append = {
        'purchase_id': (
            table.purchase_id,
            st.selectbox,
            {
                'label': 'ID покупки ',
                'options': query_purchases(db)
            }
        ),
        'server_id': (
            table.server_id,
            number_update_box,
            {
                'label': 'ID сервера'
            }
        ),
        'time_stamp': (
            table.time_stamp,
            date_time_box,
            {
                'label': 'совершения '
            }
        ),
        'confirmation_status': (
            table.online_status,
            bool_update_box,
            {
                'label': 'Подтвержден '
            }
        ),
        'pending': (
            table.pending,
            bool_update_box,
            {
                'label': 'В обработке '
            }
        ),
        'receiver_id': (
            table.receiver_id,
            st.selectbox,
            {
                'label': 'ID получателя ',
                'options': query_accounts(db)
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
