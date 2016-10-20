package com.spbau.news.on.the.map.sync.entity;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;

public class LocationBeanTest extends BaseBeanTestCase {
  @Test
  public void SerializeTest() throws IOException {
    final ObjectMapper mapper = new ObjectMapper();

    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(location);
    System.out.println(json);
    LocationBean after = mapper.readValue(json, LocationBean.class);

    assertEquals(location.getLatitude(), after.getLatitude(), 1e-6);
    assertEquals(location.getLongitude(), after.getLongitude(), 1e-6);
  }
}