create extension if not exists pgcrypto;

create table if not exists public.users (
	id text primary key,
	email text unique,
	phone text unique,
	full_name text not null,
	display_name text,
	role text not null default 'traveller',
	password_hash text,
	profile_picture text,
	airport_code text,
	interests text[] not null default '{}',
	is_email_verified boolean not null default false,
	is_phone_verified boolean not null default false,
	contact_sharing jsonb not null default '{"email": false, "phone": false}'::jsonb,
	status text not null default 'active',
	created_at timestamptz not null default now()
);

create table if not exists public.connection_requests (
	id uuid primary key default gen_random_uuid(),
	user_a_id text not null references public.users(id) on delete restrict,
	user_b_id text not null references public.users(id) on delete restrict,
	status text not null default 'pending' check (status in ('pending', 'accepted', 'declined', 'cancelled')),
	created_at timestamptz not null default now(),
	responded_at timestamptz,
	accepted_at timestamptz,
	connection_id uuid,
	constraint connection_request_distinct_users check (user_a_id <> user_b_id)
);

create unique index if not exists connection_requests_one_pending_per_pair
	on public.connection_requests (least(user_a_id, user_b_id), greatest(user_a_id, user_b_id))
	where status = 'pending';

create index if not exists connection_requests_incoming_idx
	on public.connection_requests (user_b_id, status, created_at desc);

create index if not exists connection_requests_outgoing_idx
	on public.connection_requests (user_a_id, status, created_at desc);

create table if not exists public.confirmed_pairs (
	id uuid primary key default gen_random_uuid(),
	user_a_id text not null references public.users(id) on delete restrict,
	user_b_id text not null references public.users(id) on delete restrict,
	accepted_request_id uuid not null unique references public.connection_requests(id) on delete restrict,
	status text not null default 'active' check (status in ('active', 'disconnected')),
	created_at timestamptz not null default now(),
	accepted_at timestamptz not null default now(),
	disconnected_at timestamptz,
	constraint confirmed_pair_distinct_users check (user_a_id < user_b_id),
	constraint confirmed_pair_disconnect_timestamp check (
		(status = 'active' and disconnected_at is null)
		or (status = 'disconnected' and disconnected_at is not null)
	)
);

do $$
begin
	if not exists (
		select 1 from pg_constraint
		where conname = 'connection_requests_connection_id_fkey'
		  and conrelid = 'public.connection_requests'::regclass
	) then
		alter table public.connection_requests
			add constraint connection_requests_connection_id_fkey
			foreign key (connection_id) references public.confirmed_pairs(id) on delete restrict;
	end if;
end;
$$;

create unique index if not exists confirmed_pairs_one_active_pair_per_identity
	on public.confirmed_pairs (least(user_a_id, user_b_id), greatest(user_a_id, user_b_id))
	where status = 'active';

create table if not exists public.pairing_locks (
	user_id text primary key references public.users(id) on delete restrict,
	connection_id uuid not null references public.confirmed_pairs(id) on delete restrict,
	paired_at timestamptz not null default now(),
	constraint pairing_lock_one_member_per_pair unique (connection_id, user_id)
);

alter table public.connection_requests enable row level security;
alter table public.confirmed_pairs enable row level security;
alter table public.pairing_locks enable row level security;
alter table public.users enable row level security;

grant select on public.connection_requests to service_role;
grant select on public.confirmed_pairs to service_role;
grant select on public.pairing_locks to service_role;
grant select, insert, update, delete on public.users to service_role;

create or replace function public.create_connection_request(
	p_sender_user_id text,
	p_recipient_user_id text
) returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
	v_request public.connection_requests%rowtype;
	v_user_count integer;
