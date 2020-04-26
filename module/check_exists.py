import os
import errno


def folder_checker(folder):  # check if db folder and db file is available.
    try:
        os.makedirs(folder)  # check if "input" folder exists, if not creates it.
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def file_checker(file):
    try:
        file = open(file, 'r')  # checks if a file is available, if not creates a blank one
        return True
    except FileNotFoundError:
        #file = open(file, 'w+')
        return False