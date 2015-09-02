from edx_data_research.reporting.edx_base import EdX

class Basic(EdX):

    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        self.basic_cmd = args.basic.replace('-', '_')

    def user_info(self):
        '''Retrieve info about students registered in given course'''
        self.collections = ['certificates_generatedcertificate',
                            'auth_userprofile','user_id_map',
                            'student_courseenrollment']
        cursor = self.collections['auth_userprofile'].find()
        result = []
        for item  in cursor:
            user_id = item['user_id']
            try:
                final_grade = (self.collections['certificates_generatedcertificate']
                               .find_one({'user_id' : user_id})['grade'])
                user_id_map = (self.collections['user_id_map']
                               .find_one({'id' : user_id}))
                username = user_id_map['username']
	        hash_id = user_id_map['hash_id']
                enrollment_date = (self.collections['student_courseenrollment']
                                   .find_one({'user_id' : user_id})['created'])
                row = ([hash_id] if self.anonymize else
                       [hash_id, user_id, username, item['name']])
                row.extend([final_grade, item['gender'], item['year_of_birth'],
                            item['level_of_education'], item['country'],
                            item['city'], enrollment_date])
                result.append(row)
            except KeyError:
                print "Exception occurred for user_id {0}".format(user_id)
        headers = (['User Hash ID'] if self.anonymize else
                   ['User Hash ID', 'User ID', 'Username', 'Name'])
        headers.extend(['Final Grade', 'Gender', 'Year of Birth',
                        'Level of Education', 'Country', 'City', 'Enrollment Date'])
        self.generate_csv(result, headers, self.report_name(self.db.name,
                          self.basic_cmd))

    def course_completers(self):
        '''
        Extract the student IDs from the collection
        certificates_generatedcertificate of the students who completed the
        course and achieved a certificate. The ids are then used to extract
        the usernames of the course completers
        '''
        self.collections = ['certificates_generatedcertificate', 'auth_user']
        cursor = (self.collections['certificates_generatedcertificate']
                  .find({'status' : 'downloadable'}))
        result = []
        for item in cursor:
            user_document = (self.collections['auth_user']
                             .find_one({"id" : item['user_id']}))
            result.append([user_document['id'], user_document['username'],
                           item['name'], item['grade']])
        headers = ['User ID','Username', 'Name', 'Grade']
        self.generate_csv(result, headers, self.report_name(self.db.name,
                          self.basic_cmd))

    def forum(self):
        '''Retrieve info from the forum collection for a given course'''
        self.collections = ['forum']
        cursor = self.collections['forum'].find()
        result = []
        for item in cursor:
            result.append([item['_id'], item['author_username'], item['_type'],
                           item.get('title', ''), item['body'],
                           item['created_at']]) 
        headers = ['ID', 'Author Username', 'Type', 'Title', 'Body', 'Created At Date']
        self.generate_csv(result, headers, self.report_name(self.db.name,
                          self.basic_cmd))
