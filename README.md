# scUptime.py

Python script for checking site availability. Optional ability to look for string at URL target, verifying database availability, etc. Supports MySQL and MongoDB.

## Installation

Requires the following third party modules:

    requests
    argparse
    
If using default configuration files, modify scUptime.ini and choose either MongoDB or MySQL type and provide the parameters you wish to use.

If using MySQL, create destination table. Here is a sample table structure for the log table:

    CREATE TABLE IF NOT EXISTS `weblog` (
      `id` bigint(20) NOT NULL AUTO_INCREMENT,
      `siteName` varchar(64) NOT NULL,
      `status` varchar(16) NOT NULL,
      `msg` varchar(255) NOT NULL,
      `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `siteName` (`siteName`)
    ) ENGINE=InnoDB;


## Usage

python scUptime.py


## Configuration

Can specify configuration (--config) and URL files (--urls) through optional arguments.
    
## Version History

1.0.0
-----
- Script tested and released
    
## Authors

[William Lee](https://github.com/robotomeister)