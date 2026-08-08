FROM freqtradeorg/freqtrade:stable

USER root

RUN pip install psycopg2-binary --no-cache-dir && \
    mkdir -p /freqtrade/user_data/logs \
             /freqtrade/user_data/data && \
    chown -R ftuser:ftuser /freqtrade/user_data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh

USER ftuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["trade", \
     "--logfile", "/freqtrade/user_data/logs/freqtrade.log", \
     "--config", "/freqtrade/config.json", \
     "--strategy-path", "/freqtrade/user_data/strategies"]
