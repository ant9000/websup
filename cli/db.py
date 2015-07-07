import sqlite3

class Database:

    def __init__(self, dbfile):
        self.dbfile = dbfile
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

    def messages(self, date='now'):
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM messages "
            "WHERE date(timestamp) = date(?) "
            "ORDER BY timestamp DESC",
            [date]
        ).fetchall()
        return [ dict(row) for row in rows ]

    def save(self, item):
        if item.item_type == 'message':
            timestamp = item.content['timestamp']
            message   = item.asJson()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages VALUES (?,?)",
                [timestamp, message]
            )
            self.conn.commit()
