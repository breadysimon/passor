# 用例浏览页面生成器

* build
 
  docker build -t caseviewer .

* 用法

  docker run -p 9999:80 caseviewer 

  http://localhost:9999/update : 自动从git-lab上拉取feature文件最新版本，生成html
  
  http://localhost:9999 : 浏览生成的html文件
  
 