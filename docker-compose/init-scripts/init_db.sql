DROP DATABASE IF EXISTS btc_db;

CREATE DATABASE IF NOT EXISTS btc_db;
USE btc_db;

CREATE TABLE klines (
    kline_open_time BIGINT,                      -- Timestamp d'ouverture du kline (en millisecondes)
    open_price DECIMAL(18, 8),                   -- Prix d'ouverture
    high_price DECIMAL(18, 8),                   -- Prix le plus haut
    low_price DECIMAL(18, 8),                    -- Prix le plus bas
    close_price DECIMAL(18, 8),                  -- Prix de clôture
    volume DECIMAL(24, 8),                       -- Volume échangé
    kline_close_time BIGINT,                     -- Timestamp de fermeture du kline (en millisecondes)
    quote_asset_volume DECIMAL(24, 8),           -- Volume total échangé en asset quote
    number_of_trades INT,                        -- Nombre de trades
    taker_buy_base_asset_volume DECIMAL(24, 8),  -- Volume des achats côté maker
    taker_buy_quote_asset_volume DECIMAL(24, 8), -- Volume total des achats côté maker (en asset quote)
    PRIMARY KEY (kline_open_time)                -- Définir la clé primaire comme le timestamp d'ouverture du kline
);

CREATE TABLE ticker_24h (
    symbol VARCHAR(10),                          -- Symbole de la paire de trading (ex: BTCUSDT)
    price_change DECIMAL(18, 8),                 -- Variation de prix
    price_change_percent DECIMAL(18, 6),         -- Pourcentage de variation
    weighted_avg_price DECIMAL(18, 8),           -- Prix moyen pondéré
    prev_close_price DECIMAL(18, 8),             -- Prix de clôture précédent
    last_price DECIMAL(18, 8),                   -- Dernier prix
    last_qty DECIMAL(24, 8),                     -- Dernière quantité échangée
    bid_price DECIMAL(18, 8),                    -- Prix d'achat (bid)
    bid_qty DECIMAL(24, 8),                      -- Quantité en bid
    ask_price DECIMAL(18, 8),                    -- Prix de vente (ask)
    ask_qty DECIMAL(24, 8),                      -- Quantité en ask
    open_price DECIMAL(18, 8),                   -- Prix d'ouverture des dernières 24h
    high_price DECIMAL(18, 8),                   -- Prix le plus haut des dernières 24h
    low_price DECIMAL(18, 8),                    -- Prix le plus bas des dernières 24h
    volume DECIMAL(24, 8),                       -- Volume total échangé
    quote_volume DECIMAL(24, 8),                 -- Volume total échangé en quote asset
    open_time BIGINT,                            -- Timestamp d'ouverture des dernières 24h
    close_time BIGINT,                           -- Timestamp de clôture des dernières 24h
    first_trade_id INT,                          -- Premier trade ID
    last_trade_id INT,                           -- Dernier trade ID
    trade_count INT,                             -- Nombre total de trades
    PRIMARY KEY (symbol)                         -- Définir la clé primaire comme le symbole de la paire
);
