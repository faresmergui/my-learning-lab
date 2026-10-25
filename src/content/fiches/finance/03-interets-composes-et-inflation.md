---
title: Intérêts composés, inflation et rendement réel
chapter: 3
order: 1
duration: 14
level: Fondations
tags:
- intérêts composés
- inflation
- rendement réel
- règle de 72
- temps
cards:
- q: Que sont les intérêts composés ?
  a: 'Des intérêts qui **rapportent à leur tour des intérêts**, parce qu''ils sont réinvestis. La croissance devient exponentielle : 1 000 € à 7 % par an deviennent environ 1 970 € en 10 ans, mais environ 7 600 € en 30 ans.'
- q: Qu'est-ce que la règle de 72 ?
  a: 'Un calcul rapide : **72 divisé par le taux annuel** donne le nombre d''années pour **doubler** un capital. À 6 %, environ 12 ans ; à 3 %, environ 24 ans ; à 1,7 %, environ 42 ans.'
- q: Qu'est-ce que l'inflation ?
  a: 'La **hausse générale des prix**. Elle réduit le pouvoir d''achat de l''argent : avec 2 % d''inflation par an, 1 000 € n''achètent plus que l''équivalent d''environ 500 € d''aujourd''hui au bout de 35 ans.'
- q: Qu'est-ce que le rendement réel ?
  a: 'Le rendement **après inflation**, à peu près : rendement nominal − inflation. Un placement à 3 % avec 2 % d''inflation rapporte environ 1 % réel. C''est lui qui mesure l''enrichissement véritable.'
- q: Pourquoi commencer tôt compte-t-il autant ?
  a: 'Parce que le temps est l''ingrédient principal des intérêts composés : les dernières années rapportent le plus. 200 € par mois pendant 30 ans à 7 % donnent environ 244 000 € (pour 72 000 € versés) ; pendant 20 ans, environ 104 000 €.'
- q: Quelle est la différence entre rendement nominal et rendement net ?
  a: 'Le **nominal** est le rendement affiché. Le **net** retire les **frais** et les **impôts**. Le **réel net** retire en plus l''inflation : c''est le seul qui compte pour comparer deux placements.'
- q: Pourquoi un rendement moyen ne suffit-il pas à décrire un placement ?
  a: 'Parce que les rendements **varient** d''une année à l''autre. Une baisse de 50 % demande une hausse de **100 %** pour revenir au point de départ : la volatilité réduit le rendement effectivement obtenu.'
quiz:
- q: Avec la règle de 72, combien de temps faut-il pour doubler un capital placé à 8 % par an ?
  options:
  - 8 ans
  - 9 ans
  - 12 ans
  - 72 ans
  answer: 1
  explain: 72 / 8 = 9 ans.
- q: 'Ton placement rapporte 2,5 % net de frais et d''impôts, l''inflation est à 2 %. Ton rendement réel est d''environ :'
  options:
  - 4,5 %
  - 0,5 %
  - 2,5 %
  - −2 %
  answer: 1
  explain: Rendement réel ≈ 2,5 − 2 = 0,5 %. Ton pouvoir d'achat progresse à peine.
- q: Alex investit 200 € par mois de 25 à 35 ans puis arrête. Sam commence à 35 ans et investit 200 € par mois jusqu'à 55 ans. À 7 % par an, qui a le plus à 55 ans ?
  options:
  - Sam, qui a versé deux fois plus
  - Alex, grâce aux 20 ans de capitalisation supplémentaire (environ 140 000 € contre 104 000 €)
  - Ils ont autant
  - Impossible à dire
  answer: 1
  explain: Alex verse 24 000 €, Sam 48 000 €, mais l'argent d'Alex a eu beaucoup plus de temps pour se composer.
- q: Un placement perd 50 % une année puis gagne 50 % l'année suivante. Où en est-on ?
  options:
  - Au point de départ
  - À −25 % par rapport au départ
  - À +25 %
  - À −50 %
  answer: 1
  explain: 100 → 50 → 75. Une baisse de 50 % demande +100 % pour revenir à 100.
---

