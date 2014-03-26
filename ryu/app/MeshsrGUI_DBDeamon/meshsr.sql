-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 26, 2014 at 07:28 PM
-- Server version: 5.5.35
-- PHP Version: 5.4.4-14+deb7u8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `meshr`
--

-- --------------------------------------------------------

--
-- Table structure for table `meshsr_connection`
--

CREATE TABLE IF NOT EXISTS `meshsr_connection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `begin_node_id` int(11) NOT NULL DEFAULT '0',
  `end_node_id` int(11) NOT NULL DEFAULT '0',
  `type` int(11) NOT NULL DEFAULT '0',
  `des` varchar(255) NOT NULL DEFAULT '0',
  KEY `ID` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=57 ;

--
-- Dumping data for table `meshsr_connection`
--

INSERT INTO `meshsr_connection` (`id`, `begin_node_id`, `end_node_id`, `type`, `des`) VALUES
(53, 10, 13, 0, '00000004-->00000004'),
(54, 13, 10, 0, '00000004-->00000004'),
(55, 13, 11, 0, '00000003-->00000003'),
(56, 11, 13, 0, '00000003-->00000003');

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
(40, 10, 0, 0, 0, 'eth1\n00:0a:35:01:00:01\n00000001\n0000000000000010\neth2\n00:0a:35:01:00:02\n00000002\n0000000000000010\neth3\n00:0a:35:01:00:03\n00000003\n0000000000000010\neth4\n00:0a:35:01:00:04\n00000004\n0000000000000010\n'),
(41, 11, 0, 0, 0, 'eth1\n00:0a:35:01:01:01\n00000001\n0000000000000011\neth2\n00:0a:35:01:01:02\n00000002\n0000000000000011\neth3\n00:0a:35:01:01:03\n00000003\n0000000000000011\neth4\n00:0a:35:01:01:04\n00000004\n0000000000000011\n'),
(42, 13, 0, 0, 0, 'eth1\n00:0a:35:01:03:01\n00000001\n0000000000000013\neth2\n00:0a:35:01:03:02\n00000002\n0000000000000013\neth3\n00:0a:35:01:03:03\n00000003\n0000000000000013\neth4\n00:0a:35:01:03:04\n00000004\n0000000000000013\n');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
