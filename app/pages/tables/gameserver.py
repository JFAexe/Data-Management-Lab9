import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, bool_compare_box,
                            bool_update_box, default_or_value, groupby_box,
                            limitby_box, non_empty_button, non_empty_dataframe,
                            number_compare_box, number_update_box, orderby_box,
                            populate_elements)
from app.queries import QUERY_TYPE


def gameserver_insert(db, query, table, fields, populate, append):
    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    query = query.into(table)

    server_id = default_or_value(
        'server_id' in options,
        'DEFAULT',
        st.number_input,
        {
            'label': 'ID сервера',
            'value': 1,
            'min_value': 1,
            'step': 1
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

    blank()

    non_empty_button(
        db,
        query.insert(
            server_id,
            online_status
        ),
        'Добавить'
    )


def gameserver_select(db, query, table, fields, populate, append):
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


def gameserver_update(db, query, table, fields, populate, append):
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


def gameserver_delete(db, query, table, fields, populate, append):
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
    'INSERT': gameserver_insert,
    'SELECT': gameserver_select,
    'UPDATE': gameserver_update,
    'DELETE': gameserver_delete,
}


def tables_gameserver(db):
    table = Table('GameServer')
    query = PostgreSQLQuery()

    fields = [
        'server_id',
        'online_status'
    ]

    populate = {
        'server_id': (
            number_compare_box,
            {
                'label': 'ID',
                'compared': table.server_id
            }
        ),
        'online_status': (
            bool_compare_box,
            {
                'label': 'Online',
                'compared': table.online_status
            }
        )
    }

    append = {
        'server_id': (
            table.server_id,
            number_update_box,
            {
                'label': 'ID '
            }
        ),
        'online_status': (
            table.online_status,
            bool_update_box,
            {
                'label': 'Online '
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
