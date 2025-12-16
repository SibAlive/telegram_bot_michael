--
-- PostgreSQL database dump
--

\restrict FV2eqUEzoqRQPjO7Wh88vMPRn0quv3EXZQk139TdhP3Yx9SlucgydBApcusbsdO

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: appoints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appoints (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    slot_id integer NOT NULL,
    service character(50) NOT NULL,
    accepted boolean NOT NULL,
    notified boolean DEFAULT false NOT NULL
);


ALTER TABLE public.appoints OWNER TO postgres;

--
-- Name: appoints_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.appoints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appoints_id_seq OWNER TO postgres;

--
-- Name: appoints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.appoints_id_seq OWNED BY public.appoints.id;


--
-- Name: doctor_slots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctor_slots (
    id integer NOT NULL,
    doctor_id integer NOT NULL,
    "time" timestamp without time zone NOT NULL,
    is_available boolean NOT NULL
);


ALTER TABLE public.doctor_slots OWNER TO postgres;

--
-- Name: doctor_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctor_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_slots_id_seq OWNER TO postgres;

--
-- Name: doctor_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctor_slots_id_seq OWNED BY public.doctor_slots.id;


--
-- Name: doctors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctors (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    speciality character varying(50) NOT NULL
);


ALTER TABLE public.doctors OWNER TO postgres;

--
-- Name: doctors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctors_id_seq OWNER TO postgres;

--
-- Name: doctors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctors_id_seq OWNED BY public.doctors.id;


--
-- Name: finance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    income_points integer,
    expense_points integer,
    date timestamp with time zone DEFAULT now(),
    notified boolean DEFAULT false NOT NULL
);


ALTER TABLE public.finance OWNER TO postgres;

--
-- Name: finance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_id_seq OWNER TO postgres;

--
-- Name: finance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_id_seq OWNED BY public.finance.id;


--
-- Name: points; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.points AS
 SELECT telegram_id,
    COALESCE(sum((income_points - expense_points)), (0)::bigint) AS total_points
   FROM public.finance f
  GROUP BY telegram_id;


ALTER VIEW public.points OWNER TO postgres;

--
-- Name: statistics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.statistics (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    message text,
    contact_phone bigint,
    date timestamp with time zone DEFAULT now()
);


ALTER TABLE public.statistics OWNER TO postgres;

--
-- Name: statistics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.statistics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.statistics_id_seq OWNER TO postgres;

--
-- Name: statistics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.statistics_id_seq OWNED BY public.statistics.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    telegram_id bigint NOT NULL,
    full_name text,
    phone_number bigint,
    age integer
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_telegram_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_telegram_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_telegram_id_seq OWNER TO postgres;

--
-- Name: users_telegram_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_telegram_id_seq OWNED BY public.users.telegram_id;


--
-- Name: appoints id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appoints ALTER COLUMN id SET DEFAULT nextval('public.appoints_id_seq'::regclass);


--
-- Name: doctor_slots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_slots ALTER COLUMN id SET DEFAULT nextval('public.doctor_slots_id_seq'::regclass);


--
-- Name: doctors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctors ALTER COLUMN id SET DEFAULT nextval('public.doctors_id_seq'::regclass);


--
-- Name: finance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance ALTER COLUMN id SET DEFAULT nextval('public.finance_id_seq'::regclass);


--
-- Name: statistics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.statistics ALTER COLUMN id SET DEFAULT nextval('public.statistics_id_seq'::regclass);


