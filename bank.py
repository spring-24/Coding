days = int(input("며칠 동안 저축할까요? "))
sum = 0
i = 100
j = 1
while(1):
  if(j > days):
    break
  sum += i
  print(f"{j}일차: {i}원 (누적: {sum}원)")
  i += 100
  j += 1
print(f"총 저축액: {sum} 원")
