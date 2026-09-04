--
-- PostgreSQL database dump
--

\restrict cluhdbZrocVeugq8vPbXrBmEfeyVuhUC1ykIQH0A0DtHCNE126z45cWkjMpvTmY

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 17.7 (Debian 17.7-0+deb13u1)

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
-- Name: assignments; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.assignments (
    id integer NOT NULL,
    assessment character varying NOT NULL,
    subject_id integer NOT NULL,
    weighted_mark double precision,
    unweighted_mark double precision,
    mark_weight double precision,
    grade_type character varying NOT NULL,
    is_exam boolean NOT NULL
);


ALTER TABLE public.assignments OWNER TO "Michael";

--
-- Name: assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assignments_id_seq OWNER TO "Michael";

--
-- Name: assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.assignments_id_seq OWNED BY public.assignments.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    grading_scale_id integer NOT NULL,
    university_id integer
);


ALTER TABLE public.courses OWNER TO "Michael";

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO "Michael";

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: exam_settings; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.exam_settings (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    ps_exam boolean NOT NULL,
    ps_factor double precision NOT NULL
);


ALTER TABLE public.exam_settings OWNER TO "Michael";

--
-- Name: exam_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.exam_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_settings_id_seq OWNER TO "Michael";

--
-- Name: exam_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.exam_settings_id_seq OWNED BY public.exam_settings.id;


--
-- Name: examinations; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.examinations (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    exam_mark double precision NOT NULL,
    exam_weight double precision NOT NULL,
    exam_type character varying(32) DEFAULT 'main'::character varying
);


ALTER TABLE public.examinations OWNER TO "Michael";

--
-- Name: examinations_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.examinations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.examinations_id_seq OWNER TO "Michael";

--
-- Name: examinations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.examinations_id_seq OWNED BY public.examinations.id;


--
-- Name: grade_scales; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.grade_scales (
    id integer NOT NULL,
    scale_name character varying NOT NULL,
    grade character varying NOT NULL,
    label character varying NOT NULL,
    min_mark double precision NOT NULL,
    gpa_point double precision NOT NULL,
    band_type character varying NOT NULL
);


ALTER TABLE public.grade_scales OWNER TO "Michael";

--
-- Name: grade_scales_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.grade_scales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grade_scales_id_seq OWNER TO "Michael";

--
-- Name: grade_scales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.grade_scales_id_seq OWNED BY public.grade_scales.id;


--
-- Name: semesters; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.semesters (
    id integer NOT NULL,
    name character varying NOT NULL,
    year integer NOT NULL,
    course_id integer
);


ALTER TABLE public.semesters OWNER TO "Michael";

--
-- Name: semesters_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.semesters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.semesters_id_seq OWNER TO "Michael";

--
-- Name: semesters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.semesters_id_seq OWNED BY public.semesters.id;


--
-- Name: subject_prerequisite; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.subject_prerequisite (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    prerequisite_subject_id integer,
    is_corequisite boolean DEFAULT false NOT NULL,
    custom_text text
);


ALTER TABLE public.subject_prerequisite OWNER TO "Michael";

--
-- Name: subject_prerequisite_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.subject_prerequisite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subject_prerequisite_id_seq OWNER TO "Michael";

--
-- Name: subject_prerequisite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.subject_prerequisite_id_seq OWNED BY public.subject_prerequisite.id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.subjects (
    id integer NOT NULL,
    subject_code character varying NOT NULL,
    semester_id integer NOT NULL,
    subject_name character varying NOT NULL,
    total_mark double precision,
    credit_points integer NOT NULL,
    sync_subject boolean NOT NULL,
    has_exam boolean NOT NULL
);


ALTER TABLE public.subjects OWNER TO "Michael";

--
-- Name: subjects_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.subjects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_id_seq OWNER TO "Michael";

--
-- Name: subjects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.subjects_id_seq OWNED BY public.subjects.id;


