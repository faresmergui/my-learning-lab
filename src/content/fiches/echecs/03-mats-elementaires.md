---
title: Les mats élémentaires
chapter: 3
order: 1
duration: 13
level: Bases
tags:
- mat
- finale
- roi et dame
- roi et tour
- pat
cards:
- q: Quel est le principe commun à tous les mats élémentaires ?
  a: '**Repousser le roi adverse vers un bord** (ou un coin), en réduisant pas à pas la « boîte » dans laquelle il peut bouger, puis **amener son propre roi** pour aider à donner le mat. Le roi attaquant est indispensable, sauf avec deux tours.'
- q: Comment mater avec roi et dame ?
  a: La dame se place à un **saut de cavalier** du roi adverse et le suit pour réduire sa zone, jusqu'à le bloquer sur un bord. On **amène ensuite le roi**, puis la dame donne mat, soutenue par le roi. Moins de 10 coups depuis presque toute position.
- q: Quel est le piège du mat roi et dame ?
  a: 'Le **pat** : quand le roi adverse est bloqué dans le coin, la dame ne doit pas lui retirer sa dernière case alors qu''il n''est pas en échec. Exemple : roi noir en a8, dame blanche en b6 : si les Noirs sont au trait, c''est pat.'
- q: Comment mater avec roi et tour ?
  a: 'La tour **coupe** le roi adverse sur une rangée ou une colonne. Les rois se mettent **en opposition** (face à face, une case entre eux) : la tour donne alors échec sur le côté et le roi adverse recule d''une ligne. On recommence jusqu''au bord. Environ 16 coups au maximum.'
- q: Comment mater avec deux tours ?
  a: 'Par l''**escalier** (le « rouleau ») : une tour coupe une rangée, l''autre donne échec sur la rangée suivante, et elles alternent. Le roi attaquant n''est pas nécessaire. Si le roi adverse attaque une tour, on la déplace loin de l''autre côté.'
- q: Peut-on mater avec deux cavaliers ?
  a: '**Non**, contre un roi seul, deux cavaliers ne peuvent pas **forcer** le mat (sauf erreur de l''adversaire). Roi et fou seul, ou roi et cavalier seul, ne peuvent pas mater du tout : nulle par matériel insuffisant.'
- q: Qu'est-ce que le mat fou et cavalier ?
  a: 'Le plus difficile des mats élémentaires : il faut pousser le roi adverse vers un **coin de la couleur du fou**, ce qui peut prendre jusqu''à **33 coups**. Technique connue : la méthode du « W » du cavalier. Rare en partie, utile surtout à haut niveau.'
quiz:
- q: Roi noir en h8, roi blanc en g6, dame blanche en d4, Blancs au trait. Lequel de ces coups est mat ?
  options:
  - Dd8#
  - Dh4+
  - Df6+
  - Dd5
  answer: 0
  explain: Dd8 donne échec sur la 8ᵉ rangée ; g8 est contrôlée par la dame, g7 et h7 par le roi g6. Après Dh4+ ou Df6+, le roi s'échappe en g8.
- q: Roi noir en a8, roi blanc en c7, dame blanche en c6, Blancs au trait. Ils jouent Db6. Que se passe-t-il ?
  options:
  - Mat
  - 'Pat : le roi noir n''est pas en échec et n''a plus aucune case'
  - Échec simple
  - Rien de spécial
  answer: 1
  explain: 'a7, b7 et b8 sont contrôlées, sans échec : pat. Il fallait jouer Db7#, la dame étant protégée par le roi c7.'
- q: Ta tour en a7 enferme le roi noir (e8) sur la 8ᵉ rangée. Ton roi est en e6, face à lui. Quel coup ?
  options:
  - Te7+
  - 'Une tour sur la 8ᵉ rangée : Ta8#'
  - Re7
  - Attendre
  answer: 1
  explain: 'Les rois sont en opposition : l''échec de la tour sur la 8ᵉ rangée est mat, car d7, e7, f7 sont contrôlées par le roi blanc.'
