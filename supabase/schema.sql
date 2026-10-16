-- CyberQuiz backend (Supabase / Postgres). Chạy toàn bộ file trong Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists questions(
  id bigint primary key,
  level int not null check(level between 1 and 4),
  difficulty int not null check(difficulty between 1 and 3),
  tags text[] default '{}',
  image text,
  situation text not null,
  options jsonb not null,
  answer int not null check(answer between 0 and 3),
  spell text, legal text, source text default 'ORIGINAL',
  hidden boolean default false,
  updated_at timestamptz default now()
);
create table if not exists admins(
  username text primary key,
  pass_hash text not null,
  role text not null default 'admin' check(role in ('super','admin')),
  created_at timestamptz default now()
);
create table if not exists admin_sessions(
  token uuid primary key default gen_random_uuid(),
  username text references admins(username) on delete cascade,
  expires_at timestamptz not null default now()+interval '12 hours'
);
create table if not exists sessions(
  id uuid primary key default gen_random_uuid(),
  player text, age int, level int, total int, correct int, duration_sec int,
  created_at timestamptz default now()
);
create table if not exists answers(
  id bigserial primary key,
  session_id uuid references sessions(id) on delete cascade,
  question_id bigint, correct boolean, created_at timestamptz default now()
);

alter table questions enable row level security;
alter table admins enable row level security;
alter table admin_sessions enable row level security;
alter table sessions enable row level security;
alter table answers enable row level security;
-- Công khai: chỉ đọc câu hỏi không ẩn. Mọi ghi đều đi qua hàm SECURITY DEFINER bên dưới.
drop policy if exists q_read on questions;
create policy q_read on questions for select using (not hidden);

-- Ghi kết quả phiên (ẩn danh)
create or replace function submit_session(p_player text,p_age int,p_level int,p_duration int,p_answers jsonb)
returns uuid language plpgsql security definer set search_path=public,extensions as $$
declare sid uuid; a jsonb; n int:=0; c int:=0;
begin
  if jsonb_array_length(p_answers)>60 then raise exception 'too many'; end if;
  insert into sessions(player,age,level,total,correct,duration_sec)
    values(left(p_player,80),p_age,p_level,0,0,least(p_duration,86400)) returning id into sid;
  for a in select * from jsonb_array_elements(p_answers) loop
    insert into answers(session_id,question_id,correct) values(sid,(a->>'q')::bigint,(a->>'c')::boolean);
    n:=n+1; if (a->>'c')::boolean then c:=c+1; end if;
  end loop;
  update sessions set total=n,correct=c where id=sid;
  return sid;
end $$;

create or replace function _admin(p_token uuid) returns admins language plpgsql security definer set search_path=public,extensions as $$
declare r admins;
begin
  select a.* into r from admin_sessions s join admins a using(username) where s.token=p_token and s.expires_at>now();
  if r.username is null then raise exception 'unauthorized'; end if;
  return r;
end $$;

create or replace function admin_login(p_user text,p_pass text) returns jsonb language plpgsql security definer set search_path=public,extensions as $$
declare r admins; t uuid;
begin
  select * into r from admins where username=p_user;
  if r.username is null or r.pass_hash<>crypt(p_pass,r.pass_hash) then raise exception 'invalid login'; end if;
  insert into admin_sessions(username) values(p_user) returning token into t;
  return jsonb_build_object('token',t,'username',r.username,'role',r.role);
end $$;

-- Chỉ dùng MỘT LẦN để tạo super admin (bị khóa nếu đã có super admin)
create or replace function setup_super_admin(p_user text,p_pass text) returns text language plpgsql security definer set search_path=public,extensions as $$
begin
  if exists(select 1 from admins where role='super') then raise exception 'super admin already exists'; end if;
  insert into admins(username,pass_hash,role) values(p_user,crypt(p_pass,gen_salt('bf')),'super');
  return 'ok';
end $$;

