# Pull base image.
FROM library/elasticsearch:2.4.1

# Install HEAD plugin
RUN \
  cd /usr/share/elasticsearch && \
  bin/plugin install mobz/elasticsearch-head