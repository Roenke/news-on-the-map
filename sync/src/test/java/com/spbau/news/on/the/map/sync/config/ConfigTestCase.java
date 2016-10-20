package com.spbau.news.on.the.map.sync.config;

public class ConfigTestCase {
  static final DatabaseConfig db = new DatabaseConfig("localhost", 5432, "user", "*****", "news");
  static final ElasticConfig elastic = new ElasticConfig("192.168.1.1", 9300);
}
