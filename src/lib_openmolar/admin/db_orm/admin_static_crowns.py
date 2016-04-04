#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides a DemoGenerator for static_crowns table
'''

from random import randint
from PyQt4 import QtSql

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "static_crowns"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.database = database
        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            self.min_patient_id = q_query.value(0).toInt()[0]
            self.max_patient_id = q_query.value(1).toInt()[0]
        else:
            self.min_patient_id, self.max_patient_id = 0,0

        self.length = (self.max_patient_id - self.min_patient_id) * 3

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('date_charted'))


    def crown_list(self):
        CROWNS = SETTINGS.OM_TYPES["crowns"].allowed_values
        TEETH = SETTINGS.upper_back + SETTINGS.lower_back
        randno = len(TEETH) - 1
        for i in range(3):
            tooth = TEETH[randint(0, randno)]
            type_ = CROWNS[randint(0, len(CROWNS)-1)]
            crown = (tooth, type_)
            yield crown

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        for patient in xrange(self.min_patient_id, self.max_patient_id+1):
            for tooth, type_ in self.crown_list():
                self.record.clearValues()
                #set values, or allow defaults
                self.record.setValue('patient_id', patient)
                self.record.setValue('type', type_)
                self.record.setValue('tooth', tooth)
                self.record.setValue('comment', "generated by demo_installer")

                yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    queries = builder.demo_queries()
    print queries.next()