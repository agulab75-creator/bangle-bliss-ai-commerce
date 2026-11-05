import json
import execution_agent as ea

all_products = []
cursor = None

while True:
    after_clause = f', after: "{cursor}"' if cursor else ''
    query = f'''
    query {{
      products(first: 50{after_clause}) {{
        pageInfo {{
          hasNextPage
          endCursor
        }}
        nodes {{
          id
          title
          handle
          status
          productType
          featuredMedia {{
            ... on MediaImage {{
              id
              image {{
                url
                altText
                width
                height
              }}
            }}
          }}
          media(first: 50) {{
            nodes {{
              ... on MediaImage {{
                id
                image {{
                  url
                  altText
                  width
                  height
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    res = ea.gql(query)
    prod_data = res.get('products', {})
    nodes = prod_data.get('nodes', [])
    all_products.extend(nodes)
    print(f"Fetched page, cumulative products: {len(all_products)}")
    page_info = prod_data.get('pageInfo', {})
    if page_info.get('hasNextPage'):
        cursor = page_info.get('endCursor')
    else:
        break

print(f"Total products retrieved from Shopify: {len(all_products)}")
with open('shopify_all_products_dump.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, indent=2)
print("Saved to shopify_all_products_dump.json")
