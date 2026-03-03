"""Constants for Waktu Solat Malaysia integration."""

DOMAIN = "solat_my"

API_BASE_URL = "https://solat.my/api"
API_DAILY_ENDPOINT = "/daily/{zone}"
API_LOCATIONS_ENDPOINT = "/locations"

DEFAULT_SCAN_INTERVAL = 3600  # 1 hour in seconds

CONF_NAME = "name"
CONF_ZONE = "zone"

DEFAULT_NAME = "Waktu Solat"
DEFAULT_ZONE = "SGR01"

# Prayer time keys from API
PRAYER_IMSAK = "imsak"
PRAYER_FAJR = "fajr"
PRAYER_SYURUK = "syuruk"
PRAYER_DHUHA = "dhuha"
PRAYER_DHUHR = "dhuhr"
PRAYER_ASR = "asr"
PRAYER_MAGHRIB = "maghrib"
PRAYER_ISHA = "isha"

PRAYER_TIMES = [
    PRAYER_IMSAK,
    PRAYER_FAJR,
    PRAYER_SYURUK,
    PRAYER_DHUHA,
    PRAYER_DHUHR,
    PRAYER_ASR,
    PRAYER_MAGHRIB,
    PRAYER_ISHA,
]

PRAYER_NAMES_MS = {
    PRAYER_IMSAK: "Imsak",
    PRAYER_FAJR: "Subuh",
    PRAYER_SYURUK: "Syuruk",
    PRAYER_DHUHA: "Dhuha",
    PRAYER_DHUHR: "Zohor",
    PRAYER_ASR: "Asar",
    PRAYER_MAGHRIB: "Maghrib",
    PRAYER_ISHA: "Isyak",
}

PRAYER_NAMES_EN = {
    PRAYER_IMSAK: "Imsak",
    PRAYER_FAJR: "Fajr",
    PRAYER_SYURUK: "Syuruk",
    PRAYER_DHUHA: "Dhuha",
    PRAYER_DHUHR: "Dhuhr",
    PRAYER_ASR: "Asr",
    PRAYER_MAGHRIB: "Maghrib",
    PRAYER_ISHA: "Isha",
}

PRAYER_ICONS = {
    PRAYER_IMSAK: "mdi:weather-night",
    PRAYER_FAJR: "mdi:weather-sunset-up",
    PRAYER_SYURUK: "mdi:weather-sunrise",
    PRAYER_DHUHA: "mdi:weather-sunny-alert",
    PRAYER_DHUHR: "mdi:weather-sunny",
    PRAYER_ASR: "mdi:weather-partly-cloudy",
    PRAYER_MAGHRIB: "mdi:weather-sunset",
    PRAYER_ISHA: "mdi:weather-night",
}

# Malaysian prayer time zones
ZONES = {
    "JHR01": "Johor - Pulau Aur, Pemanggil",
    "JHR02": "Johor - Kota Tinggi, Mersing",
    "JHR03": "Johor - Kluang, Pontian",
    "JHR04": "Johor - Batu Pahat, Muar, Segamat, Gemas",
    "KDH01": "Kedah - Kota Setar, Kubang Pasu, Pokok Sena",
    "KDH02": "Kedah - Pendang, Yan, Sik",
    "KDH03": "Kedah - Padang Terap, Baling",
    "KDH04": "Kedah - Baling",
    "KDH05": "Kedah - Kulim, Bandar Baharu",
    "KDH06": "Kedah - Langkawi",
    "KDH07": "Kedah - Gunung Jerai",
    "KTN01": "Kelantan - Kota Bahru, Bachok, Pasir Puteh",
    "KTN02": "Kelantan - Jeli, Krai",
    "MLK01": "Melaka - Bandar Melaka, Alor Gajah, Jasin",
    "NGS01": "Negeri Sembilan - Jempol, Tampin",
    "NGS02": "Negeri Sembilan - Kuala Pilah, Rembau, Kerajaan",
    "NGS03": "Negeri Sembilan - Port Dickson, Seremban, Nilai",
    "PHG01": "Pahang - Pulau Tioman",
    "PHG02": "Pahang - Kuantan, Rompin",
    "PHG03": "Pahang - Maran, Chenor",
    "PHG04": "Pahang - Bentong, Temerloh, Jerantut",
    "PHG05": "Pahang - Genting Sempah, Janda Baik",
    "PHG06": "Pahang - Bukit Fraser",
    "PLS01": "Perlis - Kangar, Padang Besar",
    "PNG01": "Pulau Pinang - Seluruh Negeri",
    "PRK01": "Perak - Tapah, Slim River, Tanjung Malim",
    "PRK02": "Perak - Ipoh, Batu Gajah, Kampar",
    "PRK03": "Perak - Pengkalan Hulu, Hulu Perak",
    "PRK04": "Perak - Temengor, Belum",
    "PRK05": "Perak - Teluk Intan, Hilir Perak",
    "PRK06": "Perak - Selama, Kuala Kangsar, Sungai Siput",
    "PRK07": "Perak - Bukit Larut",
    "SBH01": "Sabah - Sandakan, Kinabatangan, Tongod",
    "SBH02": "Sabah - Pinangah, Membakut, Beaufort",
    "SBH03": "Sabah - Lahad Datu, Silam",
    "SBH04": "Sabah - Tawau, Semporna, Kunak",
    "SBH05": "Sabah - Kudat, Pitas, Marudu",
    "SBH06": "Sabah - Gunung Kinabalu",
    "SBH07": "Sabah - Kota Kinabalu, Papar, Ranau",
    "SBH08": "Sabah - Pensiangan, Keningau, Nabawan",
    "SBH09": "Sabah - Sipitang",
    "SGR01": "Selangor - Gombak, Petaling, Sepang, Hulu Langat",
    "SGR02": "Selangor - Sabak Bernam, Kuala Selangor, Hulu Selangor",
    "SGR03": "Selangor - Klang, Shah Alam, Kuala Langat",
    "SWK01": "Sarawak - Limbang, Lawas, Sundar, Trusan",
    "SWK02": "Sarawak - Miri, Niah, Bekenu, Sibuti",
    "SWK03": "Sarawak - Marudi, Baram, Matu, Song, Oya",
    "SWK04": "Sarawak - Sibu, Mukah, Dalat, Igan",
    "SWK05": "Sarawak - Sarikei, Meradong, Julau",
    "SWK06": "Sarawak - Sri Aman, Betong, Kabong",
    "SWK07": "Sarawak - Serian, Simunjan, Samarahan, Asajaya",
    "SWK08": "Sarawak - Kuching, Bau, Lundu, Sematan",
    "SWK09": "Sarawak - Zon Khas (Kapit, Belaga, Pakan)",
    "TRG01": "Terengganu - Kuala Terengganu, Marang, Hulu Terengganu",
    "TRG02": "Terengganu - Besut, Setiu",
    "TRG03": "Terengganu - Hulu Terengganu",
    "TRG04": "Terengganu - Kemaman, Dungun",
    "WLY01": "W.P. Kuala Lumpur & Putrajaya",
    "WLY02": "W.P. Labuan",
}
