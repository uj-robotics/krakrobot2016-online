__author__ = 'sulphux'
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('KrakRobotTestServ.uploader.views',
    url(r'^list/$', 'list', name='list'),
)
