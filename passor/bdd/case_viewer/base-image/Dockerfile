FROM node:alpine

ADD . /html_gen
RUN set -x \
  && apk update \
  && apk add git openssh \
  && mkdir ~/.ssh \
  && ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa \
  && mv /html_gen/ssh/* /root/.ssh/ \
  && chmod 0400 ~/.ssh/id_rsa* \
  && cd /html_gen \
  && npm install gherkin-htmlify \
  && npm install express \
  && mkdir /html

WORKDIR /html_gen
EXPOSE 80
CMD node server.js