begin
	if p_sender_user_id = p_recipient_user_id then
		raise exception 'You cannot connect with yourself';
	end if;

	perform id
	from public.users
	where id in (p_sender_user_id, p_recipient_user_id)
	order by id
	for update;

	select count(*) into v_user_count
	from public.users
	where id in (p_sender_user_id, p_recipient_user_id);
	if v_user_count <> 2 then
		raise exception 'User not found';
	end if;

	if exists (
		select 1 from public.pairing_locks
		where user_id in (p_sender_user_id, p_recipient_user_id)
	) then
		raise exception 'One or both users already belong to a pair';
	end if;

	select * into v_request
	from public.connection_requests
	where status = 'pending'
	  and least(user_a_id, user_b_id) = least(p_sender_user_id, p_recipient_user_id)
	  and greatest(user_a_id, user_b_id) = greatest(p_sender_user_id, p_recipient_user_id)
	limit 1;
	if found then
		return to_jsonb(v_request);
	end if;

	insert into public.connection_requests (user_a_id, user_b_id)
	values (p_sender_user_id, p_recipient_user_id)
	returning * into v_request;
	return to_jsonb(v_request);
exception
	when unique_violation then
		select * into v_request
		from public.connection_requests
		where status = 'pending'
		  and least(user_a_id, user_b_id) = least(p_sender_user_id, p_recipient_user_id)
		  and greatest(user_a_id, user_b_id) = greatest(p_sender_user_id, p_recipient_user_id)
		limit 1;
		if found then
			return to_jsonb(v_request);
		end if;
		raise exception 'One or both users already belong to a pair';
end;
$$;

create or replace function public.respond_to_connection_request(
	p_request_id uuid,
	p_actor_user_id text,
	p_response text
) returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
	v_request public.connection_requests%rowtype;
	v_pair public.confirmed_pairs%rowtype;
	v_now timestamptz := now();
begin
	select * into v_request
	from public.connection_requests
	where id = p_request_id
	;
	if not found then
		raise exception 'Connection request not found';
	end if;

	perform id
	from public.users
	where id in (v_request.user_a_id, v_request.user_b_id)
	order by id
	for update;

	select * into v_request
	from public.connection_requests
	where id = p_request_id
	for update;
	if not found then
		raise exception 'Connection request not found';
	end if;

	if p_response = 'accepted' and v_request.status = 'accepted' then
		select * into v_pair
		from public.confirmed_pairs
		where id = v_request.connection_id and status = 'active';
		if found then
			return to_jsonb(v_request);
		end if;
		raise exception 'This connection request has already been completed';
	end if;

	if v_request.status <> 'pending' then
		raise exception 'This connection request is no longer pending';
	end if;

	if p_response = 'declined' then
		if p_actor_user_id <> v_request.user_b_id then
			raise exception 'Only the recipient can decline this request';
		end if;
		update public.connection_requests
		set status = 'declined', responded_at = v_now
		where id = p_request_id
		returning * into v_request;
		return to_jsonb(v_request);
	elsif p_response = 'cancelled' then
		if p_actor_user_id <> v_request.user_a_id then
			raise exception 'Only the sender can cancel this request';
		end if;
		update public.connection_requests
		set status = 'cancelled', responded_at = v_now
		where id = p_request_id
		returning * into v_request;
		return to_jsonb(v_request);
	elsif p_response <> 'accepted' then
		raise exception 'Unsupported connection status';
	end if;

	if p_actor_user_id <> v_request.user_b_id then
		raise exception 'Only the recipient can accept this request';
	end if;
	if exists (
		select 1 from public.pairing_locks
		where user_id in (v_request.user_a_id, v_request.user_b_id)
	) then
		raise exception 'One or both users already belong to a pair';
	end if;

	insert into public.confirmed_pairs (user_a_id, user_b_id, accepted_request_id, accepted_at)
	values (
		least(v_request.user_a_id, v_request.user_b_id),
		greatest(v_request.user_a_id, v_request.user_b_id),
		p_request_id,
		v_now
	)
	returning * into v_pair;

	insert into public.pairing_locks (user_id, connection_id, paired_at)
	values
		(v_request.user_a_id, v_pair.id, v_now),
		(v_request.user_b_id, v_pair.id, v_now);

	update public.connection_requests
	set status = 'accepted', responded_at = v_now, accepted_at = v_now, connection_id = v_pair.id
	where id = p_request_id
	returning * into v_request;

	update public.connection_requests
	set status = 'cancelled', responded_at = v_now
	where status = 'pending'
	  and id <> p_request_id
	  and (user_a_id in (v_request.user_a_id, v_request.user_b_id)
		   or user_b_id in (v_request.user_a_id, v_request.user_b_id));

	return to_jsonb(v_request);
