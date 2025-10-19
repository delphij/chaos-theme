<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">

  <xsl:output method="html" encoding="utf-8"/>
  <xsl:template match="/">
    <html{{ with .Site.Params.lang }} lang="{{ . }}"{{ end }}>
      <head>
        <title><xsl:value-of select="atom:feed/atom:title"/></title>
        {{ partialCached "head/css.html" . }}
      </head>
      <body>
          <div id="">
            <h1><xsl:value-of select="atom:feed/atom:title"/></h1>
            <h2><xsl:value-of select="atom:feed/atom:subtitle"/></h2>
            <h3>Atom feed</h3>
            <p>This is an <a href="https://tools.ietf.org/html/rfc5023">Atom</a>
              feed from <xsl:value-of select="atom:feed/atom:title"/>, which
              allows you to stay up to date with its contents.</p>
            <p>To subscribe to it, you will need an <a href="https://en.wikipedia.org/wiki/Comparison_of_feed_aggregators">
              RSS feed aggregator</a>.</p>
            <ul class="flat"><xsl:apply-templates select="//atom:entry"/></ul>
          </div>
        </body>
      </html>
    </xsl:template>
  <xsl:template match="atom:entry">
    <li>
      <h2>
        <a>
          <xsl:attribute name="href"><xsl:value-of select="atom:link[@type='text/html']/@href"/></xsl:attribute>
          <xsl:value-of select="atom:title" disable-output-escaping="yes"/>
        </a>
      </h2>
      <xsl:value-of select="atom:content" disable-output-escaping="yes"/>
    </li>
  </xsl:template>
</xsl:stylesheet>
