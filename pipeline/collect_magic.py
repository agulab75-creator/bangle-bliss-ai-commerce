import json, re, subprocess, tempfile, urllib.request, os
from pathlib import Path
from PIL import Image, ImageDraw
STORE="your-store.myshopify.com"
def gql(q,v=None):
    d=Path(tempfile.mkdtemp()); qf,vf,of=d/"q",d/"v",d/"o"
    qf.write_text(q); cmd=f'shopify store execute --store {STORE} --query-file "{qf}" --output-file "{of}"'
    if v is not None: vf.write_text(json.dumps(v)); cmd+=f' --variable-file "{vf}"'
    subprocess.run(cmd,shell=True,capture_output=True,text=True)
    j=json.loads(of.read_text()); return j.get("data",j)
NAMES={2:"Sky Aqua",4:"Parrot Green",6:"Coral Peach",8:"Orchid Pink",9:"Mint Green",10:"Magenta",11:"Ruby Red",12:"Plum Wine",13:"Emerald Green",14:"Maroon",7:"Royal Blue"}
nodes=[];cur=None
while True:
    r=gql('query($a:String){files(first:100,after:$a,sortKey:CREATED_AT,reverse:true){nodes{id createdAt ... on MediaImage{image{url}}} pageInfo{hasNextPage endCursor}}}',{"a":cur})["files"]
    nodes+=r["nodes"]
    if not r["pageInfo"]["hasNextPage"] or len(nodes)>300: break
    cur=r["pageInfo"]["endCursor"]
groups={}
for n in nodes:
    if not n.get("image"): continue
    m=re.search(r"bb-glass-image-(\d+)(?:_[0-9a-f-]{36})?\.png",n["image"]["url"])
    if m and n["createdAt"]>="2026-10-05T06:05:00Z":
        groups.setdefault(int(m.group(1)),[]).append((n["createdAt"],n["id"],n["image"]["url"]))
out={}
for k,v in groups.items():
    v.sort(); out[k]=v[:4] if len(v)>=4 else v
    print(NAMES.get(k,k),len(v))
json.dump(out,open("magic_files.json","w"))
# contact sheets
os.makedirs("review",exist_ok=True)
order=[2,4,6,8,9,10,11,12,13,14,7]
T=300
for part,(a,b) in enumerate([(0,6),(6,11)]):
    ks=order[a:b]
    W=Image.new("RGB",(4*T,len(ks)*(T+16)),"white");d=ImageDraw.Draw(W)
    for i,k in enumerate(ks):
        for j,(ts,fid,url) in enumerate(out.get(k,[])[:4]):
            p=f"review/{k}-{j+1}.png"
            if not os.path.exists(p): urllib.request.urlretrieve(url,p)
            im=Image.open(p).convert("RGB"); im.thumbnail((T,T)); W.paste(im,(j*T,i*(T+16)+16))
        d.text((4,i*(T+16)+2),f"{NAMES[k]}: shot1 white | shot2 lifestyle | shot3 hand | shot4 macro",fill="black")
    W.save(f"review/sheet{part}.jpg",quality=85)