create or replace function admin_create(p_token uuid,p_user text,p_pass text) returns text language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin
  if me.role<>'super' then raise exception 'only super admin'; end if;
  insert into admins(username,pass_hash,role) values(p_user,crypt(p_pass,gen_salt('bf')),'admin');
  return 'ok';
end $$;
create or replace function admin_delete(p_token uuid,p_user text) returns text language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin
  if me.role<>'super' then raise exception 'only super admin'; end if;
  delete from admins where username=p_user and role<>'super'; return 'ok';
end $$;
create or replace function admin_list(p_token uuid) returns setof jsonb language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin
  return query select jsonb_build_object('username',username,'role',role,'created_at',created_at) from admins order by created_at;
end $$;
create or replace function admin_change_password(p_token uuid,p_old text,p_new text) returns text language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin
  if me.pass_hash<>crypt(p_old,me.pass_hash) then raise exception 'wrong password'; end if;
  update admins set pass_hash=crypt(p_new,gen_salt('bf')) where username=me.username; return 'ok';
end $$;

create or replace function admin_questions(p_token uuid) returns setof questions language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin return query select * from questions order by id; end $$;

create or replace function admin_upsert_questions(p_token uuid,p_items jsonb) returns int language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token); q jsonb; n int:=0; nid bigint;
begin
  for q in select * from jsonb_array_elements(p_items) loop
    nid:=coalesce((q->>'id')::bigint,(select coalesce(max(id),0)+1 from questions));
    insert into questions(id,level,difficulty,tags,image,situation,options,answer,spell,legal,source,hidden,updated_at)
    values(nid,(q->>'level')::int,(q->>'difficulty')::int,
      coalesce(array(select jsonb_array_elements_text(q->'tags')),'{}'),q->>'image',q->>'situation',q->'options',(q->>'answer')::int,
      q->>'spell',q->>'legal',coalesce(q->>'source','ORIGINAL'),coalesce((q->>'hidden')::boolean,false),now())
    on conflict(id) do update set level=excluded.level,difficulty=excluded.difficulty,tags=excluded.tags,image=excluded.image,
      situation=excluded.situation,options=excluded.options,answer=excluded.answer,spell=excluded.spell,legal=excluded.legal,
      source=excluded.source,hidden=excluded.hidden,updated_at=now();
    n:=n+1;
  end loop; return n;
end $$;
create or replace function admin_delete_question(p_token uuid,p_id bigint) returns text language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin delete from questions where id=p_id; return 'ok'; end $$;

create or replace function admin_stats(p_token uuid) returns jsonb language plpgsql security definer set search_path=public,extensions as $$
declare me admins:=_admin(p_token);
begin
  return jsonb_build_object(
    'sessions',(select count(*) from sessions),
    'answers',(select count(*) from answers),
    'correct',(select count(*) from answers where correct),
    'by_level',(select coalesce(jsonb_agg(x),'[]') from (select level,count(*) n,round(avg(correct::numeric/nullif(total,0))*100,1) pct from sessions group by level order by level) x),
    'by_question',(select coalesce(jsonb_agg(x),'[]') from (select question_id id,count(*) n,sum(case when correct then 1 else 0 end) ok from answers group by question_id) x),
    'recent',(select coalesce(jsonb_agg(x),'[]') from (select player,age,level,total,correct,duration_sec,created_at from sessions order by created_at desc limit 50) x));
end $$;

revoke all on function _admin(uuid) from public, anon, authenticated;
grant execute on function submit_session(text,int,int,int,jsonb), admin_login(text,text), admin_create(uuid,text,text), admin_delete(uuid,text),
  admin_list(uuid), admin_change_password(uuid,text,text), admin_questions(uuid), admin_upsert_questions(uuid,jsonb),
  admin_delete_question(uuid,bigint), admin_stats(uuid) to anon;
revoke all on function setup_super_admin(text,text) from public, anon, authenticated;
