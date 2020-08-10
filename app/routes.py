from app import  app
from flask import  render_template,redirect,url_for,request,stream_with_context,Response
from app.forms import Citychoice
from app.models import Group
from app.scrapy import *
from flask import jsonify


@app.route('/',methods=['GET','POST'])
def main():
    city_form = Citychoice()
    if city_form.validate_on_submit():
        city = city_form.city.data
        print(city)
        return redirect(url_for('city_group', city=city))
    return render_template('index.html', form=city_form)
import subprocess





@app.route('/group/<city>')
def city_group(city):
    # grouplist = city_group(city)
    grouplist = Group.query.filter(Group.group_name.like("%{}%".format(city)))
    return render_template('group.html', grouplist=grouplist)

@app.route('/group_rec',methods=['POST'])
def group_rec():
    groups = request.form.getlist('check')
    # post_get(groups)
    if len(groups)>0:
        return redirect(render_large_template(groups))
    # return redirect('/')
    return redirect(url_for(group_topics,groups=groups))

@app.route('/_get_topics')
def group_topics(groups):
    for group_link in groups:
        for i in worker(group_link):
            for j in i:
                 jsonify(j)

@app.route('/topics')
def topics(groups):
    for i in group_topics:
        return render_template('topics.html',topic=i)



def stream_template(template_name, **context):
    # app.update_template_context(context)
    # t = app.jinja_env.get_template(template_name) #获取template对应的env
    # rv = t.stream(context) #修改template中context对应的显示
    # rv.enable_buffering(5)
    # return rv
    yield render_template(template_name,**context)
def _topics_stream(group_list):
    topics = []
    for group_link in group_list:
        topics.append(worker(group_link))
        yield topics

@app.route('/topics')
def render_large_template(group_list):
    # rows = i
    print(group_list)
    return stream_with_context(worker(group_list[0]))

@app.route('/api/group',methods=['GET','POST'])
def test_api():
    group_test = ['https://www.douban.com/group/atlaslj/', 'https://www.douban.com/group/254559/',
                  'https://www.douban.com/group/263734/', 'https://www.douban.com/group/bpiao/']

    # group_test = ['https://www.douban.com/group/atlaslj/', 'https://www.douban.com/group/254559/']
    result = []
    groupres = []

    groups = make_get_or_rotate_series(group_test)
    for i in groups():
        result.append(i)

    print(len(result))
    return jsonify(result)