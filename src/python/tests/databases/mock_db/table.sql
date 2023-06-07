CREATE TABLE `gibberish` (
    `id`    INTEGER NOT NULL,
    `grp`   VARCHAR(20) DEFAULT "",
    `value` INT DEFAULT NULL,
    PRIMARY KEY (`id`, `grp`)
);
CREATE INDEX `id_idx` ON `gibberish` (`id`);
CREATE TABLE `meta` (
    `meta_id`    INTEGER PRIMARY KEY /*!40101 AUTO_INCREMENT */,
    `species_id` INTEGER /*!40101 UNSIGNED */ DEFAULT '1',
    `meta_key`   VARCHAR(40) NOT NULL,
    `meta_value` VARCHAR(255) NOT NULL
);
CREATE UNIQUE INDEX `species_key_value_idx` ON `meta` (`species_id`, `meta_key`, `meta_value`);
CREATE INDEX `species_value_idx` ON `meta` (`species_id`, `meta_value`);
