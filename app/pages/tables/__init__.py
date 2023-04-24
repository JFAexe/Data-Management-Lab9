import streamlit as st

from .gameserver import tables_gameserver
from .item import tables_item
from .itemtransfer import tables_itemtransfer
from .itemtype import tables_itemtype
from .player import tables_player
from .purchase import tables_purchase
from .trade import tables_trade

TABLES = {
    'GameServer': tables_gameserver,
    'Player': tables_player,
    'Item': tables_item,
    'ItemType': tables_itemtype,
    'ItemTransfer': tables_itemtransfer,
    'Trade': tables_trade,
    'Purchase': tables_purchase,
}


def page_tables():
    option = st.selectbox(
        label='Таблица',
        options=TABLES.keys()
    )

    TABLES.get(option)(st.session_state.db)
