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
from elasticsearch import Elasticsearch
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=["localhost"])
redis_cli = redis.StrictRedis()

class IndexView(View):
    #首页
    def get(self, request):
        # pass
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"topn_search":topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = PipipaneType.search()
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

class SearchView(View):

    def get(self, request):
        key_words = request.GET.get("q", "")

        redis_cli.zincrby("search_keywords_set", key_words)
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        start_time = datetime.now()
        response = client.search(
            index="ebooksearch",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page - 1) * 10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "tags": {},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10) > 0:
            page_nums = int(total_nums/10) +1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "tag" in hit["highlight"]:
                hit_dict["tag"] = "".join(hit["highlight"]["tags"])[:500]
            else:
                hit_dict["tag"] = hit["_source"]["tag"][:500]

            hit_dict["upload_time"] = hit["_source"]["upload_time"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page":page,
                                               "all_hits":hit_list,
                                               "key_words":key_words,
                                               "total_nums":total_nums,
                                               "page_nums":page_nums,
                                               "last_seconds":last_seconds,
                                               "topn_search":topn_search
                                               })
