import os
import mysql.connector

HOST = os.environ.get('DB_HOST', 'localhost')
USER = os.environ.get('DB_USER', 'root')
PASSWORD = os.environ.get('DB_PASSWORD', '')
DATABASE = os.environ.get('DB_NAME', 'db_donations')


class MySQLDatabase:

    def __init__(self, table):
        self.__table = table
        self.__conn = self.__connect(HOST, USER, PASSWORD, DATABASE)
        self.__cursor = self.__conn.cursor()

    def __connect(self, host, user, password, database):
        """ Cria um objeto de conexão com o MySQL """
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database)

    def __is_connected(self) -> bool:
        """ Verifica se ainda há conexão com o banco """
        return self.__conn.is_connected()

    def __str_values(self, size):
        """ Cria uma 'string' com tamanho n para fazer o insert no banco """
        values = ''
        while size > 1:
            values += '%s, '
            size -= 1
        values += '%s'
        return values

    def __create_columns(self, columns: dict):
        """
            Cria as colunas no padrão necessário
            para o comando CREATE TABLE
        """
        columns_types = [f"{c} {t}" for c, t in columns.items()]
        return ", ".join(columns_types)

    def create_table(self, columns):
        """ Cria uma tabela se ela não existir no banco """
        if self.__is_connected():
            sql = f"""CREATE TABLE IF NOT EXISTS {self.__table} \
                ({self.__create_columns(columns)})"""
            self.__cursor.execute(sql)
            self.__conn.commit()

    def save_all(self, columns: str, values):
        """ Salva 'n' registros no banco de dados """
        if self.__is_connected():
            sql = "INSERT INTO " + self.__table + " " + str(columns) + \
                  " VALUES (" + self.__str_values(columns.count(',') + 1) + ")"
            self.__cursor.executemany(sql, values)
            self.__conn.commit()

    def select_all(self):
        """ Retorna todos os registros da tabela """
        sql = "SELECT * FROM " + self.__table
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def delete(self, where):
        """ Deleta dados que atendam a condição recebida no parâmetro where"""
        if self.__is_connected():
            sql = "DELETE FROM " + self.__table
            sql += " WHERE " + where
            self.__cursor.execute(sql)
            self.__conn.commit()

    def close(self):
        """ Encerra a conexão com o banco """
        self.__cursor.close()
        self.__conn.close()
