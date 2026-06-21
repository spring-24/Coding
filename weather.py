temp = int(input("오늘 기온을 입력(°C): "))
if(temp >= 28):
  print("반팔을 입으세요.")
elif(temp >= 20):
  print("가벼운 긴팔을 입으세요.")
elif(temp >= 10):
  print("자켓이나 가디건을 입으세요.")
else:
  print("두꺼운 패딩을 입으세요.")
