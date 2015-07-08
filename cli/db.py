import sqlite3

class Database:

    def __init__(self, dbfile, page_rows=100):
        self.dbfile = dbfile
        self.page_rows = page_rows
        self.conn = sqlite3.connect(self.dbfile)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS messages "
            "(timestamp TEXT, message TEXT);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS messages_timestamp_idx "
            "ON messages (timestamp);"
        )
        self.conn.commit()

    def __del__(self):
        if self.conn:
            self.conn.close()   
            self.conn = None

    def count(self):
        cursor = self.conn.cursor()
        n = cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        return n

    def messages(self, offset=0):
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM messages "
            "ORDER BY timestamp DESC "
            "LIMIT ? "
            "OFFSET ?",
            [self.page_rows, offset]
        ).fetchall()
        return [ dict(row) for row in rows ]

    def save(self, item):
        saved = False
        if item.item_type == 'message':
            timestamp = item.content['timestamp']
            message   = item.asJson()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages VALUES (?,?)",
                [timestamp, message]
            )
            self.conn.commit()
            saved = True
        return saved
