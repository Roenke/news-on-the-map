package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.*;

public class ArticleBeanTest extends BaseBeanTestCase {
  @Test
  public void serializeTest() throws IOException {
    ObjectMapper mapper = new ObjectMapper();

    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(article);
    System.out.println(json);
    ArticleBean after = mapper.readValue(json, ArticleBean.class);

    assertNotSame(after, article);
    assertEquals(article.getId(), after.getId());
    assertEquals(article.getGeoId(), after.getGeoId());
    assertEquals(article.getRawId(), after.getRawId());

    assertEquals(article.getContent(), after.getContent());
  }
}