import psycopg2
from psycopg2 import sql


class PostgresDB:
    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        self.conn = psycopg2.connect(url)
        self.cur = self.conn.cursor()

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = [sql.Identifier(column) for column in columns]
        placeholders = [sql.Placeholder(column) for column in columns]

        upsert_query = sql.SQL("""
            INSERT INTO {} ({}) VALUES ({})
            ON CONFLICT (id) DO UPDATE
            SET ({}) = ROW({})
        """).format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(values),
            sql.SQL(', ').join(placeholders),
            sql.SQL(', ').join(values),
            sql.SQL(', ').join(placeholders)
        )
        self.cur.execute(upsert_query, _dict)
        self.conn.commit()

    def delete(self, table_name, _id):
        self.cur.execute(
            "DELETE FROM {} WHERE id = %s".format(table_name), (_id,))
        self.conn.commit()

    def get(self, table_name, _id):
        self.cur.execute(
            "SELECT * FROM {} WHERE id = %s".format(table_name), (_id,))
        return self.cur.fetchone()

    def get_all(self, table_name):
        self.cur.execute("SELECT * FROM {}".format(table_name))
        return self.cur.fetchall()

    def run_sql(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        formatted_result = "\n".join("\t".join(str(item) for item in row) for row in result)
        return formatted_result

    def get_table_definitions(self, table_name):
        self.cur.execute("""
            SELECT pg_tables.tablename, pg_tables.schemaname,
                   pg_tables.tableowner, pg_tables.tablespace,
                   pg_tables.hasindexes, pg_tables.hasrules,
                   pg_tables.hastriggers, pg_tables.rowsecurity
            FROM pg_tables
            WHERE tablename = %s
        """, (table_name,))
        return self.cur.fetchone()

    def get_all_table_names(self):
        self.cur.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        return [row[0] for row in self.cur.fetchall()]

    def get_table_column_definitions(self, table_name):
        self.cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table_name,))
        return self.cur.fetchall()

    def get_foreign_keys(self, table_name):
        self.cur.execute("""
            SELECT 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' AND 
                tc.table_name = %s;
        """, (table_name,))
        return self.cur.fetchall()

    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        result = []
        for table_name in table_names:
            result.append(f"Table: {table_name}")
            columns = self.get_table_column_definitions(table_name)
            for column in columns:
                col_name, data_type, is_nullable, col_default = column
                result.append(
                    f"    {col_name} ({data_type})")

            # Add foreign key relationships
            fks = self.get_foreign_keys(table_name)
            for fk in fks:
                col_name, foreign_table_name, foreign_column_name = fk
                result.append(
                    f"    FOREIGN KEY ({col_name}) REFERENCES {foreign_table_name}({foreign_column_name})")
        return "\n".join(result)
