import json
import math
import os
import re
import shutil

import pandas as pd
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from pyecharts import options as opts
from pyecharts.charts import Bar, Map
from pyecharts.components import Table
from pyecharts.globals import CurrentConfig
from pyecharts.options import ComponentTitleOpts
from sqlalchemy import create_engine

from userApp import forms, models


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


def pack_files(filename):
    dest = os.path.join(settings.MEDIA_ROOT, 'achieved')
    if not os.path.exists(dest):
        os.makedirs(dest)
    shutil.move(filename, dest)


def read_files(file_dir):
    file_lists = get_filenames(file_dir)
    for f in file_lists:
        day = get_file_date(f)
        df = pd.DataFrame(pd.read_csv(f))
        df.columns = ['roam', 'host', 'msisdn', 'imsi']
        df['day'] = day
        pack_files(f)
        write_db(df)


def write_db(data):
    engine = create_engine(
        "mysql+pymysql://root@localhost:3306/roam?charset=utf8")
    con = engine.connect()
    data.to_sql(
        name='userapp_orig',
        con=con,
        # if_exists='append',
        if_exists='replace',
        index_label='id')


def get_file_date(filename):
    return re.compile(r'\d{8}').search(filename).group()


def query_db_for_out_by_date(date):
    q = models.Orig.objects.filter(day=date).filter(
        host='浙江绍兴').values('roam').annotate(Count('roam'))
    return [
        tuple((re.sub(u'浙江([\u4e00-\u9fa5]{2})', lambda x: x.group(1) + '市',
                      x['roam']), x['roam__count'])) for x in list(q)
    ]


def query_db_for_in_by_date(date):
    q = models.Orig.objects.filter(day=date).filter(
        roam='浙江绍兴').values('host').annotate(Count('host'))
    return [
        tuple((re.sub(u'浙江([\u4e00-\u9fa5]{2})', lambda x: x.group(1) + '市',
                      x['host']), x['host__count'])) for x in list(q)
    ]


def query_db_for_in_top_users():
    q = models.Orig.objects.filter(roam='浙江绍兴').values('msisdn').annotate(
        Count('msisdn'))[:50]
    return ([str(x['msisdn'])[2:] for x in q], [x['msisdn__count'] for x in q])


def get_max(data):
    d = sorted(data, key=lambda x: x[1], reverse=True)
    max1 = math.ceil(d[0][1] / 1000) * 1000
    max2 = math.ceil(d[1][1] / 1000) * 1000
    return (max1, max2)


def bar_base(name, x_data, y_data) -> Bar:
    return (Bar().add_xaxis(x_data).add_yaxis(
        name, sorted(y_data, reverse=False)).reversal_axis().set_series_opts(
            label_opts=opts.LabelOpts(position="right")).set_global_opts(
                title_opts=opts.TitleOpts(title=''),
                datazoom_opts=opts.DataZoomOpts(orient='vertical'),
                toolbox_opts=opts.ToolboxOpts()).dump_options())


def map_base(name, data, maptype, maxdata) -> Map:
    return (Map().add(
        series_name=name,
        data_pair=data,
        maptype=maptype,
        zoom=1.0,
        is_roam=False,
    ).set_global_opts(title_opts=opts.TitleOpts(title=''),
                      visualmap_opts=opts.VisualMapOpts(max_=maxdata)))


def table_base(data, title) -> Table:
    table = Table()
    headers = ['省市', '用户数']
    rows = sorted(data, key=lambda x: x[1], reverse=True)
    table.add(headers,
              rows).set_global_opts(title_opts=ComponentTitleOpts(title=title))
    return table


def bar_view(request):
    x, y = query_db_for_in_top_users()
    return JsonResponse(json.loads(bar_base('漫入用户 TOP-N', x, y)))


def index_view(request):
    read_files(settings.MEDIA_ROOT)
    today = timezone.now().strftime('%Y%m%d')

    form = forms.OrigForm()
    context = {'form': form}

    if request.method == 'POST':
        day = request.POST.get('day', today)
    else:
        day = today

    out_users = query_db_for_out_by_date(day)
    in_users = query_db_for_in_by_date(day)
    out_max_zj, out_max_cn = get_max(out_users)
    in_max_zj, in_max_cn = get_max(in_users)

    map_base('本地->省外漫出用户数', out_users, 'china',
             out_max_cn).render('./templates/map_sx_to_cn.html')
    map_base('本地->省内漫出用户数', out_users, '浙江',
             out_max_zj).render('./templates/map_sx_to_zj.html')

    map_base('省外->本地漫入用户数', in_users, 'china',
             in_max_cn).render('./templates/map_cn_to_sx.html')
    map_base('省内->本地漫入用户数', in_users, '浙江',
             in_max_zj).render('./templates/map_zj_to_sx.html')

    table_base(out_users, '漫出用户数统计表').render('./templates/tbl_sx_to_cn.html')
    table_base(in_users, '漫入用户数统计表').render('./templates/tbl_cn_to_sx.html')

    return render(request, 'index.html', context)
