from svg import D, figure
from inject import put

# ============================ OBSERVABILITÉ ============================
M = 'observabilite'

# --- 03 : l'architecture de Prometheus --------------------------------
d = D(680, 330)
d.text(14, 40, 'cibles', 'zl', anchor='start')
targets = [('app', 'bibliothèque client'), ('node_exporter', 'la machine'), ('mysqld_exporter', 'une base'), ('blackbox_exporter', 'sondes HTTP, ICMP'), ('pushgateway', 'jobs batch')]
for i, (t, s) in enumerate(targets):
    y = 52 + i * 54
    d.box(14, y, 176, 44, t, s, d=i)
    d.arrow([(190, y + 22), (222, y + 22), (222, 185), (246, 185)], color='c')
d.box(230, 14, 250, 36, 'découverte de services', tk='s', k='ghost', d=0)
d.arrow([(355, 50), (355, 128)], k='dash')
d.text(365, 96, 'liste des cibles', 's', anchor='start')
d.box(248, 130, 210, 112, 'Prometheus', 'lit /metrics toutes les 15-30 s\nTSDB locale\nrègles : recording, alerting', k='c', d=5)
outs = [(96, 'Alertmanager', 'Slack, PagerDuty…', 'a'), (166, 'Grafana', 'requêtes PromQL', ''), (236, 'long terme', 'Thanos, Mimir,\nVictoriaMetrics', '')]
for i, (y, t, s, k) in enumerate(outs):
    d.box(520, y, 146, 52, t, s, k=k, d=6 + i)
    d.arrow([(458, 185), (490, 185), (490, y + 26), (518, y + 26)], color='a' if k else 'c', start=(t == 'Grafana'))
d.text(593, 306, 'via remote_write', 's')
put(f'{M}/03-prometheus.md', 'archi', figure(d, "L'architecture de Prometheus", "Prometheus va chercher les métriques (pull) ; il garde peu d'historique et délègue les notifications à Alertmanager."), fence='découverte de services (Kubernetes, Consul')

# --- 04 : la vie d'une alerte -----------------------------------------
d = D(680, 210)
st = [('inactive', 'condition fausse', ''), ('pending', 'vraie depuis\nmoins que for', 'c'), ('firing', 'vraie pendant\nfor (10 min)', 'a'), ('Alertmanager', 'regroupe (30 s),\nchoisit la route', 'c'), ('receiver', 'Slack, PagerDuty…', 'ok')]
for i, (t, s, k) in enumerate(st):
    x = 14 + i * 134
    d.box(x, 30, 118, 64, t, s, k=k, d=i)
    if i:
        d.arrow([(x - 16, 62), (x - 2, 62)], color='c')
d.arrow('M207 94 C 207 150, 73 150, 73 96', k='dash')
d.text(140, 162, 'redevient fausse avant 10 min :', 's')
d.text(140, 176, 'personne n\'est prévenu', 's')
d.text(475, 126, 'silences et inhibitions', 's')
d.text(475, 140, "agissent ici", 's')
d.arrow([(475, 112), (475, 96)])
put(f'{M}/04-promql-et-alertes.md', 'vie', figure(d, "La vie d'une alerte", "La durée for évite de réveiller quelqu'un pour un pic de quelques secondes."), before='Les **silences** et **inhibitions**')

# --- 06 : Grafana au centre -------------------------------------------
d = D(680, 250)
d.box(190, 14, 300, 64, 'Grafana', 'tableaux de bord, Explore,\nalertes, annotations', k='c', d=0)
d.arrow([(340, 78), (340, 118)], color='c', end=False)
d.arrow([(89, 118), (593, 118)], color='c', end=False)
srcs = [('Prometheus · Mimir', 'métriques', 'PromQL'), ('Loki', 'logs', 'LogQL'), ('Tempo', 'traces', 'TraceQL'), ('Elasticsearch, SQL…', "et bien d'autres", 'SQL…')]
for i, (t, s, q) in enumerate(srcs):
    x = 14 + i * 168
    d.box(x, 170, 150, 56, t, s, d=1 + i)
    d.arrow([(x + 75, 118), (x + 75, 168)], color='c')
    d.text(x + 83, 150, q, 's', anchor='start')
put(f'{M}/06-grafana.md', 'centre', figure(d, 'Grafana au centre', 'Grafana ne stocke rien : il interroge chaque source dans son propre langage.'), fence='┌───────── Grafana ─────────┐')

