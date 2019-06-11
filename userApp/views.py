import datetime
import json
import os
import re
import shutil
from random import randrange

import pandas as pd
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from pyecharts import options as opts
from pyecharts.charts import Bar, Map
from rest_framework.views import APIView
from sqlalchemy import create_engine

from userApp import models


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


def get_filenames(file_dir):
    filelist = []
    for filename in os.listdir(file_dir):
        if os.path.splitext(filename)[1] == '.csv':
            filelist.append(os.path.join(file_dir, filename))
    return filelist


def move_files(filename, from_dir, to_dir):
    filebasename = os.path.basename(filename)
    src_file = os.path.join(from_dir, filebasename)
    dst_file = os.path.join(to_dir, filebasename)
    shutil.move(src_file, dst_file)


def read_files(file_dir):
    file_lists = get_filenames(file_dir)
    for f in file_lists:
        day = get_file_date(f)
        df = pd.DataFrame(pd.read_csv(f))
        df.columns = ['roam', 'host', 'msisdn', 'imsi']
        df['day'] = day
        write_db(df)
        # print(df)
        # query_db_by_date()
        # query_db_by_date(
        #     datetime.datetime.strptime('20190611', '%Y%m%d').date())


def write_db(data):
    engine = create_engine(
        "mysql+pymysql://root@localhost:3306/roam?charset=utf8")
    con = engine.connect()
    data.to_sql(name='userapp_orig',
                con=con,
                if_exists='replace',
                index_label='id')


def get_file_date(filename):
    return re.compile(r'\d{8}').search(filename).group()


def query_db_for_out_by_date(date=datetime.date.today()):
    print(date)
    # o = models.Orig.objects.filter(day='2019-06-09').count()
    # print(o)
    # o = models.Orig.objects.filter(host='浙江绍兴').count()
    q = models.Orig.objects.filter(host='浙江绍兴').values('roam').annotate(
        Count('roam'))
    # o = models.Orig.objects.count()
    # o = models.Orig.objects.all()
    return [
        tuple((re.sub(u'浙江([\u4e00-\u9fa5]{2})', lambda x: x.group(1) + '市',
                      x['roam']), x['roam__count'])) for x in list(q)
    ]


def query_db_for_in_by_date(date=datetime.date.today()):
    q = models.Orig.objects.filter(roam='浙江绍兴').values('host').annotate(
        Count('host'))
    return [
        tuple((re.sub(u'浙江([\u4e00-\u9fa5]{2})', lambda x: x.group(1) + '市',
                      x['host']), x['host__count'])) for x in list(q)
    ]


def bar_base() -> Bar:
    c = (Bar().add_xaxis(["A", "B", "C", "D", "E", "F"]).add_yaxis(
        "商家A", [randrange(0, 100) for _ in range(6)]).add_yaxis(
            "商家B",
            [randrange(0, 100)
             for _ in range(6)]).set_global_opts(title_opts=opts.TitleOpts(
                 title="Bar-基本示例", subtitle="我是副标题")).dump_options())
    return c


def map_base(name, data, maptype, maxdata) -> Map:
    return (Map().add(
        series_name=name,
        data_pair=data,
        maptype=maptype,
        zoom=1,
        is_roam=False,
    ).set_global_opts(title_opts=opts.TitleOpts(title=''),
                      visualmap_opts=opts.VisualMapOpts(max_=maxdata)))


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        read_files(settings.MEDIA_ROOT)
        map_base('本地->省外漫出用户数', query_db_for_out_by_date(), 'china',
                 5000).render('./templates/map_sx_to_cn.html')
        map_base('本地->省内漫出用户数', query_db_for_out_by_date(), '浙江',
                 20000).render('./templates/map_sx_to_zj.html')

        map_base('省外->本地漫入用户数', query_db_for_in_by_date(), 'china',
                 25000).render('./templates/map_cn_to_sx.html')
        map_base('省内->本地漫入用户数', query_db_for_in_by_date(), '浙江',
                 50000).render('./templates/map_zj_to_sx.html')
        # return HttpResponse(content=open("./templates/index.html").read())
        return render(request, 'index.html')


class MapView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            content=open(map_base().render("./templates/map.html")).read())
        # content=open(map2_base().render("./templates/map2.html")).read())
