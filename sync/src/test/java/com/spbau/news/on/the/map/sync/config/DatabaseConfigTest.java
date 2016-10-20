package com.spbau.news.on.the.map.sync.config;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.*;

public class DatabaseConfigTest extends ConfigTestCase {
  @Test
  public void serializeTest() throws IOException {
    ObjectMapper mapper = new ObjectMapper();
    final String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(db);
    DatabaseConfig after = mapper.readValue(json, DatabaseConfig.class);

    assertNotSame(db, after);
    assertEquals(db.getAddress(), after.getAddress());
    assertEquals(db.getPort(), after.getPort());
    assertEquals(db.getDatabase(), after.getDatabase());
    assertEquals(db.getUser(), after.getUser());
    assertEquals(db.getPassword(), after.getPassword());
  }
}