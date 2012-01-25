-- phpMyAdmin SQL Dump
-- version 3.3.7deb7
-- http://www.phpmyadmin.net
--
-- Vert: localhost
-- Generert den: 25. Jan, 2012 16:23 PM
-- Tjenerversjon: 5.1.49
-- PHP-Versjon: 5.3.3-7+squeeze3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `pyyrlib`
--

-- --------------------------------------------------------

--
-- Tabellstruktur for tabell `countries`
--

CREATE TABLE IF NOT EXISTS `countries` (
  `countryid` int(11) NOT NULL AUTO_INCREMENT,
  `countrycode` varchar(2) NOT NULL,
  `countryname` varchar(20) NOT NULL,
  PRIMARY KEY (`countryid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dataark for tabell `countries`
--


-- --------------------------------------------------------

--
-- Tabellstruktur for tabell `verda`
--

CREATE TABLE IF NOT EXISTS `verda` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `countryid` int(11) NOT NULL,
  `placename` varchar(20) NOT NULL,
  `xml` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `countryid` (`countryid`),
  KEY `placename_2` (`placename`),
  FULLTEXT KEY `placename` (`placename`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dataark for tabell `verda`
--

