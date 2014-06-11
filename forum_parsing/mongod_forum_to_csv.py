'''
Export the collection of .mongo dicussion data from mongodb to csv
'''

import pymongo
import json
import csv

# 1. Assume we have a working mongo database, if not, see mongo_to_mongod.py to insert .mongo files into mongodb
# 2. Start mongod
# 3. Fill up the query dictionaries and projection dictionaries
# 4. Specify output_csv_filename with a name ending in .csv
# 5. Run query_to_csv()

# SPECIFY connection details
DATABASE_ADDRESS = "mongodb://localhost"
DATABASE_NAME = "edx"
DATABASE_FORUM_COLLECTION = "forum"

# SPECIFY output filename
OUTPUT_FILENAME = DATABASE_NAME + "_" + DATABASE_FORUM_COLLECTION + ".csv"

# establish a connection to the database
connection = pymongo.Connection(DATABASE_ADDRESS)

# get a handle to the edx database
db = connection[DATABASE_NAME]

# specify collection
forum = db[DATABASE_FORUM_COLLECTION]

def query_to_csv():

  # SPECIFY query to filter
  query_dict = {}

  # SPECIFY keys of values to project
  proj_dict = {"author_username":1,
                "_type":1,
                "_id":0}

  # SPECIFY output .csv filename
  output_csv_filename = OUTPUT_FILENAME

  # Output file handler
  csv_file = open(output_csv_filename,'w+')
  csv_writer = csv.writer(csv_file)

  # Produce an array of the keys, use this for the first row of our csv file
  keys_array = []
  for key in proj_dict.keys():
    if proj_dict[key]!=0:
      keys_array.append(key)

  # Write the first line of titles (keys)
  csv_writer.writerow(keys_array)
  
  cursor = db.forum.find(query_dict,proj_dict)
  
  for obj in cursor:
    array = []
    for value in obj.values():
      array.append(value.encode('utf-8'))
    csv_writer.writerow(array)

  csv_file.close()

query_to_csv()
