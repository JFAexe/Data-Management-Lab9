import streamlit as st

from app.components import display_sql

QUERY_SERVER_COUNT = '''
SELECT COUNT(*)
FROM GameServer;
'''

QUERY_PLAYER_COUNTS = '''
SELECT *
FROM server_player_counts;
'''

QUERY_TOP_SERVERS = '''
SELECT *
FROM server_player_counts
ORDER BY player_count DESC
LIMIT \
'''


def view_player_counts(db):
    servers = db.run_query(QUERY_SERVER_COUNT)[0].get('count')

    if servers == 0:
        st.write('Сервера отсутствуют')
        return

    query = QUERY_PLAYER_COUNTS
    display_sql(query)

    st.dataframe(
        data=db.run_query(query),
        use_container_width=True
    )


def view_top_servers(db):
    servers = db.run_query(QUERY_SERVER_COUNT)[0].get('count')

    if servers == 0:
        st.write('Сервера отсутствуют')
        return

    count = st.slider('Количество', 1, servers, 1) if servers > 1 else 1

    query = QUERY_TOP_SERVERS + str(count) + ';'
    display_sql(query)

    st.dataframe(
        data=db.run_query(query),
        use_container_width=True
    )


VIEWS = {
    'Количество игроков на каждом сервере': view_player_counts,
    'Сервера с наибольшим количеством игроков': view_top_servers,
}


def page_views():
    option = st.selectbox(
        label='Представление',
        options=VIEWS.keys()
    )

    VIEWS.get(option)(st.session_state.db)
