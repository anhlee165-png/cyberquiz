import json,re,random,glob,os
R='/workspace/cyberquiz'
LAW={'A':'Luật An ninh mạng số 116/2025/QH15','B':'Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15'}
DEC={'327':'phòng ngừa, xử lý thông tin xâm phạm ANQG, TTATXH trên không gian mạng','328':'phòng, chống tin giả, tin sai sự thật','329':'lực lượng bảo vệ an ninh mạng','330':'xử phạt VPHC lĩnh vực an ninh mạng và bảo vệ dữ liệu cá nhân','331':'bảo vệ an ninh mạng đối với hệ thống thông tin','332':'kinh doanh sản phẩm, dịch vụ an ninh mạng','333':'quy định chi tiết và biện pháp thi hành Luật An ninh mạng'}
def law(c):
    out=[]
    for x in c.split(';'):
        x=x.strip()
        if x=='H': out.append('Cẩm nang “Kết nối không tổn thương” 2026 (Chiến dịch Không Một Mình)');continue
        if x=='D356': out.append('Nghị định 356/2025/NĐ-CP ngày 31/12/2025 quy định chi tiết Luật Bảo vệ dữ liệu cá nhân');continue
        if x.startswith('N'): out.append(f'Nghị định {x[1:]}/2026/NĐ-CP ({DEC[x[1:]]})');continue
        m=re.fullmatch(r'([AB])(\d+)?(?:\.(\d+)([a-zđ]?))?',x); assert m,x
        L,d,k,p=m.groups(); s=''
        if p: s+=f'điểm {p} '
        if k: s+=f'khoản {k} '
        if d: s+=f'Điều {d} '
        out.append((s[0].upper()+s[1:] if s else '')+LAW[L])
    return '; '.join(out)
TAG={'matkhau':'mật khẩu','nguoila':'người lạ','anhrieng':'quyền riêng tư','linkla':'lừa đảo','tingia':'tin giả','batnat':'bắt nạt mạng','taikhoan':'tài khoản','dulieu':'dữ liệu cá nhân','webcam':'camera','banquyen':'bản quyền','game':'game','baocao':'báo cáo','muasam':'mua sắm','deepfake':'AI-deepfake','cookie':'cookie','hack':'tấn công mạng','luat':'pháp luật','luadao':'lừa đảo'}
rnd=random.Random(2026)
orig=[]
for f in sorted(glob.glob(R+'/bank/c*.txt')):
    for ln in open(f,encoding='utf-8'):
        ln=ln.strip()
        if not ln: continue
        p=ln.split('|'); assert len(p)==11,(f,ln[:60],len(p))
        lv,df,tags,img,sit,c,w1,w2,w3,sp,lw=p
        opts=[c,w1,w2,w3]; rnd.shuffle(opts)
        orig.append({'level':int(lv),'difficulty':int(df),'tags':tags.split(','),'image':f'img/{img}.svg','situation':sit,'options':opts,'answer':opts.index(c),'spell':sp,'legal':law(lw),'source':'ORIGINAL'})
# drop 3 originals from the most crowded level (4): last three of level 4
l4=[len(orig)-3,len(orig)-2,len(orig)-1]  # fixed: last 3 lines of bank/c4.txt
orig=[q for i,q in enumerate(orig) if i not in l4]
src={x['n']:x for x in json.load(open('/workspace/hhanm/questions.json',encoding='utf-8'))}
NOSH=re.compile(r'tất cả|cả 3|cả ba|cả a|cả hai|các phương án|các đáp án',re.I)
hh=[]
for f in sorted(glob.glob(R+'/hh/b*.txt')):
    for ln in open(f,encoding='utf-8'):
        ln=ln.strip()
        if not ln: continue
        n,lv,img,sit,sp,lw=ln.split('|'); n=int(n); x=src[n]
        opts=[re.sub(r'^\s*\d+\.\s*','',o).strip() for o in x['opts']]
        assert len(opts)==4 and len(x['correct'])==1,n
        c=opts[x['correct'][0]-1]
        if not any(NOSH.search(o) for o in opts): rnd.shuffle(opts)
        hh.append({'level':int(lv),'difficulty':int(x['lv']),'tags':[TAG[img]],'image':f'img/{img}.svg','situation':sit,'options':opts,'answer':opts.index(c),'spell':sp,'legal':law(lw),'source':f'HHANM-{n}'})
assert len(hh)==397 and len({q['source'] for q in hh})==397
qs=orig+hh
for i,q in enumerate(qs,1): q['id']=i
qs=[{'id':q.pop('id'),**q} for q in qs]
assert len(qs)==600
json.dump({'version':2,'updated':'2026-10-15','questions':qs},open(R+'/questions.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(qs),sorted(Counter(q['level'] for q in qs).items()),Counter(q['source'][:5] for q in qs),sorted(Counter((q['source'][:5],q['level']) for q in qs).items()))
