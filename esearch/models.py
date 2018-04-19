# encoding: utf-8
__author__ = '得一'

from django.db import models
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

# 连接服务器，可连接多个
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class IshareType(DocType):
    # ishare 类型
    suggest = Completion(analyzer=ik_analyzer) # 词条推荐
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    load_num = Integer()
    read_num = Integer()
    crawl_time = Date()
    type = Text(analyzer="ik_smart")
    source_website = Keyword()
    upload_time = Date()

    class Meta:
        index = "ebooksearch"
        doc_type = "ishare"


class PipipaneType(DocType):
    # pipipan 类型
    suggest = Completion(analyzer=ik_analyzer) # 词条推荐
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    read_num = Integer()
    type = Text(analyzer="ik_smart")
    source_website = Keyword()
    upload_time = Date()
    crawl_time = Date()
    tag = Text(analyzer="ik_smart")
    description = Text(analyzer="ik_smart")

    class Meta:
        index = "ebooksearch"
        doc_type = "pipipan"


class MebookType(DocType):
    # mebook 类型
    suggest = Completion(analyzer=ik_analyzer) # 词条推荐
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    type = Text(analyzer="ik_smart")
    source_website = Keyword()
    upload_time = Date()
    crawl_time = Date()
    tag = Text(analyzer="ik_smart")
    description = Text(analyzer="ik_smart")

    class Meta:
        index = "ebooksearch"
        doc_type = "mebook"


if __name__ == "__main__":
    IshareType.init()
    PipipaneType.init()
    MebookType.init()