--
-- Name: university; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.university (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.university OWNER TO "Michael";

--
-- Name: university_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.university_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.university_id_seq OWNER TO "Michael";

--
-- Name: university_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.university_id_seq OWNED BY public.university.id;


--
-- Name: user_courses; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.user_courses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    is_default boolean NOT NULL
);


ALTER TABLE public.user_courses OWNER TO "Michael";

--
-- Name: TABLE user_courses; Type: COMMENT; Schema: public; Owner: Michael
--

COMMENT ON TABLE public.user_courses IS 'Association table linking users to their courses';


--
-- Name: COLUMN user_courses.is_default; Type: COMMENT; Schema: public; Owner: Michael
--

COMMENT ON COLUMN public.user_courses.is_default IS 'Flag indicating if this is the user''s default/active course';


--
-- Name: user_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.user_courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_courses_id_seq OWNER TO "Michael";

--
-- Name: user_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.user_courses_id_seq OWNED BY public.user_courses.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: Michael
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL
);


ALTER TABLE public.users OWNER TO "Michael";

--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: Michael
--

COMMENT ON TABLE public.users IS 'Stores user accounts for multi-user support';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: Michael
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO "Michael";

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Michael
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: assignments id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.assignments ALTER COLUMN id SET DEFAULT nextval('public.assignments_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: exam_settings id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.exam_settings ALTER COLUMN id SET DEFAULT nextval('public.exam_settings_id_seq'::regclass);


--
-- Name: examinations id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.examinations ALTER COLUMN id SET DEFAULT nextval('public.examinations_id_seq'::regclass);


--
-- Name: grade_scales id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.grade_scales ALTER COLUMN id SET DEFAULT nextval('public.grade_scales_id_seq'::regclass);


--
-- Name: semesters id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.semesters ALTER COLUMN id SET DEFAULT nextval('public.semesters_id_seq'::regclass);


--
-- Name: subject_prerequisite id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subject_prerequisite ALTER COLUMN id SET DEFAULT nextval('public.subject_prerequisite_id_seq'::regclass);


--
-- Name: subjects id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subjects ALTER COLUMN id SET DEFAULT nextval('public.subjects_id_seq'::regclass);


--
-- Name: university id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.university ALTER COLUMN id SET DEFAULT nextval('public.university_id_seq'::regclass);


--
-- Name: user_courses id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.user_courses ALTER COLUMN id SET DEFAULT nextval('public.user_courses_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: assignments; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.assignments (id, assessment, subject_id, weighted_mark, unweighted_mark, mark_weight, grade_type, is_exam) FROM stdin;
1	Assignment 1	1	8	1	8	numeric	f
2	Assignment 2	1	8	1	8	numeric	f
3	Assignment 3	1	7.6	0.95	8	numeric	f
4	Assignment 4	1	7.505	0.9381	8	numeric	f
5	Assignment 5	1	7.75	0.9688	8	numeric	f
6	Assignment 1	2	6.975	0.6975	10	numeric	f
7	Assignment 2	2	7.508	0.7508	10	numeric	f
8	Assignment 3	2	9.25	0.925	10	numeric	f
9	Group Project - Part A	2	6	0.6	10	numeric	f
10	Group Project - Part B	2	7.742	0.7742	10	numeric	f
11	Assignment 1	3	7.6	0.76	10	numeric	f
12	Assignment 2	3	12.5	0.8333	15	numeric	f
13	Assignment 3	3	14	0.9333	15	numeric	f
14	Assignment 1	4	10.3	0.8583	12	numeric	f
15	Assignment 2	4	11.04	0.92	12	numeric	f
16	Assignment 3	4	12	0.75	16	numeric	f
18	Assignment 1	5	9.5	0.95	10	numeric	f
19	Assignment 2	5	9.5	0.95	10	numeric	f
20	Assignment 3	5	9.5	0.95	10	numeric	f
75	Lab Test 1	19	3.5	0.7	5	numeric	f
17	Mid-Term Quiz	5	13.2	0.66	20	numeric	f
21	Assignment 1	6	9.5	0.95	10	numeric	f
22	Assignment 2	6	10	1	10	numeric	f
23	Assignment 3	6	8.4	0.84	10	numeric	f
24	Assignment 4	6	8	0.8	10	numeric	f
25	Week 4 Quiz	7	4.59	0.918	5	numeric	f
26	Week 8 Quiz	7	4.23	0.846	5	numeric	f
27	Group Project - Part A	7	14.15	0.7075	20	numeric	f
28	Group Project - Part B	7	14.25	0.7125	20	numeric	f
29	Group Project - Part C	7	8	0.8	10	numeric	f
30	Assignment 1	8	10	1	10	numeric	f
31	Assignment 2	8	9.5	0.95	10	numeric	f
32	Assignment 3	8	9	0.9	10	numeric	f
33	Assignment 4	8	9	0.9	10	numeric	f
34	Lab Test	9	8	0.8	10	numeric	f
35	Group Project	9	37.5	0.9375	40	numeric	f
36	Quiz 1	10	8	0.8	10	numeric	f
37	Quiz 2	10	9.25	0.925	10	numeric	f
38	Quiz 3	10	10	1	10	numeric	f
39	Assignment	10	17.4	0.87	20	numeric	f
40	Tutorial Preparation	11	8.75	0.875	10	numeric	f
41	Quiz 1	11	2	0.4	5	numeric	f
42	Quiz 2	11	2.5	0.5	5	numeric	f
43	Discrete Exam	11	24	0.8	30	numeric	t
44	Assessment 1	11	4.11	0.822	5	numeric	f
45	Assessment 2	11	4.5	0.9	5	numeric	f
46	Assignment 1	12	15	1	15	numeric	f
47	Assignment 2	12	14.5	0.9667	15	numeric	f
48	Assignment 3	12	15	1	15	numeric	f
49	Individual Assignment	13	15	1	15	numeric	f
51	Week 10 Assessed Lab	13	2.9	0.58	5	numeric	f
50	Week 6 Assessed Lab	13	3.75	0.75	5	numeric	f
52	Group Project	13	15	1	15	numeric	f
53	Assignment 1	14	8	1	8	numeric	f
54	Assignment 2	14	14	1	14	numeric	f
55	Assignment 3	14	7.04	0.88	8	numeric	f
56	Lab Exercises	14	9.4	0.94	10	numeric	f
57	Assessment 1	15	8.6	0.86	10	numeric	f
58	Assessment 2	15	11.4	0.95	12	numeric	f
59	Assessment 3	15	10	1	10	numeric	f
60	Initial Project Description	16	\N	\N	\N	S	f
61	Design Progress	16	10.8	0.72	15	numeric	f
62	Project Requirements and Interface Presentation	16	7.5	0.75	10	numeric	f
63	Prototype Presentation	16	12.15	0.81	15	numeric	f
64	Final Product & Documentation	16	\N	0	45	numeric	t
65	Marketing and Technical Presentation	16	12.15	0.81	15	numeric	f
66	Quiz 1	17	4.5	0.9	5	numeric	f
67	Quiz 2	17	9.5	0.95	10	numeric	f
68	Assignment	17	11.3	0.7533	15	numeric	f
69	Group Project	17	18.6	0.744	25	numeric	f
70	Quiz 1	18	4	0.8	5	numeric	f
71	Quiz 2	18	3	0.6	5	numeric	f
72	Assignment	18	14.5	0.9667	15	numeric	f
73	Project Presentation	18	4.5	0.72	6.25	numeric	f
74	Project Report	18	13.5	0.72	18.75	numeric	f
76	Lab Test 2	19	5.5	0.55	10	numeric	f
77	Assignment 1	19	14	0.9333	15	numeric	f
78	Assignment 2	19	13	0.65	20	numeric	f
79	Lab Assessment 1	20	1.5	0.25	6	numeric	f
80	Lab Assessment 2	20	5.08	0.7257	7	numeric	f
81	Lab Assessment 3	20	7	1	7	numeric	f
82	Assignment	20	30	1	30	numeric	f
83	Assignment 1	21	9.8	0.98	10	numeric	f
84	Assignment 2	21	16.4	0.82	20	numeric	f
85	Assignment 3	21	19.5	0.975	20	numeric	f
86	Problem Solving 1	23	0	0	20	numeric	f
87	Problem Solving 2	23	0	0	30	numeric	f
88	Report	23	0	0	50	numeric	f
89	Quiz 1	22	0	0	20	numeric	f
91	Problem Solving	22	0	0	30	numeric	f
90	Quiz 2	22	0	0	50	numeric	f
92	Project Report 1	24	0	0	30	numeric	f
93	Project Report 2	24	0	0	30	numeric	f
94	Project Report 3	24	0	0	40	numeric	f
95	Problem Solving 1	26	0	0	30	numeric	f
96	Problem Solving 2	26	0	0	20	numeric	f
97	Problem Solving 3	26	0	0	50	numeric	f
98	Project Report - Part 1	25	0	0	50	numeric	f
99	Project Report - Part 2	25	0	0	50	numeric	f
100	Workbook 1	37	0	0	20	numeric	f
101	Workbook 2	37	0	0	30	numeric	f
102	Report	37	0	0	50	numeric	f
103	Quiz	36	0	0	10	numeric	f
104	Technical Artefact 1	36	0	0	20	numeric	f
105	Technical Artefact 2	36	0	0	20	numeric	f
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.courses (id, name, code, grading_scale_id, university_id) FROM stdin;
2	Master of Data Science	MADS	8	2
1	Bachelor of Computer Science	766	6	1
\.


--
-- Data for Name: exam_settings; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.exam_settings (id, subject_id, ps_exam, ps_factor) FROM stdin;
1	1	f	40
2	2	f	40
3	3	f	40
4	4	f	40
5	5	f	40
6	6	f	40
7	7	f	40
8	8	f	40
9	9	f	40
10	10	f	40
11	11	f	40
12	12	f	40
13	13	f	40
14	14	f	40
15	15	f	40
16	16	f	40
17	17	f	40
18	18	t	40
19	19	t	40
20	20	f	40
21	21	f	40
\.


--
-- Data for Name: examinations; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.examinations (id, subject_id, exam_mark, exam_weight, exam_type) FROM stdin;
1	1	56.145	60	main
2	2	42.525	50	main
3	3	38.9	60	main
4	4	45.66	60	main
6	5	38.3	50	main
7	6	57.1	60	main
8	7	23.78	40	main
9	8	41.50000000000001	60	main
10	9	22.5	50	main
11	10	48.35	50	main
12	11	24	30	assignment
21	11	21.14	40	main
22	12	21.5	55	main
23	13	38.35	60	main
24	14	29.56	60	main
25	15	38	68	main
27	16	36.4	45	main
28	17	18.099999999999998	45	main
29	18	20	50	main
30	19	20	50	main
31	20	38.42	50	main
32	21	39.3	50	main
\.


--
-- Data for Name: grade_scales; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.grade_scales (id, scale_name, grade, label, min_mark, gpa_point, band_type) FROM stdin;
1	UOW 4-Point	HD	High Distinction	85	4	both
2	UOW 4-Point	D	Distinction	75	3.7	both
3	UOW 4-Point	C	Credit	65	3.3	both
4	UOW 4-Point	P	Pass	50	2	both
5	UOW 4-Point	PS	Pass Supplmentary	50	2	both
6	Standard	HD	High Distinction	85	4	both
7	Standard	D	Distinction	75	3.7	both
8	Standard	C	Credit	65	3.3	both
10	Standard	PS	Pass Supplementary	50	2	both
11	Standard	F	Fail	0	0	both
9	Standard	P	Pass	50	2	both
\.


--
-- Data for Name: semesters; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.semesters (id, name, year, course_id) FROM stdin;
1	Autumn	2023	1
2	Spring	2023	1
3	Autumn	2024	1
4	Spring	2024	1
5	Annual	2025	1
6	Autumn	2025	1
7	Spring	2025	1
8	Trimester 1	2026	2
9	Trimester 2	2026	2
10	Trimester 3	2026	2
11	Trimester 1	2027	2
12	Trimester 2	2027	2
13	Trimester 3	2027	2
14	Trimester 1	2028	2
15	Trimester 2	2028	2
16	Trimester 3	2028	2
17	Trimester 1	2029	2
18	Trimester 2	2029	2
19	Trimester 3	2029	2
\.


--
-- Data for Name: subject_prerequisite; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.subject_prerequisite (id, subject_id, prerequisite_subject_id, is_corequisite, custom_text) FROM stdin;
1	5	1	f	\N
2	8	4	f	\N
3	9	2	f	\N
4	12	1	f	\N
5	12	3	f	\N
6	13	1	f	\N
7	13	\N	f	18cp @ 100 level
8	10	\N	f	CSIT127
9	10	\N	f	12cp @ 100 level CSIT
10	14	5	f	\N
11	15	5	f	\N
12	15	4	f	\N
13	15	\N	f	CSIT127
14	16	7	t	\N
15	16	9	f	\N
16	16	\N	f	18cp @ 200 level CSCI/CSIT/ISIT
17	17	12	f	\N
18	18	1	f	\N
19	18	\N	f	12cp @ 200 level
20	19	5	f	\N
21	19	\N	f	CSIT127
22	19	\N	f	18cp @ 200 level
23	20	1	f	\N
24	20	\N	f	18cp @ 200 level
25	21	4	f	\N
26	21	\N	f	18cp @ 200 level
29	25	\N	t	CSC5020
32	24	22	f	\N
33	23	22	t	\N
35	28	22	f	\N
36	23	\N	t	CSC5020
38	24	\N	f	CSC5020
39	25	22	t	\N
40	35	\N	f	CISS5310
41	30	24	f	\N
42	26	22	f	\N
45	31	24	t	\N
47	26	36	f	\N
48	33	36	f	\N
49	33	22	f	\N
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.subjects (id, subject_code, semester_id, subject_name, total_mark, credit_points, sync_subject, has_exam) FROM stdin;
1	CSIT110	1	Fundamental Programming with Python	95	6	f	t
2	CSIT114	1	System Analysis	80	6	f	t
3	CSIT123	1	Computing and Cyber Security Fundamentals	73	6	f	t
4	CSIT115	2	Data Management and Security	79	6	f	t
5	CSIT121	2	Object Oriented Design and Programming	80	6	f	t
6	CSIT128	2	Introduction to Web Technology	93	6	f	t
7	CSIT226	2	Human Computer Interaction	69	6	f	t
8	CSCI235	3	Database Systems	79	6	f	t
9	CSIT214	3	IT Project Management	68	6	f	t
10	CSIT302	3	Cybersecurity	93	6	f	t
11	MATH255	3	Mathematics for Computing	67	6	f	t
12	CSCI203	4	Algorithms and Data Structures	66	6	f	t
13	CSCI218	4	Foundations of Artificial Intelligence	75	6	f	t
14	CSCI251	4	Advanced Programming	68	6	f	t
15	CSCI262	4	System Security	68	6	f	t
17	CSCI316	6	Big Data Mining Techniques & Implementation	62	6	f	t
18	CSCI323	6	Modern Artificial Intelligence	50	6	f	t
16	CSIT321	5	Capstone Project	79	6	t	t
19	CSIT375	6	Artificial Intelligence for Cybersecurity	50	6	f	t
20	CSCI369	7	Ethical Hacking	82	6	f	t
21	ISIT312	7	Big Data Management	85	6	f	t
22	STA6200	8	Statistics for Quantitative Researchers	0	1	f	f
24	CSC6003	9	Machine Learning	0	1	f	f
25	CSC6002	9	Big Data 	0	1	f	f
28	STA6100	12	Multivariate Analysis for High-Dimensional Data	0	1	f	f
31	CSC6203	15	Intelligent Multimedia (Computer Vision, Audio) Analysis	0	1	f	f
30	CSC6201	14	Deep Learning	0	1	f	f
32	Elective 3	16	Elective 3	0	1	f	f
34	CSC6370	18	Network Security Management	0	1	f	f
35	CSC6200	19	Advanced ICT Professional Project	0	1	f	f
23	CSC6004	11	Data Mining	0	1	f	f
33	CSC6202	17	Natural Language Processing: Techniques and Applications	0	1	f	f
26	CSC6204	13	Information Retrieval and Knowledge Management	0	1	f	f
29	CSC5090	10	Systems Administration	0	1	f	f
36	CSC5020	8	Foundations of Programming	0	1	f	t
37	CIS5310	10	IS/ICT Project Management	0	1	f	f
\.


--
-- Data for Name: university; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.university (id, name) FROM stdin;
1	University of Wollongong
2	University of Southern Queensland
\.


--
-- Data for Name: user_courses; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.user_courses (id, user_id, course_id, is_default) FROM stdin;
1	1	1	t
2	1	2	f
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: Michael
--

COPY public.users (id, username, email, password_hash) FROM stdin;
1	Michael	mcmillanbmac@gmail.com	$2b$12$fTEhwofm3DeB7HQuLzTtye82cbtlvSDp68XAOvcJXKjztEgSCokoa
2	Test	test@email.com	$2b$12$wVh4m2iqZaqSsi37PQzqquMvWHUkjmRhdYpNl4/oqviglPXrtgmaq
\.


--
-- Name: assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.assignments_id_seq', 105, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.courses_id_seq', 2, true);


--
-- Name: exam_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.exam_settings_id_seq', 21, true);


--
-- Name: examinations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.examinations_id_seq', 32, true);


--
-- Name: grade_scales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.grade_scales_id_seq', 11, true);


--
-- Name: semesters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.semesters_id_seq', 19, true);


--
-- Name: subject_prerequisite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.subject_prerequisite_id_seq', 49, true);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.subjects_id_seq', 37, true);


