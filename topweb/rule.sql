/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1
Source Server Version : 50045
Source Host           : 127.0.0.1:3306
Source Database       : topscan

Target Server Type    : MYSQL
Target Server Version : 50045
File Encoding         : 65001

Date: 2014-06-23 12:28:40
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for rule
-- ----------------------------
DROP TABLE IF EXISTS `rule`;
CREATE TABLE `rule` (
  `id` int(11) NOT NULL auto_increment,
  `rule_id` int(11) NOT NULL,
  `rule_name` char(255) NOT NULL,
  `run_type` tinyint(2) NOT NULL,
  `risk` char(8) default NULL,
  `priority` tinyint(2) NOT NULL,
  `filename` char(255) NOT NULL,
  `category_id` int(11) NOT NULL,
  `description` mediumtext NOT NULL,
  `solution` mediumtext NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of rule
-- ----------------------------
INSERT INTO `rule` VALUES ('1', '1', 'robots.txt站点结构泄露', '2', 'low', '1', 'robots_leak', '1', '', '');
INSERT INTO `rule` VALUES ('2', '2', 'Web应用指纹识别', '2', 'low', '1', 'app_fingure', '1', '', '');
INSERT INTO `rule` VALUES ('3', '3', '内部IP地址泄露', '1', 'low', '10', 'inter_ip_leak', '1', '', '');
INSERT INTO `rule` VALUES ('7', '7', 'SQL注入', '1', 'high', '1', 'sql_inject', '2', '', '');
INSERT INTO `rule` VALUES ('4', '4', '服务器错误', '1', 'middle', '1', 'server_error', '1', '', '');
INSERT INTO `rule` VALUES ('5', '5', '发现死链接', '1', 'low', '9', 'deak_link', '1', '', '');
INSERT INTO `rule` VALUES ('6', '6', '发现后台登陆页面', '2', 'low', '1', 'adminpage_leak', '1', '', '');
INSERT INTO `rule` VALUES ('8', '8', '跨站脚本攻击', '1', 'middle', '1', 'xss', '0', '', '');
INSERT INTO `rule` VALUES ('9', '9', '检测到文件上传', '1', 'high', '1', 'file_upload', '0', '', '');
INSERT INTO `rule` VALUES ('10', '10', '检测到phpMyAdmin', '2', 'low', '1', 'phpmyadmin_leak', '0', '', '');
INSERT INTO `rule` VALUES ('11', '11', '检测到WebShell', '1', 'high', '8', 'webshell_check', '0', '', '');
