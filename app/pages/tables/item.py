from copy import deepcopy
from random import choice

import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, bool_compare_box,
                            bool_update_box, date_time_box,
                            date_time_compare_box, date_time_update_box,
                            default_or_value, groupby_box, limitby_box,
                            non_empty_button, non_empty_dataframe,
                            number_compare_box, number_select_update_box,
                            number_update_box, orderby_box, populate_elements,
                            text_compare_box)
from app.queries import QUERY_TYPE, query_accounts, query_items, query_types
from app.utils import time_now


def item_insert(db, query, table, fields, populate, append):
    fields_noids = deepcopy(fields)
    fields_noids.remove('item_id')

    options = st.multiselect(
        label='Поля',
        options=fields_noids,
        default=None
    )

    accounts = query_accounts(db)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    type_ids = query_types(db)

    if len(type_ids) < 1:
        st.write('Не хватает типов предметов')
        return

    query = query.into(table)

    player_id = default_or_value(
        'player_id' in options,
        choice(accounts),
        st.selectbox,
        {
            'label': 'ID аккаунта',
            'options': accounts
        }
    )

    type_id = default_or_value(
        'type_id' in options,
        choice(type_ids),
        st.selectbox,
        {
            'label': 'ID типа',
            'options': type_ids
        }
    )

    price = default_or_value(
        'price' in options,
        'DEFAULT',
        st.number_input,
        {
            'label': 'Цена',
            'value': 100,
            'min_value': 1,
            'step': 1
        }
    )

    minimum_level = default_or_value(
        'minimum_level' in options,
        'DEFAULT',
        st.number_input,
        {
            'label': 'Минимальный уровень',
            'value': 1,
            'min_value': 1,
            'max_value': 255,
            'step': 1
        }
    )

    tradable = default_or_value(
        'tradable' in options,
        'DEFAULT',
        st.checkbox,
        {
            'label': 'Обмениваемый'
        }
    )

    expiration_date = default_or_value(
        'expiration_date' in options,
        time_now(),
        date_time_box,
        {
            'label': 'истечения'
        }
    )

    blank()

    non_empty_button(
        db,
        query.insert(
            'DEFAULT',
            player_id,
            type_id,
            price,
            minimum_level,
            tradable,
            expiration_date
        ),
        'Добавить'
    )


def item_select(db, query, table, fields, populate, append):
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


def item_update(db, query, table, fields, populate, append):
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


def item_delete(db, query, table, fields, populate, append):
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
    'INSERT': item_insert,
    'SELECT': item_select,
    'UPDATE': item_update,
    'DELETE': item_delete,
}


def tables_item(db):
    table = Table('Item')
    query = PostgreSQLQuery()

    fields = [
        'item_id',
        'player_id',
        'type_id',
        'price',
        'minimum_level',
        'tradable',
        'expiration_date'
    ]

    populate = {
        'player_id': (
            text_compare_box,
            {
                'label': 'ID аккаунта',
                'compared': table.player_id,
                'options': query_accounts(db)
            }
        ),
        'item_id': (
            text_compare_box,
            {
                'label': 'ID предмета',
                'compared': table.item_id,
                'options': query_items(db),
                'uid': True
            }
        ),
        'type_id': (
            number_compare_box,
            {
                'label': 'ID типа',
                'compared': table.type_id
            }
        ),
        'price': (
            number_compare_box,
            {
                'label': 'Цена',
                'compared': table.price
            }
        ),
        'minimum_level': (
            number_compare_box,
            {
                'label': 'Минимальный уровень',
                'compared': table.minimum_level
            }
        ),
        'tradable': (
            bool_compare_box,
            {
                'label': 'Обмениваемый',
                'compared': table.tradable
            }
        ),
        'expiration_date': (
            date_time_compare_box,
            {
                'label': 'истечения',
                'compared': table.expiration_date
            }
        )
    }

    append = {
        'player_id': (
            table.player_id,
            st.text_input,
            {
                'label': 'ID аккаунта '
            }
        ),
        'item_id': (
            table.item_id,
            st.selectbox,
            {
                'label': 'ID предмета ',
                'options': query_items(db)
            }
        ),
        'type_id': (
            table.type_id,
            number_select_update_box,
            {
                'label': 'ID типа ',
                'options': query_types(db)
            }
        ),
        'price': (
            table.price,
            number_update_box,
            {
                'label': 'Цена '
            }
        ),
        'minimum_level': (
            table.minimum_level,
            number_update_box,
            {
                'label': 'Минимальный уровень '
            }
        ),
        'tradable': (
            table.tradable,
            bool_update_box,
            {
                'label': 'Обмениваемый '
            }
        ),
        'expiration_date': (
            table.expiration_date,
            date_time_update_box,
            {
                'label': 'истечения '
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
