-------------------------------------------------------------------------------
-- Somewhat of online game trade/purchase DB ----------------------------------
-- by Alexandr 'JFAexe' Konichenko --------------------------------------------
-------------------------------------------------------------------------------

BEGIN;

    ---------------------------------------------------------------------------
    SAVEPOINT _fresh; ---------------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE TABLE IF NOT EXISTS GameServer (
        server_id
            SERIAL2 PRIMARY KEY NOT NULL,

        online_status
            BOOL NOT NULL DEFAULT false
    );

    CREATE TABLE IF NOT EXISTS Player (
        account_id
            VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE CHECK(length(account_id) > 9),

        server_id
            SERIAL2 NOT NULL,

        register_stamp
            TIMESTAMP NOT NULL DEFAULT now(),

        login_stamp
            TIMESTAMP NOT NULL DEFAULT now(),

        online_status
            BOOL NOT NULL DEFAULT false,

        account_level
            INT2 NOT NULL CHECK(account_level > 0 AND account_level <= 255) DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS Item (
        item_id
            UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),

        player_id
            VARCHAR(20) NOT NULL,

        type_id
            SERIAL2 NOT NULL,

        price
            BIGINT NOT NULL CHECK(price >= 0) DEFAULT 0,

        minimum_level
            INT2 NOT NULL CHECK(minimum_level >= 0) DEFAULT 0,

        tradable
            BOOL NOT NULL DEFAULT false,

        expiration_date
            TIMESTAMP NULL DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS ItemType (
        type_id
            SERIAL2 PRIMARY KEY NOT NULL,

        type_name
            VARCHAR(64) NOT NULL DEFAULT 'item',

        type_description
            VARCHAR(255) DEFAULT 'description'
    );

    CREATE TABLE IF NOT EXISTS ItemTransfer (
        transfer_id
            BIGSERIAL PRIMARY KEY NOT NULL,

        trade_id
            UUID NULL,

        purchase_id
            UUID NULL,

        initiator_id
            VARCHAR(20) NULL,

        receiver_id
            VARCHAR(20) NOT NULL,

        item_id
            UUID NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Trade (
        trade_id
            UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),

        server_id
            SERIAL2 NOT NULL,

        time_stamp
            TIMESTAMP NOT NULL DEFAULT now(),

        confirmation_status
            BOOL NOT NULL DEFAULT false,

        pending
            BOOL NOT NULL DEFAULT true,

        initiator_id
            VARCHAR(20) NOT NULL,

        receiver_id
            VARCHAR(20) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Purchase (
        purchase_id
            UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),

        server_id
            SERIAL2 NOT NULL,

        time_stamp
            TIMESTAMP NOT NULL DEFAULT now(),

        confirmation_status
            BOOL NOT NULL DEFAULT false,

        pending
            BOOL NOT NULL DEFAULT true,

        receiver_id
            VARCHAR(20) NOT NULL
    );

    ---------------------------------------------------------------------------
    SAVEPOINT _tables; --------------------------------------------------------
    ---------------------------------------------------------------------------

    ALTER TABLE IF EXISTS Player ADD CONSTRAINT fk_Player_GameServer
        FOREIGN KEY (server_id) REFERENCES GameServer(server_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;


    ALTER TABLE IF EXISTS Item ADD CONSTRAINT fk_Item_Player
        FOREIGN KEY (player_id) REFERENCES Player(account_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS Item ADD CONSTRAINT fk_Item_ItemType
        FOREIGN KEY (type_id) REFERENCES ItemType(type_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;


    ALTER TABLE IF EXISTS ItemTransfer ADD CONSTRAINT fk_ItemTransfer_Player_sender
        FOREIGN KEY (initiator_id) REFERENCES Player(account_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS ItemTransfer ADD CONSTRAINT fk_ItemTransfer_Player_receiver
        FOREIGN KEY (receiver_id) REFERENCES Player(account_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS ItemTransfer ADD CONSTRAINT fk_ItemTransfer_Item
        FOREIGN KEY (item_id) REFERENCES Item (item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS ItemTransfer ADD CONSTRAINT fk_ItemTransfer_Trade
        FOREIGN KEY (trade_id) REFERENCES Trade(trade_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS ItemTransfer ADD CONSTRAINT fk_ItemTransfer_Purchase
        FOREIGN KEY (purchase_id) REFERENCES Purchase(purchase_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;


    ALTER TABLE IF EXISTS Trade ADD CONSTRAINT fk_Trade_GameServer
        FOREIGN KEY (server_id)
        REFERENCES GameServer(server_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS Trade ADD CONSTRAINT fk_Trade_Initiator_Player
        FOREIGN KEY (initiator_id)
        REFERENCES Player(account_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS Trade ADD CONSTRAINT fk_Trade_Receiver_Player
        FOREIGN KEY (receiver_id)
        REFERENCES Player(account_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;


    ALTER TABLE IF EXISTS Purchase ADD CONSTRAINT fk_Purchase_GameServer
        FOREIGN KEY (server_id)
        REFERENCES GameServer(server_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    ALTER TABLE IF EXISTS Purchase ADD CONSTRAINT fk_Purchase_Receiver_Player
        FOREIGN KEY (receiver_id)
        REFERENCES Player(account_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;


    CREATE OR REPLACE FUNCTION
    restrict_item_type_deletion()
    RETURNS TRIGGER
    AS $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM Item
            WHERE type_id = OLD.type_id
        ) THEN
            RAISE EXCEPTION 'Нельзя удалить используемый тип';
        END IF;

        RETURN OLD;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE TRIGGER restrict_item_type_deletion_trigger
    BEFORE DELETE ON ItemType
    FOR EACH ROW
    EXECUTE FUNCTION restrict_item_type_deletion();

    ---------------------------------------------------------------------------
    SAVEPOINT _constraints; ---------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE UNIQUE INDEX IF NOT EXISTS idx_GameServer_server_id ON GameServer (server_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_Player_account_id ON Player (account_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_Item_item_id ON Item (item_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_ItemType_type_id ON ItemType (type_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_ItemTransfer_transfer_id ON ItemTransfer (transfer_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_Trade_trade_id ON Trade (trade_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_Purchase_purchase_id ON Purchase (purchase_id);

    ---------------------------------------------------------------------------
    SAVEPOINT _indexes; -------------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE OR REPLACE FUNCTION
    calculate_item_price()
    RETURNS TRIGGER
    AS $$
    BEGIN
        UPDATE Item
        SET price = CAST(
            CAST(
                (
                    SELECT price
                    FROM ItemType
                    WHERE ItemType.type_id = NEW.type_id
                )
                AS REAL
            )
            * (
                (
                    CAST(
                        NEW.minimum_level
                        AS REAL
                    )
                    / 255
                )
                + 0.5
            )
            AS BIGINT
        )
        WHERE Item.item_id = NEW.item_id;

        RETURN NEW;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE TRIGGER calculate_item_price_trigger
    AFTER INSERT ON Item
    FOR EACH ROW
    EXECUTE FUNCTION calculate_item_price();

    ---------------------------------------------------------------------------
    SAVEPOINT _triggers; ------------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE OR REPLACE VIEW server_player_counts AS
    SELECT server_id,
        COUNT(*) AS player_count,
        COUNT(
            CASE online_status
            WHEN true
                THEN 1
                ELSE null
            END
        ) AS player_count_online
    FROM Player
    GROUP BY server_id
    ORDER BY player_count;

    ---------------------------------------------------------------------------
    SAVEPOINT _views; ---------------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE OR REPLACE FUNCTION
    give_random_item(
        _player_id VARCHAR(20)
    )
    RETURNS UUID
    AS $$
    DECLARE _item_id UUID;
    BEGIN
        INSERT INTO Item (player_id, type_id, price, minimum_level, tradable, expiration_date)
        SELECT
            _player_id,
            type_id,
            CASE
                WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 1000)
                WHEN RANDOM() < 0.8 THEN FLOOR(RANDOM() * 10000) + 1000
                ELSE FLOOR(RANDOM() * 100000) + 11000
            END,
            FLOOR(RANDOM() * 10),
            (RANDOM() < 0.8),
            CASE
                WHEN RANDOM() < 0.3 THEN NULL
                ELSE NOW() + interval '30 days' + (RANDOM() * interval '90 days')
            END
        FROM GENERATE_SERIES(1, 1)
        CROSS JOIN (SELECT type_id FROM ItemType ORDER BY RANDOM()) AS type_randomizer
        LIMIT 1
        RETURNING item_id INTO _item_id;

        RETURN _item_id;
    END;
    $$
    LANGUAGE plpgsql;

    ---------------------------------------------------------------------------
    SAVEPOINT _functions; -----------------------------------------------------
    ---------------------------------------------------------------------------

    CREATE OR REPLACE PROCEDURE
    increase_account_level(
        _player_id VARCHAR(20),
        _amount INT2
    )
    AS $$
    BEGIN
        UPDATE Player
        SET account_level = GREATEST(
            account_level,
            LEAST(
                account_level + _amount,
                255
            )
        )
        WHERE account_id = _player_id;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE PROCEDURE
    decrease_account_level(
        _player_id VARCHAR(20),
        _amount INT2
    )
    AS $$
    BEGIN
        UPDATE Player
        SET account_level = GREATEST(
            1,
            LEAST(
                account_level - _amount,
                account_level
            )
        )
        WHERE account_id = _player_id;
    END;
    $$
    LANGUAGE plpgsql;


    CREATE OR REPLACE PROCEDURE
    make_random_trade(
        _initiator_id VARCHAR(20),
        _receiver_id VARCHAR(20),
        _amount INT2
    ) AS $$
    DECLARE _trade_id UUID;
    BEGIN
        SELECT gen_random_uuid() INTO _trade_id;

        INSERT INTO Trade (trade_id, server_id, confirmation_status, initiator_id, receiver_id)
        VALUES (
            _trade_id,
            (SELECT server_id FROM Player WHERE account_id = _receiver_id),
            true,
            _initiator_id,
            _receiver_id
        );

        INSERT INTO ItemTransfer (trade_id, initiator_id, receiver_id, item_id)
        SELECT
            _trade_id,
            _initiator_id,
            _receiver_id,
            (
                SELECT item_id
                FROM Item
                WHERE player_id = _initiator_id
                ORDER BY RANDOM()
                LIMIT 1
            ) -- selects only first in randomly ordered bunch :(
        FROM GENERATE_SERIES(1, _amount);

        UPDATE Item
        SET player_id = _receiver_id
        FROM ItemTransfer
            INNER JOIN Trade ON ItemTransfer.trade_id = Trade.trade_id
        WHERE Trade.pending = true
            AND Trade.confirmation_status = true
            AND Item.player_id = _initiator_id
            AND Item.item_id = ItemTransfer.item_id
            AND ItemTransfer.item_id IS NOT NULL;

        UPDATE Trade
        SET pending = false
        WHERE pending = true
            AND trade_id = _trade_id;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE PROCEDURE
    make_random_purchase(
        _receiver_id VARCHAR(20),
        _amount INT2
    ) AS $$
    DECLARE _purchase_id UUID;
    BEGIN
        SELECT gen_random_uuid() INTO _purchase_id;

        INSERT INTO Purchase (purchase_id, server_id, confirmation_status, receiver_id)
        VALUES (
            _purchase_id,
            (SELECT server_id FROM Player WHERE account_id = _receiver_id),
            true,
            _receiver_id
        );

        INSERT INTO ItemTransfer (purchase_id, receiver_id, item_id)
        SELECT
            _purchase_id,
            _receiver_id,
            give_random_item(_receiver_id)
        FROM GENERATE_SERIES(1, _amount);

        UPDATE Purchase
        SET pending = false
        WHERE pending = true
            AND purchase_id = _purchase_id;
    END;
    $$
    LANGUAGE plpgsql;

    ---------------------------------------------------------------------------
    SAVEPOINT _procedures; ----------------------------------------------------
    ---------------------------------------------------------------------------

END;
