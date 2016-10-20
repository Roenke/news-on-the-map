package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class LocationBean {
  private final float myLatitude;
  private final float myLongitude;

  @JsonCreator
  public LocationBean(@JsonProperty("lat") float lat, @JsonProperty("lon") float lon) {
    myLatitude = lat;
    myLongitude = lon;
  }

  @JsonProperty("lat")
  public float getLatitude() {
    return myLatitude;
  }

  @JsonProperty("lon")
  public float getLongitude() {
    return myLongitude;
  }
}
