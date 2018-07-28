#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_socket()
import base64
import datetime
import json
import logging
import socket
import string
import sys
import time
import traceback
import types

import colorful
import gevent
import gevent.pool
import requests
import requests.exceptions
import requests.packages.urllib3.exceptions
import upyun
import upyun.modules.exception
from django.core.management.base import BaseCommand

import grouptb_app.models
import upyun_app.models

job_files = 0  # 已删的总文件数，每超过5000个就清零，用于防止同时打开的fd过多
jobs = []  # 删文件的jobs，同样每超过5000个就joinall然后清空
deleted_bytes = 0  # 总删除的文件字节数
deleted_files = 0  # 总删除的文件数
pool = None  # gevent pool
session = None  # requests的session，用于复用连接，减少TCP连接数和TIME_WAIT数

logger = None


class ColorFormatter(logging.Formatter):
    FORMAT = u"%(asctime)s %(levelname)s %(message)s"

    def __init__(self):
        logging.Formatter.__init__(self, self.FORMAT)

    def format(self, record):
        levelname = record.levelname
        if levelname in ('NOTSET', 'DEBUG'):
            record.levelname = colorful.cyan(levelname)
        elif levelname in ('INFO', ):
            record.levelname = colorful.green(levelname)
        elif levelname in ('WARNING', ):
            record.levelname = colorful.bold_yellow(levelname)
        elif levelname in ('ERROR', 'CRITICAL'):
            record.levelname = colorful.bold_red(levelname)
        return logging.Formatter.format(self, record)


def handle_exception(e):
        if isinstance(e, upyun.modules.exception.UpYunClientException):  # args, message, msg
            # Name or service not known, DNS暂时抽风了，可以忽略的异常
            # UpYunClientException: HTTPConnectionPool(host='v0.api.upyun.com', port=80): Max retries exceeded with url: /oebbt-420111/2016-11-08/jiaoxuedian/1478612487.000384.jpg (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7f76475c0f10>: Failed to establish a new connection: [Errno -2] Name or service not known',))
            if isinstance(e.msg, str) and 'Name or service not known' in e.msg:
                print datetime.datetime.now(), e.msg
                return
            # UpYunClientException: HTTPConnectionPool(host='v0.api.upyun.com', port=80): Max retries exceeded with url: /oebbt-450399/2016-10-20/zhi-shu/gui-lin-shi-zhong-shan-zhong-xue/1476932885.190000.jpg (Caused by ReadTimeoutError("HTTPConnectionPool(host='v0.api.upyun.com', port=80): Read timed out. (read timeout=60)",))
            # Read timed out可能是调用UpYun API要超过频率限制了？先sleep一会儿试试
            if isinstance(e.msg, str) and 'Read timed out' in e.msg:
                print datetime.datetime.now(), e.msg
                time.sleep(5)
                return
        elif isinstance(e, upyun.modules.exception.UpYunServiceException):  # args, err, headers, message, msg, request_id, status
            err = json.loads(e.err)
            if err['code'] == 40100012:  # bucket not exist
                logger.warning(e.err)
                return 40100012  # 需要跳过这个bucket
            if err['code'] == 40400001:  # file or directory not found, 可以忽略
                logger.warning(e.err)
                return 40400001

        traceback.print_exc()
        return


def handle_protocolerror(e):
    # 处理requests.packages.urllib3.exceptions.ProtocolError

    # 检查e.args[1]是否为socket.error，然后根据e.args[1].strerror分别处理
    # e.args: tuple(str, socket.error(args: tuple(int, str), errno: int, filename: None, message: str, strerror: str))
    # e.message: str
    if hasattr(e, 'args') and isinstance(e.args, tuple) and len(e.args) >= 2 and isinstance(e.args[1], socket.error):
        strerror = e.args[1].strerror
    else:
        logger.error('handle_protocolerror: e.args[0] %s' % e.args[0])
        logger.error('handle_protocolerror: e.args[1].args[0] %s' % e.args[1].args[0])
        logger.error('handle_protocolerror: e.args[1].args[1] %s' % e.args[1].args[1])
        logger.error('handle_protocolerror: e.args[1].errno %s' % e.args[1].errno)
        logger.error('handle_protocolerror: e.args[1].filename %s' % e.args[1].filename)
        logger.error('handle_protocolerror: e.args[1].message %s' % e.args[1].message)
        logger.error('handle_protocolerror: e.args[1].strerror %s' % e.args[1].strerror)
        sys.exit(-1)
    # Connection reset by peer估计是访问太快被upyun屏蔽了，需要退出重运行
    if strerror == 'Connection reset by peer':
        logger.error('Connection reset by peer')
        sys.exit(-1)
    else:
        logger.error('handle_protocolerror: e.args[0] %s' % e.args[0])
        logger.error('handle_protocolerror: e.args[1].args[0] %s' % e.args[1].args[0])
        logger.error('handle_protocolerror: e.args[1].args[1] %s' % e.args[1].args[1])
        logger.error('handle_protocolerror: e.args[1].errno %s' % e.args[1].errno)
        logger.error('handle_protocolerror: e.args[1].filename %s' % e.args[1].filename)
        logger.error('handle_protocolerror: e.args[1].message %s' % e.args[1].message)
        logger.error('handle_protocolerror: e.args[1].strerror %s' % e.args[1].strerror)
        sys.exit(-1)

