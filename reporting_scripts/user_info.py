'''
This module will retrieve info about students registered in the course

Usage:

python user_info.py

'''
import sys
import csv

from base_edx import EdXConnection
from generate_csv_report import CSV 

db_name = sys.argv[1]

connection = EdXConnection(db_name, 'certificates_generatedcertificate', 'auth_userprofile','user_id_map')
collection = connection.get_access_to_collection()
documents = collection['auth_userprofile'].find()

result = []
for document in documents:
    user_id = document['user_id']
    try:
        final_grade = collection['certificates_generatedcertificate'].find_one({'user_id' : user_id})['grade']
        username = collection['user_id_map'].find_one({'id' : user_id})['username']
        result.append([user_id, document['name'], final_grade, username, document['gender'], document['year_of_birth'], document['level_of_education'], document['country'], document['city']])
    except:
        # Handle users with no grades
        pass
    
<<<<<<< HEAD
output = CSV(result, ['User ID','Name', 'Final Grade', 'Username', 'Gender', 'Year of Birth', 'Level of Education', 'Country', 'City'], output_file=db_name+'-user_info.csv')
=======
output = CSV(result, ['User ID','Name', 'Final Grade', 'Gender', 'Year of Birth', 'Level of Education', 'Country', 'City'], output_file=db_name+'-user_info.csv')
>>>>>>> origin/master
output.generate_csv()
