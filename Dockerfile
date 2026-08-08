FROM freqtradeorg/freqtrade:stable

USER root

# Dependências extras
RUN pip install psycopg2-binary --no-cache-dir

# Copia estratégias para dentro da imagem
COPY strategies/active/   /freqtrade/user_data/strategies/
COPY strategies/candidates/ /freqtrade/user_data/strategies/

# Entrypoint que gera config.json a partir de env vars
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ftuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["trade", "--logfile", "/freqtrade/user_data/logs/freqtrade.log", "--config", "/freqtrade/config.json", "--strategy", "FSupertrendStrategy", "--strategy-path", "/freqtrade/user_data/strategies"]
