AAE
========
>- AAE(Automatic Answering Engine)，是一个基于python研发的自动应答引擎，主要针对特定知识领域提供一问一答匹配服务，比如电影，保险，税务等专业领域，当然也可以用来打造一款闲聊机器人。

## QuickStart
>- 搭建好python相关环境，建议使用Anaconda3-5.1.0-Windows-x86_64.exe
>- 执行 pip install --no-index -f whls -r kbqa_sf/requirements.txt 命令安装本项目所需的包。（whls目录及文件下载：https://pan.baidu.com/s/1z3kUqId5AolcqrVGNUWdzQ 提取码：613u）
>- 创建mongodb数据库，在kbqa_config_blank.py中修改数据库相关配置，改完后务必将该文件重命名为kbqa_config.py
>- 下载搜狗词向量模型文件(链接：https://pan.baidu.com/s/1iCNgp3bjBgqgzoXUUPBgMw 提取码：j6xo) ，放入resources/trained_models目录下
>- 依次执行testmain.py中的CheckChatterbot('test_train_sf')、CheckChatterbot('test_train_talk')、CheckChatterbot('test_build_text_vec_indx')、CheckIntentClassifier('test_full_retrain_clf')项，其它项都注释掉，此时分类器模型会生成，数据库中也会准备好相应数据。
>- 从kbqa_main.py启动项目(修改app.run中的内容即可)
>- 直接访问 http://localhost:5002 即可开始聊天

## 语料注意事项
>- 特定领域的语料需要自行准备，路径：resources/original_corpus，该路径下有生产环境和开发环境目录，必须放入相应的语料文本，注意文本的命名：QA_sf_开头的表示“业务”语料，QA_talk开头的表示“闲聊”语料
>- 问题简洁明了，问题内容限制在100字以内
>- 答案简洁明了，答案内容限制在300字以内
>- 为了让回答更有礼貌，请在语料中注意礼貌用语的使用
>- 各类型的txt文件中的问答数量要尽量均衡，不要相差太大，比如不要出现一个txt里有几十条、但是某个txt里只有几条的情况

## 环境说明
>- python 3.6.4
>- mongodb-win32-x86_64-2008plus-ssl-4.0.4

## 补充说明
>- 在resources下手动创建几个空目录：corpus、learn、trained_models
>- 以上所有的python安装操作都建议在你创建的python虚拟环境下进行，什么是虚拟环境，以及如何创建，属于python相关内容，就不在本文档中介绍了。
>- 本项目中提供的前端UI仅仅使用了后台的部分接口，具体可以参考接口说明文档自行扩展前端的功能。
>- 执行testmain.py中的填充数据库的方法的时候，务必确保数据库中的所有集合已经删除，否则可能会出现重复数据。
>- 本引擎最重要的知识数据是original_corpus/question下的语料文件，所以只要这些语料文件完好保存，即便删除了模型和数据库集合，也能重新生成它们。
>- 部署到生产环境后，请使用python tornado_main.py来启动项目，会提供更高的可用性，记得修改该文件中的相关配置。
>- 在开发环境下，从kbqa_main.py启动项目，将会得到更详细的错误信息。

## 常见问题
- replicaSet是不是必须设置？
> 不是，一般情况下都不需要配置，除非你的MongoDB数据库已经配置好了replicaSet，否则，在连接字符串中去掉replicaSet即可。
- 有时候意图分类会出现分类错误，怎么回事？
> 一般分类错误的情况，常见的原因是数据分布不均匀，所以请尽量保证各个意图类别的样本数量相差不大。
- 在线学习的功能在数据量非常大的时候，比如某个意图分类下有超过5000个样本，学习还是很耗时的，这会不会影响系统的性能？
> 样本量达到一定规模的时候，不建议将在线学习开放给所有用户使用，目前在线学习的接口有两个，一个是记录，一个是学习，建议记录功能可以开放，而学习功能指定管理员或者采用定时器定期执行的方式，并定期维护学习样本的数据，让分布尽量均衡。
- 本项目和基于关键字的搜索方式相比，有什么优势？
> 基于关键字检索的方式是看搜索目标中是否包含关键字，未能考虑整个输入内容的语义，比如“外销发票汇率开错怎么办？”这个问题，基于关键字的检索会将所有包含“外销”，“发票”，“汇率”，“开错”，“怎么办”的文本都查询出来，而本项目是从整体考虑和问题相关的文本，所以简单来说就是前者查的更全，而后者查的更准。所以可以考虑混合使用。


