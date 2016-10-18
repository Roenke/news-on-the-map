package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Date;

public class PropertiesBean {
  private final LocationBean myLocation;
  private final int myCategory;
  private final Date myDate;

  @JsonCreator
  public PropertiesBean(@JsonProperty("location") LocationBean loc, @JsonProperty("category") int category,
                        @JsonProperty("date") Date date) {
    myLocation = loc;
    myCategory = category;
    myDate = date;
  }

  @JsonProperty("location")
  public LocationBean getLocation() {
    return myLocation;
  }

  @JsonProperty("category")
  public int getCategory() {
    return myCategory;
  }

  @JsonProperty("date")
  public Date getDate() {
    return myDate;
  }
}
