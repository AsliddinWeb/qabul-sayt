from django.core.management.base import BaseCommand
from apps.regions.models import Country, Region, District


class Command(BaseCommand):
    help = "O‘zbekiston davlatiga barcha viloyat va tumanlarni qo‘shadi"

    def handle(self, *args, **kwargs):
        try:
            uzbekistan = Country.objects.get(id=1)
        except Country.DoesNotExist:
            self.stdout.write(self.style.ERROR("Country with id=1 (O‘zbekiston) topilmadi."))
            return

        regions_districts = {
            "Toshkent shahri": ["Bektemir", "Chilonzor", "Hamza (Yashnobod)", "Mirobod", "Mirzo Ulug‘bek",
                                "Olmazor", "Sergeli", "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yunusobod"],
            "Toshkent viloyati": ["Angren", "Bekobod", "Bo‘ka", "Bo‘stonliq", "Chinoz", "Ohangaron", "Oqqo‘rg‘on",
                                  "Parkent", "Piskent", "Quyi Chirchiq", "Toshkent tumani", "Yangiyo‘l", "Yuqori Chirchiq", "Zangiota"],
            "Andijon": ["Andijon shahri", "Andijon tumani", "Asaka", "Baliqchi", "Bo‘z", "Buloqboshi",
                        "Izboskan", "Jalaquduq", "Qo‘rg‘ontepa", "Marhamat", "Oltinko‘l", "Paxtaobod",
                        "Shahrixon", "Ulug‘nor", "Xo‘jaobod"],
            "Namangan": ["Namangan shahri", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Norin", "Pop",
                         "To‘raqo‘rg‘on", "Uchqo‘rg‘on", "Yangiqo‘rg‘on"],
            "Farg‘ona": ["Farg‘ona shahri", "Qo‘qon", "Marg‘ilon", "Beshariq", "Bog‘dod", "Buvayda",
                         "Dang‘ara", "Furqat", "Oltiariq", "Quva", "Rishton", "So‘x", "Toshloq",
                         "Uchko‘prik", "Yozyovon"],
            "Samarqand": ["Samarqand shahri", "Bulung‘ur", "Ishtixon", "Jomboy", "Kattaqo‘rg‘on", "Kattaqo‘rg‘on tumani",
                          "Narpay", "Nurobod", "Oqdaryo", "Paxtachi", "Payariq", "Pastdarg‘om", "Samarqand tumani",
                          "Tayloq", "Urgut"],
            "Buxoro": ["Buxoro shahri", "Buxoro tumani", "G‘ijduvon", "Jondor", "Kogon", "Kogon tumani",
                       "Olot", "Peshku", "Qorako‘l", "Qorovulbozor", "Romitan", "Shofirkon", "Vobkent"],
            "Qashqadaryo": ["Qarshi shahri", "Qarshi tumani", "Dehqonobod", "G‘uzor", "Kasbi", "Kitob",
                            "Koson", "Mirishkor", "Muborak", "Nishon", "Shahrisabz", "Shahrisabz tumani",
                            "Yakkabog‘", "Chiroqchi"],
            "Surxondaryo": ["Termiz shahri", "Angor", "Bandixon", "Boysun", "Denov", "Jarqo‘rg‘on", "Qiziriq",
                            "Qumqo‘rg‘on", "Muzrabot", "Oltinsoy", "Sariosiyo", "Sherobod", "Sho‘rchi", "Termiz tumani"],
            "Jizzax": ["Jizzax shahri", "Arnasoy", "Baxmal", "Dostlik", "Forish", "G‘allaorol", "Sharof Rashidov",
                       "Mirzacho‘l", "Paxtakor", "Yangiobod", "Zafarobod", "Zarbdor", "Zomin"],
            "Sirdaryo": ["Guliston shahri", "Boyovut", "Guliston tumani", "Mirzaobod", "Oqoltin",
                         "Sayxunobod", "Sardoba", "Sirdaryo", "Xovos", "Shirin", "Yangiyer"],
            "Navoiy": ["Navoiy shahri", "Karmana", "Konimex", "Navbahor", "Nurota", "Xatirchi",
                       "Qiziltepa", "Tomdi", "Uchquduq", "Zarafshon"],
            "Xorazm": ["Urganch shahri", "Bog‘ot", "Gurlan", "Hazorasp", "Xiva", "Xiva tumani",
                       "Qo‘shko‘pir", "Shovot", "Urganch tumani", "Yangiariq", "Yangibozor"],
            "Qoraqalpog‘iston Respublikasi": ["Nukus shahri", "Amudaryo", "Beruniy", "Chimboy", "Ellikqal’a", "Kegeyli",
                                              "Mo‘ynoq", "Nukus tumani", "Qo‘ng‘irot", "Qanliko‘l", "Qorao‘zak", "Shumanay",
                                              "Taxtako‘pir", "To‘rtko‘l", "Xo‘jayli"]
        }

        total_regions = 0
        total_districts = 0

        for region_name, districts in regions_districts.items():
            region, created = Region.objects.get_or_create(name=region_name, country=uzbekistan)
            if created:
                total_regions += 1
            for district_name in districts:
                _, created = District.objects.get_or_create(name=district_name, region=region)
                if created:
                    total_districts += 1

        self.stdout.write(self.style.SUCCESS(
            f"{total_regions} ta viloyat/shahar va {total_districts} ta tuman muvaffaqiyatli qo‘shildi."))
