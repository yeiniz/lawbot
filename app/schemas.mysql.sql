CREATE TABLE IF NOT EXISTS cases (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  jurisdiction VARCHAR(8) NOT NULL,
  external_id VARCHAR(191) NOT NULL,
  title VARCHAR(512), court VARCHAR(255), case_number VARCHAR(255),
  decision_date DATE, outcome VARCHAR(50), url VARCHAR(1024),
  cited_statutes JSON NULL, summary MEDIUMTEXT, body LONGTEXT,
  UNIQUE KEY uq_cases_external_id (external_id), KEY idx_cases_date (decision_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS statutes (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  jurisdiction VARCHAR(8) NOT NULL,
  law_id VARCHAR(191), law_name VARCHAR(512), article VARCHAR(255),
  url VARCHAR(1024), body LONGTEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS embeddings (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ref_table ENUM('cases','statutes') NOT NULL,
  ref_id BIGINT NOT NULL, model VARCHAR(255) NOT NULL, dim INT NOT NULL,
  vector LONGBLOB NOT NULL, KEY idx_embeddings_table_ref (ref_table, ref_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
