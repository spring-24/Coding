lst = ['오징어게임', '기생충', '범죄도시', '스물다섯 스물하나']
print("[내 찜 목록]")

for i in lst:
  print(i)
print("==============")
name = input("추가할 작품 입력: ")
print("==============")
if(name in lst):
  print("이미 찜한 작품")
else:
  lst.append(name)
  print("[업데이트된 찜 목록]")
  num = 1
  for i in lst:
    print(f"{num}. {i}")
    num += 1
