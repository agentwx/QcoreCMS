#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2013-08-24 16:23:58
# @Author  : vfasky (vfasky@gmail.com)
# @Link    : http://vfasky.com
# @Version : $Id$
__all__ = [
    'Index',
    'Login',
]
import time

from xcat.web import RequestHandler, route, form, session
from xcat.utils import sha1
from tornado import gen
from tornado.web import asynchronous
from app.models import User
from ..api.helpers import admin_menu

@route(r"/admin", allow=['admin'])
class Index(RequestHandler):

    '''Admin Cp'''

    def get(self):
        #print self.current_user
        self.render('admin/index.html', admin_menu=admin_menu.list()['menu'])


@route(r"/admin/login")
class Login(RequestHandler):

    '''Admin Login'''

    @form('app.forms.Login')
    def get(self):
        self.render('admin/login.html', form=self.form)

    @form('app.forms.Login')
    @session
    @gen.engine
    @asynchronous
    def post(self):
        if not self.form.validate():
            self.render('admin/login.html',
                        form=self.form
                        )
            return
        # 防止穷举
        time.sleep(1.5)

        post = self.form.data
        user = User.select().where(User.email == post['email'])\
                            .where(User.password == sha1(post['password']))

        if 0 == (yield gen.Task(user.count)):
            self.form.email.errors.append('Email 或 密码错误')
            self.render('admin/login.html',
                        form=self.form
                        )
            return

        user = yield gen.Task(user.get)
        role_codes, role_ids = yield gen.Task(user.get_roles)

        # 写入 session
        self.set_current_user({
            'id': user.id,
            'gravatar': user.gravatar_url(80),
            'name': user.name,
            'email': user.email,
            'sex': user.sex,
            'roles': role_codes
        })

        self.redirect(route.url_for('admin.Index'))