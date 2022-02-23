-- MySQL dump 10.16  Distrib 10.1.41-MariaDB, for Linux (x86_64)
--
-- Host: sql11.freemysqlhosting.net    Database: sql11402476
-- ------------------------------------------------------
-- Server version	5.5.62-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'Admins','We are the admins'),(2,'Users','We are the users'),(3,'Viewers','We are the viewers');
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups_perm_relation`
--

DROP TABLE IF EXISTS `groups_perm_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups_perm_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) DEFAULT NULL,
  `perm_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  KEY `perm_id` (`perm_id`),
  CONSTRAINT `groups_perm_relation_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `groups_perm_relation_ibfk_2` FOREIGN KEY (`perm_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups_perm_relation`
--

LOCK TABLES `groups_perm_relation` WRITE;
/*!40000 ALTER TABLE `groups_perm_relation` DISABLE KEYS */;
INSERT INTO `groups_perm_relation` VALUES (1,1,1),(2,1,2),(3,1,3);
/*!40000 ALTER TABLE `groups_perm_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'Vizualizare','Acest user poate vizualiza'),(2,'Editare','Acest user poate edita'),(3,'Stergere','Acest user poate sterge');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_groups_relation`
--

DROP TABLE IF EXISTS `user_groups_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_groups_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `user_groups_relation_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_groups_relation_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_groups_relation`
--

LOCK TABLES `user_groups_relation` WRITE;
/*!40000 ALTER TABLE `user_groups_relation` DISABLE KEYS */;
INSERT INTO `user_groups_relation` VALUES (1,3,1),(2,3,2);
/*!40000 ALTER TABLE `user_groups_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ovi','cvscvs','Ovi Pro','ovi.pro@yahoo.com','0773978453',1),(2,'pro','$5$rounds=535000$lv2xW1PMBJ6kLJQl$O8NAOrnAsfkyVQHDJvozViETHMgGkylACWR6CkCLqWA','Protiuc Pro?iuc','ovidiu.protiuc00@e-uvt.ro','0773978462',NULL),(3,'dia','$5$rounds=535000$NlNXjeWEpvDK5f.Z$ZNXYVw3LxYhrVX.r6FGbP6SGYSr.ehXBNIP/gP2u8D.','diana','dia@yahoo.com','044257654',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-21  9:07:12
