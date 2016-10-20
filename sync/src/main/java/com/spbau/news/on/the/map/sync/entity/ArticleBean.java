package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Date;

public class ArticleBean {
  private final int myId;
  private final int myRawId;
  private final int myGeoId;
  private final String myContent;
  private final Date myDate;

  private final LinksBean myLinks;

  private final LocationBean myLocation;
  private final int myCategory;

  @JsonCreator
  public ArticleBean(@JsonProperty("id") int id, @JsonProperty("raw_id") int rawId,
                     @JsonProperty("geo_id") int geoId, @JsonProperty("content") String content,
                     @JsonProperty("publish_date") Date date, @JsonProperty("links") LinksBean links,
                     @JsonProperty("location") LocationBean loc, @JsonProperty("category") int category) {
    myId = id;
    myGeoId = geoId;
    myRawId = rawId;
    myContent = content;

    myDate = date;
    myLinks = links;

    myLocation = loc;
    myCategory = category;
  }


  @JsonProperty("id")
  public int getId() {
    return myId;
  }

  @JsonProperty("raw_id")
  public int getRawId() {
    return myRawId;
  }

  @JsonProperty("geo_id")
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

  @JsonProperty("publish_date")
  public Date getDate() {
    return myDate;
  }

  @JsonProperty("location")
  public LocationBean getLocation() {
    return myLocation;
  }

  @JsonProperty("category")
  public int getCategory() {
    return myCategory;
  }
}
