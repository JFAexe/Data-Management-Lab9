-------------------------------------------------------------------------------
-- Somewhat of online game trade/purchase DB ----------------------------------
-- by Alexandr 'JFAexe' Konichenko --------------------------------------------
-------------------------------------------------------------------------------

BEGIN;

    ---------------------------------------------------------------------------
    SAVEPOINT _fresh; ---------------------------------------------------------
    ---------------------------------------------------------------------------

    INSERT INTO GameServer (online_status)
    SELECT
        (RANDOM() < 0.5)
    FROM GENERATE_SERIES(1, 10)
    LIMIT 10;

    ---------------------------------------------------------------------------
    SAVEPOINT _servers; -------------------------------------------------------
    ---------------------------------------------------------------------------

    INSERT INTO Player (account_id, server_id, register_stamp, login_stamp, online_status, account_level)
    SELECT
        SUBSTRING('account_' || md5(random()::text), 1, 20),
        server_id,
        NOW() - interval '10 days' + (RANDOM() * interval '100 days'),
        NOW() - interval '10 days' + (RANDOM() * interval '100 days'),
        (RANDOM() < 0.5),
        FLOOR(RANDOM() * 254) + 1
    FROM GENERATE_SERIES(1, 40)
    CROSS JOIN (SELECT server_id FROM GameServer ORDER BY RANDOM()) AS server_randomizer
    LIMIT 40;

    ---------------------------------------------------------------------------
    SAVEPOINT _players; -------------------------------------------------------
    ---------------------------------------------------------------------------

    INSERT INTO ItemType (type_name, type_description)
    SELECT
        CONCAT(
            CASE WHEN RANDOM() < 0.4 THEN 'Common '
                WHEN RANDOM() < 0.7 THEN 'Uncommon '
                ELSE 'Rare '
            END,
            CASE
                WHEN RANDOM() < 0.33 THEN 'Weapon'
                WHEN RANDOM() < 0.66 THEN 'Armor'
                ELSE 'Consumable'
            END
        ),
        'This is a '
        || CASE
            WHEN RANDOM() < 0.33 THEN 'basic'
            WHEN RANDOM() < 0.66 THEN 'intermediate'
            ELSE 'advanced'
        END
        || ' '
        || CASE
            WHEN RANDOM() < 0.5 THEN 'item'
            ELSE 'product'
        END
        || ' that can be used for '
        || CASE
            WHEN RANDOM() < 0.25 THEN 'healing.'
            WHEN RANDOM() < 0.5 THEN 'buffing.'
            WHEN RANDOM() < 0.75 THEN 'debuffing.'
            ELSE 'crafting.'
        END
    FROM GENERATE_SERIES(1, 40)
    LIMIT 40;

    ---------------------------------------------------------------------------
    SAVEPOINT _types; ---------------------------------------------------------
    ---------------------------------------------------------------------------

END;
