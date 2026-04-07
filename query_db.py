import psycopg2
conn = psycopg2.connect(host="192.168.8.8", user="Michael", password="Mickyb26*", database="marks-manager-db")
cur = conn.cursor()
cur.execute("SELECT s.subject_name, a.assessment, a.weighted_mark, a.unweighted_mark, a.mark_weight FROM assignments a JOIN subjects s ON a.subject_id = s.id WHERE s.subject_name LIKE '%Statistics%';")
for row in cur.fetchall():
    print(row)
