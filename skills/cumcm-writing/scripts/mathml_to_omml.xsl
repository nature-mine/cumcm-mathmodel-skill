<?xml version="1.0" encoding="UTF-8"?>
<!-- Project-owned transform for the MathML subset accepted by docx_export.py. -->
<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:mml="http://www.w3.org/1998/Math/MathML"
    xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
    exclude-result-prefixes="mml">

  <xsl:output method="xml" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/mml:math">
    <m:oMathPara>
      <m:oMathParaPr>
        <m:jc m:val="center"/>
      </m:oMathParaPr>
      <m:oMath>
        <xsl:apply-templates/>
      </m:oMath>
    </m:oMathPara>
  </xsl:template>

  <xsl:template match="mml:mrow | mml:mstyle | mml:mpadded">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="mml:mi | mml:mn | mml:mo | mml:mtext">
    <m:r>
      <m:t xml:space="preserve"><xsl:value-of select="."/></m:t>
    </m:r>
  </xsl:template>

  <xsl:template match="mml:mspace">
    <m:r>
      <m:t xml:space="preserve"> </m:t>
    </m:r>
  </xsl:template>

  <xsl:template match="mml:mfrac">
    <m:f>
      <m:num><xsl:apply-templates select="*[1]"/></m:num>
      <m:den><xsl:apply-templates select="*[2]"/></m:den>
    </m:f>
  </xsl:template>

  <xsl:template match="mml:msqrt">
    <m:rad>
      <m:radPr><m:degHide m:val="1"/></m:radPr>
      <m:deg/>
      <m:e><xsl:apply-templates/></m:e>
    </m:rad>
  </xsl:template>

  <xsl:template match="mml:mroot">
    <m:rad>
      <m:deg><xsl:apply-templates select="*[2]"/></m:deg>
      <m:e><xsl:apply-templates select="*[1]"/></m:e>
    </m:rad>
  </xsl:template>

  <xsl:template match="mml:msub">
    <m:sSub>
      <m:e><xsl:apply-templates select="*[1]"/></m:e>
      <m:sub><xsl:apply-templates select="*[2]"/></m:sub>
    </m:sSub>
  </xsl:template>

  <xsl:template match="mml:msup">
    <m:sSup>
      <m:e><xsl:apply-templates select="*[1]"/></m:e>
      <m:sup><xsl:apply-templates select="*[2]"/></m:sup>
    </m:sSup>
  </xsl:template>

  <xsl:template match="mml:msubsup">
    <m:sSubSup>
      <m:e><xsl:apply-templates select="*[1]"/></m:e>
      <m:sub><xsl:apply-templates select="*[2]"/></m:sub>
      <m:sup><xsl:apply-templates select="*[3]"/></m:sup>
    </m:sSubSup>
  </xsl:template>

  <xsl:template match="mml:munder">
    <m:limLow>
      <m:e><xsl:apply-templates select="*[1]"/></m:e>
      <m:lim><xsl:apply-templates select="*[2]"/></m:lim>
    </m:limLow>
  </xsl:template>

  <xsl:template match="mml:mover">
    <xsl:choose>
      <xsl:when test="normalize-space(*[2]) = '&#x00AF;' or normalize-space(*[2]) = '&#x203E;'">
        <m:bar>
          <m:e><xsl:apply-templates select="*[1]"/></m:e>
        </m:bar>
      </xsl:when>
      <xsl:otherwise>
        <m:limUpp>
          <m:e><xsl:apply-templates select="*[1]"/></m:e>
          <m:lim><xsl:apply-templates select="*[2]"/></m:lim>
        </m:limUpp>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="mml:munderover">
    <m:limUpp>
      <m:e>
        <m:limLow>
          <m:e><xsl:apply-templates select="*[1]"/></m:e>
          <m:lim><xsl:apply-templates select="*[2]"/></m:lim>
        </m:limLow>
      </m:e>
      <m:lim><xsl:apply-templates select="*[3]"/></m:lim>
    </m:limUpp>
  </xsl:template>

  <xsl:template match="mml:mtable">
    <m:m>
      <xsl:for-each select="mml:mtr">
        <m:mr>
          <xsl:for-each select="mml:mtd">
            <m:e><xsl:apply-templates/></m:e>
          </xsl:for-each>
        </m:mr>
      </xsl:for-each>
    </m:m>
  </xsl:template>

</xsl:stylesheet>