exception
	when unique_violation then
		raise exception 'One or both users already belong to a pair';
end;
$$;

create or replace function public.disconnect_connection(
	p_connection_id uuid,
	p_actor_user_id text
) returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
	v_pair public.confirmed_pairs%rowtype;
begin
	select * into v_pair
	from public.confirmed_pairs
	where id = p_connection_id
	for update;
	if not found then
		raise exception 'Connection not found';
	end if;
	if p_actor_user_id not in (v_pair.user_a_id, v_pair.user_b_id) then
		raise exception 'Only a member of this pair can disconnect it';
	end if;

	if v_pair.status = 'active' then
		update public.confirmed_pairs
		set status = 'disconnected', disconnected_at = now()
		where id = p_connection_id
		returning * into v_pair;
	end if;
	return to_jsonb(v_pair);
end;
$$;

revoke all on function public.create_connection_request(text, text) from public, anon, authenticated;
revoke all on function public.respond_to_connection_request(uuid, text, text) from public, anon, authenticated;
revoke all on function public.disconnect_connection(uuid, text) from public, anon, authenticated;
grant execute on function public.create_connection_request(text, text) to service_role;
grant execute on function public.respond_to_connection_request(uuid, text, text) to service_role;
grant execute on function public.disconnect_connection(uuid, text) to service_role;

create table if not exists public.airports (
	iata_code text primary key check (iata_code ~ '^[A-Z]{3}$'),
	icao_code text unique check (icao_code is null or icao_code ~ '^[A-Z]{4}$'),
	name text not null,
	city text not null,
	country text not null,
	country_code text not null check (country_code ~ '^[A-Z]{2}$'),
	latitude double precision not null check (latitude between -90 and 90),
	longitude double precision not null check (longitude between -180 and 180),
	timezone text not null,
	type text not null,
	source_name text not null,
	source_url text not null,
	source_snapshot_date date not null,
	updated_at timestamptz not null default now()
);

create index if not exists airports_city_country_search_idx
	on public.airports (lower(city), lower(country));

create table if not exists public.airport_price_quotes (
	id text primary key,
	airport_code text not null references public.airports(iata_code) on update cascade on delete restrict,
	category text not null,
	provider text not null,
	duration text not null,
	original_amount numeric(12, 2) not null check (original_amount >= 0),
	original_currency text not null check (original_currency ~ '^[A-Z]{3}$'),
	amount_usd numeric(12, 2) not null check (amount_usd >= 0),
	currency text not null default 'USD' check (currency = 'USD'),
	exchange_rate_to_usd numeric(18, 10),
	exchange_rate_date date,
	exchange_rate_source text,
	exchange_rate_source_url text,
	status text not null check (status in ('provider_quoted_converted', 'estimate', 'unavailable')),
	source_name text not null,
	source_url text not null,
	verified_at date,
	assumptions text not null,
	updated_at timestamptz not null default now()
);

create index if not exists airport_price_quotes_airport_category_idx
	on public.airport_price_quotes (airport_code, category, status);

alter table if exists public.bookings
	add column if not exists currency text;
alter table if exists public.bookings
	add column if not exists price_metadata jsonb;
alter table if exists public.payments
	add column if not exists currency text;

alter table public.airports enable row level security;
alter table public.airport_price_quotes enable row level security;
grant select on public.airports to service_role;
grant select, insert, update on public.airports to service_role;
grant select, insert, update on public.airport_price_quotes to service_role;
