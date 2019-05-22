import json
from random import randrange

from django.http import HttpResponse
from django.shortcuts import render
from pyecharts import options as opts
from pyecharts.charts import Bar, Map
from rest_framework.views import APIView


# Create your views here.
def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {"code": code, "msg": error_string, "data": {}}
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


def bar_base() -> Bar:
    c = (Bar().add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]).add_yaxis(
        "商家A", [randrange(0, 100) for _ in range(6)]).add_yaxis(
            "商家B",
            [randrange(0, 100)
             for _ in range(6)]).set_global_opts(title_opts=opts.TitleOpts(
                 title="Bar-基本示例", subtitle="我是副标题")).dump_options())
    return c


def map_base() -> Map:
    return (Map().add(series_name='用户数',
                      data_pair=[
                          ('北京', 120),
                          ('上海', 200),
                          ('浙江', 150),
                          ('安徽', 100),
                      ],
                      maptype='china',
                      zoom=1.25).set_global_opts(
                          title_opts=opts.TitleOpts(title='Example'),
                          visualmap_opts=opts.VisualMapOpts(
                              max_=200, is_piecewise=True)))


def map2_base() -> Map:
    return (Map().add(series_name='用户数',
                      data_pair=[
                          ('杭州市', 120),
                          ('宁波市', 200),
                          ('绍兴市', 150),
                          ('台州市', 100),
                      ],
                      maptype='浙江',
                      zoom=1.25).set_global_opts(
                          title_opts=opts.TitleOpts(title='Example'),
                          visualmap_opts=opts.VisualMapOpts(
                              max_=200, is_piecewise=True)))


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())


class MapView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            content=open(map_base().render("./templates/map.html")).read())
        # content=open(map2_base().render("./templates/map.html")).read())
