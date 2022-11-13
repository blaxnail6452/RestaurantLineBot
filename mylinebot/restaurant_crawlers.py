#import所有需要的library
from bs4 import BeautifulSoup as BS
from urllib.request import Request, urlopen
import pandas as pd
import csv
import requests
import pymongo

#設定爬蟲的header訊息
hdr = {'User-Agent': 'Mozilla/5.0'}

#記錄餐廳的四個要件[名字、評價、地址、類型]
R_name = [] 
R_rating = [] 
R_address = [] 
R_type = [] 

#以淡水、八里區附近的餐廳進行搜尋
href = "https://ifoodie.tw/explore/list?place=%E5%8F%B0%E7%81%A3%E6%96%B0%E5%8C%97%E5%B8%82%E5%85%AB%E9%87%8C%E5%8D%80&latlng=25.14666748046875%2C121.39965057373047&page="
for i in range(1, 37):
	site = href + str(i)
	req = Request(site, headers = hdr)
	page = urlopen(req)
	soup = BS(page, "html.parser") #BS將page進行解讀，利用html.parser的方式，如果沒加上的話，會形成亂碼
	restaurant = soup.find_all("div", {"class":"jsx-558691085 info-rows"})

	if(str(restaurant) != None):
		res_len = len(restaurant)
		k = 1
		for res in restaurant:
			res_type = ""
			if k>= res_len:
				break
			restaurant_name = res.find("a", {"class":"jsx-558691085 title-text"}).get_text()
			restaurant_rating = res.find("div", {"class":"jsx-1207467136 text"})
			if restaurant_rating != None:
				restaurant_rating = restaurant_rating.get_text()
			else:
				restaurant_rating = "No_rating"
			restaurant_address = res.find("div", {"class":"jsx-558691085 address-row"}).get_text()
			#print(restaurant_name)
			#print(restaurant_rating)
			#print(restaurant_address)
			R_name.append(restaurant_name)
			R_rating.append(restaurant_rating)
			R_address.append(restaurant_address)
			restaurant_type = res.find_all("a", {"class":"jsx-558691085 category"})
			for j in restaurant_type:
				res_type = res_type + " " + j.get_text()
			#print(res_type)
			R_type.append(res_type)
			k += 1

"""	
array_len = len(R_name)
for i in range(array_len):
	print(R_name[i])
	print(R_rating[i])
	print(R_address[i])
	print(R_type[i])
	print()
"""
#將所有爬蟲結果存進csv
df = pd.DataFrame({'restaurant_name':R_name, 'restaurant_rating':R_rating, 'restaurant_address':R_address, 'restaurant_type': R_type}, columns = ["restaurant_name", "restaurant_rating", "restaurant_address", "restaurant_type"])
df.to_csv("restaurant_crawlers.csv", encoding = "utf_8_sig") #python會有中文編碼的問題，因此存進csv檔時須加上encoding參數

#將所有爬蟲結果同步備份至MongoDB
#mongoDB基本設定
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["restaurant_line_bot"] #databaseName
mycol = mydb["foodlinebot_taipei_restaurant"] #collectionName
#儲存
array_len = len(R_name)
for i in range(array_len):
	restaurant_info = {'restaurant_number':i, 'restaurant_name': R_name[i], 'restaurant_rating':R_rating[i], 'restaurant_address':R_address[i], 'restaurant_type': R_type[i]}
	mycol.insert_one(restaurant_info)
