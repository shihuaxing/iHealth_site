#coding=utf8
from django.db import models
from django.conf import settings
from bson.objectid import ObjectId
import pymongo

class Articles():
    def __init__(self):
        '''初始化'''
        # 连接 mongo 数据库，获得数据指定集合
        self.client = pymongo.MongoClient('mongodb://%s:%s@%s:%d/%s'%(settings.
MONGO_USER,settings.MONGO_PWD,settings.MONGO_HOST,settings.MONGO_PORT,settings.
MONGO_AUTHDB))[settings.MONGO_DBNAME]
        self.articles = self.client['articles']
    
    def find_one(self,id):
        '''获取指定数据'''
        article = self.articles.find_one({"_id": ObjectId(id)})
        return article

    def find_all(self):
        '''返回全部文章'''
        '''默认按照倒序排列，即取出最新插入的文章'''
        article_list = self.articles.find().sort('_id', pymongo.DESCENDING)
        return article_list

    def updateRead(self,id=None,cnt=1):
        '''阅读量+1'''
        if id == None:
            raise Exception,'请提供 id 参数!'
        self.articles.update_one({'_id':ObjectId(id)},{'$inc':{'read':cnt}})

    def find_labelArticle(self, labels):
        category = [{'category':stri} for stri in labels.keys()]
        article_list = self.articles.find({'$or':category }).sort('_id', pymongo.DESCENDING)
        return article_list

    def updateUpvote(self,id=None):
        if id == None:
            raise Exception,'请提供 id 参数!'
        self.articles.update_one({'_id':ObjectId(id)},{'$inc':{'upvote':1}})


class Users():
    def __init__(self):
        '''初始化'''
        # 连接 mongo 数据库，获得数据指定集合
        self.client = pymongo.MongoClient('mongodb://%s:%s@%s:%d/%s'%(settings.
MONGO_USER,settings.MONGO_PWD,settings.MONGO_HOST,settings.MONGO_PORT,settings.
MONGO_AUTHDB))[settings.MONGO_DBNAME]
        self.users = self.client['users']
    
    def find_one(self,id):
        '''获取指定数据'''
        user = self.users.find_one({"_id": ObjectId(id)})
        return user

    def find_label(self, id):
        '''获取用户对应的labels'''
        user = self.users.find_one({"_id": ObjectId(id)})
        if user.has_key('labels'):
            return user['labels']
        else: #用户没有label
            return None

    def find_all(self):
        '''返回全部用户数据'''
        user_list = self.users.find()
        return user_list

    def find_one_by_email(self,email):
        '''获取指定数据'''
        user = self.users.find_one({"email": email})
        return user

    def find_many_by_name(self,name):
        '''获取指定数据'''
        # 正则方式模糊查询 + 类全文索引
        user_list = self.users.find({ '$or' : [{ 'name' : { '$regex' : name } }, { 'nickname' : { '$regex' : name } }] })
        return user_list

    def insert_one(self,data):
        '''插入数据'''
        self.users.insert_one(data)

    def insert_label(self, id):
        '''给没有labels的用户设置空labels'''
        if self.find_label(id) == None:
            self.users.update_one({"_id": ObjectId(id)},{'$set':{'labels':{}}})

    def update_label(self, id, label, value):
        '''更新labels中label的值'''
        #没有labels的用户首先设置label
        self.insert_label(id)
        #首先找到对应用户的labels
        user = self.users.find_one({"_id": ObjectId(id)})
        cur_labels = user['labels']
        if cur_labels.has_key(label):
            cur_labels[label] = cur_labels[label] + value
        else: #新增对应label
            cur_labels[label] = value
        self.users.update_one({"_id": ObjectId(id)}, {'$set': {'labels':cur_labels}})

    def changeNickname(self,id=None,newName=None):
        if id == None or newName == None:
            raise Exception,'请提供 id 和昵称完整参数!'
        self.users.update_one({'_id':ObjectId(id)},{'$set':{'nickname':newName}})

    def changePhone(self,id=None,newPhone=None):
        if id == None or newPhone == None:
            raise Exception,'请提供 id 和昵称完整参数!'
        self.users.update_one({'_id':ObjectId(id)},{'$set':{'phone':newPhone}})
