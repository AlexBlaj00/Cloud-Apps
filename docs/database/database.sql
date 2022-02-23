-- MySQL dump 10.19  Distrib 10.3.29-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: test
-- ------------------------------------------------------
-- Server version	10.5.8-MariaDB-1:10.5.8+maria~focal

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'Pesti','Aici putem vedea pesti'),(2,'Google','Search on Google');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups_perm_relation`
--

LOCK TABLES `groups_perm_relation` WRITE;
/*!40000 ALTER TABLE `groups_perm_relation` DISABLE KEYS */;
INSERT INTO `groups_perm_relation` VALUES (1,1,1),(2,1,2),(3,1,3),(4,2,4);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'Pesti-vizualizare','Acest user poate vizualiza'),(2,'Pesti-editare','Acest user poate edita'),(3,'Pesti-Stergere','Acest user poate sterge'),(4,'Cautare-Google','Acest user poate cauta pe google');
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_groups_relation`
--

LOCK TABLES `user_groups_relation` WRITE;
/*!40000 ALTER TABLE `user_groups_relation` DISABLE KEYS */;
INSERT INTO `user_groups_relation` VALUES (1,1,1),(2,1,2),(3,2,1),(4,3,1),(5,3,2),(6,4,1),(7,5,1),(8,5,2),(9,6,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=euckr;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ovi','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','Ovi Pro','ovi.pro@yahoo.com','0773978453',1),(2,'mario','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','Mario Stuart','mario.stuart@yahoo.com','0773324313',0),(3,'andrei','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','Andrei Milano','andrei@yahoo.com','0723224313',1),(4,'ion','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','Ion Vesa','ion_vesa@yahooss.com','0723446313',0),(5,'george','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','George Vesa','g_vesa@yahooss.com','0767446313',1),(6,'andi','$5$rounds=535000$LoMOqM6Qy5BRSVtK$oxGFftJds1oUIgmwiyZmbwmrytNjE9JRb5ygeq.CXM5','Andi Popescu','andi_pop@yahooss.com','0790046313',0);
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

-- Dump completed on 2021-05-21 19:08:06
