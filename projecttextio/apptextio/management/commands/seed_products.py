from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from decimal import Decimal
from apptextio.models import Product, Category, SizeVariant, Variant


class Command(BaseCommand):
    help = "Seed the database with 5 products and 5 variants each"

    def handle(self, *args, **options):
        # Get or create a default category
        category, created = Category.objects.get_or_create(name="T-Shirts")
        
        # Get or create size variants
        sizes = []
        for size_choice in ['S', 'M', 'L', 'XL']:
            size_obj, _ = SizeVariant.objects.get_or_create(size=size_choice)
            sizes.append(size_obj)

        # Product data
        products_data = [
            {
                "brand": "TrendWear",
                "title": "Classic Cotton T-Shirt",
                "description": "Premium quality 100% cotton t-shirt, perfect for everyday wear.",
                "base_price": Decimal("500.00"),
            },
            {
                "brand": "StyleMax",
                "title": "Premium Polo Shirt",
                "description": "Elegant polo shirt made from high-quality material, ideal for casual and formal occasions.",
                "base_price": Decimal("750.00"),
            },
            {
                "brand": "ComfortZone",
                "title": "Graphic Print T-Shirt",
                "description": "Cool graphic printed t-shirt with trendy designs and comfortable fit.",
                "base_price": Decimal("450.00"),
            },
            {
                "brand": "FitLife",
                "title": "Sports Performance Tee",
                "description": "Breathable sports t-shirt designed for active lifestyle and gym workouts.",
                "base_price": Decimal("800.00"),
            },
            {
                "brand": "ElegantStudio",
                "title": "Solid Color Crew Neck",
                "description": "Simple yet elegant crew neck t-shirt available in multiple solid colors.",
                "base_price": Decimal("550.00"),
            },
        ]

        # Variant colors
        colors = ["White", "Black", "Blue", "Red", "Green"]

        # Create products and variants
        for product_idx, product_data in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                title=product_data["title"],
                defaults={
                    "category": category,
                    "brand": product_data["brand"],
                    "description": product_data["description"],
                    "base_price": product_data["base_price"],
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created product: {product.title}")
                )
            else:
                self.stdout.write(f"○ Product already exists: {product.title}")

            # Create 5 variants for each product
            for variant_idx, size in enumerate(sizes):
                color = colors[variant_idx]
                
                # Generate or use placeholder image
                try:
                    # Create a simple colored image
                    img = Image.new('RGB', (200, 200), color=color)
                    img_io = BytesIO()
                    img.save(img_io, 'JPEG')
                    img_io.seek(0)
                    image_content = ContentFile(img_io.read(), name=f'{product.title.lower().replace(" ", "_")}_{color.lower()}.jpg')
                except:
                    image_content = None

                # Calculate discounted price (10% discount)
                dis_price = product_data["base_price"] * Decimal("0.90")

                variant, variant_created = Variant.objects.get_or_create(
                    product=product,
                    size=size,
                    color=color,
                    defaults={
                        "price": product_data["base_price"],
                        "dis_price": dis_price,
                        "stock": 50,
                        "image": image_content if image_content else "img",
                    }
                )

                if variant_created:
                    self.stdout.write(
                        f"  ├─ Created variant: {color} - {size.get_size_display()}"
                    )
                else:
                    self.stdout.write(
                        f"  ├─ Variant already exists: {color} - {size.get_size_display()}"
                    )

        self.stdout.write(
            self.style.SUCCESS("\n✓ Seeding completed successfully!")
        )
        self.stdout.write(
            f"\nTotal: 5 products × 4 variants (S, M, L, XL) = 20 product variants created"
        )
