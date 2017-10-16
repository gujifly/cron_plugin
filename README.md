# cron_plugin
供 open-falcon 系统使用，提供 windows 版的 plugins（插件式）脚本管理功能 

<br>

#### 背景
* open-falcon 监控系统 目前只提供了 linux 版的 agent 
* windows版的agent 我用的是 https://github.com/freedomkk-qfeng/windows-agent 这个开源项目
* linux 版的 agent 提供插件式管理功能，从 HBS 处获取配置，定时运行指定目录下的脚本，获取结果并发送到 Transfer
* windows 版暂时没有这个功能，于是乎自己实现一个，逻辑参照 linux 版 plugins

<br>

#### 部署
* 这个是一个 python 项目，需要客户机安装有 python 2.7 环境
* 复制到任意文件夹，增加一个每分钟运行一次的计划任务（用域环境的，可通过域控下发策略实现），运行 cron_plugin.py

<br>

#### 分布
* 所有要定时运行的脚本名称，以 “周期_文件名.后缀” 命名，放置在 plugins 文件夹内（或其子文件夹中，这个看 HBS 策略）
* 周期以 “秒” 为单位，对分钟取整，如 190_PortTest.py (每三分钟运行一次，结果 push 到 agent）
* 脚本运行管理方式： 8 进程并行，单进程 10 秒超时
