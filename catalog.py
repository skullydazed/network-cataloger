"""Config and common functions used by all scripts.
"""
import sqlite3


class Catalog(dict):
    def __init__(self, database='hosts.db'):
        super().__init__()
        self.conn = sqlite3.connect(database)
        self.db = self.conn.cursor()

        self.commit = self.conn.commit
        self.execute = self.db.execute

        self.db.execute('CREATE TABLE IF NOT EXISTS hosts (mac text, ip text, hostname text, reviewed int)')  # Setup the database
        self.fetch_hosts()

    def __getitem__(self, key):
        """Return a single host record.

            If key is an integer we'll sort the hostnames case insensitively
            and return the Nth host record. Otherwise the host will be looked
            up by hostname.
        """
        if isinstance(key, int):
            host = self.hosts[key]
            return self[host]
        else:
            return super().__getitem__(key)

    @property
    def hosts(self):
        """Return a list of hosts ordered alphabetically.
        """
        return sorted(self)

    def fetch_hosts(self):
        """Populate self with the current host list from SQL. Should be called
        after any changes are made.
        """
        self.clear()

        for hostname, mac, ip, reviewed in self.execute("SELECT hostname, mac, ip, reviewed FROM hosts ORDER BY hostname"):
            if hostname in self:
                self[hostname.lower()]['ip'].append(ip)
                self[hostname.lower()]['mac'].append(mac)
            else:
                self[hostname.lower()] = {
                    'hostname': hostname,
                    'ip': [ip],
                    'mac': [mac],
                    'reviewed': reviewed
                }

    def add_host(self, hostname, ip, mac, reviewed=False):
        """Add a host to the database.
        """
        reviewed = 1 if reviewed else 0
        self.execute('INSERT INTO hosts (mac, ip, hostname, reviewed) VALUES (?, ?, ?, ?)', (mac, ip, hostname, reviewed))
        return self.db.lastrowid


    def del_host(self, hostname):
        """Remove a host from the database.
        """
        self.execute('DELETE FROM hosts WHERE hostname = ?', (hostname,))
        return self.db.lastrowid


    def get_host_by_mac(self, mac):
        """Gets a host entry by mac address.
        """
        result = self.execute('SELECT mac, ip, hostname, reviewed FROM hosts WHERE mac = ?', (mac,))
        return result.fetchall()
