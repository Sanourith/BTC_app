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

CREATE TABLE ticker24h (
    symbol VARCHAR(10),                          -- Symbole de la paire de trading (ex: BTCUSDT)
    priceChange DECIMAL(18, 8),                  -- Variation de prix
    priceChangePercent DECIMAL(18, 6),           -- Pourcentage de variation
    weightedAvgPrice DECIMAL(18, 8),             -- Prix moyen pondéré
    prevClosePrice DECIMAL(18, 8),               -- Prix de clôture précédent
    lastPrice DECIMAL(18, 8),                    -- Dernier prix
    lastQty DECIMAL(24, 8),                      -- Dernière quantité échangée
    bidPrice DECIMAL(18, 8),                     -- Prix d'achat (bid)
    bidQty DECIMAL(24, 8),                       -- Quantité en bid
    askPrice DECIMAL(18, 8),                     -- Prix de vente (ask)
    askQty DECIMAL(24, 8),                       -- Quantité en ask
    openPrice DECIMAL(18, 8),                    -- Prix d'ouverture des dernières 24h
    highPrice DECIMAL(18, 8),                    -- Prix le plus haut des dernières 24h
    lowPrice DECIMAL(18, 8),                     -- Prix le plus bas des dernières 24h
    volume DECIMAL(24, 8),                       -- Volume total échangé
    quoteVolume DECIMAL(24, 8),                  -- Volume total échangé en quote asset
    openTime BIGINT,                             -- Timestamp d'ouverture des dernières 24h
    closeTime BIGINT,                            -- Timestamp de clôture des dernières 24h
    firstId INT,                                 -- Premier trade ID
    lastId INT,                                  -- Dernier trade ID
    count INT,                                   -- Nombre total de trades
    PRIMARY KEY (open_time)                      -- Définir la clé primaire comme le symbole de la paire
);