--
-- Name: university_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.university_id_seq', 2, true);


--
-- Name: user_courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.user_courses_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Michael
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: assignments assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: exam_settings exam_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.exam_settings
    ADD CONSTRAINT exam_settings_pkey PRIMARY KEY (id);


--
-- Name: examinations examinations_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.examinations
    ADD CONSTRAINT examinations_pkey PRIMARY KEY (id);


--
-- Name: grade_scales grade_scales_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.grade_scales
    ADD CONSTRAINT grade_scales_pkey PRIMARY KEY (id);


--
-- Name: semesters semesters_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_pkey PRIMARY KEY (id);


--
-- Name: subject_prerequisite subject_prerequisite_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subject_prerequisite
    ADD CONSTRAINT subject_prerequisite_pkey PRIMARY KEY (id);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: university university_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.university
    ADD CONSTRAINT university_pkey PRIMARY KEY (id);


--
-- Name: assignments uq_assignment_subject; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT uq_assignment_subject UNIQUE (assessment, subject_id);


--
-- Name: courses uq_course_code; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT uq_course_code UNIQUE (code);


--
-- Name: examinations uq_examinations_subject_id_exam_type; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.examinations
    ADD CONSTRAINT uq_examinations_subject_id_exam_type UNIQUE (subject_id, exam_type);


