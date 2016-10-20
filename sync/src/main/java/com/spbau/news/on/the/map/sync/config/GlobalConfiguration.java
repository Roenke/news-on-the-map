package com.spbau.news.on.the.map.sync.config;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class GlobalConfiguration {
  private final DatabaseConfig myDatabaseConfig;
  private final ElasticConfig myElasticConfig;

  @JsonCreator
  public GlobalConfiguration(@JsonProperty("db")DatabaseConfig databaseConfig,
                             @JsonProperty("elastic") ElasticConfig elasticConfig) {
    myDatabaseConfig = databaseConfig;
    myElasticConfig = elasticConfig;
  }

  @JsonProperty("elastic")
  public ElasticConfig getElasticConfig() {
    return myElasticConfig;
  }

  @JsonProperty("db")
  public DatabaseConfig getDatabaseConfig() {
    return myDatabaseConfig;
  }
}
