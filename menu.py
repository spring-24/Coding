water = int(800)
cola = int(1200)
cider = int(1000)
bakcas = int(500)
ion = int(900)

def input_layer():
    print("===== 음료 자판기 =====")
    print("원하는 메뉴를 선택하세요")
    print("1---생수 (800원)")
    print("2---콜라 (1200원)")
    print("3---사이다 (1000원)")
    print("4---박카스 (500원)")
    print("5---포카리스웨트 (900원)")
    print("(종료하려면 0 입력)")
    menu = int(input("메뉴 번호 선택: "))
    if(menu == 0):
        exit("시스템 종료")
    money = int(input("투입 금액: "))
    
    return menu, money

def system(menu, money):
    if(menu == 1): 
        print("==========")
        print("정상 출고")
        money -= water
        coin_500 = money // 500
        coin_100 = (money % 500) // 100
        print("[잔돈] 500원:", coin_500, "개", "100원:", coin_100, "개")
        print("==========")
        print("\n")
    
    elif(menu == 2): 
        print("==========")
        print("정상 출고")
        money -= cola
        coin_500 = money // 500
        coin_100 = (money % 500) // 100
        print("[잔돈] 500원:", coin_500, "개", "100원:", coin_100, "개")
        print("==========")
        print("\n")

    elif(menu == 3):
        print("==========")
        print("정상 출고")
        money -= cider
        coin_500 = money // 500
        coin_100 = (money % 500) // 100
        print("[잔돈] 500원:", coin_500, "개", "100원:", coin_100, "개")
        print("==========")
        print("\n")
    
    elif(menu == 4):
        print("==========")
        print("정상 출고")
        money -= bakcas
        coin_500 = money // 500
        coin_100 = (money % 500) // 100
        print("[잔돈] 500원:", coin_500, "개", "100원:", coin_100, "개")
        print("==========")
        print("\n")
    
    elif(menu == 5): 
        print("==========")
        print("정상 출고")
        money -= ion
        coin_500 = money // 500
        coin_100 = (money % 500) // 100
        print("[잔돈] 500원:", coin_500, "개", "100원:", coin_100, "개")
        print("==========")
        print("\n")
    
    else:
        print("올바르지 않은 경로")
        print("\n")

def __main__():
    while(1):
        menu, money = input_layer()
        system(menu, money)
        
if __name__ == "__main__":
    __main__()
