import json
from pathlib import Path
import execution_agent as ea

ROOT = Path(__file__).resolve().parent

PID = "gid://shopify/Product/<id>"

COLOR_GROUPS = [
    ("Wine Maroon", "WMR"),
    ("Deep Maroon", "DMR"),
    ("Emerald Green", "EMR"),
    ("Turquoise Blue", "TRQ"),
    ("Mustard Yellow", "MYL"),
    ("Crimson Red", "RED"),
    ("Rani Pink", "RNP"),
    ("Multi Color", "MLT"),
]
SIZES = ["2.4", "2.6", "2.8"]

# First update existing variant (Wine Maroon / 2.4)
update_mut = """
mutation($pid: ID!, $v: [ProductVariantsBulkInput!]!) {
    productVariantsBulkUpdate(productId: $pid, variants: $v) {
        productVariants {
            id
            title
            sku
            price
        }
        userErrors { field message }
    }
}
"""
up_res = ea.gql(update_mut, {
    "pid": PID,
    "v": [{
        "id": "gid://shopify/ProductVariant/<id>",
        "price": "1299.00",
        "compareAtPrice": "2499.00",
        "sku": "BB-JHM-WMR-2.4"
    }]
})
print("Updated first variant:", up_res)

# Now prepare the remaining 23 variants to create
variants_to_create = []
for color, code in COLOR_GROUPS:
    for sz in SIZES:
        if color == "Wine Maroon" and sz == "2.4":
            continue  # already exists
        sku = f"BB-JHM-{code}-{sz}"
        variants_to_create.append({
            "optionValues": [
                {"name": color, "optionName": "Color"},
                {"name": sz, "optionName": "Size"}
            ],
            "price": "1299.00",
            "compareAtPrice": "2499.00",
            "sku": sku
        })

print(f"Creating {len(variants_to_create)} additional variants...")

create_mut = """
mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
        productVariants {
            id
            title
            sku
            price
        }
        userErrors {
            field
            message
        }
    }
}
"""

c_res = ea.gql(create_mut, {
    "productId": PID,
    "variants": variants_to_create
})

print("Creation response:", json.dumps(c_res, indent=2))
