import json
import sqlite3
import csv
import os

import PowerShell
import Log

TRACK_PATH = os.path.dirname(os.path.realpath(__file__))
LOGGER = Log.MyLog(name=__name__)


def init(config_f="config"):
    with open(config_f, 'r') as f:
        config = json.load(f)

    database = open_database()

    for _class in config:
        if create_table(database, _class):
            fill_table(database,
                       _class,
                       config[_class])

    create_schedule(database)

    database.close()

    reconcile()


def open_database(db=os.path.join(TRACK_PATH, 'Interconnects.db')):
    """
    opens given data base and passes the connection back
    :param db: path (relative or absolute) to sqlite database
    :return: connect instance for database (false if the connection failed)
    """
    conn = sqlite3.connect(db)
    if conn:
        conn.text_factory = str  # Could not decode to UTF-8
        return conn
    else:
        return False


def create_schedule(conn):
    """
    checks if the Schedule table exists in given database then creates it if it does not
    :param conn: connect instance for database
    :return: Boolean (True is everything worked)
    """
    if not find_table(conn, "Schedule"):
        sql_create = 'CREATE TABLE Schedule(Cache VARCHAR(12),\
                                            Start VARCHAR(%d),\
                                            End VARCHAR(%d),\
                                            PRIMARY KEY (Cache, Start))' % (len("00/00/0000"), len("00/00/0000"))
        if try_sql(conn, sql_create):
            return True
        else:
            return False
    else:
        sql_add_column = 'ALTER TABLE Schedule\
                                ADD COLUMN Trainer VARCHAR(255)'
        try_sql(conn, sql_add_column)
        return True


def save_schedule(cache, start, end, trainer="Jimmy McCann"):
    database = open_database()
    sql_put = "INSERT INTO Schedule (Cache, Start, End, Trainer) \
                VALUES ('%s','%s','%s','%s')" % (cache, start, end, trainer)
    try_sql(database, sql_put)
    database.close()
    return


def setup_schedule(start):
    database = open_database()
    sql_get = "SELECT Cache, Trainer\
                FROM Schedule\
                WHERE Start='%s'" % start
    results = database.execute(sql_get).fetchall()
    database.close()
    return results


def cleanup_schedule(end):
    database = open_database()
    sql_get = "SELECT Cache\
                FROM Schedule\
                WHERE End='%s'" % end
    results = database.execute(sql_get).fetchall()
    database.close()
    return results


def create_table(conn, name):
    """
    checks if given table exists in given database then creates the table if it does not
    :param conn: connect instance for database
    :param name: name of the table you want to create (and populate) or update
    :return: Boolean (True is everything worked)
    """
    if not find_table(conn, name):
        sql_create = 'CREATE TABLE %s(Interconnect VARCHAR(8), \
                                      Cache VARCHAR(12),\
                                      PRIMARY KEY (Interconnect))' % name
        if try_sql(conn, sql_create):
            return True
        else:
            return False
    else:
        return True


def fill_table(conn, name, interconnects):
    """
    attempts to fill the given table from the database with the Interconnect intances from the config file
    :param conn: connect instance for database
    :param name: name of the table to populate/update
    :param interconnects:
    :return: Boolean (True if we were able to completely populate the table without error)
    """
    for ic in interconnects:
        if not check_table(conn, name, ic):
            sql_insert = "INSERT INTO %s (Interconnect)\
                          VALUES ('%s')" % (name, ic)
            if not try_sql(conn, sql_insert):
                return False

    return True


def find_table(conn, table_name):
    """
    searches database for given table
    :param conn: connect instance for database
    :param table_name: name of table you want to check for
    :return: results of SQL query searching for table
    """
    cur = conn.cursor()
    sql_search = "SELECT name \
                  FROM sqlite_master \
                  WHERE type='table' \
                    AND name='%s'" % table_name
    found = cur.execute(sql_search).fetchone()
    return found


def check_table(conn, table, interconnect):
    """
    searches if Interconnect exists in table in database 
    :param conn: connect instance for database
    :param table: name of table you want to check
    :param interconnect: name of the Interconnect you are looking for
    :return: results of SQL query searching for table
    """
    cur = conn.cursor()
    sql_search = "SELECT * \
                  FROM %s \
                  WHERE Interconnect='%s'" % (table, interconnect)
    found = cur.execute(sql_search).fetchone()
    return found
    

def try_sql(conn, sql_string):
    """
    tries to execute SQL query and catches any OperationalErrors. Writes the error to the ERR global.
    :param conn: connect instance for database
    :param sql_string: SQL query to try
    :return:
    """
    try:
        cur = conn.cursor()
        cur.execute(sql_string)
        conn.commit()
        return True
    except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
        msg = "%s\n%s\n\n" % (sql_string, e)

        LOGGER.exception(msg)

        return False


def get(mode, table):
    if str(mode).upper() in ["ASSIGNED", "1"]:
        return get_assigned(table)
    elif str(mode).upper() in ["UNASSIGNED", "2"]:
        return get_unassigned(table)


def get_assigned(table):
    database = open_database()
    sql_get = "SELECT * \
               FROM %s \
               WHERE Cache IS NOT NULL" % table
    results = database.execute(sql_get).fetchall()
    database.close()
    return results


def get_unassigned(table):
    database = open_database()
    sql_get = "SELECT * \
               FROM %s \
               WHERE Cache IS NULL" % table
    results = database.execute(sql_get).fetchone()[0]
    database.close()
    return results    


def get_funds(cache):
    database = open_database()
    sql_get = "SELECT * \
                FROM AMB_IP \
                WHERE cache='%s'" % cache
    results = database.execute(sql_get).fetchone()
    database.close()
    return results


def assign(table, interconnect, cache):
    database = open_database()
    sql_put = "UPDATE %s \
               SET Cache='%s' \
               WHERE Interconnect='%s'" % (table, cache, interconnect)
    if try_sql(database, sql_put):
        database.close()
        return True
    else:
        database.close()
        return False


def unassign(table, interconnect):
    database = open_database()
    sql_put = "UPDATE %s \
               SET Cache=NULL \
               WHERE Interconnect='%s'" % (table, interconnect)
    if try_sql(database, sql_put):
        database.close()
        return True
    else:
        database.close()
        return False


def get_instructor(_class):
    database = open_database()

    if "CE500" in _class:
        ic = "train01"
    else:
        return ""
    
    sql_get = "SELECT Cache \
               FROM Instructors \
               WHERE Interconnect='%s'" % ic
    results = database.execute(sql_get).fetchone()[0]
    database.close()

    if results:
        return results
    else:
        return ""


def reconcile():
    instances = range(1, 51)  # Interconnects 1 through 50
    web_apps = PowerShell.get_webapplications()
    for app in web_apps:  # make sure existing setup is reflected in database
        cache = "epic-trn"+str(app.cache)

        interconnect = app.interconnect
        if interconnect > 40:
            assign("AMB_IP", "train"+str(interconnect), cache)
        elif interconnect == 1:
            assign("Instructors", "train"+str(interconnect), cache)
        else:
            assign("CE500", "train"+str(interconnect), cache)

        if app.interconnect in instances:
            instances.remove(app.interconnect)

    for i in instances:  # unassign what ever is left
        if i > 40:
            unassign("AMB_IP", "train"+str(i))
        elif i == 1:
            unassign("Instructors", "train"+str(i))
        else:
            unassign("CE500", "train"+str(i))


# # # #


if __name__ == "__main__":
    print TRACK_PATH
