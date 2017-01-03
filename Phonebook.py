import pypyodbc

import sys
sys.path.append(r"F:\personal\jwmccann\Python\Personal\MyLib.py")
from MyLog import MyLog


class TrnPhonebook:
    # cephonebookdev-sql.epic.com
    # CE_Phonebook_TRN

    def __init__(self):
        self.phonebook_dbo = "[CE_Phonebook_TRN].[dbo].[phonebook]"
        self.update_phonebook = "UPDATE {0}".format(self.phonebook_dbo)
        self.class_orgs = "OrgID > 99 AND OrgID < 900000"
        self.class_orgs_under_10000 = "OrgID > 99 and OrgID < 10000"
        self.class_orgs_over_9999 = "OrgID > 9999 and OrgID < 900000"
        self.where_class_org = "WHERE {0}".format(self.class_orgs)
        self.prep_orgs = "OrgID > 899999"
        self.where_prep_org = "WHERE {0}".format(self.prep_orgs)
        self.active = "status = 1"
        self.where_active_and_class_org = "WHERE {0} AND {1}".format(self.active, self.class_orgs)
        self.where_active_and_class_org_under_10000 = "WHERE {0} AND {1}".format(self.active,
                                                                                 self.class_orgs_under_10000)
        self.where_active_and_class_org_over_9999 = "WHERE {0} and {1}".format(self.active,
                                                                               self.class_orgs_over_9999)
        self.go_live_on = "5554137600"  # 1/1/2017 12:00:00 AM
        self.go_live_off = "10500278400"  # 9/27/2173 12:00:00 AM

        self.conn = pypyodbc.connect('Driver={SQL Server};Server=cephonebooktrn-sql;database=CE_Phonebook_TRN')
        self.my_log = MyLog(name=__name__, level='debug')

    def reset(self):
        """
        returns the Training Phonebook to a clean state
        :return: <bool> True if all the updates were successful
        """
        self.my_log.info("Resetting the Phonebook")

        sql_default = "{0} SET status = 4 WHERE OrgType IN (4, 10)\
                       {0} SET QueryPhone = NULL {1}\
                       {0} SET QueryEmail = NULL {1}\
                       {0} SET QueryHours = NULL {1}\
                       {0} SET AuditPhone = NULL {1}\
                       {0} SET AuditEmail = NULL {1}\
                       {0} SET ITPhone = NULL {1}\
                       {0} SET ITEmail = NULL {1}\
                       {0} SET AuthText = ' ' {1}\
                       {0} SET ContactInfoType = NULL {1}\
                       {0} SET ContactInfoPhone = NULL {1}\
                       {0} SET ContactInfoIntlPhone = NULL {1}\
                       {0} SET QueryInstructions = NULL {1}\
                       {0} SET PPOCDefaultDays = NULL {1}\
                       {0} SET PPOCOrgDays = NULL {1}\
                       {0} SET PPOCOrgs = NULL {1}\
                       {0} SET GoLive = '{3}' {1}\
                       {0} SET GoLive = '{4}' {2}".format(self.update_phonebook,
                                                          self.where_class_org,
                                                          self.where_prep_org,
                                                          self.go_live_off,
                                                          self.go_live_on)

        sql_reset_address = "{0} SET Address = concat(substring(URL,12,2),' Main Street') {2}\
                             {0} SET Address = concat(substring(URL,12,3),' Main Street') {3}\
                             {0} SET CareEverywhereCountry = 1 {1}\
                             {0} SET City = 'Verona' {1}\
                             {0} SET State = '50 Wisconsin WI' {1}\
                             {0} SET StateName = 'Wisconsin' {1}\
                             {0} SET Zip = '53593' {1}\
                             {0} SET Country = 'United States of America' {1}\
                             {0} SET DisplayAddress = CONCAT(Address,CHAR(0x5),City,' WI ',Zip,CHAR(0x5),Country) {1}\
                            ".format(self.update_phonebook,
                                     self.where_class_org,
                                     self.where_active_and_class_org_under_10000,
                                     self.where_active_and_class_org_over_9999)
        
        sql_reset_name = "{0} SET OrgName = concat(substring(URL, 9, 5), ' Health System') {1}\
                          {0} SET OrgName = concat(substring(URL, 9, 6), ' Health System') {2}\
                          ".format(self.update_phonebook,
                                   self.where_active_and_class_org_under_10000,
                                   self.where_active_and_class_org_over_9999)
        
        return self.try_sql(sql_default) and self.try_sql(sql_reset_address) and self.try_sql(sql_reset_name)

    def instructor(self, cache):
        """
        registers the instructor environment with the Phonebook
        :param cache: <string> the cache training environment for the instructor
        :return: <bool> True if all the updates were successful
        """
        self.my_log.info("Registering %s as Instructor with the Phonebook" % cache)

        sql_instructor = "UPDATE [CE_Phonebook_TRN].[dbo].[phonebook]\
                           SET OrgName = 'Instructor Health System'\
                           WHERE status = 1 AND OrgID = %d" % (int(cache)*100)

        sql_prep = "{0} SET GoLive = '{2}' {1}".format(self.update_phonebook, self.where_prep_org, self.go_live_off)

        return self.try_sql(sql_instructor) and self.try_sql(sql_prep) and self.register(cache)

    def register(self, cache):
        """
        updates the Go Live date for the specified cache environment so that it is usable in class
        :param cache: <string> the number of the training environment to be used in class
        :return: <bool> True if the update was successful
        """
        self.my_log.info("Registering %s with the Phonebook" % cache)

        sql_register = "UPDATE [CE_Phonebook_TRN].[dbo].[phonebook]\
                         SET GoLive = '5499187200'\
                         WHERE status = 1 AND OrgID = %d" % (int(cache)*100)

        self.my_log.debug("Updating GoLive for %d" % int(cache)*100)

        return self.try_sql(sql_register)

    def register_gwn(self, cache):
        """
        particular registration required for the Galaxy Wide Network environment
        :param cache: <string> the number for the cache training environment
        :return: <bool> True if the update was successful
        """
        self.my_log.info("Registering %s as GWN with the Phonebook" % cache)

        old_interconnect = self.get_interconnect(72)
        sql_register = "UPDATE [CE_Phonebook_TRN].[dbo].[phonebook]\
                         SET GoLive='5499187200', UrlValue=REPLACE(UrlValue,'%s','Interconnect-train%s')\
                         WHERE status = 1 AND OrgID = 72" % (old_interconnect, cache)

        self.my_log.debug("Updating %s to Interconnect-train%s" % (old_interconnect, cache))

        return self.try_sql(sql_register)

    def get_interconnect(self, env_id):
        """
        retrieves the IIS directory in use for the specified organization ID
        :param env_id: <string> the DXO ID of the environment you are searching for
        :return: <string> the IIS directory for said organization/environment
        """
        self.my_log.info("Finding IIS directory for %s" % env_id)
        sql_get = "SELECT UrlValue\
                    FROM [CE_Phonebook_TRN].[dbo].[phonebook]\
                    WHERE status=1 and OrgID=%s" % env_id
        cur = self.conn.cursor()
        cur.execute(sql_get)
        url_values = cur.fetchone()[0]
        first_url = url_values.split('\x05')[0]
        if first_url:
            self.my_log.debug("Found %s for %s" % (first_url.split("/")[3], env_id))
            return first_url.split("/")[3]
        return ""

    def try_sql(self, sql_string):
        """
        tries to execute SQL query and catches any OperationalErrors. Writes the error to the err file.
        :param sql_string: <string> SQL query to attempt
        :return:
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql_string)
            self.conn.commit()
            return True
        except pypyodbc.OperationalError as e:
            msg = "%s\n%s\n\n" % (sql_string, e)
            self.my_log.exception(msg)
            return False

    def __del__(self):
        self.conn.close()

# # # #


if __name__ == "__main__":
    phonebook = TrnPhonebook()
    interconnect = phonebook.get_interconnect(72)
    print interconnect