Deux forces travaillent en permanence sur ton argent : les **intérêts composés**, qui le font croître, et l'**inflation**, qui le grignote. Comprendre les deux est la base de toute décision financière de long terme.

## Les intérêts composés

Quand les intérêts sont **réinvestis**, ils rapportent à leur tour. La croissance n'est plus linéaire, mais exponentielle.

| 1 000 € à 7 % par an | Valeur |
| --- | --- |
| après 10 ans | environ 1 970 € |
| après 20 ans | environ 3 870 € |
| après 30 ans | environ 7 610 € |

La moitié de la croissance arrive dans les **dernières années**. C'est pour cela que le temps est l'ingrédient le plus précieux.

<!-- schema:composes -->
<figure class="diagram"><svg viewBox="0 0 680 320" role="img" aria-label="Les intérêts composés" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><line x1="80" y1="250.0" x2="560" y2="250.0" class="dg-grid"/><text x="72" y="254.0" class="dg-s" text-anchor="end">0 k€</text><line x1="80" y1="206.0" x2="560" y2="206.0" class="dg-grid"/><text x="72" y="210.0" class="dg-s" text-anchor="end">50 k€</text><line x1="80" y1="162.0" x2="560" y2="162.0" class="dg-grid"/><text x="72" y="166.0" class="dg-s" text-anchor="end">100 k€</text><line x1="80" y1="118.0" x2="560" y2="118.0" class="dg-grid"/><text x="72" y="122.0" class="dg-s" text-anchor="end">150 k€</text><line x1="80" y1="74.0" x2="560" y2="74.0" class="dg-grid"/><text x="72" y="78.0" class="dg-s" text-anchor="end">200 k€</text><line x1="80" y1="30.0" x2="560" y2="30.0" class="dg-grid"/><text x="72" y="34.0" class="dg-s" text-anchor="end">250 k€</text><text x="80.0" y="268" class="dg-s" text-anchor="middle">0</text><text x="160.0" y="268" class="dg-s" text-anchor="middle">5</text><text x="240.0" y="268" class="dg-s" text-anchor="middle">10</text><text x="320.0" y="268" class="dg-s" text-anchor="middle">15</text><text x="400.0" y="268" class="dg-s" text-anchor="middle">20</text><text x="480.0" y="268" class="dg-s" text-anchor="middle">25</text><text x="560.0" y="268" class="dg-s" text-anchor="middle">30</text><text x="320.0" y="286" class="dg-s" text-anchor="middle">années</text><path d="M80.0 250.0 L96.0 247.81890498902328 L112.0 245.48013844334793 L128.0 242.9723022749818 L144.0 240.28317442723036 L160.0 237.3996493099322 L176.0 234.30767392875353 L192.0 230.99217939726398 L208.0 227.43700749801465 L224.0 223.62483193471076 L240.0 219.53707389169747 L256.0 215.15381148923402 L272.0 210.4536826932824 L288.0 205.4137812066367 L304.0 200.00954483401392 L320.0 194.21463577704802 L336.0 188.00081227579952 L352.0 181.33779097121942 L368.0 174.19309931778434 L384.0 166.53191732702965 L400.0 158.31690787070892 L416.0 149.50803471655598 L432.0 140.062367409837 L448.0 129.93387204977427 L464.0 119.07318694118055 L480.0 107.42738202793248 L496.0 94.93970093586978 L512.0 81.54928436795495 L528.0 67.19087350364688 L544.0 51.794491956990925 L560.0 35.28510474343372" class="dg-l c thick draw" pathLength="1"/><text x="568.0" y="39.28510474343372" class="dg-ct" text-anchor="start">244 k€</text><path d="M80.0 250.0 L96.0 247.888 L112.0 245.776 L128.0 243.664 L144.0 241.552 L160.0 239.44 L176.0 237.328 L192.0 235.216 L208.0 233.10399999999998 L224.0 230.992 L240.0 228.88 L256.0 226.768 L272.0 224.656 L288.0 222.544 L304.0 220.432 L320.0 218.32 L336.0 216.208 L352.0 214.096 L368.0 211.984 L384.0 209.872 L400.0 207.76 L416.0 205.648 L432.0 203.536 L448.0 201.424 L464.0 199.312 L480.0 197.2 L496.0 195.088 L512.0 192.976 L528.0 190.864 L544.0 188.752 L560.0 186.64" class="dg-l dash draw" pathLength="1"/><text x="568.0" y="190.64" class="dg-s" text-anchor="start">72 k€ versés</text><text x="100" y="44" class="dg-tl" text-anchor="start">200 € par mois à 7 % par an</text></svg><figcaption>La courbe pleine est le capital, la droite en tirets ce que tu as versé. Après 30 ans, plus des deux tiers du capital sont des intérêts : l&#x27;écart se creuse surtout à la fin.</figcaption></figure>
<!-- /schema:composes -->

