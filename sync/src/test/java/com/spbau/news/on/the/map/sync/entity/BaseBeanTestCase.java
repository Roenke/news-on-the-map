package com.spbau.news.on.the.map.sync.entity;

import java.util.Date;

abstract class BaseBeanTestCase {
  final LinksBean links = new LinksBean("http://vk.com", "http://vk.com/groupId/wall-123123");
  final LocationBean location = new LocationBean(1.1f, 2.4f);
  protected final ArticleBean article = new ArticleBean(1, 2, 3, "putin",  new Date(), links, location, 23);
}
