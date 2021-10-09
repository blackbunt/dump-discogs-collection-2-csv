from pandas import ExcelWriter



def write_2_csv(collection, filename):
    filename = filename + '.csv'
    collection.to_csv(filename, sep='\t', encoding='utf-8')
    return filename


def write_2_excel(collection, filename):
    filename = filename + '.xlsx'
    writer = ExcelWriter(filename)
    collection.to_excel(writer, 'Sheet1', index=False)
    writer.save()
    return filename

def write_file(_db, filetype):
    _db.sort_values(["date_added", "artist"], axis=0,
                    ascending=[False, True], inplace=True)
    while True:
        filename = str(input("Enter Filename of {}-File: ".format(filetype)))
        if filename != "_db":
            if filetype == 'Csv':
                filename = write_2_csv(_db, filename)
            elif filetype == 'Excel':
                filename = write_2_excel(_db, filename)
            break

        else:
            print("You can't name the file '_db' !\n")

    print("Write to file '{}' successful.\n".format(filename))
