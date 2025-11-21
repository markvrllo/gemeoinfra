FROM nginx:alpine

# Copia a nossa config para dentro da imagem
# (O contexto de build é a raiz, por isso acessamos config/...)
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos da interface web
COPY --chown=nginx:nginx ./web-interface/ /usr/share/nginx/html/

# Expor porta
EXPOSE 80
