import configparser #引入模块

config = configparser.ConfigParser()    #类中一个方法 #实例化一个对象

config["DEFAULT"] = {'ServerAliveInterval': '45',
                      'Compression': r'%%(asctime)s [{job_id}] %%(name)s %%(levelname)-8s %%(lineno)-2d  %%(message)s',
                     'CompressionLevel': '9',
                     'ForwardX11':'yes'
                     }	#类似于操作字典的形式

config['bitbucket.org'] = {'User':'Atlan'} #类似于操作字典的形式

config['topsecret.server.com'] = {'Host Port':'50022','ForwardX11':'no'}

with open('example.ini', 'w') as configfile:

   config.write(configfile)	#将对象写入文件