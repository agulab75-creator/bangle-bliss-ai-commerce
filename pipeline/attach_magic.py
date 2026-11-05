import json, subprocess, tempfile
from pathlib import Path
STORE="your-store.myshopify.com"
KUNDAN="gid://shopify/Product/<id>"; ROYAL="gid://shopify/Product/<id>"
def gql(q,v=None):
    d=Path(tempfile.mkdtemp()); qf,vf,of=d/"q",d/"v",d/"o"
    qf.write_text(q); cmd=f'shopify store execute --store {STORE} --query-file "{qf}" --output-file "{of}"'
    if v is not None: vf.write_text(json.dumps(v)); cmd+=f' --variable-file "{vf}"'
    if q.lstrip().startswith("mutation"): cmd+=" --allow-mutations"
    subprocess.run(cmd,shell=True,capture_output=True,text=True)
    j=json.loads(of.read_text()); return j.get("data",j)
F=json.load(open("magic_files.json"))
ORDER=[(2,"Sky Aqua",KUNDAN),(4,"Parrot Green",KUNDAN),(6,"Coral Peach",KUNDAN),(8,"Orchid Pink",KUNDAN),(9,"Mint Green",KUNDAN),
       (10,"Magenta",KUNDAN),(11,"Ruby Red",KUNDAN),(12,"Plum Wine",KUNDAN),(13,"Emerald Green",KUNDAN),(14,"Maroon",KUNDAN),(7,"Royal Blue",ROYAL)]
SHOT=["white studio","lifestyle","worn on hand","close-up detail"]
white={}
order={KUNDAN:[],ROYAL:[]}
for n,colour,pid in ORDER:
    files=F[str(n)]
    ups=[]
    for i,(ts,fid,url) in enumerate(files):
        ups.append({"id":fid,"alt":f"{colour} kundan glass bangles - {SHOT[i]}","referencesToAdd":[pid]})
        order[pid].append(fid)
    r=gql("mutation($f:[FileUpdateInput!]!){fileUpdate(files:$f){userErrors{message}}}",{"f":ups})
    print(colour,"attached",r["fileUpdate"]["userErrors"])
    white[(pid,colour)]=files[0][1]
# variants -> white shot
for pid in (KUNDAN,ROYAL):
    vs=gql('query($id:ID!){product(id:$id){variants(first:100){nodes{id selectedOptions{name value} media(first:5){nodes{id}}}}}}',{"id":pid})["product"]["variants"]["nodes"]
    det=[];app=[]
    for v in vs:
        col=next(o["value"] for o in v["selectedOptions"] if o["name"]=="Color")
        old=[m["id"] for m in v["media"]["nodes"]]
        if old: det.append({"variantId":v["id"],"mediaIds":old})
        app.append({"variantId":v["id"],"mediaIds":[white[(pid,col)]]})
    if det: print("detach",gql("mutation($p:ID!,$vm:[ProductVariantDetachMediaInput!]!){productVariantDetachMedia(productId:$p,variantMedia:$vm){userErrors{message}}}",{"p":pid,"vm":det}))
    print("append",gql("mutation($p:ID!,$vm:[ProductVariantAppendMediaInput!]!){productVariantAppendMedia(productId:$p,variantMedia:$vm){userErrors{message}}}",{"p":pid,"vm":app}))
    moves=[{"id":fid,"newPosition":str(i)} for i,fid in enumerate(order[pid])]
    print("reorder",gql("mutation($id:ID!,$m:[MoveInput!]!){productReorderMedia(id:$id,moves:$m){userErrors{message}}}",{"id":pid,"m":moves}))
