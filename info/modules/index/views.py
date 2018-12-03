from info import models
from info.constants import HOME_PAGE_MAX_NEWS
from info.utils.response_code import RET
from . import index_blue
from flask import render_template,current_app,session, jsonify,request


@index_blue.route('/newslist')
def news_list():
    """
    请求方式:get
    请求路径：/newslist
    请求参数： cid 分类编码  page 当前页  per_page 每页数据条数
    返回数据:data
    :return:
    1.获取参数
    2.转换参数数据类型
    3.提取数据库数据,判断分类编码,如最新类型不进行分类查询
    4.返回数据
    """
    cid = request.args.get("cid",1)
    page = request.args.get("page",1)
    per_page = request.args.get("per_page",10)

    try:
        new_cid = int(cid)
        new_page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        new_cid = 1
        per_page = 10
    # if new_cid == 1:
    #     o_new_cid = ""
    # else:
    #     o_new_cid = (models.News.category_id == new_cid)

    # print (o_new_cid)
    # if o_new_cid.category_id == 1 :
    #     o_new_cid = None
    try:
        o_new_cid = ""
        if new_cid != 1:
            o_new_cid = (models.News.category_id == new_cid)
        paginate = models.News.query.filter(o_new_cid).order_by(models.News.update_time.desc()).paginate(new_page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    tl_page =  paginate.page
    tl_pages = paginate.pages
    tl_items = paginate.items

    tl_news_list = []
    for item in tl_items:
        tl_news_list.append(item.to_dict())


    return jsonify(errno=RET.OK,errmsg="数据查询成功",currentPage=tl_page,totalPage=tl_pages,newsList=tl_news_list)

#显示首页排行和分类信息
@index_blue.route('/',methods=["GET","POST"])
def show_index():
    #查看是否有session信息
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = models.User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    #排行显示前10条数据
    try:
        news_list =  models.News.query.order_by(models.News.clicks.desc()).limit(HOME_PAGE_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询新闻失败!")

    news_list_ne = [ ]
    for item in news_list:
        news_list_ne.append(item.to_dict())

    #显示分类
    try:
        category_list = models.Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询分类失败!")

    new_category_list = [ ]
    for category_item in category_list:
        new_category_list.append(category_item.to_dict())


    data = {
        "user_info":user.to_dict() if user else "",
        "news_list" : news_list_ne,
        "new_category_list" : new_category_list
    }

    return render_template("news/index.html",data=data)

    # return ('hello word')

@index_blue.route('/favicon.ico')
def get_web_logo():

    return current_app.send_static_file("news/favicon.ico")
