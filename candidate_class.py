# candidate_class.py

class Candidate:
    """A sample Candidate class"""

    # def __init__(self,candidate_id, candidate_name, party, total_votes, delegate_tally, age, sex, phone_number):
    #     self.candidate_id=candidate_id
    #     self.candidate_name=candidate_name
    #     self.party=party
    #     self.total_votes=total_votes
    #     self.delegate_tally=delegate_tally
    #     self.age=age
    #     self.sex=sex
    #     self.phone_number=phone_number


    def __init__(self,candidate_id, candidate_name, party, total_votes, delegate_tally, age, sex, phone_number):
        self.candidate_id=candidate_id
        self.candidate_name=candidate_name
        self.party=party
        self.total_votes=total_votes
        self.delegate_tally=delegate_tally
        self.age=age
        self.sex=sex
        self.phone_number = phone_number

    # @property
    # def email(self):
    #     return '{}.{}@email.com'.format(self.first, self.last)
    #
    # @property
    # def fullname(self):
    #     return '{}.{}'.format(self.first, self.last)
    #
    # def __repr__(self):
    #     return "Employee('{}', '{}', {})".format(self.first, self.last, self.age)
