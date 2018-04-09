#!/usr/bin/python
# coding:utf-8
import sys
import os
import os.path
import subprocess
import argparse as arg
import stat
import json
import re

VERSION = '4.0.0'
APP = 'drz'
HOME = os.path.join(os.path.dirname(sys.argv[0]), '..')
pattern = re.compile(r'^([\da-z]+)\.(\w+-\d\.\d)$')
print('''
      _      _ _             ____             _             
     | | ___| | |_   _      |  _ \  ___ _ __ | | ___  _   _ 
  _  | |/ _ \ | | | | |_____| | | |/ _ \ '_ \| |/ _ \| | | |
 | |_| |  __/ | | |_| |_____| |_| |  __/ |_) | | (_) | |_| |
  \___/ \___|_|_|\__, |     |____/ \___| .__/|_|\___/ \__, |
                 |___/                 |_|            |___/ 
''')
print 'app code: %s' % APP
print 'home: %s' % HOME

parser = arg.ArgumentParser(prog="convert")
parser.add_argument('package', metavar='PACKAGE', type=str, help=u'发布包(.jar)')

parser.add_argument('-mv', '--major_version', required=True, help=u'主版本号')
parser.add_argument('-rv', '--revision_version', required=True, help=u'修正版本号')
parser.add_argument('-n', '--name', required=True, help=u'包名称')
args = parser.parse_args(sys.argv[1:])

config_path = os.path.join(HOME, 'config/akka.json')
f = open(config_path, 'r')
global_config = json.loads(f.read())
f.close()


def __get_command():
    """
    给执行脚本加上参数
    :return: 
    """
    script = 'java -jar %s' % args.package
    if script:
        # os.chmod(script, stat.S_IRWXU)  # Read, write, and execute by owner
        return script + ' %(app)s %(major_version)s %(revision_version)s %(hostname)s %(name)s %(zookeeper)s'


def startup(**kwargs):
    """
    升级
    :param kwargs: 
    :return: 
    """
    return __run_command(__get_command() % dict({}, **kwargs))


def __run_command(cmd):
    """
    启动worker
    :param cmd: 
    :return: 
    """
    cmd_args = ['nohup', cmd, '&']
    print "cmd =", ' '.join(cmd_args)
    subprocess.Popen(' '.join(cmd_args), shell=True)


def deploy():
    config = {
        'app': APP,
        'major_version': args.major_version,
        'revision_version': args.revision_version,
        'hostname': global_config['hostname'],
        'zookeeper': ','.join(global_config['zookeeper']),
        'name': args.name
    }
    startup(**config)

    print('finish...')
    exit(0)


"""
./jelly-deploy.py [-h] [-up | -p] -v VERSION PACKAGE
"""

print('args %s' % sys.argv)
print('after parse % s' % args)
deploy()
