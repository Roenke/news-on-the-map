package com.spbau.news.on.the.map.sync;

import org.elasticsearch.action.admin.indices.exists.indices.IndicesExistsRequest;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;

import java.io.IOException;
import java.net.InetAddress;
import java.util.concurrent.ExecutionException;

public class EntryPoint {
  private EntryPoint() {
  }

  public static void main(String[] args) throws Exception {
    new EntryPoint().run();
  }

  private void run() throws IOException, ExecutionException, InterruptedException {
    TransportClient client = TransportClient.builder().build()
        .addTransportAddress(new InetSocketTransportAddress(InetAddress.getLocalHost(), 9300));

    final boolean isIndexExists = client.admin().indices().exists(new IndicesExistsRequest("news")).get().isExists();
    if (!isIndexExists) {
      client.admin().indices().prepareCreate("news").addMapping("article", ARTICLE_MAPPING).get();
    }

  }

  private static final String ARTICLE_MAPPING = "{\n" +
      "  \"article\": {\n" +
      "    \"properties\": {\n" +
      "      \"id\": {\n" +
      "        \"type\": \"integer\"\n" +
      "      },\n" +
      "      \"geo_id\": {\n" +
      "        \"type\": \"integer\"\n" +
      "      },\n" +
      "      \"raw_id\": {\n" +
      "        \"type\": \"integer\"\n" +
      "      },\n" +
      "      \"content\": {\n" +
      "        \"type\": \"string\"\n" +
      "      },\n" +
      "      \"links\": {\n" +
      "        \"type\": \"nested\",\n" +
      "        \"properties\": {\n" +
      "          \"source_url\": {\n" +
      "            \"type\": \"string\"\n" +
      "          },\n" +
      "          \"article_url\": {\n" +
      "            \"type\": \"string\"\n" +
      "          }\n" +
      "        }\n" +
      "      },\n" +
      "      \"properties\": {\n" +
      "        \"type\": \"nested\",\n" +
      "        \"properties\": {\n" +
      "          \"location\": {\n" +
      "            \"type\": \"geo_point\"\n" +
      "          },\n" +
      "          \"category\": {\n" +
      "            \"type\": \"integer\"\n" +
      "          },\n" +
      "          \"publish_date\": {\n" +
      "            \"type\": \"date\"\n" +
      "          }\n" +
      "        }\n" +
      "      }\n" +
      "    }\n" +
      "  }\n" +
      "}";
}
