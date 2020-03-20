# -*- coding: utf-8 -*-

"""
扩展chatterbot的Mongodbstorage
"""
import logging
import re
from datetime import datetime

from bson import Regex

from kbqa_sf.train.classifier.intent_classifier import IntentClassifier

__author__ = '程序员涤生'

from chatterbot.storage import StorageAdapter


class Query(object):

    def __init__(self, query={}):
        self.query = query

    def value(self):
        return self.query.copy()

    def raw(self, data):
        query = self.query.copy()

        query.update(data)

        return Query(query)

    def statement_text_equals(self, statement_text):
        query = self.query.copy()

        query['text'] = statement_text

        return Query(query)

    def statement_text_not_in(self, statements):
        query = self.query.copy()

        if 'text' not in query:
            query['text'] = {}

        if '$nin' not in query['text']:
            query['text']['$nin'] = []

        query['text']['$nin'].extend(statements)

        return Query(query)

    def statement_response_list_contains(self, statement_text):
        query = self.query.copy()

        if 'in_response_to' not in query:
            query['in_response_to'] = {}

        if '$elemMatch' not in query['in_response_to']:
            query['in_response_to']['$elemMatch'] = {}

        query['in_response_to']['$elemMatch']['text'] = statement_text

        return Query(query)

    def statement_response_list_equals(self, response_list):
        query = self.query.copy()

        query['in_response_to'] = response_list

        return Query(query)


