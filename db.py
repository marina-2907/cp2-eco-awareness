import oracledb

def get_connection():
    conn = oracledb.connect(
        user="rm564666",
        password="100706",
        dsn="oracle.fiap.com.br:1521/ORCL"
    )
    return conn