def up_delete(up, name):
    # 封装up.delete，用于删目录，有错误时exit
    try:
        return up.delete(name)
    except (upyun.modules.exception.UpYunClientException, upyun.modules.exception.UpYunServiceException), e:
        handle_exception(e)

def async_delete_file(up, authstr, start_path, f):
    global session

    if f['type'] != u'N':
        return
    try:
        #url = 'http://%s/%s%s/%s' % (upyun.ED_AUTO, up.bucket, start_path, f['name'])
        url = 'http://%s/%s%s/%s' % (upyun.ED_AUTO, up.service, start_path, f['name'])
    except AttributeError:
        traceback.print_exc()
        print 'up:', up, dir(up)
        sys.exit(0)
    headers = {'Authorization': 'Basic %s' % authstr, 'x-upyun-async': 'true'}
    try:
        r = session.delete(url, headers=headers)
    except requests.exceptions.ConnectionError, e:
        # e.args(tuple),
        # e.errno(None),
        # e.filename(None),
        # e.message(requests.packages.urllib3.exceptions.MaxRetryError),
        #    e.message.args(tuple),
        #    e.message.message(str),
        #    e.message.pool(requests.packages.urllib3.connectionpool.HTTPConnectionPool),
        #    e.message.reason(requests.packages.urllib3.exceptions.ProtocolError),
        #    e.message.url(str)
        # e.request(requests.models.PreparedRequest),
        # e.response(None),
        # e.strerror(None)
        if hasattr(e, 'message') and isinstance(e.message, requests.packages.urllib3.exceptions.MaxRetryError) and hasattr(e.message, 'reason'):
            if isinstance(e.message.reason, requests.packages.urllib3.exceptions.ProtocolError):
                handle_protocolerror(e.message.reason)
            elif isinstance(e.message.reason, requests.packages.urllib3.exceptions.NewConnectionError):
                # e.message.reason.args(tuple)
                # e.message.reason.message(str): <...0x7fbf129ec9d0>: Failed to establish a new connection: [Errno -2] Name or service not known
                # e.message.reason.pool(requests.packages.urllib3.connection.HTTPConnection)
                # 如果出现DNS错误，就不断重试解析upyun域名，直到能够解析为止
                if e.message.reason.message.endswith('[Errno -2] Name or service not known'):
                    while True:
                        try:
                            print colorful.yellow('DNS error, starting resolving hostname...')
                            socket.gethostbyname(upyun.ED_AUTO)
                            break
                        except socket.gaierror, e:
                            if e.strerror == 'Name or service not known':
                                pass
                            else:
                                print e
                    return
                for attr in ('args', 'message', 'pool'):
                    print 'e.message.reason.%s:' % attr, type(getattr(e.message.reason, attr)), getattr(e.message.reason, attr)
            else:
                logger.warning('e.message.reason: %s' % type(e.message.reason))
            sys.exit(0)
        elif hasattr(e, 'message') and isinstance(e.message, requests.packages.urllib3.exceptions.ProtocolError):
            handle_protocolerror(e.message)
        else:
            print '#####'
            for attr in ('args', 'errno', 'filename', 'message', 'request', 'response', 'strerror'):
                print '%s:' % attr, type(getattr(e, attr)), getattr(e, attr)
            sys.exit(0)
    except Exception, e:
        print '+++++', type(e), dir(e)
        sys.exit(0)

def getlist(up, name):
    # 封装up.getlist，有错误时exit
    global logger
    if 1 < name.count('/') <= 3:  # 大于1级小于3级的目录，打log
        logger.info('getting list %s' % name)
    try:
        return up.getlist(name)
    except (upyun.modules.exception.UpYunClientException, upyun.modules.exception.UpYunServiceException), e:
        handle_exception(e)