# --- 07 : la chaîne d'un log ------------------------------------------
d = D(680, 212)
steps = [('application', 'stdout, fichier,\njournald', '', ''), ('agent', 'lire, parser,\nenrichir, masquer', 'c', 'Fluent Bit\nVector · Alloy\nFilebeat\nOTel Collector'),
         ('tampon', 'optionnel', 'ghost', 'Kafka\nLogstash'), ('stockage', 'indexé', 'c', 'Loki\nElasticsearch\nDatadog · Splunk'), ('recherche', 'tableaux de bord', '', 'Grafana\nKibana\nDatadog')]
for i, (t, s, k, tools) in enumerate(steps):
    x = 14 + i * 133
    d.box(x, 30, 120, 70, t, s, k=k, d=i)
    if i:
        d.arrow([(x - 12, 65), (x - 1, 65)], color='c')
    if tools:
        d.text(x + 60, 136, tools, 's', d=i)
d.text(14, 124, 'outils', 'zl', anchor='start')
put(f'{M}/07-collecter-les-logs.md', 'chaine', figure(d, "La chaîne d'un log", "Masquer les données sensibles se fait dans l'agent, avant que le log ne soit stocké."), fence='application ──► stdout / fichier / journald')

# --- 08 : Loki, écrire puis chercher ----------------------------------
d = D(680, 300)
d.text(14, 16, 'écriture', 'zl', anchor='start')
d.box(14, 24, 140, 50, 'logs entrants', d=0)
d.box(200, 24, 170, 50, 'distributor', 'vérifie, répartit', d=1)
d.box(416, 24, 250, 50, 'ingesters', 'regroupent par flux, compressent', k='c', d=2)
d.arrow([(154, 49), (198, 49)], color='c'); d.arrow([(370, 49), (414, 49)], color='c')
d.box(220, 120, 260, 52, 'stockage objet', 'chunks + petit index (étiquettes)', k='c', d=3)
d.arrow([(540, 74), (540, 98), (420, 98), (420, 118)], color='c')
d.text(14, 212, 'lecture', 'zl', anchor='start')
d.box(14, 222, 120, 50, 'Grafana', 'LogQL', d=4)
d.box(170, 222, 170, 50, 'query-frontend', 'découpe la période', d=5)
d.box(386, 206, 280, 82, 'queriers', '1. choisir les flux par étiquettes\n2. lire leurs chunks\n3. filtrer le contenu en parallèle', k='a', d=6)
d.arrow([(134, 247), (168, 247)], color='a'); d.arrow([(340, 247), (384, 247)], color='a')
d.arrow([(450, 206), (450, 190), (300, 190), (300, 174)], color='a')
put(f'{M}/08-loki.md', 'flux', figure(d, 'Loki : indexer peu, lire vite', "Seules les étiquettes sont indexées ; le contenu est filtré à la lecture, d'où l'importance de bien choisir les étiquettes."), fence='logs entrants ──► distributor')

# --- 11 : l'arbre d'une trace -----------------------------------------
d = D(680, 280)
d.text(14, 24, 'trace 4bf92f35… · POST /commandes · 1 840 ms au total', 'ct', anchor='start')
spans = [('api-gateway', 0, 40, 0, ''), ('commandes', 40, 1790, 0, 'c'), ('SELECT clients', 60, 25, 1, ''), ('POST paiement', 100, 1600, 1, 'a'),
         ('appel Stripe', 110, 1580, 2, 'a'), ('publish RabbitMQ', 1720, 12, 1, ''), ('notifications (async)', 1780, 60, 0, '')]
X0, W = 230, 380
for i, (n, s, dur, ind, k) in enumerate(spans):
    y = 50 + i * 30
    d.text(14 + ind * 16, y + 13, n, 's', anchor='start', d=i)
    x = X0 + s / 1840 * W
    w = max(dur / 1840 * W, 3)
    d.box(x, y, w, 18, '', k=k, rx=3, d=i)
    d.text(676, y + 13, f'{dur:,} ms'.replace(',', ' '), 'at' if k == 'a' else 's', anchor='end', d=i)
d.line(X0, 44, X0, 262, k='grid')
d.text(X0, 272, '0', 's'); d.text(X0 + W, 272, '1 840 ms', 's')
put(f'{M}/11-traces-et-opentelemetry.md', 'arbre', figure(d, "L'arbre d'une trace", "La trace montre d'un coup d'œil où part le temps : ici, l'appel au prestataire de paiement."), fence='trace 4bf92f35…')

