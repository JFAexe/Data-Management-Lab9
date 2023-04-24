from copy import deepcopy
from random import choice

import streamlit as st
from pypika import PostgreSQLQuery, Table

from app.components import (append_elements, blank, default_or_value,
                            groupby_box, limitby_box, non_empty_button,
                            non_empty_dataframe, number_compare_box,
                            number_update_box, orderby_box, populate_elements,
                            text_compare_box, uuid_select_box, warning)
from app.queries import (QUERY_TYPE, query_accounts, query_items,
                         query_purchases, query_trades)


def itemtransfer_insert(db, query, table, fields, populate, append):
    if not warning():
        blank()
    else:
        return

    options = st.multiselect(
        label='Поля',
        options=fields,
        default=None
    )

    accounts = query_accounts(db)

    if len(accounts) < 1:
        st.write('Не хватает игроков')
        return

    trade = 'trade_id' in options
    purchase = 'purchase_id' in options

    trade_ids = query_trades(db)
    purchase_ids = query_purchases(db)

    not_enough_trades = len(trade_ids) < 1
    not_enough_purchases = len(purchase_ids) < 1

    if not_enough_trades and not_enough_purchases:
        st.write('Не хватает обменов и покупок')
        return
    elif not_enough_trades:
        purchase = True
    elif not_enough_purchases:
        trade = True

    query = query.into(table)

    trade_default = (choice(trade_ids), 'Обмен')
    purchase_default = (choice(purchase_ids), 'Покупка')

    selected = choice([trade_default, purchase_default])
    if trade:
        selected = trade_default
    elif purchase:
        selected = purchase_default

    action_id, action = default_or_value(
        trade or purchase,
        selected,
        uuid_select_box,
        {
            'label': 'ID',
            'options': ['Обмен', 'Покупка'],
            'selected': selected[1],
            'options_': [trade_ids, purchase_ids]
        }
    )

    trade_id, purchase_id = None, None
    if action == 'Обмен':
        trade_id = action_id
    else:
        purchase_id = action_id

    initiator_id = default_or_value(
        'initiator_id' in options,
        choice(accounts),
        st.selectbox,
        {
            'label': 'ID инициатора',
            'options': accounts,
            'disabled': purchase
        }
    )

    initiator_id = initiator_id if trade_id is not None else None

    receiver_default = choice(accounts)

    while receiver_default == initiator_id and initiator_id is not None:
        receiver_default = choice(accounts)

    accounts_receiver = deepcopy(accounts)
    if initiator_id is not None:
        accounts_receiver.remove(initiator_id)

    receiver_id = default_or_value(
        'initiator_id' in options,
        receiver_default,
        st.selectbox,
        {
            'label': 'ID получателя',
            'options': accounts_receiver
        }
    )

    item_ids = query_items(db)
    if initiator_id is not None:
        item_ids = query_items(db, initiator_id)

    disabled = len(item_ids) < 1

    item_id = default_or_value(
        'item_id' in options,
        'NULL' if disabled else choice(item_ids),
        st.selectbox,
        {
            'label': 'ID предмета',
            'options': item_ids,
            'disabled': disabled
        }
    )

    blank()

    if item_id == 'NULL':
        st.write('Не хватает предметов для заполнения `item_id`')
        return

    non_empty_button(
        db,
        query.insert(
            'DEFAULT',
            trade_id,
            purchase_id,
            initiator_id,
            receiver_id,
            item_id
        ),
        'Добавить'
    )


def itemtransfer_select(db, query, table, fields, populate, append):
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


def itemtransfer_update(db, query, table, fields, populate, append):
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


def itemtransfer_delete(db, query, table, fields, populate, append):
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
    'INSERT': itemtransfer_insert,
    'SELECT': itemtransfer_select,
    'UPDATE': itemtransfer_update,
    'DELETE': itemtransfer_delete,
}


def tables_itemtransfer(db):
    table = Table('ItemTransfer')
    query = PostgreSQLQuery()

    fields = [
        'transfer_id',
        'trade_id',
        'purchase_id',
        'initiator_id',
        'receiver_id',
        'item_id'
    ]

    populate = {
        'transfer_id': (
            number_compare_box,
            {
                'label': 'ID передачи',
                'compared': table.transfer_id
            }
        ),
        'trade_id': (
            text_compare_box,
            {
                'label': 'ID обмена',
                'compared': table.trade_id,
                'options': query_trades(db),
                'uid': True
            }
        ),
        'purchase_id': (
            text_compare_box,
            {
                'label': 'ID покупки',
                'compared': table.purchase_id,
                'options': query_purchases(db),
                'uid': True
            }
        ),
        'initiator_id': (
            text_compare_box,
            {
                'label': 'ID инициатора',
                'compared': table.initiator_id,
                'options': query_accounts(db)
            }
        ),
        'receiver_id': (
            text_compare_box,
            {
                'label': 'ID получателя',
                'compared': table.receiver_id,
                'options': query_accounts(db)
            }
        ),
        'item_id': (
            text_compare_box,
            {
                'label': 'ID предмета',
                'compared': table.purchase_id,
                'options': query_items(db),
                'uid': True
            }
        )
    }

    append = {
        'transfer_id': (
            table.transfer_id,
            number_update_box,
            {
                'label': 'ID передачи '
            }
        ),
        'trade_id': (
            table.trade_id,
            st.selectbox,
            {
                'label': 'ID обмена ',
                'options': query_trades(db)
            }
        ),
        'purchase_id': (
            table.purchase_id,
            st.selectbox,
            {
                'label': 'ID покупки ',
                'options': query_purchases(db)
            }
        ),
        'initiator_id': (
            table.initiator_id,
            st.selectbox,
            {
                'label': 'ID инициатора ',
                'options': query_accounts(db)
            }
        ),
        'receiver_id': (
            table.receiver_id,
            st.selectbox,
            {
                'label': 'ID получателя ',
                'options': query_accounts(db)
            }
        ),
        'item_id': (
            table.purchase_id,
            st.selectbox,
            {
                'label': 'ID предмета ',
                'options': query_items(db)
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