--
-- Name: grade_scales uq_scale_grade_type; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.grade_scales
    ADD CONSTRAINT uq_scale_grade_type UNIQUE (scale_name, grade, band_type);


--
-- Name: semesters uq_semester_course_name_year; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT uq_semester_course_name_year UNIQUE (course_id, name, year);


--
-- Name: subjects uq_subject_code_semester; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT uq_subject_code_semester UNIQUE (subject_code, semester_id);


--
-- Name: user_courses uq_user_course; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.user_courses
    ADD CONSTRAINT uq_user_course UNIQUE (user_id, course_id);


--
-- Name: user_courses user_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.user_courses
    ADD CONSTRAINT user_courses_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_user_courses_course_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX idx_user_courses_course_id ON public.user_courses USING btree (course_id);


--
-- Name: idx_user_courses_is_default; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX idx_user_courses_is_default ON public.user_courses USING btree (user_id, is_default);


--
-- Name: idx_user_courses_user_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX idx_user_courses_user_id ON public.user_courses USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: ix_assignments_assessment; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_assignments_assessment ON public.assignments USING btree (assessment);


--
-- Name: ix_assignments_subject_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_assignments_subject_id ON public.assignments USING btree (subject_id);


--
-- Name: ix_courses_code; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_courses_code ON public.courses USING btree (code);


