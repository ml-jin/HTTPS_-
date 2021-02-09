# HTTPS 的证书生成和使用

[TOC]

## [创建自定义ssl证书用于https](https://www.cnblogs.com/ddcoder/p/11044209.html)

这里，不探究证书原理。我们要完成的任务是，自己充当CA，然后签出证书供服务器使用。

本次教程是在windows实现，实验之前，确认自己的电脑中有openssl程序。如果没有，博主帮你准备了一个：http://download.okcoder.cn/openssl_create.zip

 

## 第一步：生成CA证书

1、创建私钥

openssl genrsa -out ca/ca-key.pem 1024

2、创建证书请求
openssl req -new -out ca/ca-req.csr -key ca/ca-key.pem

3、自签署证书，有效期10年
openssl x509 -req -in ca/ca-req.csr -out ca/ca-cert.pem -signkey ca/ca-key.pem -days 3650

4、将证书导出成浏览器支持的.p12格式 （这一步不需要，可以省略）
openssl pkcs12 -export -clcerts -in ca/ca-cert.pem -inkey ca/ca-key.pem -out ca/ca.p12

**创建之后，将这个根证书导入浏览器中（受信任的根证书颁发机构）：**

IE：双击第4步生成的p12证书文件

Firefox：选项->隐私与安全 ->证书->查看证书->将ca-cert.pem导入“证书颁发机构”

Chrome：“菜单”设置->左上角"设置"->高级->隐私设置和安全性->证书管理->受信任的根证书颁发机构->导入ca-cert.pem证书文件

##　第二步：生成Server证书

1、创建私钥

openssl genrsa -out server/server-key.pem 1024

2、创建证书请求
openssl req -new -out server/server-req.csr -key server/server-key.pem

（这一步，Common Name要填写自己的域名）

3、用自己的CA证书，签署Server证书
openssl x509 -req -in server/server-req.csr -out server/server-cert.pem -signkey server/server-key.pem -CA ca/ca-cert.pem -CAkey ca/ca-key.pem -CAcreateserial -days 3650

4、将证书导出成浏览器支持的.p12格式 （这一步不需要，可以省略）
openssl pkcs12 -export -clcerts -in server/server-cert.pem -inkey server/server-key.pem -out server/server.p12

**创建Server证书之后，与Ca证书合成完整的证书链：**

cat server-cert.pem ca-cert.pem > full.pem

## 第三步：将Server证书布署到服务器上

server {
    listen 80;
    listen 443 ssl;
    server_name 域名;    #这里的域名要和Server证书域名对应
    index index.html index.htm index.php;
    root 站点根目录;
    **ssl_protocols TLSv1.2 TLSv1.1 TLSv1;**

​    **ssl_certificate /path/to/full.pem;**
​    **ssl_certificate_key /path/to/server-key.pem;**

​    **ssl_prefer_server_ciphers on;**
​    **ssl_ciphers HIGH:!aNULL:!MD5;**


    location ~ .*\.(php|php5)?$
    {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        include fastcgi.conf;
    }
    location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$
    {
        expires 30d;
     }
    location ~ .*\.(js|css)?$
    {
        expires 1h;
    }
}

到这里，自签证书可以使用了。

实验结果：IE和Firefox都可以正常访问，但是Chrome却一直无法识别自签证书（NET::ERR_CERT_AUTHORITY_INVALID），如果有实验成功的小伙伴欢迎留言。

参考资料：

https://blog.csdn.net/xiaxiaorui2003/article/details/41312381