package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;

public class PropertiesBeanTest extends BaseBeanTestCase {
  @Test
  public void serializeTest() throws IOException {
    ObjectMapper mapper = new ObjectMapper();

    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(properties);
    System.out.println(json);
    final PropertiesBean after = mapper.readValue(json, PropertiesBean.class);

    assertEquals(properties.getCategory(), after.getCategory());
    assertEquals(properties.getDate(), after.getDate());
    assertEquals(properties.getLocation().getLatitude(), after.getLocation().getLatitude(), 1e-6);
    assertEquals(properties.getLocation().getLongitude(), after.getLocation().getLongitude(), 1e-6);
  }
}