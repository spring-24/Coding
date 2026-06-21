store = {
    '삼각김밥': 1200,
    '컵라면': 1500,
    '초코바': 900,
    '에너지음료': 2500,
    '과자': 1800
}
print("=== 편의점 상품 목록 ===")
lst = list(store.keys())
for i in lst:
  print(f"{i} : {store[i]}원")

name = input("구매할 상품: ")
if(name in store):
  num = int(input("수량: "))
  print(f"{name} {num}개 → {store[name] * num}원입니다.")
else:
  print("해당 상품은 판매하지 않습니다.")
