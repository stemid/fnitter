import psycopg2

class Database:
    def __init__(self, config):
        self._conn = psycopg2.connect(
            "host='%s' dbname='%s' user='%s' password='%s'" % (
            config.get('db', 'hostname'),
            config.get('db', 'database'),
            config.get('db', 'username'),
            config.get('db', 'password')
        ))

        # Use underscore prefixed variables to keep them "private"
        self._cur = self._conn.cursor()

    # Iterator method
    def __iter__(self):
        # First copy the cursor so it can be shared with the __next__ method
        self._iter_cur = self._conn.cursor()
        cur = self._iter_cur

        # Execute the query
        cur.execute('select user_id, account_data from accounts')
        return self

    # Iterator next method
    def next(self):
        # Use the special cursor put aside for the iterator
        cur = self._iter_cur
        
        # Fetch one result for each iteration call
        data = cur.fetchone()
        if data is not None:
            return data
        else: 
            raise StopIteration

    def add_account(self, user_id, account_data):
        cur = self._cur
        cur.execute(
            'insert into accounts (user_id, account_data) values (%s, %s)',
            (user_id, account_data,)
        )
        self._conn.commit()

    def delete_account(self, user_id):
        cur = self._cur
        cur.execute(
            'delete from accounts where user_id = %s',
            (user_id, )
        )
        self._conn.commit()

    def log_screenshot(self, user_id, screenshot_data):
        cur = self._cur
        cur.execute(
            'insert into tweets (user_id, tweet) values (%s, %s)',
            (user_id, screenshot_data,)
        )
        self._conn.commit()

    # Deletes a tweet based on timestamp, which must be datetime object
    def delete_screenshot(self, user_id, timestamp):
        cur = self._cur
        cur.execute(
            'delete from tweets where user_id = %s and time = %s',
            (user_id, timestamp,)
        )
        cur._conn.commit()
