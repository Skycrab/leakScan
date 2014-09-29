/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1
Source Server Version : 50045
Source Host           : 127.0.0.1:3306
Source Database       : topscan

Target Server Type    : MYSQL
Target Server Version : 50045
File Encoding         : 65001

Date: 2014-06-11 18:58:08
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for category
-- ----------------------------
DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` tinyint(4) NOT NULL auto_increment,
  `category_id` tinyint(4) default NULL,
  `category_name` char(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of category
-- ----------------------------
INSERT INTO `category` VALUES ('1', '1', '信息泄露');