--
-- Name: users telegram_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN telegram_id SET DEFAULT nextval('public.users_telegram_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
8baf223f801a
\.


--
-- Data for Name: appoints; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.appoints (id, telegram_id, slot_id, service, accepted, notified) FROM stdin;
1	8084334783	11	Проверка                                          	t	t
2	1159187641	46	Болит левая пятка                                 	t	t
3	1159187641	57	Болит ухо                                         	f	f
\.


--
-- Data for Name: doctor_slots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.doctor_slots (id, doctor_id, "time", is_available) FROM stdin;
1	1	2025-12-05 08:00:00	t
2	1	2025-12-05 09:00:00	t
3	1	2025-12-05 10:00:00	t
4	1	2025-12-05 11:00:00	t
5	1	2025-12-05 12:00:00	t
6	1	2025-12-05 13:00:00	t
7	1	2025-12-05 14:00:00	t
8	1	2025-12-05 15:00:00	t
9	1	2025-12-05 16:00:00	t
10	1	2025-12-05 17:00:00	t
12	2	2025-12-05 09:00:00	t
13	2	2025-12-05 10:00:00	t
14	2	2025-12-05 11:00:00	t
15	2	2025-12-05 12:00:00	t
16	2	2025-12-05 13:00:00	t
17	2	2025-12-05 14:00:00	t
18	2	2025-12-05 15:00:00	t
19	2	2025-12-05 16:00:00	t
20	2	2025-12-05 17:00:00	t
21	3	2025-12-05 08:00:00	t
22	3	2025-12-05 09:00:00	t
23	3	2025-12-05 10:00:00	t
24	3	2025-12-05 11:00:00	t
25	3	2025-12-05 12:00:00	t
26	3	2025-12-05 13:00:00	t
27	3	2025-12-05 14:00:00	t
28	3	2025-12-05 15:00:00	t
29	3	2025-12-05 16:00:00	t
30	3	2025-12-05 17:00:00	t
31	4	2025-12-05 08:00:00	t
32	4	2025-12-05 09:00:00	t
33	4	2025-12-05 10:00:00	t
34	4	2025-12-05 11:00:00	t
35	4	2025-12-05 12:00:00	t
36	4	2025-12-05 13:00:00	t
37	4	2025-12-05 14:00:00	t
38	4	2025-12-05 15:00:00	t
39	4	2025-12-05 16:00:00	t
40	4	2025-12-05 17:00:00	t
11	2	2025-12-05 08:00:00	f
41	1	2025-12-13 08:00:00	t
42	1	2025-12-13 09:00:00	t
43	1	2025-12-13 10:00:00	t
44	1	2025-12-13 11:00:00	t
45	1	2025-12-13 12:00:00	t
47	1	2025-12-13 14:00:00	t
48	1	2025-12-13 15:00:00	t
49	1	2025-12-13 16:00:00	t
50	1	2025-12-13 17:00:00	t
51	2	2025-12-13 08:00:00	t
52	2	2025-12-13 09:00:00	t
53	2	2025-12-13 10:00:00	t
54	2	2025-12-13 11:00:00	t
55	2	2025-12-13 12:00:00	t
56	2	2025-12-13 13:00:00	t
58	2	2025-12-13 15:00:00	t
59	2	2025-12-13 16:00:00	t
60	2	2025-12-13 17:00:00	t
61	3	2025-12-13 08:00:00	t
62	3	2025-12-13 09:00:00	t
63	3	2025-12-13 10:00:00	t
64	3	2025-12-13 11:00:00	t
65	3	2025-12-13 12:00:00	t
66	3	2025-12-13 13:00:00	t
67	3	2025-12-13 14:00:00	t
68	3	2025-12-13 15:00:00	t
69	3	2025-12-13 16:00:00	t
70	3	2025-12-13 17:00:00	t
71	4	2025-12-13 08:00:00	t
72	4	2025-12-13 09:00:00	t
73	4	2025-12-13 10:00:00	t
74	4	2025-12-13 11:00:00	t
75	4	2025-12-13 12:00:00	t
76	4	2025-12-13 13:00:00	t
77	4	2025-12-13 14:00:00	t
78	4	2025-12-13 15:00:00	t
79	4	2025-12-13 16:00:00	t
80	4	2025-12-13 17:00:00	t
46	1	2025-12-13 13:00:00	f
57	2	2025-12-13 14:00:00	f
\.


--
-- Data for Name: doctors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.doctors (id, name, speciality) FROM stdin;
1	Пушкин Александр Сергеевич	Лор
2	Горшенев Михаил Юрьевич	Хирург
3	Цой Виктор Робертович	Окулист
4	Клинских Юрий Николаевич	Невролог
\.


--
-- Data for Name: finance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance (id, telegram_id, income_points, expense_points, date, notified) FROM stdin;
2	8084334783	100	0	2025-12-04 06:50:18.914407+03	t
3	8084334783	100	0	2025-12-04 10:53:09.38202+03	t
4	8084334783	0	50	2025-12-04 10:53:13.315145+03	t
5	5873099605	1	0	2025-12-04 11:55:42.709175+03	t
6	5873099605	1	0	2025-12-04 11:57:18.013112+03	t
7	5873099605	0	2	2025-12-04 11:57:26.312943+03	t
8	1159187641	500	0	2025-12-12 16:03:35.712016+03	t
9	1159187641	0	100	2025-12-12 16:04:08.444309+03	t
\.


--
-- Data for Name: statistics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.statistics (id, telegram_id, message, contact_phone, date) FROM stdin;
1	8084334783	Запрос на запись	79138523699	2025-12-03 19:22:55.278277+03
2	8084334783	Запрос на запись	79138523699	2025-12-03 19:48:23.572953+03
3	8084334783	Запрос на запись	79138523699	2025-12-04 06:39:26.128847+03
4	1159187641	Запрос на запись	79138288458	2025-12-12 15:55:28.250844+03
5	1159187641	Запрос обратного звонка	79138288458	2025-12-12 15:56:54.699597+03
6	1159187641	Запрос на запись	79138288458	2025-12-12 16:01:22.103681+03
7	1159187641	Запрос на запись	79138288458	2025-12-12 16:01:40.08639+03
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (telegram_id, full_name, phone_number, age) FROM stdin;
8084334783	Рощупкин Антон Борисович	79138523699	31
5873099605	Марков Антон Борисович	79234443055	31
1159187641	Рощупкин Михаил Эдуардович	79138288458	26
\.


--
-- Name: appoints_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.appoints_id_seq', 3, true);


--
-- Name: doctor_slots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.doctor_slots_id_seq', 80, true);


--
-- Name: doctors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.doctors_id_seq', 4, true);


--
-- Name: finance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_id_seq', 9, true);


--
-- Name: statistics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.statistics_id_seq', 7, true);


--
-- Name: users_telegram_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_telegram_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: appoints appoints_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appoints
    ADD CONSTRAINT appoints_pkey PRIMARY KEY (id);


--
-- Name: doctor_slots doctor_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_slots
    ADD CONSTRAINT doctor_slots_pkey PRIMARY KEY (id);


--
-- Name: doctors doctors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_pkey PRIMARY KEY (id);


--
-- Name: finance finance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance
    ADD CONSTRAINT finance_pkey PRIMARY KEY (id);


--
-- Name: statistics statistics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.statistics
    ADD CONSTRAINT statistics_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (telegram_id);


--
-- Name: ix_appoints_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_appoints_telegram_id ON public.appoints USING btree (telegram_id);


--
-- Name: ix_finance_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_finance_telegram_id ON public.finance USING btree (telegram_id);


--
-- Name: ix_statistics_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_statistics_telegram_id ON public.statistics USING btree (telegram_id);


--
-- Name: ix_users_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: appoints appoints_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appoints
    ADD CONSTRAINT appoints_slot_id_fkey FOREIGN KEY (slot_id) REFERENCES public.doctor_slots(id) ON DELETE CASCADE;


--
-- Name: appoints appoints_telegram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appoints
    ADD CONSTRAINT appoints_telegram_id_fkey FOREIGN KEY (telegram_id) REFERENCES public.users(telegram_id) ON DELETE CASCADE;


--
-- Name: doctor_slots doctor_slots_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_slots
    ADD CONSTRAINT doctor_slots_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id) ON DELETE CASCADE;


--
-- Name: finance finance_telegram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance
    ADD CONSTRAINT finance_telegram_id_fkey FOREIGN KEY (telegram_id) REFERENCES public.users(telegram_id) ON DELETE CASCADE;


--
-- Name: statistics statistics_telegram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.statistics
    ADD CONSTRAINT statistics_telegram_id_fkey FOREIGN KEY (telegram_id) REFERENCES public.users(telegram_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict FV2eqUEzoqRQPjO7Wh88vMPRn0quv3EXZQk139TdhP3Yx9SlucgydBApcusbsdO

