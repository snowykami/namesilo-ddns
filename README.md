<center>

# namesilo-ddns

一个简易的DDNS服务

去tmd内网穿透

需要一个namesilo的域名

`python3.9+` `DDNS` `NameSilo`

## 开始使用

</center>

### 1.配置`config.json`(自行创建文件，可参考config.example)

| 字段             | 数据类型        | 备注                     | 默认值     |
|----------------|-------------|------------------------|---------|
| `key`          | `str`       | NameSilo的key，必填        | 无       |
| `host_ipv4`    | `str`       | ipv4主机记录，选择性必填         | 无       |
| `host_ipv6`    | `str`       | ipv6主机记录，选择性必填         | 无       |
| `domain`       | `str`       | 域名，必填                  | 无       |
| `duration`     | `int`       | ip检测间隔秒数，可选            | `600`   |
| `enable_email` | `bool`      | 是否启用邮件提示，如不启用则无需考虑后续字段 | `false` |
| `sender`       | `str`       | 邮件发送账户                 | 无       |
| `mail_host`    | `str`       | 邮箱服务器                  | 无       |
| `mail_port`    | `str`       | 邮箱服务端口                 | 无       |
| `mail_user`    | `str`       | 邮箱账户                   | 无       |
| `receivers`    | `list[str]` | 接收账户                   | 无       |
| `mail_auth`    | `str`       | 授权码                    | 无       |

### 2.运行

- Windows用户直接`run.cmd`启用，自动安装依赖
- Linux用户先用`pip3 install -r requirements.txt`安装依赖再运行`main.py`
- 可添加至计划任务程序使其在机器启动后运行
