#coding:utf8

import os,time,json,socket
import falcon_common as FC
import python_rpc as PYRPC
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import logging,sys
from logging.handlers import RotatingFileHandler

##########################  设置 日志 logger #######################################
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Log等级总开关
#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
Rthandler = RotatingFileHandler('%s.log'%(sys.argv[0]), maxBytes=10*1024*1024,backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
Rthandler.setFormatter(formatter)
logger.addHandler(Rthandler)
#------------------------------- logger end ----------------------------------------#

#输出列表
p = []
#当前时间戳（秒）
timestamp = time.time()
#当前时间戳（分）
minutes = int(timestamp/60)
#插件目录
plugin_dir = "plugins"
#后缀名 -- 运行指令
suffix_cmd = {".py":"python",".exe":"NONE",".bat":"NONE"}
#当前待运行命令列表
cmd_list = []

#获取主机名
hostname = socket.gethostname()

# agent 配置文件
agent_conf = "C:\\windows-agent\cfg.json"


#遍历指定插件目录，返回待运行文件指令列表
def get_cmd_list(subdir):
    for root, dirs, files in os.walk("%s\\%s"%(plugin_dir,subdir), topdown=False):
        for name in files:
            if name.split('_')[0].isdigit(): #格式 cycle_filename.suffix
                cycle = (int(name.split('_')[0])/60) #循环间隔（分）
                if minutes%cycle == 0:
                    suffix = os.path.splitext(name)[1]  #获取后缀名
                    cmd_prefix = suffix_cmd[suffix]
                    if cmd_prefix == "NONE":
                        cmd_prefix = ""
                    cmd_list.append("%s %s" %(cmd_prefix,os.path.join(root, name)))


 # 各进程回调函数，收集结果
def collectMyResult(result):
    try:
        for enum in json.loads(result):
            p.append(enum)
    except:
        return

# 包装 worker 函数，确保超时中断进程
def abortable_worker(func, *args, **kwargs):
    timeout = kwargs.get('timeout', None)
    p = ThreadPool(1)
    res = p.apply_async(func, args=args)
    try:
        out = res.get(timeout)  # Wait timeout seconds for func to complete.
        return out
    except multiprocessing.TimeoutError:
        p.terminate()
        raise

#woker 函数，各进程分别执行此函数
def worker(*cmd):
   return FC.run_cmd('%s'*len(cmd)%(cmd))

def get_hbs(hbs_addr):
    addr = hbs_addr.split(':')[0].strip()
    port = hbs_addr.split(':')[1].strip()
    try:
        rpc = PYRPC.RPCClient((str(addr), int(port)))
        args = {"Hostname": hostname, "Checksum": ""}
        result = rpc.call("Agent.MinePlugins", args)
        logger.info(u'%s'%(result))
        return result
    except:
        logger.error(u"rpc connection failed !!!")
        exit(1)
        

# 执行命令，合并返回的结果
if __name__ == "__main__":
    #start_time = time.time()
    if not os.path.exists(agent_conf):
        logger.error(u"%s does not exist !"%(agent_conf))
        exit(1)
    try:
        f = open(agent_conf,'r')
        conf_dic = json.load(f,encoding='utf-8')
        hbs_addr = conf_dic[u'heartbeat'][u'addr']
        dir_list = list(get_hbs(str(hbs_addr))["Plugins"])
        for subdir in dir_list:
            get_cmd_list(subdir)
        pool = multiprocessing.Pool(processes = 8)
        for each in cmd_list:
            abortable_func = partial(abortable_worker, worker, timeout=10)
            pool.apply_async(abortable_func, args=each, callback=collectMyResult)
        pool.close()
        pool.join()
        #end_time = time.time()
        if p:
            #print json.dumps(p, sort_keys=True, indent=4)
            FC.postdata(p)
        #print "Cost Time : %f seconds"%(float(end_time - start_time))
    except Exception as e:
        logger.error(u'%s'%(e))
        exit(1)
