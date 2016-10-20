package com.spbau.news.on.the.map.sync.config;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DatabaseConfig {
  private final String myAddress;
  private final int myPort;
  private final String myUser;
  private final String myPassword;
  private final String myDatabase;

  public DatabaseConfig(@JsonProperty("host") String address, @JsonProperty("port") int port,
                        @JsonProperty("user") String user, @JsonProperty("password") String password,
                        @JsonProperty("database") String database) {
    myAddress = address;
    myPort = port;
    myUser = user;
    myPassword = password;
    myDatabase = database;
  }

  @JsonProperty("host")
  public String getAddress() {
    return myAddress;
  }

  @JsonProperty("port")
  public int getPort() {
    return myPort;
  }

  @JsonProperty("user")
  public String getUser() {
    return myUser;
  }

  @JsonProperty("password")
  public String getPassword() {
    return myPassword;
  }

  @JsonProperty("database")
  public String getDatabase() {
    return myDatabase;
  }
}
