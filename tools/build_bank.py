import json,re,random,glob,os
R='/workspace/cyberquiz'
LAW={'A':'Luật An ninh mạng số 116/2025/QH15','B':'Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15'}
DEC={'327':'phòng ngừa, xử lý thông tin xâm phạm ANQG, TTATXH trên không gian mạng','328':'phòng, chống tin giả, tin sai sự thật','329':'lực lượng bảo vệ an ninh mạng','330':'xử phạt VPHC lĩnh vực an ninh mạng và bảo vệ dữ liệu cá nhân','331':'bảo vệ an ninh mạng đối với hệ thống thông tin','332':'kinh doanh sản phẩm, dịch vụ an ninh mạng','333':'quy định chi tiết và biện pháp thi hành Luật An ninh mạng'}
def law(c):
    out=[]
    for x in c.split(';'):
        x=x.strip()
        if x=='H': out.append('Cẩm nang “Kết nối không tổn thương” 2026 (Chiến dịch Không Một Mình)');continue
        if x.startswith('N'): out.append(f'Nghị định {x[1:]}/2026/NĐ-CP ({DEC[x[1:]]})');continue
        m=re.fullmatch(r'([AB])(\d+)?(?:\.(\d+)([a-zđ]?))?',x); assert m,x
        L,d,k,p=m.groups(); s=''
        if p: s+=f'điểm {p} '
        if k: s+=f'khoản {k} '
        if d: s+=f'Điều {d} '
        out.append((s[0].upper()+s[1:] if s else '')+LAW[L])
    return '; '.join(out)
qs=[];rnd=random.Random(2026);n=0
for f in sorted(glob.glob(R+'/bank/c*.txt')):
    for ln in open(f,encoding='utf-8'):
        ln=ln.strip()
        if not ln: continue
        p=ln.split('|'); assert len(p)==11,(f,ln[:60],len(p))
        lv,df,tags,img,sit,c,w1,w2,w3,sp,lw=p
        n+=1; opts=[c,w1,w2,w3]; rnd.shuffle(opts)
        qs.append({'id':n,'level':int(lv),'difficulty':int(df),'tags':tags.split(','),'image':f'img/{img}.svg','situation':sit,'options':opts,'answer':opts.index(c),'spell':sp,'legal':law(lw),'source':'ORIGINAL'})
json.dump({'version':1,'updated':'2026-10-15','questions':qs},open(R+'/questions.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(qs),Counter(q['level'] for q in qs),sorted(set(q['image'] for q in qs)))
