'''
This module aims to create a new collection which will have data relevant to
all the problem ids in a course whether they are homework assignment questions
or questions in the acitivities of a lecture

Creating a new collection with information only about problem ids and students
answers to those problem ids will allow us and others to focus on analysis
only on problem ids; hence the time taken to run queries on the data can be 
relatively less because we run these queries on only a subset of the tracking logs

Usage:

python create_problem_ids_collection.py <db_name> 

Note:

Make sure the module base_edx is in the same directory as this script so that it 
can be imported

'''
from common.base_edx import EdXConnection
import sys

db_name = sys.argv[1]

# The second argument in line 27 is the name of the new collection which will 
# contain the results of this script. Each new document will be inserted into
# this new collection. The name of the resulting collection could be anything;
# preferrably relevant to the course
connection = EdXConnection(db_name, 'tracking','problem_ids')
collection = connection.get_access_to_collection()

cursor = collection['tracking'].find({'event_type' : 'problem_check', 'event_source' : 'server'})
for document in cursor:
   doc_result = {}
   doc_result['username'] = document['username']
   doc_result['problem_id'] = document['event']['problem_id']
   doc_result['course_id'] = document['context']['course_id']
   doc_result['module'] = document['context']['module']
   doc_result['time'] = document['time']
   doc_result['event'] = document['event']
   collection['problem_ids'].insert(doc_result)
