-- Create the user table
CREATE TABLE `user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `name` CHAR(255) NOT NULL,
  `admin` BOOLEAN NOT NULL
);

-- Create the resumes table
CREATE TABLE `resumes` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `text` TEXT NOT NULL,
  `date` BIGINT NOT NULL,
  `added_by` BIGINT UNSIGNED NOT NULL,
  CONSTRAINT `fk_resumes_user` FOREIGN KEY (`added_by`) REFERENCES `user`(`id`)
);

-- Create the job_descriptions table
CREATE TABLE `job_descriptions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `text` TEXT NOT NULL,
  `date` DATETIME NOT NULL,
  `added_by` BIGINT UNSIGNED NOT NULL,
  CONSTRAINT `fk_job_descriptions_user` FOREIGN KEY (`added_by`) REFERENCES `user`(`id`)
);

-- Create the documents table
CREATE TABLE `documents` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `resumes` BIGINT UNSIGNED NOT NULL,
  `jobs` BIGINT UNSIGNED NOT NULL,
  CONSTRAINT `fk_documents_resumes` FOREIGN KEY (`resumes`) REFERENCES `resumes`(`id`),
  CONSTRAINT `fk_documents_jobs` FOREIGN KEY (`jobs`) REFERENCES `job_descriptions`(`id`)
);

-- Create the doc_join table
CREATE TABLE `doc_join` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `job_descs` BIGINT UNSIGNED NOT NULL,
  `resumes` BIGINT UNSIGNED NOT NULL,
  CONSTRAINT `fk_doc_join_job_descs` FOREIGN KEY (`job_descs`) REFERENCES `job_descriptions`(`id`),
  CONSTRAINT `fk_doc_join_resumes` FOREIGN KEY (`resumes`) REFERENCES `resumes`(`id`)
);

-- Create the keyword table
CREATE TABLE `keywords` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `word` VARCHAR(255) NOT NULL UNIQUE
);

-- Create the relationship between keywords and resumes
CREATE TABLE `resume_keywords` (
  `resume_id` BIGINT UNSIGNED NOT NULL,
  `keyword_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`resume_id`, `keyword_id`),
  CONSTRAINT `fk_resume_keywords_resumes` FOREIGN KEY (`resume_id`) REFERENCES `resumes`(`id`),
  CONSTRAINT `fk_resume_keywords_keywords` FOREIGN KEY (`keyword_id`) REFERENCES `keywords`(`id`)
);

-- Create the relationship between keywords and job_descriptions
CREATE TABLE `job_desc_keywords` (
  `job_desc_id` BIGINT UNSIGNED NOT NULL,
  `keyword_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`job_desc_id`, `keyword_id`),
  CONSTRAINT `fk_job_desc_keywords_job_descs` FOREIGN KEY (`job_desc_id`) REFERENCES `job_descriptions`(`id`),
  CONSTRAINT `fk_job_desc_keywords_keywords` FOREIGN KEY (`keyword_id`) REFERENCES `keywords`(`id`)
);
