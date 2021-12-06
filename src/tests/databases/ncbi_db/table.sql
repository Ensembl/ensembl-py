CREATE TABLE `ncbi_taxa_name` (
`taxon_id` INTEGER  NOT NULL,
`name` TEXT NOT NULL,
`name_class` TEXT NOT NULL
);

CREATE TABLE `ncbi_taxa_node` (
`taxon_id` INTEGER  NOT NULL,
`parent_id` INTEGER  NOT NULL,
`rank` char(32) NOT NULL DEFAULT '',
`genbank_hidden_flag` tinyINTEGER NOT NULL DEFAULT '0',
`left_index` INTEGER NOT NULL DEFAULT '0',
`right_index` INTEGER NOT NULL DEFAULT '0',
`root_id` INTEGER NOT NULL DEFAULT '1',
PRIMARY KEY (`taxon_id`)
);

CREATE INDEX `ncbi_taxa_name_taxon_id` ON `ncbi_taxa_name` (`taxon_id`);
CREATE INDEX `ncbi_taxa_name_name` ON `ncbi_taxa_name` (`name`);
CREATE INDEX `ncbi_taxa_name_name_class` ON `ncbi_taxa_name` (`name_class`);
CREATE INDEX `ncbi_taxa_node_parent_id` ON `ncbi_taxa_node` (`parent_id`);
CREATE INDEX `ncbi_taxa_node_rank` ON `ncbi_taxa_node` (`rank`);
CREATE INDEX `ncbi_taxa_node_left_index` ON `ncbi_taxa_node` (`left_index`);
CREATE INDEX `ncbi_taxa_node_right_index` ON `ncbi_taxa_node` (`right_index`);
