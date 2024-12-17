DROP SCHEMA ambienteWeb;
CREATE DATABASE IF NOT EXISTS ambienteWeb;
USE `ambienteWeb`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`idAccount` int(11) NOT NULL AUTO_INCREMENT,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
);

INSERT INTO `accounts` (`id`, `username`, `password`, `email`) VALUES (1, 'test', '0ef15de6149819f2d10fc25b8c994b574245f193', 'test@test.com');

DELIMITER //
CREATE PROCEDURE passwordUsernameVerification(IN usernameIN VARCHAR(50), IN passwordIN VARCHAR(255))
BEGIN
    SELECT * FROM accounts WHERE username = usernameIN AND password = passwordIN;
END //
DELIMITER ;

