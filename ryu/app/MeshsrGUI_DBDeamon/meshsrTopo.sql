-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 29, 2014 at 09:45 PM
-- Server version: 5.5.35
-- PHP Version: 5.4.4-14+deb7u8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `meshsrTopo`
--

-- --------------------------------------------------------

--
-- Table structure for table `flowEntry`
--

CREATE TABLE IF NOT EXISTS `flowEntry` (
  `flowEntryID` int(11) NOT NULL,
  `flowID` int(11) NOT NULL,
  `flowSeqNum` int(11) NOT NULL,
  `dpid` char(16) COLLATE utf8_unicode_ci NOT NULL,
  `tableID` int(11) NOT NULL,
  `entryID` int(11) NOT NULL,
  `inPort` int(11) NOT NULL,
  `outPort` int(11) NOT NULL,
  `meterID` int(11) NOT NULL,
  `meterValue` int(11) NOT NULL,
  PRIMARY KEY (`flowEntryID`),
  KEY `dpid` (`dpid`),
  KEY `inPort` (`inPort`),
  KEY `outPort` (`outPort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `meshsr_connection`
--

CREATE TABLE IF NOT EXISTS `meshsr_connection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flow_info` varchar(50) NOT NULL DEFAULT '',
  `connect_info` text NOT NULL,
  `des` text NOT NULL,
  KEY `ID` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=58 ;

--
-- Dumping data for table `meshsr_connection`
--

INSERT INTO `meshsr_connection` (`id`, `flow_info`, `connect_info`, `des`) VALUES
(1, 'default', '[{"bid":"10","eid":"13","type":"dis"},{"bid":"11","eid":"13","type":"dis"}]', 'default flow info here'),
(4, 'flow2', '[{"bid":"10","eid":"13","type":"con"},{"bid":"11","eid":"13","type":"dis"}]', 'flow2 info here'),
(2, 'all', '[{"bid":"10","eid":"13","type":"con"},{"bid":"11","eid":"13","type":"con"}]', 'all flow info here'),
(3, 'flow1', '[{"bid":"10","eid":"13","type":"dis"},{"bid":"11","eid":"13","type":"con"}]', 'flow1 info here'),
(5, 'flow3', '[{"bid":"10","eid":"13","type":"con"},{"bid":"11","eid":"13","type":"con"}]', 'flow3 info here');

-- --------------------------------------------------------

--
-- Table structure for table `meshsr_node`
--

CREATE TABLE IF NOT EXISTS `meshsr_node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` int(11) NOT NULL DEFAULT '0',
  `x` int(11) NOT NULL DEFAULT '0',
  `y` int(11) NOT NULL DEFAULT '0',
  `type` int(11) NOT NULL DEFAULT '0',
  `des` varchar(255) NOT NULL DEFAULT '0',
  KEY `id` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=43 ;

--
-- Dumping data for table `meshsr_node`
--

INSERT INTO `meshsr_node` (`id`, `node_id`, `x`, `y`, `type`, `des`) VALUES
(40, 10, 300, 800, 0, 'eth1\n00:0a:35:01:00:01\n00000001\n0000000000000010\neth2\n00:0a:35:01:00:02\n00000002\n0000000000000010\neth3\n00:0a:35:01:00:03\n00000003\n0000000000000010\neth4\n00:0a:35:01:00:04\n00000004\n0000000000000010\n'),
(41, 11, 800, 300, 1, 'eth1\n00:0a:35:01:01:01\n00000001\n0000000000000011\neth2\n00:0a:35:01:01:02\n00000002\n0000000000000011\neth3\n00:0a:35:01:01:03\n00000003\n0000000000000011\neth4\n00:0a:35:01:01:04\n00000004\n0000000000000011\n'),
(42, 13, 400, 400, 1, 'eth1\n00:0a:35:01:03:01\n00000001\n0000000000000013\neth2\n00:0a:35:01:03:02\n00000002\n0000000000000013\neth3\n00:0a:35:01:03:03\n00000003\n0000000000000013\neth4\n00:0a:35:01:03:04\n00000004\n0000000000000013\n');

-- --------------------------------------------------------

--
-- Table structure for table `phyLink`
--

CREATE TABLE IF NOT EXISTS `phyLink` (
  `phyLinkID` int(11) NOT NULL AUTO_INCREMENT,
  `srcPort` int(11) NOT NULL,
  `dstPort` int(11) NOT NULL,
  PRIMARY KEY (`phyLinkID`),
  KEY `srcPort` (`srcPort`),
  KEY `dstPort` (`dstPort`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=68 ;

--
-- Dumping data for table `phyLink`
--

INSERT INTO `phyLink` (`phyLinkID`, `srcPort`, `dstPort`) VALUES
(64, 2460, 2468),
(65, 2468, 2460),
(66, 2467, 2463),
(67, 2463, 2467);

-- --------------------------------------------------------

--
-- Table structure for table `ports`
--

CREATE TABLE IF NOT EXISTS `ports` (
  `portID` int(11) NOT NULL AUTO_INCREMENT,
  `dpid` char(16) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'ethX',
  `MAC` varchar(20) CHARACTER SET utf32 COLLATE utf32_unicode_ci NOT NULL DEFAULT '00:00:00:00:00:00',
  `number` int(11) NOT NULL,
  PRIMARY KEY (`portID`),
  KEY `dpid` (`dpid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=2481 ;

--
-- Dumping data for table `ports`
--

INSERT INTO `ports` (`portID`, `dpid`, `name`, `MAC`, `number`) VALUES
(2457, '0000000000000010', 'eth1', '00:0a:35:01:00:01', 1),
(2458, '0000000000000010', 'eth2', '00:0a:35:01:00:02', 2),
(2459, '0000000000000010', 'eth3', '00:0a:35:01:00:03', 3),
(2460, '0000000000000010', 'eth4', '00:0a:35:01:00:04', 4),
(2461, '0000000000000011', 'eth1', '00:0a:35:01:01:01', 1),
(2462, '0000000000000011', 'eth2', '00:0a:35:01:01:02', 2),
(2463, '0000000000000011', 'eth3', '00:0a:35:01:01:03', 3),
(2464, '0000000000000011', 'eth4', '00:0a:35:01:01:04', 4),
(2465, '0000000000000013', 'eth1', '00:0a:35:01:03:01', 1),
(2466, '0000000000000013', 'eth2', '00:0a:35:01:03:02', 2),
(2467, '0000000000000013', 'eth3', '00:0a:35:01:03:03', 3),
(2468, '0000000000000013', 'eth4', '00:0a:35:01:03:04', 4),
(2469, '0000000000000014', 'eth1', '00:0a:35:01:04:01', 1),
(2470, '0000000000000014', 'eth2', '00:0a:35:01:04:02', 2),
(2471, '0000000000000014', 'eth3', '00:0a:35:01:04:03', 3),
(2472, '0000000000000014', 'eth4', '00:0a:35:01:04:04', 4),
(2473, '0000000000000015', 'eth1', '00:0a:35:01:05:01', 1),
(2474, '0000000000000015', 'eth2', '00:0a:35:01:05:02', 2),
(2475, '0000000000000015', 'eth3', '00:0a:35:01:05:03', 3),
(2476, '0000000000000015', 'eth4', '00:0a:35:01:05:04', 4),
(2477, '0000000000000017', 'eth1', '00:0a:35:01:07:01', 1),
(2478, '0000000000000017', 'eth2', '00:0a:35:01:07:02', 2),
(2479, '0000000000000017', 'eth3', '00:0a:35:01:07:03', 3),
(2480, '0000000000000017', 'eth4', '00:0a:35:01:07:04', 4);

-- --------------------------------------------------------

--
-- Table structure for table `serverNIC`
--

CREATE TABLE IF NOT EXISTS `serverNIC` (
  `serNICID` int(11) NOT NULL AUTO_INCREMENT,
  `peer` int(11) NOT NULL,
  `MAC` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`serNICID`),
  KEY `peer` (`peer`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `switches`
--

CREATE TABLE IF NOT EXISTS `switches` (
  `dpid` char(16) COLLATE utf8_unicode_ci NOT NULL,
  `x` int(11) NOT NULL DEFAULT '0',
  `y` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`dpid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `switches`
--

INSERT INTO `switches` (`dpid`, `x`, `y`) VALUES
('0000000000000010', 0, 0),
('0000000000000011', 0, 0),
('0000000000000013', 0, 0),
('0000000000000014', 0, 0),
('0000000000000015', 0, 0),
('0000000000000017', 0, 0);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `flowEntry`
--
ALTER TABLE `flowEntry`
  ADD CONSTRAINT `flowEntry_ibfk_1` FOREIGN KEY (`inPort`) REFERENCES `ports` (`portID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `flowEntry_ibfk_2` FOREIGN KEY (`outPort`) REFERENCES `ports` (`portID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `flowEntry_ibfk_3` FOREIGN KEY (`dpid`) REFERENCES `switches` (`dpid`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `phyLink`
--
ALTER TABLE `phyLink`
  ADD CONSTRAINT `phyLink_ibfk_1` FOREIGN KEY (`srcPort`) REFERENCES `ports` (`portID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `phyLink_ibfk_2` FOREIGN KEY (`dstPort`) REFERENCES `ports` (`portID`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `ports`
--
ALTER TABLE `ports`
  ADD CONSTRAINT `ports_ibfk_1` FOREIGN KEY (`dpid`) REFERENCES `switches` (`dpid`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `serverNIC`
--
ALTER TABLE `serverNIC`
  ADD CONSTRAINT `serverNIC_ibfk_1` FOREIGN KEY (`peer`) REFERENCES `ports` (`portID`) ON DELETE NO ACTION ON UPDATE NO ACTION;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
