package com.spbau.news.on.the.map.sync;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.spbau.news.on.the.map.sync.config.DatabaseConfig;
import com.spbau.news.on.the.map.sync.config.GlobalConfiguration;
import com.spbau.news.on.the.map.sync.entity.ArticleBean;
import com.spbau.news.on.the.map.sync.entity.LinksBean;
import com.spbau.news.on.the.map.sync.entity.LocationBean;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.Arguments;
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
import java.util.concurrent.TimeUnit;

public class EntryPoint {
  private static final int DELTA_SYNC_TIMEOUT_SECONDS = 1;
  private static final int ARTICLE_PREVIEW_LENGTH = 100;

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

    parser.addArgument("-d")
        .action(Arguments.storeTrue())
        .help("deltas sync mode (load new articles every second)");
    return parser;
  }

  public static void main(String[] args) {
    final ArgumentParser parser = createParser();
    try {
      final Namespace namespace = parser.parseArgs(args);
      final String pathToConfig = namespace.getString("config");

      ObjectMapper mapper = new ObjectMapper();
      final GlobalConfiguration config = mapper.readValue(new File(pathToConfig), GlobalConfiguration.class);

      final Boolean realTimeMode = namespace.getBoolean("d");
      new EntryPoint().run(config, realTimeMode);
    } catch (ArgumentParserException e) {
      parser.handleError(e);
    } catch (ExecutionException | InterruptedException | ClassNotFoundException | SQLException e) {
      e.printStackTrace();
    } catch (JsonParseException e) {
      System.err.println("Cannot parse config file");
    } catch (IOException e) {
      System.err.println("Errors occurred:" + e);
    }
  }

  private void run(GlobalConfiguration config, boolean isRealTimeMode) throws IOException, ExecutionException,
      InterruptedException, ClassNotFoundException, SQLException {
    TransportClient client = TransportClient.builder().build()
        .addTransportAddress(new InetSocketTransportAddress(
            InetAddress.getByName(config.getElasticConfig().getAddress()),
            config.getElasticConfig().getPort()));

    final boolean isIndexExists = client.admin().indices().exists(new IndicesExistsRequest("news")).get().isExists();
    if (!isIndexExists) {
      client.admin().indices().prepareCreate("news").addMapping("article", ARTICLE_MAPPING).get();
    }

    final DatabaseConfig dbConfig = config.getDatabaseConfig();
    Class.forName("org.postgresql.Driver");
    Connection connection = DriverManager
        .getConnection(String.format("jdbc:postgresql://%s:%d/%s", dbConfig.getAddress(), dbConfig.getPort(),
            dbConfig.getDatabase()), dbConfig.getUser(), dbConfig.getPassword());

    if (isRealTimeMode) {
      realTimeSync(client, connection);
    } else {
      sync(client, connection);
    }
  }

  private void sync(TransportClient client, Connection dbConnection) {
    System.out.println("'Sync all' operation started");
    try {
      final ResultSet resultSet = dbConnection.createStatement().executeQuery(SELECT_READY_NEWS);
      syncAllResultSet(client, resultSet);
    } catch (SQLException | JsonProcessingException e) {
      e.printStackTrace();
    }
  }

  private void realTimeSync(TransportClient client, Connection dbConnection) throws SQLException,
      InterruptedException, JsonProcessingException {
    System.out.println(String.format("Sync only deltas (every %d seconds)", DELTA_SYNC_TIMEOUT_SECONDS));
    final ResultSet result = dbConnection.createStatement().executeQuery(MAX_ID_QUERY);
    int maxId = 0;
    if (result.next()) {
      maxId = result.getInt("max_id") - 10;
    }

    String formatString = SELECT_READY_NEWS + " WHERE news.id > %d";

    //noinspection InfiniteLoopStatement
    while (true) {
      TimeUnit.SECONDS.sleep(DELTA_SYNC_TIMEOUT_SECONDS);
      final ResultSet resultSet = dbConnection.createStatement().executeQuery(String.format(formatString, maxId));
      maxId = Math.max(maxId, syncAllResultSet(client, resultSet));
    }
  }

  private static int syncAllResultSet(TransportClient client, ResultSet records) throws SQLException, JsonProcessingException {
    int maxId = -1;
    final ObjectMapper mapper = new ObjectMapper();
    int count = 0;
    while (records.next()) {
      String sourceUrl = records.getString("sourceUrl");
      String articleUrl = records.getString("articleUrl");
      LinksBean links = new LinksBean(sourceUrl, articleUrl);

      Date date = records.getTimestamp("publishDate");
      int category = records.getInt("category");
      final PGpoint location = (PGpoint) records.getObject("location");
      LocationBean locationBean = new LocationBean((float) location.x, (float) location.y);

      int id = records.getInt("id");
      int rawId = records.getInt("rawId");
      int geoId = records.getInt("geoId");

      String content = records.getString("content");
      String locationWords = records.getString("location_words");
      ArticleBean article = new ArticleBean(id, rawId, geoId, content, locationWords, date,
          links, locationBean, category);
      String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(article);

      client.prepareIndex("news", "article", String.valueOf(id)).setSource(json).get();
      int newLineIndex = content.indexOf('\n');
      int previewLength = newLineIndex != -1
          ? Math.min(ARTICLE_PREVIEW_LENGTH, newLineIndex)
          : Math.min(ARTICLE_PREVIEW_LENGTH, content.length());
      System.out.println(String.format("id = %d, content = %s...", id, content.substring(0, previewLength)));
      maxId = Math.max(maxId, id);
      count++;
    }

    System.out.println(String.format("%d articles synchronized", count));
    return maxId;
  }

  private static final String MAX_ID_QUERY =
      "SELECT max(id) AS max_id " +
          "FROM news";

  private static final String SELECT_READY_NEWS = "" +
      "SELECT \n" +
      "\traw_news.id AS rawId,\n" +
      "    geo_news.id AS geoId,\n" +
      "    news.id AS id,\n" +
      "    raw_news.content_of_news AS content,\n" +
      "    raw_news.publish_date AS publishDate,\n" +
      "    raw_news.source_url AS sourceUrl,\n" +
      "    raw_news.article_url AS articleUrl,\n" +
      "    geo_news.coord AS location,\n" +
      "    geo_news.location_words AS location_words,\n" +
      "    news.category AS category\n" +
      "FROM news \n" +
      "JOIN geo_news\n" +
      "ON news.geo_news_id = geo_news.id\n" +
      "JOIN raw_news\n" +
      "ON geo_news.raw_news_id = raw_news.id";

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
      "      \"location_words\": {\n" +
      "        \"type\": \"string\"\n" +
      "      },\n" +
      "      \"location\": {\n" +
      "        \"type\": \"geo_point\"\n" +
      "      },\n" +
      "      \"category\": {\n" +
      "        \"type\": \"integer\"\n" +
      "      },\n" +
      "      \"publish_date\": {\n" +
      "        \"type\": \"date\",\n" +
      "        \"format\": \"epoch_millis\"\n" +
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
      "      }\n" +
      "    }\n" +
      "  }\n" +
      "}";
}