--
-- Name: ix_courses_name; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_courses_name ON public.courses USING btree (name);


--
-- Name: ix_exam_settings_subject_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE UNIQUE INDEX ix_exam_settings_subject_id ON public.exam_settings USING btree (subject_id);


--
-- Name: ix_grade_scales_band_type; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_grade_scales_band_type ON public.grade_scales USING btree (band_type);


--
-- Name: ix_grade_scales_scale_name; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_grade_scales_scale_name ON public.grade_scales USING btree (scale_name);


--
-- Name: ix_semesters_name; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_semesters_name ON public.semesters USING btree (name);


--
-- Name: ix_semesters_year; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_semesters_year ON public.semesters USING btree (year);


--
-- Name: ix_subject_prerequisite_prerequisite_subject_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_subject_prerequisite_prerequisite_subject_id ON public.subject_prerequisite USING btree (prerequisite_subject_id);


--
-- Name: ix_subject_prerequisite_subject_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_subject_prerequisite_subject_id ON public.subject_prerequisite USING btree (subject_id);


--
-- Name: ix_subjects_semester_id; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_subjects_semester_id ON public.subjects USING btree (semester_id);


--
-- Name: ix_subjects_subject_code; Type: INDEX; Schema: public; Owner: Michael
--

CREATE INDEX ix_subjects_subject_code ON public.subjects USING btree (subject_code);