# ================================= IA =================================
M = 'ia'

# --- 02 : le contexte renvoyé à chaque requête ------------------------
d = D(680, 290)
d.zone(14, 14, 420, 262, 'requête n°3 envoyée au modèle', k='c')
rows = [('prompt système (rôle, règles)', 'c'), ('message 1 + réponse 1', ''), ('message 2 + réponse 2', ''), ("fichiers, résultats d'outils", ''), ('message 3', 'c')]
for i, (t, k) in enumerate(rows):
    d.box(30, 44 + i * 44, 388, 36, t, k=k, tk='s', d=i)
d.box(480, 80, 180, 50, 'le modèle', 'ne se souvient de rien', k='a', d=5)
d.arrow([(434, 145), (456, 145), (456, 105), (478, 105)], color='a')
d.box(480, 190, 180, 56, 'réponse 3', 'comptée aussi\ndans la fenêtre', d=6)
d.arrow([(570, 130), (570, 188)], color='a')
d.text(456, 32, 'tout est renvoyé à chaque fois', 's', anchor='start')
put(f'{M}/02-comment-pense-un-llm.md', 'contexte', figure(d, 'Un modèle sans mémoire', "Chaque requête renvoie toute la conversation : plus elle est longue, plus elle coûte et plus le modèle se disperse."), fence='requête n°3 envoyée au modèle')

# --- 05 : la boucle d'un agent ----------------------------------------
d = D(680, 300)
d.box(60, 14, 480, 40, '« pourquoi le déploiement api est en erreur ? »', k='ghost', tk='s', d=0)
d.box(60, 100, 200, 60, 'le modèle', 'choisit une action', k='c', d=1)
d.box(420, 100, 246, 60, 'un outil', 'kubectl get pods, kubectl logs,\nlire values.yaml…', d=2)
d.arrow([(160, 54), (160, 98)], color='c')
d.arrow([(260, 118), (418, 118)], color='c', label='action', dy=-8)
d.arrow([(418, 144), (262, 144)], color='a', label='résultat ajouté au contexte', dy=18)
d.text(340, 200, '↻ autant de tours que nécessaire', 'zl')
d.box(60, 230, 480, 54, 'réponse', "DB_HOST pointe vers l'ancien service : voici le correctif proposé", k='ok', d=3)
d.arrow([(160, 160), (160, 228)], color='ok')
put(f'{M}/05-agents-et-outils.md', 'boucle', figure(d, "La boucle d'un agent", "Un agent n'est qu'un modèle qui appelle des outils en boucle ; ses droits sont ceux des outils qu'on lui donne."), fence='objectif : « pourquoi le déploiement api')

# --- 06 : le RAG ------------------------------------------------------
d = D(680, 330)
d.zone(14, 14, 652, 98, 'ingestion · régulière')
ing = [('documents', 'runbooks, wiki,\npostmortems'), ('chunks', 'découpage'), ('embeddings', 'texte → vecteurs'), ('base vectorielle', '+ titre, date, droits')]
for i, (t, s) in enumerate(ing):
    x = 30 + i * 160
    d.box(x, 40, 140, 56, t, s, k='c' if i == 3 else '', d=i)
    if i:
        d.arrow([(x - 20, 68), (x - 2, 68)], color='c')
d.zone(14, 132, 652, 186, 'requête', k='c')
d.box(30, 162, 150, 60, 'question', '« comment purger\nla file RabbitMQ ? »', d=4)
d.box(210, 162, 170, 60, 'recherche', 'passages proches\nfiltrés par droits', k='c', d=5)
d.box(410, 162, 240, 60, 'prompt', 'consigne + 5 passages\nsourcés + question', d=6)
d.arrow([(180, 192), (208, 192)], color='c'); d.arrow([(380, 192), (408, 192)], color='c')
d.arrow([(580, 96), (580, 122), (295, 122), (295, 160)], color='c')
d.box(210, 248, 440, 54, 'réponse avec ses sources', "« D'après le runbook rabbitmq-ops (mars) : … »", k='ok', d=7)
d.arrow([(530, 222), (530, 246)], color='ok')
put(f'{M}/06-rag-et-connaissance-d-equipe.md', 'rag', figure(d, 'Le RAG : chercher puis répondre', "Le modèle ne répond qu'à partir des passages retrouvés, et cite sa source : on peut vérifier."), fence='INGESTION (régulière)')
print('ok')
