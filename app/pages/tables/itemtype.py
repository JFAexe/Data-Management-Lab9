import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, default_or_value,
                            groupby_box, limitby_box, non_empty_button,
                            non_empty_dataframe, number_compare_box,
                            number_select_update_box, orderby_box,
                            populate_elements, text_compare_box)
from app.queries import (QUERY_TYPE, query_typedescs, query_typenames,
                         query_types)


def itemtype_insert(db, query, table, fields, populate, append):
    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    query = query.into(table)

    type_id = default_or_value(
        'type_id' in options,
        'DEFAULT',
        st.number_input,
        {
            'label': 'ID типа',
            'value': 1,
            'min_value': 1,
            'step': 1
        }
    )

    type_name = default_or_value(
        'type_name' in options,
        'DEFAULT',
        st.text_input,
        {
            'label': 'Название типа',
            'max_chars': 64
        }
    )

    type_description = default_or_value(
        'type_description' in options,
        'DEFAULT',
        st.text_area,
        {
            'label': 'Название типа',
            'max_chars': 255
        }
    )

    blank()

    non_empty_button(
        db,
        query.insert(
            type_id,
            type_name,
            type_description
        ),
        'Добавить'
    )


def itemtype_select(db, query, table, fields, populate, append):
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


def itemtype_update(db, query, table, fields, populate, append):
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


def itemtype_delete(db, query, table, fields, populate, append):
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
    'INSERT': itemtype_insert,
    'SELECT': itemtype_select,
    'UPDATE': itemtype_update,
    'DELETE': itemtype_delete,
}


def tables_itemtype(db):
    table = Table('ItemType')
    query = PostgreSQLQuery()

    fields = [
        'type_id',
        'type_name',
        'type_description'
    ]

    populate = {
        'type_id': (
            number_compare_box,
            {
                'label': 'ID',
                'compared': table.type_id
            }
        ),
        'type_name': (
            text_compare_box,
            {
                'label': 'Название',
                'compared': table.type_name,
                'options': query_typenames(db)
            }
        ),
        'type_description': (
            text_compare_box,
            {
                'label': 'Описание',
                'compared': table.type_description,
                'options': query_typedescs(db)
            }
        )
    }

    append = {
        'type_id': (
            table.type_id,
            number_select_update_box,
            {
                'label': 'ID ',
                'options': query_types(db)
            }
        ),
        'type_name': (
            table.type_name,
            st.text_input,
            {
                'label': 'Название ',
                'max_chars': 64
            }
        ),
        'type_description': (
            table.type_description,
            st.text_area,
            {
                'label': 'Название ',
                'max_chars': 255
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
