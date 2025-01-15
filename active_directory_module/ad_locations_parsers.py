def get_user_location(distinguished_name):
    # Определяем ключевые слова для локаций
    location_keywords = {
        "Locate_Khimki": "Химки",
        "Locate_Osennaya": "Осенняя",
        "Locate_Poklonka": "Поклонная",
        "Locate_Remote": "Дистанционно",
        "Locate_Domodedovo": "Домодедово",
        "Locate_Kutuzovsky": "Кутузовская",
        "Locate_Novohohlovskaya": "Новохохловская",
        "Locate_Sevastopolskaya": "Севастопольская",
        "Locate_SkladRublevka": "Склад Рублевка",
        "Locate_VDNH": "ВДНХ",
        "Locate_Vladimir": "Владимир"
    }

    # Ищем ключевые слова в DistinguishedName
    for keyword, location in location_keywords.items():
        if keyword in distinguished_name:
            if keyword == "Locate_Remote":
                remote_location = get_remote_location(distinguished_name)
                return f"Дистанционно ({remote_location})"
            return location

    return "Неизвестно"


def get_remote_location(distinguished_name):
    remote_locations = {
        "Arhangelsk": "Архангельск",
        "Astrahan": "Астрахань",
        "Barnaul": "Барнаул",
        "Belgorod": "Белгород",
        "Bryansk": "Брянск",
        "Chelyabinsk": "Челябинск",
        "Ekaterinburg": "Екатеринбург",
        "Irkutsk": "Иркутск",
        "Ivanovo": "Иваново",
        "Kaliningrad": "Калининград",
        "Kaluga": "Калуга",
        "Kazan": "Казань",
        "Kemerovo": "Кемерово",
        "Kiev": "Киев",
        "Kostroma": "Кострома",
        "Krasnodar": "Краснодар",
        "Krasnoyarsk": "Красноярск",
        "Moscow": "Москва",
        "Murmansk": "Мурманск",
        "NaberezhnieChelny": "Набережные Челны",
        "NizhniyNovgorod": "Нижний Новгород",
        "Novgorod": "Новгород",
        "Novorossisk": "Новороссийск",
        "Novosibirsk": "Новосибирск",
        "Omsk": "Омск",
        "Orenburg": "Оренбург",
        "Oskol": "Старый Оскол",
        "Penza": "Пенза",
        "Perm": "Пермь",
        "Petrozavodsk": "Петрозаводск",
        "Pyatigorsk": "Пятигорск",
        "Rostov-na-Donu": "Ростов-на-Дону",
        "Ryazan": "Рязань",
        "Samara": "Самара",
        "Sankt-Peterburg": "Санкт-Петербург",
        "Saratov": "Саратов",
        "Sochi": "Сочи",
        "Stavropol": "Ставрополь",
        "Surgut": "Сургут",
        "Tolyatti": "Тольятти",
        "Tula": "Тула",
        "Tver": "Тверь",
        "Tyumen": "Тюмень",
        "Ufa": "Уфа",
        "Ulyanovsk": "Ульяновск",
        "Vladikavkaz": "Владикавказ",
        "Vladimir": "Владимир",
        "Vladivostok": "Владивосток",
        "Volgograd": "Волгоград",
        "Vologda": "Вологда",
        "Voronezh": "Воронеж",
        "Yaroslavl": "Ярославль"
    }
    for location, name in remote_locations.items():
        if location in distinguished_name:
            return name
    return "Дистанционно"