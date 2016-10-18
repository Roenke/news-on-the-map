package com.spbau.news.on.the.map.sync;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.spbau.news.on.the.map.sync.config.DatabaseConfig;
import com.spbau.news.on.the.map.sync.config.GlobalConfiguration;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.elasticsearch.action.admin.indices.exists.indices.IndicesExistsRequest;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;

import java.io.File;
import java.io.IOException;
import java.net.InetAddress;
import java.util.concurrent.ExecutionException;

public class EntryPoint {
  private EntryPoint() {
  }

  private static ArgumentParser createParser() {
    ArgumentParser parser = ArgumentParsers.newArgumentParser("client")
        .description("Elasticsearch synchronization")
        .defaultHelp(true);

    parser.addArgument("--config")
        .type(String.class)
        .setDefault("./config.json")
        .help("path to json configuration file");

    return parser;
  }

  public static void main(String[] args) {
    final ArgumentParser parser = createParser();
    try {
      final Namespace namespace = parser.parseArgs(args);
      final String pathToConfig = namespace.getString("config");

      ObjectMapper mapper = new ObjectMapper();
      final GlobalConfiguration config = mapper.readValue(new File(pathToConfig), GlobalConfiguration.class);

      new EntryPoint().run(config);
    } catch (ArgumentParserException e) {
      parser.handleError(e);
    } catch (ExecutionException | InterruptedException e) {
      e.printStackTrace();
    } catch (JsonParseException e) {
      System.err.println("Cannot parse file");
    } catch (IOException e) {
      System.err.println("Errors occurred:" + e);
    }
  }

  private void run(GlobalConfiguration config) throws IOException, ExecutionException, InterruptedException {
    TransportClient client = TransportClient.builder().build()
        .addTransportAddress(new InetSocketTransportAddress(
            InetAddress.getByName(config.getElasticConfig().getAddress()),
            config.getElasticConfig().getPort()));

    final boolean isIndexExists = client.admin().indices().exists(new IndicesExistsRequest("news")).get().isExists();
    if (!isIndexExists) {
      client.admin().indices().prepareCreate("news").addMapping("article", ARTICLE_MAPPING).get();
    }

    sync(client, config.getDatabaseConfig());
  }

  private void sync(TransportClient client, DatabaseConfig dbConfig) {

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
