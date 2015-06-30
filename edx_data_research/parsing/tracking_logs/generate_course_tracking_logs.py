'''
This module will extract tracking logs for a given course and date range 
between when course enrollment start and when the course ended. For each log,
the parent_data and meta_data from the course_structure collection will be 
appended to the log based on the event key in the log

Usage: python generate_course_tracking_logs.py <source_db> <destination_db> <path_to_config_file>

'''

import pymongo
import sys
from datetime import datetime
import json


def connect_to_db_collection(db_name, collection_name):
    '''
    Return collection of a given database name and collection name
    
    '''
    connection = pymongo.Connection('localhost', 27017)
    db = connection[db_name]
    collection = db[collection_name]
    return collection 

def load_config(config_file):
    '''
    Return course ids and ranges of dates from which course specific tracking
    logs will be extracted

    '''
    with open(config_file) as file_handler:
        data = json.load(file_handler)
        if not isinstance(data['course_ids'], list):
            raise ValueError('Expecting list of course ids')
        try:
            start_date = datetime.strptime(data['date_of_course_enrollment'], '%Y-%m-%d')
            end_date = datetime.strptime(data['date_of_course_completion'], '%Y-%m-%d')
        except ValueError:
            raise ValueError('Incorrect data format, should be YYYY-MM-DD')
    return data['course_ids'], start_date.date(), end_date.date()


def append_course_structure_data(course_structure_collection, _id, document):
    '''
    Append parent_data and metadata (if exists) from course structure to 
    tracking log

    '''
    try:
        data = course_structure_collection.find({"_id" : _id})[0]
        if 'parent_data' in data:
            document['parent_data'] = data['parent_data']
        if 'metadata' in data:
            document['metadata'] = data['metadata']
    except:
        pass    

def extract_tracking_logs(source_collection, destination_collection, course_structure_collection, course_ids, start_date, end_date):
    '''
    Return all trackings logs that contain given ids and that contain dates
    within the given range

    '''
    documents = source_collection.find({'course_id' : { '$in' : course_ids }})
    for document in documents:
        if start_date <= datetime.strptime(document['time'].split('T')[0], "%Y-%m-%d").date() <= end_date:
            # Bind parent_data and metadata from course_structure to tracking document
            bound = False
            if document['event']:
                if isinstance(document['event'], dict):
                    if 'id' in document['event']:
                        splitted = document['event']['id'].split('-')
                        if len(splitted) > 3:
                            document['event']['id'] = splitted[-1]
                            if not bound:
                                append_course_structure_data(course_structure_collection, document['event']['id'], document)
                                bound = True
            if document['page']:
                splitted = document['page'].split('/')
                if len(splitted) > 2:
                    document['page'] = splitted[-2]
                    if not bound:
                        append_course_structure_data(course_structure_collection, document['page'], document)
            # End of binding, now insert document into collection
            destination_collection.insert(document)


def main():
    if len(sys.argv) !=  4:
        usage_message = """usage: %s source_db destination_db course_config_file 
            Provide name of course database to insert tracking logs to and 
            config file to load configurations\n
            """
        sys.stderr.write(usage_message % sys.argv[0])
        sys.exit(1)
    source_db =  sys.argv[1]
    destination_db =  sys.argv[2]
    source_collection = connect_to_db_collection(source_db, 'tracking') 
    destination_collection = connect_to_db_collection(destination_db, 'tracking') 
    course_structure_collection = connect_to_db_collection(destination_db, 'course_structure')
    course_ids, start_date, end_date = load_config(sys.argv[3])
    extract_tracking_logs(source_collection, destination_collection, course_structure_collection, course_ids, start_date, end_date)
    

if __name__ == '__main__':
    main()
