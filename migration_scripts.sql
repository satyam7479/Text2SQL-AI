## lo_askllm_logs

CREATE TABLE `lo_askllm_logs` (
  `id` int NOT NULL,
  `question` text NOT NULL COMMENT 'Question ask to Lokaly',
  `query` longtext COMMENT 'Search Result Query',
  `ip_address` varchar(100) DEFAULT NULL,
  `created_on` datetime NOT NULL,
  `created_by_id` int NOT NULL COMMENT 'user_id who asks to lokaly'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='This table is used for store the Ask to Lokaly all user Logs';

--
-- Dumping data for table `lo_askllm_logs`
--

INSERT INTO `lo_askllm_logs` (`id`, `question`, `query`, `ip_address`, `created_on`, `created_by_id`) VALUES
(1, 'How many customers registered today?', NULL, '202.131.102.226', '2024-04-25 11:38:04', 309),
(2, 'How many orders were delivered', NULL, '202.131.102.226', '2024-04-25 11:38:04', 309),
(3, 'How many orders were made by Chirendu Gupta till date?', NULL, '202.131.102.226', '2024-04-25 11:44:26', 309),
(4, 'List my store details?', NULL, '202.131.102.226', '2024-04-25 11:44:59', 309),
(5, 'Provide the default address of the customer Chirendu Gupta', NULL, '202.131.102.226', '2024-04-25 11:44:59', 309);


ALTER TABLE `lo_askllm_logs` CHANGE `id` `id` INT NOT NULL AUTO_INCREMENT, add PRIMARY KEY (`id`);
ALTER TABLE `lo_askllm_logs`  ADD `store_id` INT NULL  AFTER `query`;


###lo_master_queries

CREATE TABLE `lo_master_queries` (
   `id` INT NOT NULL AUTO_INCREMENT ,  
   `questions` TEXT NOT NULL ,  
   `query` LONGTEXT NOT NULL ,  
   `role_type` BOOLEAN NOT NULL COMMENT '0 for Platform and 1 for Store' ,  
   `added_by` BOOLEAN NOT NULL COMMENT '0 for AI and 1 for Manually' ,  
   `active` BOOLEAN NOT NULL COMMENT '0 for Inactive and 1 for Active' ,  
   `created_on` DATETIME NOT NULL ,    PRIMARY KEY  (`id`)) ENGINE = InnoDB;
ALTER TABLE `lo_master_queries` ADD `updated_on` DATETIME NULL DEFAULT NULL AFTER `created_on`;
ALTER TABLE `lo_master_queries` CHANGE `role_type` `role_type` VARCHAR(50) NOT NULL;
ALTER TABLE `lo_master_queries` CHANGE `added_by` `added_by` VARCHAR(100) NOT NULL;

02/05/2024
ALTER TABLE `lo_master_queries` ADD `deleted_at` TIMESTAMP NULL AFTER `updated_on`;
ALTER TABLE `lo_master_queries` CHANGE `updated_on` `updated_on` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

06/05
ALTER TABLE `lo_master_queries` ADD `query_status` VARCHAR(50) NULL AFTER `query`;
ALTER TABLE `lo_master_queries` CHANGE `query` `query` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL;

07/05
ALTER TABLE `lo_master_queries` DROP `query_status`;

24/july/24
ALTER TABLE `lo_askllm_logs` ADD `master_id` INT NULL AFTER `question`;
ALTER TABLE `lo_askllm_logs` CHANGE `master_id` `master_id` INT NULL DEFAULT NULL COMMENT 'search result query id';
"ALTER TABLE `lo_askllm_logs` DROP `query`;"

09/sep/24
ALTER TABLE `lo_askllm_logs` ADD `active` BOOLEAN NULL DEFAULT NULL COMMENT 'status of query from master' AFTER `master_id`;