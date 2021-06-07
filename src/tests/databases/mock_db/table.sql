CREATE TABLE `gibberish` (
    `id`      INT NOT NULL,
    `grp`     VARCHAR(20) DEFAULT NULL,
    `value`   INT DEFAULT NULL,
    PRIMARY KEY (`id`, `grp`),
    KEY (`id`)
);

CREATE TABLE `meta` (
    `meta_id` int(11) NOT NULL AUTO_INCREMENT,
    `species_id` int(10) unsigned DEFAULT '1',
    `meta_key` varchar(40) NOT NULL,
    `meta_value` text NOT NULL,
    PRIMARY KEY (`meta_id`),
    UNIQUE KEY `species_key_value_idx` (`species_id`, `meta_key`, `meta_value`(255)),
    KEY `species_value_idx` (`species_id`, `meta_value`(255))
);
