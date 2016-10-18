package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class ArticleBean {
  private final int myId;
  private final int myRawId;
  private final int myGeoId;
  private final String myContent;

  private final LinksBean myLinks;
  private final PropertiesBean myProperties;

  @JsonCreator
  public ArticleBean(@JsonProperty("id") int id, @JsonProperty("rawId") int rawId,
                     @JsonProperty("geoId") int geoId, @JsonProperty("content") String content,
                     @JsonProperty("links") LinksBean links, @JsonProperty("properties") PropertiesBean properties) {
    myId = id;
    myGeoId = geoId;
    myRawId = rawId;
    myContent = content;

    myLinks = links;
    myProperties = properties;
  }


  @JsonProperty("id")
  public int getId() {
    return myId;
  }

  @JsonProperty("rawId")
  public int getRawId() {
    return myRawId;
  }

  @JsonProperty("geoId")
  public int getGeoId() {
    return myGeoId;
  }

  @JsonProperty("content")
  public String getContent() {
    return myContent;
  }

  @JsonProperty("links")
  public LinksBean getLinks() {
    return myLinks;
  }

  @JsonProperty("properties")
  public PropertiesBean getProperties() {
    return myProperties;
  }
}
