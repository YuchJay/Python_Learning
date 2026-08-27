import unittest

class AnonymousSurvey:
    def __init__(self, question): #存储一个问题，并为存储答案做准备
        self.question = question
        self.responses = []

    def show_question(self): #显示调查问卷
        print(self.question)

    def store_response(self, new_response): #存储单份调查答卷
        self.responses.append(new_response)

    def show_results(self): #显示收集到的所有答卷
        print("Survey results:")
        for response in self.responses:
            print(f"- {response}")

"""question = "What language did you first learn to speak?"
my_survey = AnonymousSurvey(question)

my_survey.show_question()
print("Enter 'q' to quit.\n")
while True:
    response = input("> ")
    if response == 'q':
        break
    my_survey.store_response(response)

print("\nThank you for participating in the survey!")
my_survey.show_results()"""

class TestAnonymousSurvey(unittest.TestCase): #继承了unittest.TestCase
    def setUp(self):
        question = "What language did you first learn to speak?"
        self.my_survey = AnonymousSurvey(question) #创建一个调查对象
        self.responses = ['English', 'Spanish', 'Mandarin'] #创建一个答案列表

    def test_store_single_response(self): #测试单个答案会不会被妥善存储
        self.my_survey.store_response(self.responses[0]) #存储单个答案
        self.assertIn(self.responses[0], self.my_survey.responses) #检查前者是否包含在responses中

    def test_store_three_responses(self):
        for response in self.responses:
            self.my_survey.store_response(response)

        for response in self.responses:
            self.assertIn(response, self.my_survey.responses)

if __name__ == '__main__':
    unittest.main()
