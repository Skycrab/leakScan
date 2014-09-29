/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1
Source Server Version : 50045
Source Host           : 127.0.0.1:3306
Source Database       : kehan

Target Server Type    : MYSQL
Target Server Version : 50045
File Encoding         : 65001

Date: 2014-07-03 13:58:05
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for rule
-- ----------------------------
DROP TABLE IF EXISTS `rule`;
CREATE TABLE `rule` (
  `id` int(11) NOT NULL auto_increment,
  `rule_id` int(11) NOT NULL,
  `rule_name` varchar(128) NOT NULL,
  `run_type` int(11) NOT NULL,
  `risk` varchar(8) NOT NULL,
  `priority` int(11) NOT NULL,
  `file_name` varchar(128) NOT NULL,
  `category_id` int(11) NOT NULL,
  `description` longtext NOT NULL,
  `solution` longtext NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of rule
-- ----------------------------
INSERT INTO `rule` VALUES ('1', '1', 'SQL注入', '1', 'high', '1', 'sql_inject', '1', '', '');
INSERT INTO `rule` VALUES ('2', '2', '跨站脚本攻击', '1', 'middle', '1', 'xss', '2', '', '');
INSERT INTO `rule` VALUES ('3', '3', '网页木马检测', '1', 'high', '2', 'webshell_check', '3', '', '');
INSERT INTO `rule` VALUES ('4', '4', '文件上传', '1', 'high', '1', 'file_upload', '4', '', '');
INSERT INTO `rule` VALUES ('5', '5', 'robots.txt站点结构泄露', '2', 'low', '3', 'robots_leak', '4', '', '');
INSERT INTO `rule` VALUES ('6', '6', '发现PhpMyadmin', '2', 'low', '4', 'phpmyadmin_leak', '4', '', '');
INSERT INTO `rule` VALUES ('7', '7', '内部IP地址泄露', '1', 'low', '8', 'inter_ip_leak', '4', '', '');
