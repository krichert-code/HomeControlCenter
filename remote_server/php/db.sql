-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 10, 2023 at 08:45 AM
-- Server version: 10.5.20-MariaDB
-- PHP Version: 7.3.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `id21363354_hcc`
--

-- --------------------------------------------------------

--
-- Table structure for table `connections`
--

CREATE TABLE `connections` (
  `id` int(11) DEFAULT NULL,
  `req` varchar(2048) DEFAULT NULL,
  `res` varchar(8192) DEFAULT NULL,
  `reqAvailable` tinyint(1) NOT NULL,
  `resAvailable` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `connections`
--

INSERT INTO `connections` (`id`, `req`, `res`, `reqAvailable`, `resAvailable`) VALUES
(777, 'MDAwMDA3NzfdOTxtyH5kXaNe6eD9+TND/wRKugGM7z//LpsrS9yieRjtqezWAhfz9OmjzB1RB1c=\n', 'MDAwMDA3NzfHA8pcHDc/C4O2k+V1B0ytDDYRqZFpyixCijiwIGd1F3e1W28h3FHy9z3O2FilZ/uwNEjixiyZBwKinKWcKOQ/kedTjUTZJbsDMspfx59ZOg==', 0, 1);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
