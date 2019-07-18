a = 2

dict = {"sex":"男" if a==1 else "女" if a==2 else "保密" }

print(dict["sex"])


list1 = [0,1,2,3,4]
list2 = []

for item in list1:
    list2.insert(0, item)

print(list2)
