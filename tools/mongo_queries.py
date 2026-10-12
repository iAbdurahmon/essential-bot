import logging

from tools.db_conn import collection, fetch_one

logger = logging.getLogger(__name__)


def select_coin(tg_id, book, unit):
    pipeline = [
        {"$match": {"tg_id": tg_id}},
        {"$unwind": "$balance"},
        {"$match": {"balance.title": f"book{book}"}},
        {"$unwind": "$balance.units"},
        {"$match": {"balance.units.unit_number": unit}},
        {"$project": {"_id": 0, "coins": "$balance.units.coins"}}
    ]

    result = list(collection.aggregate(pipeline))
    if not result:
        return None
    return result[0].get('coins')


def update_coins(tg_id, book, unit, coins):
    filter_coin = {
        "tg_id": tg_id,
        "balance.title": f"book{book}",
        "balance.units.unit_number": unit
    }

    update = {
        "$set": {
            "balance.$[outer].units.$[inner].coins": coins
        }
    }

    array_filters = [
        {"outer.title": f"book{book}"},
        {"inner.unit_number": unit}
    ]
    result = collection.update_one(filter_coin, update, array_filters=array_filters)
    return result


def empty_balance():
    return [{"title": f"book{i}",
             "units": [{"unit_number": j, "coins": 0} for j in range(1, 31)]}
            for i in range(1, 7)]


def ensure_balance(tg_id):
    # Users who registered before the per-unit balances existed have no document.
    # Without one select_coin finds nothing, old_coins stays 0, and every repeat of
    # the same quiz pays out again. Used to be fixed by an admin backfill command.
    doc = collection.find_one({"tg_id": tg_id}, {"balance": 1})
    if doc and doc.get("balance"):
        return False
    collection.update_one({"tg_id": tg_id}, {"$set": {"balance": empty_balance()}}, upsert=True)
    logger.info('created a missing balance document for %s', tg_id)
    return True


def insert_new(tg_id):
    row = fetch_one('SELECT id, name, username, tg_id, created_on, lg FROM users WHERE tg_id = %s',
                    (tg_id,))
    if row:
        collection.insert_one({
            "user_id": row[0],
            "name": row[1],
            "username": row[2],
            "tg_id": row[3],
            "created_on": row[4].isoformat() if row[4] else None,
            "lg": row[5]
        })

    result = collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"balance": empty_balance()}},
        upsert=True
    )

    if not result.modified_count:
        logger.warning('balance was not initialised for %s', tg_id)


def select_invite(tg_id):
    result = collection.find_one(
        {"tg_id": tg_id},
        {"invite"}
    )

    if result:
        return result.get('invite')
    return None


def insert_invite(tg_id, data):
    result = collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"invite": data}},
        upsert=True
    )
    return result


def insert_new_invite(tg_id):
    new_posts = []
    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"invite": new_posts}},
        upsert=True
    )


