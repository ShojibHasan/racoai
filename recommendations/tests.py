from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase

from catalog.models import Category, Product

from .services import descendant_category_ids, recommend


class RecommendationServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.electronics = Category.objects.create(name="Electronics", slug="electronics")
        self.phones = Category.objects.create(name="Phones", slug="phones", parent=self.electronics)
        self.android = Category.objects.create(name="Android", slug="android", parent=self.phones)
        self.laptops = Category.objects.create(name="Laptops", slug="laptops", parent=self.electronics)
        self.books = Category.objects.create(name="Books", slug="books")

    def _product(self, sku, category, active=True):
        return Product.objects.create(
            name=sku, sku=sku, price=Decimal("1.00"), stock=5, category=category,
            status=Product.ACTIVE if active else Product.INACTIVE,
        )

    def test_dfs_collects_all_descendants(self):
        ids = descendant_category_ids(self.electronics.id)
        self.assertEqual(
            ids,
            {self.electronics.id, self.phones.id, self.android.id, self.laptops.id},
        )

    def test_dfs_leaf_returns_self_only(self):
        self.assertEqual(descendant_category_ids(self.books.id), {self.books.id})

    def test_recommend_covers_subtree_excludes_self(self):
        seed = self._product("SEED", self.phones)
        cousin = self._product("COUSIN", self.laptops)
        deep = self._product("DEEP", self.android)
        other = self._product("OTHER", self.books)
        result = list(recommend(seed))
        self.assertIn(cousin, result)
        self.assertIn(deep, result)
        self.assertNotIn(seed, result)
        self.assertNotIn(other, result)

    def test_recommend_skips_inactive(self):
        seed = self._product("SEED2", self.phones)
        inactive = self._product("INACT", self.laptops, active=False)
        self.assertNotIn(inactive, list(recommend(seed)))

    def test_no_category_returns_empty(self):
        loner = self._product("LONER", None)
        self.assertEqual(list(recommend(loner)), [])
