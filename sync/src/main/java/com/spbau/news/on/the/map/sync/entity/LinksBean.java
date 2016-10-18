package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class LinksBean {
  private final String mySourceUrl;

  private final String myArticleUrl;

  @JsonCreator
  public LinksBean(@JsonProperty("source_url") String source, @JsonProperty("article_url") String article) {
    mySourceUrl = source;
    myArticleUrl = article;
  }

  @JsonProperty("article_url")
  String getArticleAddress() {
    return myArticleUrl;
  }

  @JsonProperty("source_url")
  String getSourceAddress() {
    return mySourceUrl;
  }
}
