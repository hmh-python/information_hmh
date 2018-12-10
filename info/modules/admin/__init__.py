from flask import Blueprint,redirect,session,request

admin_blue = Blueprint("admin_blue",__name__,url_prefix="/admin")

from . import views

@admin_blue.before_request
def before_request():

    if not request.url.endswith('/admin/login'):
        if not session.get('is_admin'):
            return redirect('/')