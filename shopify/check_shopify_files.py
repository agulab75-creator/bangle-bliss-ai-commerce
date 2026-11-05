import json
import execution_agent as ea

query = """{
  files(first: 50, reverse: true) {
    nodes {
      ... on MediaImage {
        id
        alt
        image {
          url
        }
      }
    }
  }
}"""

res = ea.execute_shopify_graphql(query)
nodes = res.get('data', {}).get('files', {}).get('nodes', [])
print(f"Total files returned: {len(nodes)}")
for n in nodes[:25]:
    gid = n.get('id', '')
    num_id = gid.split('/')[-1] if gid else ''
    url = (n.get('image') or {}).get('url', '')
    print(f"ID: {num_id} | URL: {url[:70]}")
