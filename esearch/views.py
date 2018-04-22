import pickle
import re

from django.shortcuts import render
import json
from django.views.generic.base import View
from esearch.models import IshareType, PipipaneType, MebookType
from django.http import HttpResponse
from datetime import datetime
from ebooksearch_web.utils.common import OrderedSet
import redis
from w3lib.html import remove_tags

# 为搜索界面进行准备
from elasticsearch import Elasticsearch

class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = MebookType.search()
            # fuzzy模糊搜索。fuzziness 编辑距离 prefix_length前面不变化的前缀长度
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options[:10]:
                source = match._source
                re_datas.append(source["title"])
                # re_datas.append(source["content"])
        return HttpResponse(
            json.dumps(re_datas),
            content_type="application/json")
