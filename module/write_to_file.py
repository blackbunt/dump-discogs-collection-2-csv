import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import csv
import xlsxwriter


def write_2_csv(collection, filename):
    collection.to_csv(filename + '.csv', sep='\t', encoding='utf-8')
    return True


def write_2_excel(collection, filename):
    # Write to Excel File
    writer = ExcelWriter(filename + '.xlsx')
    collection.to_excel(writer, 'Sheet1', index=False)
    writer.save()
    print("Write to File successful.")
    return True

def write_file(_db, filetype):
    _db.sort_values(["date_added", "artist"], axis=0,
                    ascending=[False, True], inplace=True)
    while True:
        filename = str(input("Enter Filename of {}-File: ".format(filetype)))
        if filename != "_db":
            if filetype == 'Csv':
                write_2_csv(_db, filename)
            elif filetype == 'Excel':
                write_2_excel(_db, filename)
            break

        else:
            print("You can't name the file '_db' !")