def wipe_bucket(bucket, username, password, datelist):
    """
    遍历指定空间的所有符合datelist范围的/date目录，用协程删除所有文件和空的子目录
    """
    global logger
    up = upyun.UpYun(bucket, username, password, endpoint=upyun.ED_AUTO)
    if bucket.startswith('oebbt-'):
        grouptb = grouptb_app.models.GroupTB.objects.get(group_id=int(bucket[6:]))
        bucketstr = 'bucket: %s %s>%s>%s' % (bucket, grouptb.parent.parent.name, grouptb.parent.name, grouptb.name)
    else:
        bucketstr = bucket
    try:
        logger.info(u'%s 当前大小 %d MB' % (bucketstr, int(up.usage()) / 1024.0 / 1024))
        authstr = base64.b64encode('%s:%s' % (username, password))
        traverse_delete(up, '/', datelist, authstr)
        logger.info(u'%s 清理之后大小 %d MB' % (bucketstr, int(up.usage()) / 1024.0 / 1024))
    except upyun.modules.exception.UpYunServiceException, e:
        handle_exception(e)

def traverse_delete(up, start_path, datelist, authstr):
    """
    遍历指定bucket从某个start_path开始的目录，删除之下的所有文件或空目录
    """
    global job_files, jobs, deleted_bytes, deleted_files, pool, logger
    children = getlist(up, start_path)  # 先获取当前目录下的子目录或文件
    if children is None:
        return
    if len(children) == 0:  # 目录为空。如果不是根目录，就删除这个目录。
        if start_path != u'/':
            pool.spawn(up_delete, up, start_path)
        return
    files = []
    for f in children:
        try:
            if f['type'] == u'N':
                files.append(f)
        except KeyError:
            logger.error('KeyError: no type in f %s' % str(f))
            sys.exit(-1)
    if len(files) != 0:  # 目录下有文件，就批量删掉
        if start_path == u'/':
            jobs.extend([pool.spawn(up_delete, up, '/%s' % f['name']) for f in files])
        else:
            jobs.extend([pool.spawn(async_delete_file, up, authstr, start_path, f) for f in files])
        job_files += len(files)
        try:
            deleted_bytes += sum([int(f['size']) for f in files])
        except ValueError:
            # {'time': u'1491871202', 'type': u'N', 'name': u'1491871201.853000.jpg', 'size': u'undefined'}
            traceback.print_exc()
            print f
        deleted_files += len(files)
        if job_files >= 5000:  # 超过5000个，清零
            logger.warning(u'deleted %d MB, 空间占用 %d MB' % (deleted_bytes / 1024.0 / 1024, int(up.usage()) / 1024.0 / 1024))
            pool.wait_available()
            job_files = 0
            jobs = []
    # 接下来递归处理子目录
    # 注意：如果当前是在根目录，就要判断子目录是否在datelist要删除的日期列表里
    if start_path == u'/':
        folders = [f for f in children if f['type'] == u'F' and f['name'] in datelist]
    else:
        folders = [f for f in children if f['type'] == u'F']
    for folder in folders:
        if start_path == u'/':
            traverse_delete(up, '/%s' % folder['name'], datelist, authstr)
        else:
            traverse_delete(up, '%s/%s' % (start_path, folder['name']), datelist, authstr)
    # 其他节点？
    others = [f for f in children if f['type'] not in (u'F', u'N')]
    if len(others) != 0:
        logger.error('others: %s' % str(others))
        sys.exit(0)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('group_id', nargs='?', type=int)

    def handle(self, *args, **options):
        global deleted_bytes, deleted_files, logger, pool, session

        logger = logging.getLogger()
        #logger.setLevel(logging.NOTSET)  # requests有大量DEBUG log
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)

        pool = gevent.pool.Pool(1000)
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=1000, pool_maxsize=20000)
        session.mount('http://', adapter)

        datelist = [str(datetime.date(2014, 9, 1) + datetime.timedelta(days=x)) for x in range(1096)]
        #print datelist
        #return

        """遍历所有upyun空间，删除指定日期的目录树。"""
        q = upyun_app.models.OperatorToUpYunGroupTB.objects.all()

        # 长沙县的不删除
        q = q.exclude(upyungrouptb__grouptb__group_id=430121)

        # 如果命令行指定了group_id，就只删指定空间的
        if options['group_id']:
            q = q.filter(upyungrouptb__grouptb__group_id=options['group_id'])
        #"""
        for i in q:
            if i.upyungrouptb.grouptb.group_id in (420398, ):  # 420398 武当山的文件列表有点问题
                continue
            wipe_bucket('oebbt-%s' % i.upyungrouptb.grouptb.group_id, i.operator.username, i.operator.password, datelist)
        #"""
        # 如果没在命令行指定空间，再单独处理一下oe-test1
        if not options['group_id']:
            wipe_bucket('oe-test1', 'oseasy', 'oseasyoseasy', datelist)
        logger.info('total deleted: %d %d MB, %d files' % (deleted_bytes, deleted_bytes / 1024.0 / 1024, deleted_files))
