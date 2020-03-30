行为驱动测试集。
# 参考文档
* [Gherkin语法](https://julysxy.com/blog/2017/01/11/Cucumber-3/) 
* [behave文档](http://behave.readthedocs.io/en/stable/tutorial.html#)

# 用法指南
## 起步
  * PyCharm插件安装
  
  PyCharm plugins中选择安装Python BDD support...
  
  * 库安装
  
  需安装第三方库： behave，allure-behave
  
  * 编写feature文件
  
  每个产品在testcases下有一个独立的目录，所有feature文件都放在features目录下。
  
  采用中文命名，不添加子目录.
  
  如果要划分测试子集，可采用'.'分割的分级命名，例：测试集名.功能名.feature
  
  以下是几个例子：
  
      Feature: 用户登录
      作为应用使用者，我需要用户登录后按用户角色访问相应的功能，以便使用功能并明确流程和职责。

      @手工, @smoke
      Scenario: 一般用户登录
        Given 我是未登录状态
        When 我使用有效的用户名和手机号登录
        Then 我可以进入应用查看到我的用户信息
    
      @手工
      Scenario Outline: 用户角色鉴权
        Given 我是<role>类型用户
        When 我登录成功
        Then 可以打开<screen>界面
    
        Examples: 角色权限
          | role | screen  |
          | 客户经理 | 进件/宴请登记 |
          | 团队经理 | 进件/审批   |
          | 门店经理 | 某个菜单    |
          
  
  注意：Examples表格如果在最后，最后一行要加个回车空行，否则可能执行时丢了最后一行参数。
  
  * 生成代码
  
  当Given/When/Then子句还没有对应的step代码时，
  点击对应行前的Intention Action Suggested菜单, 
  选择"Create Step Definition",
  将在steps目录新建step文件，并生成一个子句的step代码。
  
  再在其他子句前选择Intention Action Suggested菜单，
  选择"Create all steps definition.
  （注意：step文件还不存在时不要选all steps,否则会只生成一个子句的代码，其他的要再做一次）
  
  * 添加测试代码
  
  behave会自动匹配features/steps下的代码文件，文件名无关，只匹配@Given/@when/@then等装饰器后的匹配字符串。
  
  behave支持几种匹配形式，生成的代码缺省使用regexp, 其他匹配方法参见[behave文档](http://behave.readthedocs.io/en/stable/tutorial.html#step-parameters)
  
  只要匹配上的step就是对应的执行代码，所以不同的步骤中如果表达式是相同的，就会复用同一个step函数。
  
  除了因为scenario outline自动生成参数，自己可以定义参数解析，以重用更多step函数。如：
  
        use_step_matcher('parse') #使用不同的匹配形式，对后面的所有代码生效
        @then("界面提示'{message}'")
        def step_impl(context,message):
            ...
  
  一般在@Then的step代码中使用assertion.
  
  * 执行测试
  
  在feature文件名上直接右键执行Run '...', 可能报错. 
  需要打开"Edit Configrations..", 将Work directory指定为feature文件所在的目录。
  
  如果报错"Test undefined"，应该是对应的step代码找不到，可以先通过Intention Action菜单生成一下。
  
  * 执行时生成allure报表数据
  
  在Terminal容器执行以下命令，可以在当前目录的result目录下生成allure需要的json文件 ：
  
  behave -f allure_behave.formatter:AllureFormatter -o result 项目对应的目录/features
  
  * 安装allure命令行程序
  
  安装allure，参考[命令行安装步骤](https://docs.qameta.io/allure/#_installing_a_commandline)。
  
   **Mac步骤**:
  
  执行 brew install allure 即可。
  
   **Windows步骤**:
  
  **以管理员方式**打开cmd, 执行﻿
  
  powershell -Version 3.0 
  
  打开powershell容器，执行：
  
      Set-ExecutionPolicy RemoteSigned -scope CurrentUser   
      iex (new-object net.webclient).downloadstring('https://get.scoop.sh') 
      exit 
      scoop install allure 
      scoop update allure
  
  * 查看报表
  
  执行以下命令生成报表，启动web服务，并打开浏览页面。result是指测试结果的目录，与前面步骤中behave -o参数一致即可。
  
  allure serve result
  
## 用例浏览页面
  
  可生成HTML页面浏览和搜索用例。使用docker容器运行（这个步骤将会加到Jenkins流水线上，当每次git提交后执行，并可以提供web链接浏览）
  
  [镜像生成和容器执行步骤](case_viewer/image/README.md)


