"""Config and common functions used by all scripts.
"""
import sqlite3
conn = sqlite3.connect('hosts.db')
db = conn.cursor()

# Setup the database
db.execute('CREATE TABLE IF NOT EXISTS hosts (mac text, ip text, hostname text, reviewed int)')

def hosts():
    """Return a dictionary of hosts we know about.
    """
    hostlist = {}

    for hostname, mac, ip, reviewed in db.execute("SELECT hostname, mac, ip, reviewed FROM hosts ORDER BY hostname"):
        if hostname in hostlist:
            hostlist[hostname]['ip'].append(ip)
            hostlist[hostname]['mac'].append(mac)
        else:
            hostlist[hostname] = {
                'hostname':hostname,
                'ip':[ip],
                'mac':[mac],
                'reviewed':reviewed
            }

    return hostlist


def add_host(hostname, ip, mac, reviewed=False):
    """Add a host to the database.
    """
    reviewed = 1 if reviewed else 0
    db.execute('INSERT INTO hosts (mac, ip, hostname, reviewed) VALUES (?, ?, ?, ?)', (mac, ip, hostname, reviewed))
    conn.commit()
    return db.lastrowid


def get_host_by_mac(mac):
    """Gets a host entry by mac address.
    """
    result = db.execute('SELECT mac, ip, hostname, reviewed FROM hosts WHERE mac = ?', (mac,))
    conn.commit()
    return result.fetchall()
