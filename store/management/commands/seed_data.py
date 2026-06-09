from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product


CATEGORIES = [
    {
        "name": "Electronics",
        "description": "Gadgets, devices, and all things tech.",
        "image": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&fit=crop",
    },
    {
        "name": "Clothing",
        "description": "Everyday fashion for men and women.",
        "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=800&fit=crop",
    },
    {
        "name": "Books",
        "description": "Fiction, non-fiction, and everything in between.",
        "image": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800&fit=crop",
    },
    {
        "name": "Home & Kitchen",
        "description": "Everything you need to make your home shine.",
        "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&fit=crop",
    },
    {
        "name": "Sports & Outdoors",
        "description": "Gear for athletes and outdoor adventurers.",
        "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&fit=crop",
    },
    {
        "name": "Beauty & Health",
        "description": "Skincare, grooming, and wellness products.",
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&fit=crop",
    },
]

PRODUCTS = [
    # Electronics
    {
        "category": "Electronics",
        "name": "Wireless Noise-Cancelling Headphones",
        "brand": "SoundCore",
        "description": "Premium over-ear headphones with active noise cancellation, 30-hour battery life, and foldable design for travel.",
        "price": "89.99",
        "stock": 42,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&fit=crop",
        "is_featured": True,
    },
    {
        "category": "Electronics",
        "name": "Mechanical Gaming Keyboard",
        "brand": "KeyForce",
        "description": "Full-size mechanical keyboard with RGB backlighting, tactile blue switches, and USB-C detachable cable.",
        "price": "64.99",
        "stock": 28,
        "image": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=800&fit=crop",
        "is_featured": False,
    },
    {
        "category": "Electronics",
        "name": "USB-C 65W GaN Charger",
        "brand": "ChargeFast",
        "description": "Compact GaN charger that charges laptops, tablets, and phones simultaneously. Folds flat for easy packing.",
        "price": "34.99",
        "stock": 85,
        "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&fit=crop",
        "is_featured": False,
    },
    # Clothing
    {
        "category": "Clothing",
        "name": "Classic Slim-Fit Chinos",
        "brand": "UrbanThread",
        "description": "Stretch-cotton slim-fit chinos in a versatile stone colour. Machine washable and wrinkle-resistant.",
        "price": "49.99",
        "stock": 60,
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&fit=crop",
        "is_featured": True,
    },
    {
        "category": "Clothing",
        "name": "Merino Wool Crew-Neck Sweater",
        "brand": "NorthKnit",
        "description": "100% extra-fine merino wool sweater. Naturally temperature-regulating, soft against skin, and odour-resistant.",
        "price": "79.99",
        "stock": 35,
        "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&fit=crop",
        "is_featured": False,
    },
    # Books
    {
        "category": "Books",
        "name": "Atomic Habits",
        "brand": "Penguin Random House",
        "description": "James Clear's bestselling guide to building good habits and breaking bad ones through tiny, incremental changes.",
        "price": "16.99",
        "stock": 120,
        "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&fit=crop",
        "is_featured": True,
    },
    {
        "category": "Books",
        "name": "The Design of Everyday Things",
        "brand": "Basic Books",
        "description": "Don Norman's classic on human-centred design. Essential reading for designers, engineers, and anyone who uses products.",
        "price": "19.99",
        "stock": 55,
        "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&fit=crop",
        "is_featured": False,
    },
    # Home & Kitchen
    {
        "category": "Home & Kitchen",
        "name": "Pour-Over Coffee Maker Set",
        "brand": "BrewCraft",
        "description": "Borosilicate glass pour-over brewer with a reusable stainless steel filter and a cork collar. Makes 600 ml per brew.",
        "price": "38.00",
        "stock": 47,
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&fit=crop",
        "is_featured": True,
    },
    {
        "category": "Home & Kitchen",
        "name": "Ceramic Non-Stick Frying Pan 28 cm",
        "brand": "PanPro",
        "description": "PFAS-free ceramic coating, induction-compatible base, and a stay-cool silicone handle. Dishwasher safe.",
        "price": "44.99",
        "stock": 33,
        "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=800&fit=crop",
        "is_featured": False,
    },
    # Sports & Outdoors
    {
        "category": "Sports & Outdoors",
        "name": "Adjustable Dumbbell Set (5–25 kg)",
        "brand": "IronFlex",
        "description": "Space-saving adjustable dumbbells that replace 15 pairs. Click-dial weight selection in 2.5 kg increments.",
        "price": "249.99",
        "stock": 18,
        "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&fit=crop",
        "is_featured": True,
    },
    {
        "category": "Sports & Outdoors",
        "name": "Trail Running Backpack 12 L",
        "brand": "PeakPack",
        "description": "Lightweight hydration-compatible trail pack with bounce-free fit, reflective strips, and trekking-pole attachments.",
        "price": "74.99",
        "stock": 22,
        "image": "https://images.unsplash.com/photo-1622260614153-03223fb72052?w=800&fit=crop",
        "is_featured": False,
    },
    # Beauty & Health
    {
        "category": "Beauty & Health",
        "name": "Vitamin C Brightening Serum 30 ml",
        "brand": "GlowLab",
        "description": "15% L-ascorbic acid serum with hyaluronic acid and vitamin E. Reduces dark spots and boosts collagen in 4 weeks.",
        "price": "29.99",
        "stock": 76,
        "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&fit=crop",
        "is_featured": True,
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample categories and products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing categories and products before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING("Cleared existing products and categories.")
            )

        category_map = {}
        for data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=slugify(data["name"]),
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "image": data["image"],
                },
            )
            category_map[data["name"]] = cat
            status = "Created" if created else "Already exists"
            self.stdout.write(f'  {status}: category "{cat.name}"')

        for data in PRODUCTS:
            cat = category_map[data["category"]]
            _, created = Product.objects.get_or_create(
                slug=slugify(data["name"]),
                defaults={
                    "category": cat,
                    "name": data["name"],
                    "brand": data["brand"],
                    "description": data["description"],
                    "price": data["price"],
                    "stock": data["stock"],
                    "image": data["image"],
                    "is_featured": data["is_featured"],
                    "is_active": True,
                },
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f'  {status}: product "{data["name"]}"')

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {Category.objects.count()} categories, {Product.objects.count()} products in DB."
            )
        )
