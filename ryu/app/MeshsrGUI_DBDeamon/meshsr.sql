-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 15, 2014 at 01:50 PM
-- Server version: 5.5.35
-- PHP Version: 5.4.4-14+deb7u8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `meshsr`
--

-- --------------------------------------------------------

--
-- Table structure for table `flowEntry`
--

CREATE TABLE IF NOT EXISTS `flowEntry` (
  `flowEntryID` int(11) NOT NULL,
  `flowID` int(11) NOT NULL,
  `flowSeqNum` int(11) NOT NULL,
  `dpid` char(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `meshsr_connection`
--

CREATE TABLE IF NOT EXISTS `meshsr_connection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flow_info` varchar(50) NOT NULL DEFAULT '',
  `connect_info` text NOT NULL,
  `des` text NOT NULL,
  `control_node` text NOT NULL,
  KEY `ID` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=63 ;

--
-- Dumping data for table `meshsr_connection`
--

INSERT INTO `meshsr_connection` (`id`, `flow_info`, `connect_info`, `des`, `control_node`) VALUES
(62, 'default', '[{"bid": "0000000000000010", "type": "dis", "eid": "0000000000000013"}, {"bid": "0000000000000013", "type": "dis", "eid": "0000000000000010"}, {"bid": "0000000000000013", "type": "dis", "eid": "0000000000000011"}, {"bid": "0000000000000011", "type": "dis", "eid": "0000000000000013"}, {"bid": "F000000000000001", "type": "dis", "eid": "0000000000000010"}, {"bid": "F000000000000003", "type": "dis", "eid": "0000000000000010"}, {"bid": "F000000000000004", "type": "dis", "eid": "0000000000000010"}, {"bid": "F000000000000005", "type": "dis", "eid": "0000000000000010"}]', 'physical links', ''),
(4, 'flow2', '[{"bid":"10","eid":"13","type":"con"},{"bid":"11","eid":"13","type":"dis"}]', 'flow2 info here', '[{"nid":"0000000000000010","meter":"198"},{"nid":"0000000000000012","meter":"6"}]');

-- --------------------------------------------------------

--
-- Table structure for table `meshsr_node`
--

CREATE TABLE IF NOT EXISTS `meshsr_node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` char(16) NOT NULL,
  `x` int(11) NOT NULL DEFAULT '0',
  `y` int(11) NOT NULL DEFAULT '0',
  `type` int(11) NOT NULL DEFAULT '0',
  `des` varchar(255) NOT NULL DEFAULT '0',
  KEY `id` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=221 ;

--
-- Dumping data for table `meshsr_node`
--

INSERT INTO `meshsr_node` (`id`, `node_id`, `x`, `y`, `type`, `des`) VALUES
(211, '0000000000000010', 0, 0, 0, 'dpid:0000000000000010'),
(212, '0000000000000011', 0, 0, 0, 'dpid:0000000000000011'),
(213, '0000000000000013', 0, 0, 0, 'dpid:0000000000000013'),
(214, '0000000000000014', 0, 0, 0, 'dpid:0000000000000014'),
(215, '0000000000000015', 0, 0, 0, 'dpid:0000000000000015'),
(216, '0000000000000017', 0, 0, 0, 'dpid:0000000000000017'),
(217, 'F000000000000001', 0, 0, 1, 'server_nic_MAC:94:de:80:86:d3:dd'),
(218, 'F000000000000003', 0, 0, 1, 'server_nic_MAC:94:de:80:86:d3:de'),
(219, 'F000000000000004', 0, 0, 1, 'server_nic_MAC:94:de:80:86:d3:d4'),
(220, 'F000000000000005', 0, 0, 1, 'server_nic_MAC:94:de:80:86:d3:d3');

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
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=326 ;

--
-- Dumping data for table `phyLink`
--

INSERT INTO `phyLink` (`phyLinkID`, `srcPort`, `dstPort`) VALUES
(320, 3162, 3154),
(321, 3154, 3162),
(322, 3157, 3161),
(323, 3159, 3167),
(324, 3161, 3157),
(325, 3167, 3159);

-- --------------------------------------------------------

--
-- Table structure for table `ports`
--

CREATE TABLE IF NOT EXISTS `ports` (
  `portID` int(11) NOT NULL AUTO_INCREMENT,
  `dpid` char(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT 'ethX',
  `MAC` varchar(20) CHARACTER SET utf32 COLLATE utf32_unicode_ci NOT NULL DEFAULT '00:00:00:00:00:00',
  `number` int(11) NOT NULL,
  PRIMARY KEY (`portID`),
  KEY `dpid` (`dpid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3169 ;

--
-- Dumping data for table `ports`
--

INSERT INTO `ports` (`portID`, `dpid`, `name`, `MAC`, `number`) VALUES
(3153, '0000000000000010', 'eth1', '00:0a:35:01:00:01', 1),
(3154, '0000000000000010', 'eth2', '00:0a:35:01:00:02', 2),
(3155, '0000000000000010', 'eth3', '00:0a:35:01:00:03', 3),
(3156, '0000000000000010', 'eth4', '00:0a:35:01:00:04', 4),
(3157, '0000000000000011', 'eth1', '00:0a:35:01:01:01', 1),
(3158, '0000000000000011', 'eth2', '00:0a:35:01:01:02', 2),
(3159, '0000000000000011', 'eth3', '00:0a:35:01:01:03', 3),
(3160, '0000000000000011', 'eth4', '00:0a:35:01:01:04', 4),
(3161, '0000000000000012', 'eth1', '00:0a:35:01:02:01', 1),
(3162, '0000000000000012', 'eth2', '00:0a:35:01:02:02', 2),
(3163, '0000000000000012', 'eth3', '00:0a:35:01:02:03', 3),
(3164, '0000000000000012', 'eth4', '00:0a:35:01:02:04', 4),
(3165, '0000000000000013', 'eth1', '00:0a:35:01:03:01', 1),
(3166, '0000000000000013', 'eth2', '00:0a:35:01:03:02', 2),
(3167, '0000000000000013', 'eth3', '00:0a:35:01:03:03', 3),
(3168, '0000000000000013', 'eth4', '00:0a:35:01:03:04', 4);

-- --------------------------------------------------------

--
-- Table structure for table `serverNIC`
--

CREATE TABLE IF NOT EXISTS `serverNIC` (
  `serNICID` char(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT 'FFFFFFFFFFFFFFFF',
  `peer` int(11) NOT NULL,
  `MAC` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`serNICID`),
  KEY `peer` (`peer`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `switches`
--

CREATE TABLE IF NOT EXISTS `switches` (
  `dpid` char(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `x` int(11) NOT NULL DEFAULT '0',
  `y` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`dpid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `switches`
--

INSERT INTO `switches` (`dpid`, `x`, `y`) VALUES
('0000000000000010', 0, 0),
('0000000000000011', 0, 0),
('0000000000000012', 0, 0),
('0000000000000013', 0, 0);

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
