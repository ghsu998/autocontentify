-- ecommerce_data_db Schema
-- Version: 1.0
-- Description: Master DDL for ecommerce_data_db

-- TABLE: blogs
CREATE TABLE IF NOT EXISTS `blogs` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `title` varchar(255) NOT NULL,
    `content` mediumtext NOT NULL,
    `created_at` datetime DEFAULT current_timestamp(),
    `shopify_article_id` bigint(20) DEFAULT NULL,
    `synced_to_shopify` tinyint(1) DEFAULT 0,
    `last_updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: companies
CREATE TABLE IF NOT EXISTS `companies` (
    `company_id` int(11) NOT NULL AUTO_INCREMENT,
    `company_name` varchar(255) NOT NULL,
    `company_website` varchar(255) NOT NULL,
    `industry` varchar(255) DEFAULT NULL,
    `address` varchar(255) DEFAULT NULL,
    `contact_email` varchar(255) DEFAULT NULL,
    `contact_phone` varchar(20) DEFAULT NULL,
    `created_at` datetime DEFAULT current_timestamp(),
    `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    `google_ads_customer_id` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: keywords
CREATE TABLE IF NOT EXISTS `keywords` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `keyword` varchar(255) NOT NULL,
    `avg_monthly_searches` int(11) DEFAULT NULL,
    `competition_level` varchar(50) DEFAULT NULL,
    `created_at` datetime DEFAULT current_timestamp(),
    `keyword_group` varchar(50) DEFAULT NULL,
    `competition_index` float DEFAULT NULL,
    `low_bid_range` bigint(20) DEFAULT NULL,
    `high_bid_range` bigint(20) DEFAULT NULL,
    `monthly_search_volume` int(11) DEFAULT NULL,
    `low_top_of_page_bid_micros` bigint(20) DEFAULT NULL,
    `high_top_of_page_bid_micros` bigint(20) DEFAULT NULL,
    `low_top_of_page_bid_percentile` float DEFAULT NULL,
    `high_top_of_page_bid_percentile` float DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: orders
CREATE TABLE IF NOT EXISTS `orders` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `user_id` int(11) NOT NULL,
    `total_price` decimal(10,2) NOT NULL,
    `status` enum('pending','shipped','completed','cancelled') DEFAULT 'pending',
    `created_at` datetime DEFAULT current_timestamp(),
    `tracking_number` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: products
CREATE TABLE IF NOT EXISTS `products` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `shopify_product_id` bigint(20) NOT NULL,
    `name` varchar(255) NOT NULL,
    `description` text DEFAULT NULL,
    `price` decimal(10,2) DEFAULT NULL,
    `stock` int(11) DEFAULT NULL,
    `category_id` varchar(255) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `vendor` varchar(255) DEFAULT NULL,
    `weight` decimal(10,2) DEFAULT NULL,
    `images` text DEFAULT NULL,
    `inventory_policy` varchar(50) DEFAULT NULL,
    `status` varchar(50) DEFAULT NULL,
    `weight_unit` varchar(10) DEFAULT NULL,
    `last_updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `shopify_product_id` (`shopify_product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: product_variants
CREATE TABLE IF NOT EXISTS `product_variants` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `product_id` int(11) NOT NULL,
    `variant_id` bigint(20) NOT NULL,
    `variant_title` varchar(255) NOT NULL,
    `price` decimal(10,2) DEFAULT NULL,
    `sku` varchar(255) DEFAULT NULL,
    `inventory_quantity` int(11) DEFAULT NULL,
    `variant_weight` decimal(10,2) DEFAULT NULL,
    `variant_weight_unit` varchar(10) DEFAULT NULL,
    `created_at` datetime DEFAULT current_timestamp(),
    `last_updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `variant_id` (`variant_id`),
    KEY `fk_product_id` (`product_id`),
    CONSTRAINT `fk_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLE: users
CREATE TABLE IF NOT EXISTS `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `email` varchar(255) NOT NULL,
    `phone` varchar(15) DEFAULT NULL,
    `created_at` datetime DEFAULT current_timestamp(),
    `membership_level` varchar(50) DEFAULT 'basic',
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
