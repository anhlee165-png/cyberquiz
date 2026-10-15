import json
qs=json.load(open('/workspace/cyberquiz/questions.json'))['questions']
lit=lambda s:"'"+str(s).replace("'","''")+"'"
rows=[f"({q['id']},{q['level']},{q['difficulty']},ARRAY[{','.join(lit(t) for t in q['tags'])}]::text[],{lit(q['image'])},{lit(q['situation'])},{lit(json.dumps(q['options'],ensure_ascii=False))}::jsonb,{q['answer']},{lit(q['spell'])},{lit(q['legal'])},{lit(q['source'])})" for q in qs]
open('/workspace/cyberquiz/supabase/seed.sql','w').write("insert into questions(id,level,difficulty,tags,image,situation,options,answer,spell,legal,source) values\n"+",\n".join(rows)+"\non conflict(id) do nothing;\n")
