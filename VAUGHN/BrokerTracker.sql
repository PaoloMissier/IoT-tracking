-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: BrokerTracker
-- ------------------------------------------------------
-- Server version	5.7.17

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
-- Table structure for table `CONS`
--

DROP TABLE IF EXISTS `CONS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CONS` (
  `consID` varchar(100) NOT NULL,
  `dataID` varchar(45) NOT NULL,
  `timestamp` datetime NOT NULL,
  `topic` varchar(255) DEFAULT NULL,
  `prodID` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`dataID`,`timestamp`,`consID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CONS`
--

LOCK TABLES `CONS` WRITE;
/*!40000 ALTER TABLE `CONS` DISABLE KEYS */;
/*!40000 ALTER TABLE `CONS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MSGCNT`
--

DROP TABLE IF EXISTS `MSGCNT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MSGCNT` (
  `consID` varchar(10) NOT NULL,
  `prodID` varchar(10) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `winID` int(11) DEFAULT NULL,
  `cnt` int(11) DEFAULT NULL,
  PRIMARY KEY (`consID`,`prodID`,`topic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MSGCNT`
--

LOCK TABLES `MSGCNT` WRITE;
/*!40000 ALTER TABLE `MSGCNT` DISABLE KEYS */;
/*!40000 ALTER TABLE `MSGCNT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PROD`
--

DROP TABLE IF EXISTS `PROD`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PROD` (
  `prodID` varchar(500) NOT NULL,
  `dataID` varchar(45) NOT NULL,
  `timestamp` datetime NOT NULL,
  `topic` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`dataID`,`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PROD`
--

LOCK TABLES `PROD` WRITE;
/*!40000 ALTER TABLE `PROD` DISABLE KEYS */;
/*!40000 ALTER TABLE `PROD` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `WDF`
--

DROP TABLE IF EXISTS `WDF`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WDF` (
  `PROD_dataID` varchar(45) NOT NULL,
  `PROD_timestamp` datetime NOT NULL,
  `CONS_dataID` varchar(45) NOT NULL,
  `CONS_timestamp` datetime NOT NULL,
  PRIMARY KEY (`PROD_dataID`,`PROD_timestamp`,`CONS_dataID`,`CONS_timestamp`),
  KEY `fk_WDF_PROD_idx` (`PROD_dataID`,`PROD_timestamp`),
  KEY `fk_WDF_CONS1_idx` (`CONS_dataID`,`CONS_timestamp`),
  CONSTRAINT `fk_WDF_CONS1` FOREIGN KEY (`CONS_dataID`, `CONS_timestamp`) REFERENCES `CONS` (`dataID`, `timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_WDF_PROD` FOREIGN KEY (`PROD_dataID`, `PROD_timestamp`) REFERENCES `PROD` (`dataID`, `timestamp`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `WDF`
--

LOCK TABLES `WDF` WRITE;
/*!40000 ALTER TABLE `WDF` DISABLE KEYS */;
/*!40000 ALTER TABLE `WDF` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `WINDOWS`
--

DROP TABLE IF EXISTS `WINDOWS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WINDOWS` (
  `winID` int(11) NOT NULL,
  `from` datetime DEFAULT NULL,
  `to` datetime DEFAULT NULL,
  PRIMARY KEY (`winID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `WINDOWS`
--

LOCK TABLES `WINDOWS` WRITE;
/*!40000 ALTER TABLE `WINDOWS` DISABLE KEYS */;
/*!40000 ALTER TABLE `WINDOWS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-03-10 12:10:34
