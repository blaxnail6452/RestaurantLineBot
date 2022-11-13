from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from foodlinebot.models import taipei_restaurant
import random
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

input_type = ""

@csrf_exempt
def callback(request):
    global input_type
    return_message = ""
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                """ 
                #測試新使用者進入功能
                if event.message.text == "clean":
                    input_type = ""
                    return_message = "初始化成功"
                """
                if input_type == "":  #如果為新使用者，點選三個按鈕將會有三個不同的return message，但若輸入了未知訊息，會直接推薦三間餐廳回去
                    if event.message.text == "隨機推薦三間餐廳給我":
                        return_message = random_recommend(1)
                        input_type = ""
                    elif event.message.text == "我想找某地區的餐廳":
                        return_message = "請幫我輸入想搜尋的地區關鍵字"
                        input_type = "area"
                    elif event.message.text == "我想找某類型的餐廳":
                        return_message = "請幫我輸入想搜尋的類型關鍵字"
                        input_type = "type"
                    else:
                        return_message = "抱歉我現在聽不懂您說的是甚麼，您是新的使用者對吧!\n您可以點選下方的推薦方式，選擇要輸入地區或是輸入類型\n這邊我先推薦給您三間餐廳參考看看\n\n" + random_recommend(1)
                elif input_type == "area": #input area keyword
                    if event.message.text == "隨機推薦三間餐廳給我":
                        return_message = random_recommend(1)
                    elif event.message.text == "我想找某地區的餐廳":
                        return_message = "請幫我輸入想搜尋的地區關鍵字"
                        input_type = "area"
                    elif event.message.text == "我想找某類型的餐廳":
                        return_message = "請幫我輸入想搜尋的類型關鍵字"
                        input_type = "type"
                    else:
                        return_message = filter_area(event.message.text)
                elif input_type == "type": #input type keyword
                    if event.message.text == "隨機推薦三間餐廳給我":
                        return_message = random_recommend(1)
                    elif event.message.text == "我想找某地區的餐廳":
                        return_message = "請幫我輸入想搜尋的地區關鍵字"
                        input_type = "area"
                    elif event.message.text == "我想找某類型的餐廳":
                        return_message = "請幫我輸入想搜尋的類型關鍵字"
                        input_type = "type"
                    else:
                        return_message = filter_type(event.message.text)

                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=return_message)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def random_recommend(request):
    content = ""
    total_data = count_data()
    #random recommend 3 restaurants
    z = 0
    while(z < 3):
        ran = random.randint(0, total_data)
        #print(ran)
        select_data = taipei_restaurant.objects.filter(restaurant_number = ran)
        for i in select_data:
            content = content + i.restaurant_name + '\n' + i.restaurant_rating + '顆星\n' + i.restaurant_address + '\n' + i.restaurant_type
            if z != 2:
                content = content + '\n\n'
        z += 1
    return content

def filter_area(request):
    content = ""
    filter_data = taipei_restaurant.objects.filter(restaurant_address__contains = request)
    if len(filter_data) == 0:
        return "抱歉，我們查不到此地區的餐廳唷"
    highest_rating = 0.0
    for i in filter_data: #best rating in filter_data
        if i.restaurant_rating == "No_rating":
            continue
        rating  = float(i.restaurant_rating)
        if rating > highest_rating:
            highest_rating = rating
            best_restaurant = i
    content = content + best_restaurant.restaurant_name + '\n' + best_restaurant.restaurant_rating + '顆星\n' + best_restaurant.restaurant_address + '\n' + best_restaurant.restaurant_type + '\n\n'
    
    #random另外兩間推薦餐廳
    content = content + random_restaurant(filter_data, best_restaurant)
    return content

def filter_type(request):
    content = ""
    filter_data = taipei_restaurant.objects.filter(restaurant_type__contains = request)
    if len(filter_data) == 0:
        return "抱歉，我們查不到此類型的餐廳唷"
    highest_rating = 0.0
    for i in filter_data: #best rating in filter_data
        if i.restaurant_rating == "No_rating":
            continue
        rating  = float(i.restaurant_rating)
        if rating > highest_rating:
            highest_rating = rating
            best_restaurant = i
    content = content + best_restaurant.restaurant_name + '\n' + best_restaurant.restaurant_rating + '顆星\n' + best_restaurant.restaurant_address + '\n' + best_restaurant.restaurant_type + '\n\n'
    
    #random另外兩間推薦餐廳
    content = content + random_restaurant(filter_data, best_restaurant)
    return content

def count_data(): #資料庫內有幾筆資料
    co_da = taipei_restaurant.objects.filter()
    count_da = 0
    for k in co_da:
        count_da += 1
    return count_da

def random_restaurant(all_filter_data, best_restaurant): #avoid random restaurant == the others restaurant
    content = ""
    random_filter_data1 = random.choice(all_filter_data)
    while(random_filter_data1.restaurant_number == best_restaurant.restaurant_number):
        random_filter_data1 = random.choice(all_filter_data)
    content = content + random_filter_data1.restaurant_name + '\n' + random_filter_data1.restaurant_rating + '顆星\n' + random_filter_data1.restaurant_address + '\n' + random_filter_data1.restaurant_type + '\n\n'
    
    random_filter_data2 = random.choice(all_filter_data)
    while((random_filter_data2.restaurant_number == best_restaurant.restaurant_number) or (random_filter_data2.restaurant_number == random_filter_data1.restaurant_number)):
        random_filter_data1 = random.choice(all_filter_data)
    content = content + random_filter_data2.restaurant_name + '\n' + random_filter_data2.restaurant_rating + '顆星\n' + random_filter_data2.restaurant_address + '\n' + random_filter_data2.restaurant_type
    
    return content

