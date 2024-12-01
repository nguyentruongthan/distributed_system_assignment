from pymongo import MongoClient

client = MongoClient("mongodb+srv://thannguyenxlscpy:bGk9KzmpMbAGYqP4@cluster0.xbfcj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.test
userCollection = db["user"]