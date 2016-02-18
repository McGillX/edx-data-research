'''
In this module, we will generate a csv report for a given problem id, which
will include information about how students fared with a given problem id

'''
from itertools import groupby, izip_longest

from edx_data_research.reporting.report import Report


class ProblemIds(Report):

    def __init__(self, args):
        super(ProblemIds, self).__init__(args)
        self._ids = args.problem_ids
        self.final_attempt = args.final_attempt
        self.display_names = args.display_names or []
        self.include_email = args.include_email
        if ((args.start_date and not args.end_date) or
            (not args.start_date and args.end_date)):
            raise ValueError('-s/--start-date and -t/--end-date must be given together')
        self.start_date = args.start_date.isoformat()
        self.end_date = args.end_date.isoformat()
    
    def report_name(self, *args):
        '''Generate name of csv output file from problem id'''
        attempts_name = 'FinalAttempts' if args[2] else 'AllAttempts'
        display_name = args[1].replace(':', '').replace(' ', '_')
        problem_id = args[0]
        # Check if new format of problem id
        if '+' in problem_id:
            blocks = problem_id.split('@')
            _id = blocks[-1]
            course = blocks[0].split('+')[1:3]
            return '_'.join(course + [_id, display_name, attempts_name]) + '.csv'
        else:
            return ('-'.join(arg.lower() for arg in args[0].split('/')[3:]) +
                    display_name + attempts_name + '.csv')

    @staticmethod
    def _problem_id_questions(answer_map):
        problem_id_keys = sorted(answer_map['correct_map'].keys(),
                                 key=lambda x : int(x.split('_')[-2]))
        problem_id_questions = []
        for key in problem_id_keys:
            try:
                item = answer_map['submission'][key]
                value = item['question']
                problem_id_questions.append('{0} : {1}'.format(key, value))
            except UnicodeEncodeError:
                value = value.encode("utf-8")
                problem_id_questions.append('{0} : {1}'.format(key, value))
            except KeyError:
                problem_id_questions.append('{0}'.format(key))
        return problem_id_questions

    def query(self, problem_id):
        if self.start_date and self.end_date:
            return {'event.problem_id' : problem_id, 'time':
                    {'$gte': self.start_date, '$lte': self.end_date}}
        return {'event.problem_id' : problem_id}

    def problem_ids(self):
        '''Retrieve information about how students fared for a given problem id'''
        self.collections = (['problem_ids', 'auth_user'] if self.include_email
                            else ['problem_ids'])
        for problem_id, display_name in izip_longest(self._ids,
                                                     self.display_names,
                                                     fillvalue=''):
            cursor = self.collections['problem_ids'].find(self.query(problem_id))
            display_name = display_name or cursor[0]['module']['display_name']
            one_record = cursor[0]['event']
            problem_id_questions = self.__class__._problem_id_questions(one_record)
            result = []
            for document in cursor:
                answers = []
                for key in sorted(document['event']['correct_map'].keys(),
                                  key=lambda x : int(x.split('_')[-2])):
                    try:
                        answers.append(document['event']['submission'][key]['answer'])
                    except KeyError:
                        answers.append('')
                if self.include_email:
                    email = [(self.collections['auth_user']
                             .find_one({'id': document['user_id']})['email'])]
                else:
                    email = []
                row = self.anonymize_row([document['hash_id']],
                                         [document['user_id'],
                                          document['username']] + email,
                                         [document['event']['attempts'],
                                          document['time'],
                                          document['event']['success'],
                                          document['event']['grade'],
                                          document['event']['max_grade']] +
                                          answers)
                result.append(row)
            if self.final_attempt:
                result = [max(items, key=lambda x : x[1]) for key, items in
                          groupby(sorted(result, key=lambda x : x[0]),
                          lambda x : x[0])]
            csv_report_name = self.report_name(problem_id, display_name,
                                               self.final_attempt)
            headers = ['Attempt Number', 'Time', 'Success', 'Grade Achieved',
                       'Max Grade'] + problem_id_questions
            if self.include_email and not self.anonymize:
                headers = ['Email'] + headers
            headers = self.anonymize_headers(headers)
            self.generate_csv(result, headers, csv_report_name)
