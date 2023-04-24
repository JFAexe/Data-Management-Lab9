import streamlit as st

from .database import database
from .pages import PAGES
from .components import blank


def init():
    st.set_page_config(
        page_title='Что бы это могло быть',
        page_icon='💾'
    )

    global_values = {
        'db': database(),
        'sql': True
    }

    for key, value in global_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def run():
    with st.sidebar:
        st.header('''\
        Абсолютно понятное и удобное приложение \
        к моей реляционной базе данных, \
        которму гарантированно нет равных
        ''')

        app_page = st.selectbox(
            label='Страница',
            label_visibility='collapsed',
            options=PAGES.keys()
        )

        st.session_state.sql = st.checkbox(
            label='Отображать SQL',
            value=True
        )

        blank()

        st.write('by Alexandr Konichenko')

    PAGES.get(app_page)()
