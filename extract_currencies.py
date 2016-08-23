import re

file = open('currency_ticker.txt', 'r').read()

first = re.findall('"\w+":{', file, flags=re.IGNORECASE)
#second = lambda substr: substr[9:len(substr)-1]
second = lambda substr: substr[1:len(substr)-4]

result = list(map(second, first))
#print(result)
#print(first[0])

write()