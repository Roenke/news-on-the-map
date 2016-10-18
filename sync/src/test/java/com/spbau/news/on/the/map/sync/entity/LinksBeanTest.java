package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;

public class LinksBeanTest extends BaseBeanTestCase {
  @Test
  public void serializeTest() throws IOException {
    ObjectMapper mapper = new ObjectMapper();

    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(links);
    System.out.println(json);
    final LinksBean after = mapper.readValue(json, LinksBean.class);

    assertEquals(links.getArticleAddress(), after.getArticleAddress());
    assertEquals(links.getSourceAddress(), after.getSourceAddress());
  }
}
