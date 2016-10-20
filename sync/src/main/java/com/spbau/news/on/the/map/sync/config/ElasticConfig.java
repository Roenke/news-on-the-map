package com.spbau.news.on.the.map.sync.config;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ElasticConfig {
  private final String myAddress;
  private final int myPort;

  public ElasticConfig(@JsonProperty("host") String address, @JsonProperty("port") int port) {
    myAddress = address;
    myPort = port;
  }

  @JsonProperty("host")
  public String getAddress() {
    return myAddress;
  }

  @JsonProperty("port")
  public int getPort() {
    return myPort;
  }
}