class MongoDatabaseExtAdapter(StorageAdapter):
    """
    The MongoDatabaseAdapter is an interface that allows
    ChatterBot to store statements in a MongoDB database.

    :keyword database: The name of the database you wish to connect to.
    :type database: str

    .. code-block:: python

       database='chatterbot-database'

    :keyword database_uri: The URI of a remote instance of MongoDB.
    :type database_uri: str

    .. code-block:: python

       database_uri='mongodb://example.com:8100/'
    """

    def __init__(self, **kwargs):
        super(MongoDatabaseExtAdapter, self).__init__(**kwargs)
        from pymongo import MongoClient
        from pymongo.errors import OperationFailure

        self.database_name = self.kwargs.get(
            'database', 'chatterbot-database'
        )
        self.database_uri = self.kwargs.get(
            'database_uri', 'mongodb://localhost:27017/'
        )

        # Use the default host and port
        self.client = MongoClient(self.database_uri)

        # Increase the sort buffer to 42M if possible
        try:
            self.client.admin.command({'setParameter': 1, 'internalQueryExecMaxBlockingSortBytes': 44040192})
        except OperationFailure:
            pass

        # Specify the name of the database
        self.database = self.client[self.database_name]

        # The mongo collection of statement documents
        # self.statements = self.database['statements']
        # '程序员涤生' 改为根据传递的参数使用不同的集合
        self.statements = self.database[self.kwargs.get('ext_collection_name')]

        # The mongo collection of conversation documents
        self.conversations = self.database['conversations']

        # Set a requirement for the text attribute to be unique
        self.statements.create_index('text', unique=True)

        self.base_query = Query()

    def get_statement_model(self):
        """
        Return the class for the statement model.
        """
        from chatterbot.conversation import Statement

        # Create a storage-aware statement
        statement = Statement
        statement.storage = self

        return statement

    def get_response_model(self):
        """
        Return the class for the response model.
        """
        from chatterbot.conversation import Response

        # Create a storage-aware response
        response = Response
        response.storage = self

        return response

    def count(self):
        return self.statements.count()

    def find(self, statement_text):
        Statement = self.get_model('statement')
        query = self.base_query.statement_text_equals(statement_text)

        values = self.statements.find_one(query.value())

        if not values:
            return None

        del values['text']

        # Build the objects for the response list
        values['in_response_to'] = self.deserialize_responses(
            values.get('in_response_to', [])
        )

        return Statement(statement_text, **values)

    def deserialize_responses(self, response_list):
        """
        Takes the list of response items and returns
        the list converted to Response objects.
        """
        Statement = self.get_model('statement')
        Response = self.get_model('response')
        proxy_statement = Statement('')

        for response in response_list:
            text = response['text']
            del response['text']

            proxy_statement.add_response(
                Response(text, **response)
            )

        return proxy_statement.in_response_to

    def mongo_to_object(self, statement_data):
        """
        Return Statement object when given data
        returned from Mongo DB.
        """
        Statement = self.get_model('statement')
        statement_text = statement_data['text']
        del statement_data['text']

        statement_data['in_response_to'] = self.deserialize_responses(
            statement_data.get('in_response_to', [])
        )

        return Statement(statement_text, **statement_data)

    def filter(self, **kwargs):
        """
        Returns a list of statements in the database
        that match the parameters specified.
        """
        import pymongo

        query = self.base_query

        order_by = kwargs.pop('order_by', None)

        # Convert Response objects to data
        if 'in_response_to' in kwargs:
            serialized_responses = []
            for response in kwargs['in_response_to']:
                serialized_responses.append({'text': response})

            query = query.statement_response_list_equals(serialized_responses)
            del kwargs['in_response_to']

        if 'in_response_to__contains' in kwargs:
            query = query.statement_response_list_contains(
                kwargs['in_response_to__contains']
            )
            del kwargs['in_response_to__contains']

        query = query.raw(kwargs)

        matches = self.statements.find(query.value())

        if order_by:

            direction = pymongo.ASCENDING

            # Sort so that newer datetimes appear first
            if order_by == 'created_at':
                direction = pymongo.DESCENDING

            matches = matches.sort(order_by, direction)

        results = []

        for match in list(matches):
            results.append(self.mongo_to_object(match))

        return results

    # 扩展自Statement对象的serialize方法，原因是原方法没有加入created_at属性
    def serialize(self, statement):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}
        data['text'] = statement.text
        # 对statement实例添加created_at是因为Statement实例化时没创建created_at
        statement.created_at = datetime.now()
        data['created_at'] = statement.created_at.isoformat()
        data['in_response_to'] = []
        data['extra_data'] = statement.extra_data
        for response in statement.in_response_to:
            data['in_response_to'].append(response.serialize())
        return data

    def update(self, statement):
        from pymongo import UpdateOne
        from pymongo.errors import BulkWriteError

        # data = statement.serialize()
        # '程序员涤生'
        data = self.serialize(statement)

        operations = []

        # '程序员涤生' 加入下面的if逻辑可以解决在遇到添加不同问题，相同答案的时候，之前的问题答案对关系会被覆盖的bug
        statement_in_db = self.find(statement.text)
        if statement_in_db:
            statement_in_db.in_response_to.extend(statement.in_response_to)
            data = self.serialize(statement_in_db)

        update_operation = UpdateOne(
            {'text': statement.text},
            {'$set': data},
            upsert=True
        )
        operations.append(update_operation)

        # Make sure that an entry for each response is saved
        for response_dict in data.get('in_response_to', []):
            response_text = response_dict.get('text')

            # $setOnInsert does nothing if the document is not created
            update_operation = UpdateOne(
                {'text': response_text},
                {'$set': response_dict},
                upsert=True
            )
            operations.append(update_operation)

        try:
            self.statements.bulk_write(operations, ordered=False)
        except BulkWriteError as bwe:
            # Log the details of a bulk write error
            self.logger.error(str(bwe.details))

        return statement

    def create_conversation(self):
        """
        Create a new conversation.
        """
        conversation_id = self.conversations.insert_one({}).inserted_id
        return conversation_id

    def get_latest_response(self, conversation_id):
        """
        Returns the latest response in a conversation if it exists.
        Returns None if a matching conversation cannot be found.
        """
        from pymongo import DESCENDING

        statements = list(self.statements.find({
            'conversations.id': conversation_id
        }).sort('conversations.created_at', DESCENDING))

        if not statements:
            return None

        return self.mongo_to_object(statements[-2])

    def add_to_conversation(self, conversation_id, statement, response):
        """
        Add the statement and response to the conversation.
        """
        from datetime import datetime, timedelta
        self.statements.update_one(
            {
                'text': statement.text
            },
            {
                '$push': {
                    'conversations': {
                        'id': conversation_id,
                        'created_at': datetime.utcnow()
                    }
                }
            }
        )
        self.statements.update_one(
            {
                'text': response.text
            },
            {
                '$push': {
                    'conversations': {
                        'id': conversation_id,
                        # Force the response to be at least one millisecond after the input statement
                        'created_at': datetime.utcnow() + timedelta(milliseconds=1)
                    }
                }
            }
        )

    def get_random(self):
        """
        Returns a random statement from the database
        """
        from random import randint

        count = self.count()

        if count < 1:
            raise self.EmptyDatabaseException()

        random_integer = randint(0, count - 1)

        statements = self.statements.find().limit(1).skip(random_integer)

        return self.mongo_to_object(list(statements)[0])

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements if the response text matches the
        input text.
        """
        for statement in self.filter(in_response_to__contains=statement_text):
            statement.remove_response(statement_text)
            self.update(statement)

        self.statements.delete_one({'text': statement_text})

    def get_response_statements(self):
        """
        Return only statements that are in response to another statement.
        A statement must exist which lists the closest matching statement in the
        in_response_to field. Otherwise, the logic adapter may find a closest
        matching statement that does not have a known response.
        """
        # '程序员涤生' 原来的逻辑是根据in_response_to字段来判断是否是问题，如果一个句子出现在了其他句子的in_response_to字段中，那么该句子可以做为问题，
        # 因此需要先查出in_response_to字段中的text，然后查出在这些text集合中的句子，做为问题，这样的效率非常慢，
        # 通过在句子中加入Q和A标记，我们可以利用正则来直接匹配出表示问题的句子，
        # 并且我们只返回text字段，大大提升了查询的效率。
        pattern = re.compile('^Q ')
        regex = Regex.from_native(pattern)
        # response_query = self.statements.find({'text': 'Q 出现疑点“申报的美元离岸价超过海关信息中的美元离岸价”要怎么处理？'}, {'text': 1})
        response_query = self.statements.find({'text': {'$regex': regex}}, {'text': 1})

        statement_objects = []
        statement_vec = []
        import datetime as dt
        starttime2 = dt.datetime.now()
        for r in response_query:
            try:
                # 此处考虑直接使用text对应的向量，从系统启动时就构建好的text-vec索引文件中获取
                text_vec_indx = IntentClassifier().text_vec_indx
                vec = text_vec_indx.get(r['text'],None)
                if vec is not None: # 注意：下面这两个数组一定要保证长度一样，否则计算相似度的时候根据索引来取原文本会出先位置偏移，导致无法获取正确的答案！！
                    statement_vec.append(vec)
                    statement_objects.append(self.mongo_to_object({'text': r['text']}))
            except Exception as e:
                logging.warning("出现异常%s，问题句子为：%s", str(e), r['text'])
        endtime2 = dt.datetime.now()
        logging.debug("===========get_response_statements的for循环构造向量耗时: %s秒", (endtime2 - starttime2).seconds)
        return statement_objects, statement_vec

    def drop(self):
        """
        Remove the database.
        """
        self.client.drop_database(self.database_name)
