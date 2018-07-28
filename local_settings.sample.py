#!/usr/bin/env python
# -*- coding: utf-8 -*-

# copy this file to local_settings.py

DEBUG = False

DATABASE_NAME = 'grouptb_service'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '3306'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'oseasy'

# STATIC_ROOT指定部署时static目录的位置，开发时可以不管
STATIC_ROOT = '/usr/share/nginx/static-files/grouptb-service'
