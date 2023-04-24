import operator

QUERY_TYPE = [
    'INSERT',
    'SELECT',
    'UPDATE',
    'DELETE'
]

QUERY_COMAPRE_OPERATORS = {
    '=': operator.eq,
    '<>': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
}


def format_query(query):
    return query\
        .get_sql()\
        .replace('=', ' = ')\
        .replace('<', ' < ')\
        .replace('>', ' > ')\
        .replace('<  =', '<=')\
        .replace('>  =', '>=')\
        .replace('<  >', '<>')\
        .replace(',', ',\n    ')\
        .replace('(', '(\n    ')\
        .replace(')', '\n)')\
        .replace('"', '')\
        .replace('\'DEFAULT\'', 'DEFAULT')\
        .replace('null', 'NULL')\
        .replace(' FROM', '\nFROM')\
        .replace(' INTO', '\nINTO')\
        .replace(' WHERE', '\nWHERE')\
        .replace(' VALUES', '\nVALUES')\
        .replace(' SET', '\nSET')\
        .replace(' AND', '\n    AND')\
        .replace(' ORDER', '\nORDER')\
        .replace(' GROUP', '\nGROUP')\
        .replace(' LIMIT', '\nLIMIT')\
        .replace(' ASC,', ',')\
        .replace(' DESC,', ',')\
        + ';'


def query_servers(db):
    query = 'SELECT * FROM GameServer;'
    return [s['server_id'] for s in db.run_query(query)]


def query_accounts(db, server=None):
    query = 'SELECT * FROM Player'
    if server is not None:
        query += ' WHERE server_id = ' + str(server)
    query += ';'
    return [p['account_id'] for p in db.run_query(query)]


def query_items(db, player=None):
    query = 'SELECT * FROM Item'
    if player is not None:
        query += ' WHERE player_id = \'' + str(player) + '\''
    query += ';'
    return [p['item_id'] for p in db.run_query(query)]


def query_types(db):
    query = 'SELECT * FROM ItemType;'
    return [t['type_id'] for t in db.run_query(query)]


def query_typenames(db):
    query = 'SELECT * FROM ItemType;'
    return [t['type_name'] for t in db.run_query(query)]


def query_typedescs(db):
    query = 'SELECT * FROM ItemType;'
    return [t['type_description'] for t in db.run_query(query)]


def query_trades(db):
    query = 'SELECT * FROM Trade;'
    return [t['trade_id'] for t in db.run_query(query)]


def query_purchases(db):
    query = 'SELECT * FROM Purchase;'
    return [p['purchase_id'] for p in db.run_query(query)]
