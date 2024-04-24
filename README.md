# 小爱同学控制电脑开关机

利用接入米家第三方平台-巴法平台开放的MQTT接口，将Python程序部署到PVE上，随时操作电脑开关机；

> 注意：建议参考博客使用，必须配置ssh密钥才能设置远程关机，否则只能开机！！！

## 食用方法

[电脑入米家，让小爱同学随意操控电脑开关机](https://blog.csdn.net/cgy233/article/details/127407571)

### 1.修改config.ini配置文件

```dosini
# 目标主机的IP地址，windows下打开CMD输入命令ipconfig /all查看
[General]
broadcast=192.168.2.23

# 目标主机的MAC地址，windows下打开CMD输入命令ipconfig /all查看
[EthanPC]
mac=xx:xx:xx:xx:xx:xx

[MQTT_CONFIG]
bemfa_broker=bemfa.com
bemfa_port=9501
#巴法平台的主题名/设备名
bemfa_topic=ethanpc001
# 巴法平台控制台获取的私钥
bemfa_client_id=xxx

# 默认关闭，若需开启，自行配置钉钉机器人和获取京东移动端的cookie, 京东移动端地址：https://m.jd.com/, main.py 180-182行
[DINGDING_ROBOT_JD_BEAN]
#京东移动版获取的cookie
cookie=''
#钉钉机器人webhook
webhook=https://oapi.dingtalk.com/robot/send?access_token=xxx

```

### 2.将Python程序注册为Linux系统服务，开机自启动

为了方便我写了脚本，直接执行就行

```bash
cd EthanHome-WOL
./install.sh

```

> 想要卸载直接 ./uninstall.sh即可

### 3.常见错误

有小伙伴看到存在找不到主机名的问题：

```shell
Invalid Hostname specified
```

1.python版本需对应，比如我现在这个环境用的是python3，可以先使用命令测试是否通过再使用安装脚本，

```bash
python3 wol.py -p hostname
```

如果环境使用的是python，将mqtt.service文件的第8行的python3修改为python或你的python路径

2.感谢[@o9ltop](https://github.com/o9ltop)提醒，关于过了一段时间后巴法平台设备掉线的问题，为巴法平台挂掉后没有重连的问题，现在已把订阅放在连接后执行，测试了几天都稳定运行，放心食用

## 参考

[Wake-On-Lan-Python](https://github.com/bentasker/Wake-On-Lan-Python),
[多台WIN10之间的SSH免密登录](https://zhuanlan.zhihu.com/p/111812831)
