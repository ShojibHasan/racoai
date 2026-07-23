from django.core.cache import cache

from catalog.models import Category, Product

TREE_CACHE_KEY = "category_tree"
TREE_TTL = 3600


def category_tree():
    # Adjacency map {parent_id: [child_ids]}, cached to avoid repeat queries
    tree = cache.get(TREE_CACHE_KEY)
    if tree is not None:
        return tree
    tree = {}
    for row in Category.objects.values("id", "parent_id"):
        tree.setdefault(row["parent_id"], []).append(row["id"])
    cache.set(TREE_CACHE_KEY, tree, TREE_TTL)
    return tree


def clear_tree_cache():
    cache.delete(TREE_CACHE_KEY)


def descendant_category_ids(category_id):
    # Iterative DFS so a deep tree cannot blow the recursion limit
    tree = category_tree()
    seen = set()
    stack = [category_id]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for child in tree.get(current, []):
            if child not in seen:
                stack.append(child)
    return seen


def recommend(product, limit=10):
    if product.category_id is None:
        return Product.objects.none()
    # Start from the parent branch so siblings and cousins count as related
    category = product.category
    start = category.parent_id or category.id
    category_ids = descendant_category_ids(start)
    return (
        Product.objects.filter(status=Product.ACTIVE, category_id__in=category_ids)
        .exclude(pk=product.pk)
        .order_by("-created_at")[:limit]
    )
