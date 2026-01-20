-- Supabase Postgres schema for AI-Powered HRMS

create table if not exists teachers (
  id bigserial primary key,
  name text not null,
  phone text not null unique,
  department text,
  subjects text[],
  workload integer
);

create table if not exists admins (
  id bigserial primary key,
  name text not null,
  phone text not null unique
);

create table if not exists timetables (
  id bigserial primary key,
  teacher_id bigint not null references teachers(id) on delete cascade,
  day_of_week smallint not null check (day_of_week between 0 and 6),
  start_time time not null,
  end_time time not null,
  class text not null,
  subject text not null
);

create table if not exists leaves (
  id bigserial primary key,
  teacher_id bigint not null references teachers(id) on delete cascade,
  start_date date not null,
  end_date date not null,
  reason text,
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at timestamptz not null default now()
);

create table if not exists substitutions (
  id bigserial primary key,
  leave_id bigint not null references leaves(id) on delete cascade,
  substitute_teacher_id bigint not null references teachers(id) on delete cascade,
  status text not null default 'pending' check (status in ('pending','confirmed','rejected')),
  created_at timestamptz not null default now()
);

create table if not exists notifications (
  id bigserial primary key,
  target_phone text not null,
  message text not null,
  twilio_sid text,
  status text not null default 'queued' check (status in ('queued','sent','failed')),
  created_at timestamptz not null default now()
);

-- Helpful indexes
create index if not exists idx_teachers_phone on teachers(phone);
create index if not exists idx_admins_phone on admins(phone);
create index if not exists idx_timetables_teacher_day on timetables(teacher_id, day_of_week);
create index if not exists idx_leaves_teacher on leaves(teacher_id);
create index if not exists idx_subs_leave_teacher on substitutions(leave_id, substitute_teacher_id);

-- RLS placeholders (adjust per your auth model)
-- alter table teachers enable row level security;
-- alter table admins enable row level security;
-- alter table timetables enable row level security;
-- alter table leaves enable row level security;
-- alter table substitutions enable row level security;
-- alter table notifications enable row level security;