### La règle de 72

**72 / taux annuel = années pour doubler.**

| Taux | Doublement |
| --- | --- |
| 1,7 % (livret A) | environ 42 ans |
| 3 % | environ 24 ans |
| 6 % | environ 12 ans |
| 8 % | environ 9 ans |

Elle marche aussi à l'envers : avec 2 % d'inflation, les prix **doublent** en 36 ans environ.

## Commencer tôt

Le même effort ne produit pas le même résultat selon le moment où il commence. Avec 200 € par mois à 7 % par an :

| Durée | Versé | Valeur finale |
| --- | --- | --- |
| 10 ans | 24 000 € | environ 35 000 € |
| 20 ans | 48 000 € | environ 104 000 € |
| 30 ans | 72 000 € | environ 244 000 € |

Les 10 dernières années (de 20 à 30 ans) rapportent plus que les 20 premières réunies. Exemple encore plus frappant : verser 200 € par mois de 25 à 35 ans **puis arrêter** donne plus à 55 ans (environ 140 000 €) que verser 200 € par mois de 35 à 55 ans (environ 104 000 €), avec deux fois moins d'argent versé.

*Ces chiffres supposent un rendement constant. En réalité, les rendements varient : ils servent à comprendre le mécanisme, pas à prévoir un résultat.*

## L'inflation

L'inflation est la hausse générale des prix. Elle fait baisser le **pouvoir d'achat** de l'argent qui dort :

| Inflation annuelle | Pouvoir d'achat de 1 000 € après 20 ans | après 35 ans |
| --- | --- | --- |
| 2 % | environ 670 € | environ 500 € |
| 3 % | environ 550 € | environ 355 € |

Un billet de 100 € gardé dans un tiroir pendant 35 ans achète deux fois moins de choses à la fin.

## Le rendement réel

**Rendement réel ≈ rendement nominal − inflation.**

C'est le seul chiffre qui dit si l'on s'enrichit vraiment. Il faut aussi retirer les **frais** et les **impôts** :

| Étape | Exemple |
| --- | --- |
| Rendement affiché (nominal) | 4 % |
| moins les frais | − 1 % → 3 % |
| moins les impôts | − 0,6 % → 2,4 % (net) |
| moins l'inflation | − 2 % → **0,4 % réel net** |

Un placement qui affiche 4 % peut ne rapporter presque rien en réalité. D'où l'importance des fiches sur les **frais** et sur les **enveloppes fiscales**.

## La volatilité réduit le rendement

Un rendement **moyen** ne raconte pas tout. Les pertes et les gains ne sont pas symétriques :

| Baisse | Hausse nécessaire pour revenir |
| --- | --- |
| − 10 % | + 11 % |
| − 20 % | + 25 % |
| − 33 % | + 50 % |
| − 50 % | + 100 % |

C'est une raison de plus de **diversifier** (fiche Risque et diversification) : réduire les grosses baisses améliore le rendement obtenu sur la durée.

> **À retenir.** Les intérêts composés rendent le temps précieux : commencer tôt vaut plus que verser beaucoup tard. Règle de 72 : 72 / taux = années pour doubler. L'inflation grignote l'argent qui dort. Juge un placement sur son rendement réel net (après frais, impôts et inflation). Une baisse de 50 % demande +100 % pour être effacée.