--
-- Name: ix_university_name; Type: INDEX; Schema: public; Owner: Michael
--

CREATE UNIQUE INDEX ix_university_name ON public.university USING btree (name);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: Michael
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: Michael
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: assignments assignments_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: courses courses_grading_scale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_grading_scale_id_fkey FOREIGN KEY (grading_scale_id) REFERENCES public.grade_scales(id);


--
-- Name: courses courses_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.university(id);


--
-- Name: exam_settings exam_settings_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.exam_settings
    ADD CONSTRAINT exam_settings_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: examinations examinations_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.examinations
    ADD CONSTRAINT examinations_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: semesters semesters_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: subject_prerequisite subject_prerequisite_prerequisite_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subject_prerequisite
    ADD CONSTRAINT subject_prerequisite_prerequisite_subject_id_fkey FOREIGN KEY (prerequisite_subject_id) REFERENCES public.subjects(id);


--
-- Name: subject_prerequisite subject_prerequisite_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subject_prerequisite
    ADD CONSTRAINT subject_prerequisite_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: subjects subjects_semester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_semester_id_fkey FOREIGN KEY (semester_id) REFERENCES public.semesters(id);


--
-- Name: user_courses user_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.user_courses
    ADD CONSTRAINT user_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: user_courses user_courses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Michael
--

ALTER TABLE ONLY public.user_courses
    ADD CONSTRAINT user_courses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict cluhdbZrocVeugq8vPbXrBmEfeyVuhUC1ykIQH0A0DtHCNE126z45cWkjMpvTmY

