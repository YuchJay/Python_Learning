'''def count_words(filename):
    try:
        with open(filename, encoding='utf-8') as f:
            contents = f.read()
    except FileNotFoundError:
        print('File not found.')
    else:
        words = contents.split()
        num_words = len(words)
        print(f"There are {num_words} words in {filename}.")

filename = 'num.txt'
count_words(filename)'''

import unittest
def get_formatted_name(first,last,middle=''):
    if middle:
        full_name = f"{first} {middle} {last}"
    else:
        full_name = f"{first} {last}"
    return full_name.title()

'''print("Enter 'q' to quit.")
while True:
    first = input("\nEnter your first name: ")
    if first == 'q':
        break
    last = input("Enter your last name: ")
    if last == 'q':
        break

    formatted_name = get_formatted_name(first,last)
    print(f"\tformatted name: {formatted_name}")'''

class NamesTestCase(unittest.TestCase): #创建类，继承unittest.TestCase类
    def test_first_last_name(self):
        formatted_name = get_formatted_name('janis','joplin')
        self.assertEqual(formatted_name, 'Janis Joplin') #比较formatted_name的值与字符串'Janis Joplin'是否相等

    def test_first_last_middle_name(self):
        formatted_name = get_formatted_name('wolfgang','mozart','amadeus')
        self.assertEqual(formatted_name,'Wolfgang Amadeus Mozart')
if __name__ == '__main__':
    unittest.main()