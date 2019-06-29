import datetime
import json
import math
import os
import random
import re
import shutil

import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from pyecharts import options as opts
from pyecharts.charts import Bar, Calendar, Map
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


def pack_file(filename):
    dest = os.path.join(settings.UPLOAD_DIR, 'achieved')
    if not os.path.exists(dest):
        os.makedirs(dest)
    shutil.move(filename, dest)


def read_files(file_dir):
    file_lists = get_filenames(file_dir)
    for f in file_lists:
        df = pd.DataFrame(pd.read_csv(f))
        df.columns = ['roam', 'host', 'msisdn', 'imsi']
        day = get_day_from_filename(f)
        df['day'] = day
        write_db(df)
        pack_file(f)


def write_db(data):
    engine = create_engine(
        "mysql+pymysql://root@localhost:3306/roam?charset=utf8")
    con = engine.connect()
    data.to_sql(
        name='userapp_orig',
        con=con,
        if_exists='append',
        # if_exists='replace',
        index_label='id')


def get_day_from_filename(filename):
    raw = re.compile(r'\d{8}').search(filename).group()
    return '-'.join([raw[:4], raw[4:6], raw[6:]])


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


def query_db_for_out_top_users():
    q = models.Orig.objects.filter(host='浙江绍兴').values('msisdn').annotate(
        Count('msisdn'))[:50]
    return ([str(x['msisdn'])[2:] for x in q], [x['msisdn__count'] for x in q])


def get_max(data):
    if data:
        d = sorted(data, key=lambda x: x[1], reverse=True)
        max1 = math.ceil(d[0][1] / 1000) * 1000
        max2 = math.ceil(d[1][1] / 1000) * 1000
        return (max1, max2)
    else:
        return (1000, 1000)


def get_day_from_post(POST):
    y = POST['day_year']
    m = POST['day_month']
    if len(m) == 1:
        m = '0' + m
    d = POST['day_day']
    if len(d) == 1:
        d = '0' + d
    return '-'.join((y, m, d))


def bar_base(name, x_data, y_data, title, subtitle) -> Bar:
    return Bar(init_opts=opts.InitOpts(
        width='1100px', height='800px')).add_xaxis(x_data).add_yaxis(
            name,
            sorted(y_data, reverse=False),
        ).reversal_axis().set_series_opts(
            label_opts=opts.LabelOpts(position="right"), ).set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    subtitle=subtitle,
                ),
                datazoom_opts=opts.DataZoomOpts(orient='vertical'),
                toolbox_opts=opts.ToolboxOpts(),
            )


def map_base(name, data, maptype, maxdata, title, subtitle) -> Map:
    return Map(init_opts=opts.InitOpts(width='1100px', height='800px')).add(
        series_name=name,
        data_pair=data,
        maptype=maptype,
        zoom=1.0,
        is_roam=False,
    ).set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            subtitle=subtitle,
        ),
        visualmap_opts=opts.VisualMapOpts(max_=maxdata),
    )


def table_base(data, title, subtitle) -> Table:
    headers = ['省市', '用户', '占比']
    sum = 0
    for x in data:
        sum += x[1]
    new_data = [tuple((x[0], x[1], round(x[1] / sum * 100, 2))) for x in data]
    new_data.insert(0, ('合计', sum, '--'))
    rows = sorted(new_data, key=lambda x: x[1], reverse=True)
    return Table().add(
        headers,
        rows,
    ).set_global_opts(title_opts=ComponentTitleOpts(
        title=title,
        subtitle=subtitle,
    ), )


def calendar_base() -> Calendar:
    begin = datetime.date(2017, 1, 1)
    end = datetime.date(2017, 12, 31)
    data = [[str(begin + datetime.timedelta(days=i)), 1]
            for i in range((end - begin).days + 1)]
    print(data)
    c = (Calendar().add(
        "", data,
        calendar_opts=opts.CalendarOpts(range_="2017")).set_global_opts(
            title_opts=opts.TitleOpts(title="Calendar-2017年微信步数情况"),
            visualmap_opts=opts.VisualMapOpts(
                max_=20000,
                min_=500,
                orient="horizontal",
                is_piecewise=True,
                pos_top="230px",
                pos_left="100px",
            ),
        ))
    return c


@login_required()
def index_view(request):
    read_files(settings.UPLOAD_DIR)
    today = timezone.now().strftime('%Y-%m-%d')

    if request.method != 'POST':
        form = forms.OrigForm()
        day = today
    else:
        form = forms.OrigForm(request.POST)
        day = get_day_from_post(request.POST)

    out_users = query_db_for_out_by_date(day)
    in_users = query_db_for_in_by_date(day)
    out_max_zj, out_max_cn = get_max(out_users)
    in_max_zj, in_max_cn = get_max(in_users)

    # calendar_base().render('./templates/user_calendar.html')

    map_base(
        '本地->省外',
        out_users,
        'china',
        out_max_cn,
        '漫出用户数',
        '统计日期：' + day,
    ).render('./templates/map_sx_to_cn.html')

    map_base(
        '本地->省内',
        out_users,
        '浙江',
        out_max_zj,
        '漫出用户数',
        '统计日期：' + day,
    ).render('./templates/map_sx_to_zj.html')

    map_base(
        '省外->本地',
        in_users,
        'china',
        in_max_cn,
        '漫入用户数',
        '统计日期：' + day,
    ).render('./templates/map_cn_to_sx.html')

    map_base(
        '省内->本地',
        in_users,
        '浙江',
        in_max_zj,
        '漫入用户数',
        '统计日期：' + day,
    ).render('./templates/map_zj_to_sx.html')

    table_base(
        out_users,
        '漫出用户数统计表',
        '统计日期：' + day,
    ).render('./templates/tbl_sx_to_cn.html')

    table_base(
        in_users,
        '漫入用户数统计表',
        '统计日期：' + day,
    ).render('./templates/tbl_cn_to_sx.html')

    x, y = query_db_for_in_top_users()
    bar_base(
        'Top-50',
        x,
        y,
        '异地漫入本地用户',
        '统计日期：' + day,
    ).render('./templates/bar_in.html')

    x, y = query_db_for_out_top_users()
    bar_base(
        'Top-50',
        x,
        y,
        '本地漫出异地用户',
        '统计日期：' + day,
    ).render('./templates/bar_out.html')

    context = {'form': form}
    return render(request, 'userApp/index.html', context)
