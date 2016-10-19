package com.spbau.news.on.the.map.sync;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.spbau.news.on.the.map.sync.config.DatabaseConfig;
import com.spbau.news.on.the.map.sync.config.GlobalConfiguration;
import com.spbau.news.on.the.map.sync.entity.ArticleBean;
import com.spbau.news.on.the.map.sync.entity.LinksBean;
import com.spbau.news.on.the.map.sync.entity.LocationBean;
import com.spbau.news.on.the.map.sync.entity.PropertiesBean;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.elasticsearch.action.admin.indices.exists.indices.IndicesExistsRequest;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.postgresql.geometric.PGpoint;

import java.io.File;
import java.io.IOException;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;
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
    try {
      Class.forName("org.postgresql.Driver");
      ObjectMapper mapper = new ObjectMapper();
      Connection connection = DriverManager
          .getConnection(String.format("jdbc:postgresql://%s:%d/%s", dbConfig.getAddress(), dbConfig.getPort(),
              dbConfig.getDatabase()), dbConfig.getUser(), dbConfig.getPassword());
      final ResultSet resultSet = connection.createStatement().executeQuery(SELECT_READY_NEWS);
      while (resultSet.next()) {
        String sourceUrl = resultSet.getString("sourceUrl");
        String articleUrl = resultSet.getString("articleUrl");
        LinksBean links = new LinksBean(sourceUrl, articleUrl);

        Date date = resultSet.getDate("publishDate");
        int category = resultSet.getInt("category");
        final PGpoint location = (PGpoint) resultSet.getObject("location");
        LocationBean locationBean = new LocationBean((float) location.x, (float) location.y);

        PropertiesBean properties = new PropertiesBean(locationBean, category, date);

        int id = resultSet.getInt("id");
        int rawId = resultSet.getInt("rawId");
        int geoId = resultSet.getInt("geoId");

        String content = resultSet.getString("content");
        ArticleBean article = new ArticleBean(id, rawId, geoId, content, links, properties);
        String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(article);

        client.prepareIndex("news", "article", String.valueOf(id)).setSource(json).get();
        System.out.println("synchronized: " + System.lineSeparator() + json);
      }
    } catch (SQLException | JsonProcessingException e) {
      e.printStackTrace();
    } catch (ClassNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

  private static final String SELECT_READY_NEWS = "" +
      "select \n" +
      "\traw_news.id as rawId,\n" +
      "    geo_news.id as geoId,\n" +
      "    news.id as id,\n" +
      "    raw_news.content_of_news as content,\n" +
      "    raw_news.publish_date as publishDate,\n" +
      "    raw_news.source_url as sourceUrl,\n" +
      "    raw_news.article_url as articleUrl,\n" +
      "    geo_news.coord as location,\n" +
      "    news.category as category\n" +
      "from news \n" +
      "join geo_news\n" +
      "on news.geo_news_id = geo_news.id\n" +
      "join raw_news\n" +
      "on geo_news.raw_news_id = raw_news.id";

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
