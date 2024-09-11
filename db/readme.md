Making a single table directluy 

CREATE TABLE `job_descriptions` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `text` TEXT NOT NULL,
  `user_id` INT NULL,
  `date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `valid` BOOLEAN NOT NULL DEFAULT TRUE
);