

file = open('PreachesList.txt', 'r', encoding='utf-8')
content = file.readlines()

a = content[0].split(' ')
print(a)