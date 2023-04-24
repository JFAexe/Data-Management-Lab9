import psycopg2 as pg
import psycopg2.extras as pge
import streamlit as st


@st.cache_resource
def init_connection():
    return pg.connect(
        cursor_factory=pge.RealDictCursor,
        **st.secrets['postgres']
    )


def uncached_query(_con, query, fetch=True):
    with _con.cursor() as cur:
        result = None
        try:
            cur.execute(query)
            if fetch:
                result = cur.fetchall()
        except pg.Error as err:
            st.error(err, icon='⚠️')
            _con.rollback()
        else:
            _con.commit()
        return result


@st.cache_data(ttl=600)
def cached_query(_con, query, fetch=True):
    return uncached_query(_con, query, fetch)


class database():
    def __init__(self):
        self.connection = init_connection()

    def run_query(self, query, fetch=True):
        return cached_query(self.connection, query, fetch)

    def run_query_uncached(self, query, fetch=True):
        return uncached_query(self.connection, query, fetch)

    def call_proc(self, query):
        return uncached_query(self.connection, query, fetch=False)
