CREATE DATABASE bitcoin;
USE bitcoin;

CREATE TABLE blocks (
    block_height INT PRIMARY KEY,
    block_hash VARCHAR(100)
);

