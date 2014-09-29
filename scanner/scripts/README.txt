plugins--规则脚本
规则脚本命名规范：
  都用小写，用下划线隔开，只能是字母数字下划线

规则脚本分为两类
1.基于域名扫描的
	不需要爬虫爬取的链接，如：cms指纹识别规则
	如:inter_ip_leak.py, robots_leak.py

2.基于url扫描的
	需要爬虫爬取的链接以及详细参数
	如：sql_inject