- q: Tu as deux cavaliers contre un roi seul. Résultat attendu ?
  options:
  - Gain forcé
  - 'Nulle : le mat ne peut pas être forcé'
  - Gain en 50 coups
  - Perte
  answer: 1
  explain: Deux cavaliers ne forcent pas le mat contre un roi seul ; le défenseur évite simplement les cases du mat.
---

Les mats élémentaires sont les premiers « automatismes » d'un joueur. Ils paraissent simples, mais ne pas les connaître coûte des demi-points en finale, et surtout le **pat** transforme régulièrement des parties gagnées en nulles.

## Le principe : la boîte

Le roi adverse occupe une « boîte » délimitée par les pièces qui le coupent. Chaque coup doit **réduire la boîte**, jusqu'à coincer le roi sur un bord. Le roi attaquant vient ensuite **soutenir** la pièce qui mate.

## Roi et dame contre roi

Méthode :

1. placer la dame **à un saut de cavalier** du roi adverse ; elle le coupe sur deux lignes ;
2. à chaque coup adverse, suivre le roi pour garder ce saut de cavalier : la boîte rétrécit ;
3. une fois le roi sur un bord, **arrêter la dame** et amener son propre roi ;
4. mater avec la dame protégée par le roi, ou en se plaçant sur la ligne du bord.

**Le piège du pat** : ne pas « coller » la dame au roi coincé dans un coin sans donner échec. Si le roi adverse ne peut plus bouger et n'est pas en échec, c'est nulle. Règle de prudence : quand le roi est sur un bord, vérifier à chaque coup qu'il garde **au moins une case**, jusqu'au mat.

## Roi et tour contre roi

1. la tour **coupe** le roi adverse (par exemple sur une colonne) ;
2. le roi attaquant s'approche ;
3. quand les rois sont **face à face** (opposition, une case entre eux), la tour donne **échec latéral** : le roi adverse doit reculer d'une ligne ;
4. si le roi adverse ne se met pas en opposition, la tour fait un **coup d'attente** sur sa ligne pour la provoquer ;
5. si le roi adverse attaque la tour, l'éloigner sur la même ligne.

Au bord, l'échec en opposition est mat. La méthode prend au plus 16 coups.

## Deux tours contre roi : l'escalier

Les tours avancent en alternance : l'une coupe la rangée 6, l'autre donne échec sur la rangée 7, la première passe en 8 : mat. Le roi attaquant n'a pas besoin d'aider. Si le roi adverse s'approche d'une tour, la déplacer **à l'autre extrémité** de sa rangée.

La même idée fonctionne avec **dame et tour** : c'est le schéma de mat le plus fréquent en partie.

## Les autres combinaisons

| Matériel | Résultat | Remarque |
| --- | --- | --- |
| R + D | gagne | moins de 10 coups |
| R + T | gagne | au plus 16 coups |
| R + 2 T | gagne | l'escalier |
| R + 2 F (de couleurs différentes) | gagne | roi vers n'importe quel coin, environ 19 coups |
| R + F + C | gagne | coin de la couleur du fou, jusqu'à 33 coups |
| R + 2 C | **nulle** | ne peut pas forcer le mat |
| R + F ou R + C | **nulle** | matériel insuffisant |

Le **fou et cavalier** demande une technique précise (le cavalier décrit un « W ») ; c'est utile à connaître pour le principe, rarement en partie.

## Les mats sur le bord

Un roi bloqué par ses propres pions (roi roqué en g1 avec f2, g2, h2) est déjà « sur un bord » : une tour ou une dame sur la première rangée suffit. C'est le **mat du couloir**, détaillé dans la fiche Attaquer le roi.

> **À retenir.** Repousse le roi vers un bord en réduisant sa boîte, puis amène ton roi. Dame : à un saut de cavalier du roi adverse. Tour : coupe, opposition des rois, échec latéral. Deux tours : l'escalier, sans le roi. Vérifie toujours que le roi coincé garde une case tant qu'il n'est pas mat, pour éviter le pat. Deux cavaliers, ou une pièce mineure seule, ne gagnent pas.
