from tools.db_conn import collection, cur


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


def update_result_checker(result_id):
    if not isinstance(result_id, int):
        if result_id.modified_count == 1:
            return 'updated'
        else:
            return f"not updated ({result_id.raw_result})"
    else:
        return result_id


def insert_new(tg_id):
    cur.execute('SELECT * FROM users WHERE tg_id = %s', (f"{tg_id}",))
    rows = cur.fetchall()

    for row in rows:
        user_data = {
            "user_id": row[0],
            "name": row[1],
            "username": row[2],
            "tg_id": int(row[3]),
            "created_on": row[4],
            "lg": row[6]
        }
        collection.insert_one(user_data)

    new_posts = []
    for i in range(1, 7):
        units = [{"unit_number": j, "coins": 0} for j in range(1, 31)]
        new_posts.append({"title": f"book{i}", "units": units})

    result = collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"balance": new_posts}},
        upsert=True
    )

    if result.modified_count > 0:
        print("Данные успешно обновлены")
    else:
        print("Ошибка: данные не обновлены")


def select_invite(tg_id):
    result = collection.find_one(
        {"tg_id": tg_id},
        {"invite"}
    )

    if result:
        new_result = result.get('invite')
        return new_result
    else:
        print("ERROR: No result found for tg_id", tg_id)
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
    result = collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"invite": new_posts}},
        upsert=True
    )
    print(result)


