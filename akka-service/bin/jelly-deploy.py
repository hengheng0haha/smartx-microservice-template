#!/usr/bin/python
# coding:utf-8
import sys
import os
import os.path
import subprocess
import zipfile
import tarfile
import argparse as arg
import stat
import json
import re

VERSION = '1.0.0'
APP = 'drz'
DEFAULT_HOSTNAME = '127.0.0.1'
DEFAULT_MASTER = '127.0.0.1:2181'
HOME = os.path.join(sys.argv[0], '..')
pattern = re.compile(r'^([\da-z]+)\.(service-\w+-\d\.\d)$')
print('''
      _      _ _             ____             _             
     | | ___| | |_   _      |  _ \  ___ _ __ | | ___  _   _ 
  _  | |/ _ \ | | | | |_____| | | |/ _ \ '_ \| |/ _ \| | | |
 | |_| |  __/ | | |_| |_____| |_| |  __/ |_) | | (_) | |_| |
  \___/ \___|_|_|\__, |     |____/ \___| .__/|_|\___/ \__, |
                 |___/                 |_|            |___/ 
''')
print 'home: %s' % HOME

parser = arg.ArgumentParser(prog="convert")
parser.add_argument('package', metavar='PACKAGE', type=str, help=u'发布包(.zip)')

group = parser.add_mutually_exclusive_group()
group.add_argument('-up', '--upgrade', action='store_true', help=u'发布不兼容的版本')
group.add_argument('-p', '--patch', action='store_true', help=u'发布兼容版本')

parser.add_argument('-v', '--version', required=True, help=u'新的版本号或兼容的版本号')
args = parser.parse_args(sys.argv[1:])
OUTPUT_DIR = '/'.join(args.package.split('/')[:-1])
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
print 'output: %s' % OUTPUT_DIR

NAME = args.package.split('/')[-1:][0].split('-')[1]
print 'name: %s' % NAME

ZIP_PATH = os.path.join(os.getcwd(), args.package[0:-4])
match = pattern.match(os.path.split(ZIP_PATH)[1])
if match:
    ZIP_PATH = os.path.join(os.path.split(ZIP_PATH)[0], match.group(2))
print 'zip path: %s' % ZIP_PATH

try:
    config_path = os.path.join(HOME, 'config/akka.json')
    f = open(config_path, 'r')
    global_config = json.loads(f.read())
    f.close()
except FileNotFoundError as e:
    print 'no config found'
    exit(1)


def __find_runnable_script(path=ZIP_PATH):
    """
    查找gradle打包出来的执行脚本
    :param path: 
    :return: 
    """
    for parent, dirs, file_items in os.walk(os.path.join(path, 'bin')):
        for item in file_items:
            if not item.endswith(".bat"):
                return os.path.join(parent, item)


def __get_command():
    """
    给执行脚本加上参数
    :return: 
    """
    script = __find_runnable_script().replace(os.getcwd(), '')[1:]
    if script:
        os.chmod(script, stat.S_IRWXU)  # Read, write, and execute by owner
        return script + ' %(app)s %(version)s %(type)s %(hostname)s %(name)s %(zookeeper)s'


def unzip():
    """
    解压gradle打包出来的.zip或.tar包
    :return: 
    """
    if not is_newer():
        print('zip is older OR unzip failed')
        return True
    print('unzip... %s ---> %s' % (args.package, OUTPUT_DIR))
    if args.package.endswith('.zip'):
        with zipfile.ZipFile(args.package) as f:
            f.extractall(OUTPUT_DIR)
        return True
    elif args.package.endswith('.tar'):
        with tarfile.TarFile(args.package) as f:
            f.extractall(OUTPUT_DIR)
        return True
    else:
        print('FAILED...发布包必须是.zip或.tar!')
        parser.print_help()
        return False


def upgrade(**kwargs):
    """
    升级
    :param kwargs: 
    :return: 
    """
    return __run_command(__get_command() % dict({'type': 'upgrade', 'name': NAME}, **kwargs))


def patch(**kwargs):
    """
    补丁
    :param kwargs: 
    :return: 
    """
    return __run_command(__get_command() % dict({'type': 'patch', 'name': NAME}, **kwargs))


def __run_command(cmd):
    """
    启动worker
    :param cmd: 
    :return: 
    """
    cmd_args = ['nohup', cmd, '&']
    print("cmd =", cmd_args)
    subprocess.Popen(' '.join(cmd_args), shell=True)


def is_newer():
    """
    判断解压出来的文件夹是否比压缩包新
    :return: 
    """
    return os.stat(args.package).st_mtime >= os.stat(ZIP_PATH).st_mtime if os.path.isdir(ZIP_PATH) else True


def deploy():
    if unzip():
        os.chdir(ZIP_PATH)
        print('change dir to %s' % ZIP_PATH)
        config = {'app': APP,
                  'version': args.version,
                  'hostname': global_config['hostname'],
                  'zookeeper': ','.join(global_config['zookeeper'])}
        if args.upgrade:
            upgrade(**config)
        elif args.patch:
            patch(**config)
        else:
            parser.print_help()

    print('finish...')
    exit(0)


"""
./jelly-deploy.py [-h] [-up | -p] -v VERSION PACKAGE
"""

print('args %s' % sys.argv)
print('after parse % s' % args)
deploy()
