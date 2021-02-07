FROM tomcat:9.0

LABEL maintainer=”marcourbano”

ADD docker/wavsep/wavsep.war /usr/local/tomcat/webapps/

EXPOSE 8080

CMD ["catalina.sh", "run"]
