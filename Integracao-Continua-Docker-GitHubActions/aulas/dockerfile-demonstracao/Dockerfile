FROM nginx:latest

ARG VERSAO_AULA=1
ENV AMBIENTE=aula

WORKDIR /usr/share/nginx/html

RUN echo 'we are running some # of cool things'
RUN echo hello \
    world

COPY index.html ./index.html
ADD aviso.txt ./aviso.txt

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
