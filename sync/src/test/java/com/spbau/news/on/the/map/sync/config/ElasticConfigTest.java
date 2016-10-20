package com.spbau.news.on.the.map.sync.config;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.*;

public class ElasticConfigTest extends ConfigTestCase {
  @Test
  public void serializeTest() throws IOException {
    ObjectMapper mapper = new ObjectMapper();
    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(elastic);
    final ElasticConfig after = mapper.readValue(json, ElasticConfig.class);

    assertEquals(elastic.getAddress(), after.getAddress());
    assertEquals(elastic.getPort(), after.getPort());
  }
}