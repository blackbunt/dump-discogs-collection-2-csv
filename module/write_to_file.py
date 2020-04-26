import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import csv
import xlsxwriter


def write_2_csv(collection, filename):
    # Write to CSV
    collection.to_csv(filename, sep='\t', encoding='utf-8')

    return True


def write_2_excel(collection, filename):
    # Write to Excel File
    writer = ExcelWriter(filename + '.xlsx')
    collection.to_excel(writer, 'Sheet1', index=False)
    writer.save()

    return True