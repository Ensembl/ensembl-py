CREATE TABLE `ncbi_taxa_name` (
    `taxon_id`   INTEGER NOT NULL,
    `name`       VARCHAR(500) NOT NULL,
    `name_class` VARCHAR(50) NOT NULL
);
CREATE INDEX `taxon_id_idx` ON `ncbi_taxa_name` (`taxon_id`);
CREATE INDEX `name_idx` ON `ncbi_taxa_name` (`name`);
CREATE INDEX `name_class_idx` ON `ncbi_taxa_name` (`name_class`);

CREATE TABLE `ncbi_taxa_node` (
    `taxon_id`            INTEGER NOT NULL,
    `parent_id`           INTEGER NOT NULL,
    `rank`                VARCHAR(32) NOT NULL DEFAULT '',
    `genbank_hidden_flag` TINYINT NOT NULL DEFAULT '0',
    `left_index`          INTEGER NOT NULL DEFAULT '0',
    `right_index`         INTEGER NOT NULL DEFAULT '0',
    `root_id`             INTEGER NOT NULL DEFAULT '1',
    PRIMARY KEY (`taxon_id`)
);
CREATE INDEX `parent_id_idx` ON `ncbi_taxa_node` (`parent_id`);
CREATE INDEX `rank_idx` ON `ncbi_taxa_node` (`rank`);
CREATE INDEX `left_index_idx` ON `ncbi_taxa_node` (`left_index`);
CREATE INDEX `right_index_idx` ON `ncbi_taxa_node` (`right_index`);
