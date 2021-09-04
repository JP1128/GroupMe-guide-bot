import psycopg2 as pg
import sys
from config import dbname, host, user, password


def _connectdb():
    return pg.connect(dbname=dbname, host=host, user=user, password=password)
    
# Database connection
conn: pg._ext.connection = _connectdb()

def _check_connection(c):
    try:
        conn = c
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM guides")
    except:
        conn = _connectdb()
        
    
def create_guide(group_id: str, title: str,
                 content: str = None, picture_url: str = None):
    _check_connection(conn)
    title = title.strip().casefold()
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO guides(group_id, title, content, picture_url)
                    VALUES (%s, %s, %s, %s);
                    """, (group_id, title, content, picture_url))
        conn.commit()


def edit_guide(group_id: str, title: str,
               content: str = None, picture_url: str = None):
    _check_connection(conn)
    title = title.strip().casefold()
    with conn.cursor() as cur:
        cur.execute("""
                    UPDATE guides
                    SET content=%s,
                        picture_url=%s
                    WHERE group_id=%s AND title=%s;
                    """, (content, picture_url, group_id, title))
        conn.commit()


def delete_guide(group_id: str, title: str):
    _check_connection(conn)
    title = title.strip().casefold()
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM guides
                    WHERE group_id=%s AND title=%s;
                    """, (group_id, title))
        conn.commit()


def get_guide(group_id: str, title: str):
    _check_connection(conn)
    title = title.strip().casefold()
    with conn.cursor() as cur:
        cur.execute("""
                SELECT content, picture_url FROM guides
                WHERE group_id=%s AND title=%s;
                """, (group_id, title))

        if cur.rowcount != 0:  # If guide found
            return (True, cur.fetchone())

        # Find similar guides
        cur.execute("""
                    SELECT title FROM guides
                    WHERE group_id=%s 
                    ORDER BY similarity(title, %s) DESC 
                    LIMIT 3;
                    """, (group_id, title))

        return (False, cur.fetchall())


def search_guide(group_id: str, title_query: str):
    _check_connection(conn)
    title_query = title_query.strip().casefold()
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT title FROM guides
                    WHERE group_id=%s
                    ORDER BY similarity(title, %s) DESC
                    LIMIT 6;
                    """, (group_id, title_query))
        return cur.fetchall()
