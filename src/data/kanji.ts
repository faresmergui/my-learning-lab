// Kanji by JLPT level, for the Japanese summary page.
// The JLPT has not published an official list since 2010: these follow the
// reference lists commonly used for studying.
// Line format: kanji | on readings (katakana) | kun readings (hiragana) | meaning (French)
const N5 = `
日|ニチ・ジツ|ひ・か|jour, soleil
一|イチ・イツ|ひと(つ)|un
二|ニ|ふた(つ)|deux
三|サン|みっ(つ)|trois
四|シ|よ・よん・よっ(つ)|quatre
五|ゴ|いつ(つ)|cinq
六|ロク|むっ(つ)|six
七|シチ|なな(つ)|sept
八|ハチ|やっ(つ)|huit
九|キュウ・ク|ここの(つ)|neuf
十|ジュウ|とお|dix
百|ヒャク||cent
千|セン|ち|mille
万|マン・バン||dix mille
円|エン|まる(い)|yen, cercle
年|ネン|とし|année
月|ゲツ・ガツ|つき|lune, mois
火|カ|ひ|feu
水|スイ|みず|eau
木|モク・ボク|き|arbre
金|キン・コン|かね|or, argent
土|ド・ト|つち|terre, sol
時|ジ|とき|heure, moment
分|ブン・フン|わ(ける)|minute, partager
半|ハン|なか(ば)|moitié
今|コン・キン|いま|maintenant
午|ゴ||midi
毎|マイ||chaque
何|カ|なに・なん|quoi
人|ジン・ニン|ひと|personne
男|ダン・ナン|おとこ|homme
女|ジョ・ニョ|おんな|femme
子|シ|こ|enfant
父|フ|ちち|père
母|ボ|はは|mère
友|ユウ|とも|ami
名|メイ・ミョウ|な|nom
先|セン|さき|avant, pointe
生|セイ・ショウ|い(きる)・う(まれる)|vie, naître
学|ガク|まな(ぶ)|étude
校|コウ||école
語|ゴ|かた(る)|langue, mot
国|コク|くに|pays
本|ホン|もと|livre, origine
大|ダイ・タイ|おお(きい)|grand
小|ショウ|ちい(さい)・こ|petit
高|コウ|たか(い)|haut, cher
長|チョウ|なが(い)|long, chef
白|ハク|しろ(い)|blanc
上|ジョウ|うえ・あ(がる)|dessus, monter
下|カ・ゲ|した・さ(がる)|dessous, descendre
中|チュウ|なか|milieu, dedans
外|ガイ|そと|dehors
右|ウ・ユウ|みぎ|droite
左|サ|ひだり|gauche
前|ゼン|まえ|avant, devant
後|ゴ・コウ|あと・うし(ろ)|après, derrière
間|カン・ケン|あいだ・ま|intervalle, entre
東|トウ|ひがし|est
西|セイ・サイ|にし|ouest
南|ナン|みなみ|sud
北|ホク|きた|nord
山|サン|やま|montagne
川|セン|かわ|rivière
天|テン|あめ|ciel
気|キ・ケ||esprit, énergie
雨|ウ|あめ|pluie
電|デン||électricité
車|シャ|くるま|voiture
行|コウ・ギョウ|い(く)・おこな(う)|aller
来|ライ|く(る)|venir
出|シュツ|で(る)・だ(す)|sortir
入|ニュウ|い(る)・はい(る)|entrer
見|ケン|み(る)|voir
聞|ブン|き(く)|entendre, demander
話|ワ|はな(す)・はなし|parler, histoire
読|ドク|よ(む)|lire
書|ショ|か(く)|écrire
食|ショク|た(べる)|manger
休|キュウ|やす(む)|repos
`;

const N4 = `
会|カイ|あ(う)|rencontrer, réunion
同|ドウ|おな(じ)|même
事|ジ|こと|chose, fait
自|ジ・シ|みずか(ら)|soi-même
社|シャ|やしろ|entreprise, sanctuaire
発|ハツ||départ, émettre
者|シャ|もの|personne (qui fait)
地|チ・ジ||sol, terre
業|ギョウ|わざ|métier, industrie
方|ホウ|かた|direction, manière
新|シン|あたら(しい)|nouveau
場|ジョウ|ば|lieu
員|イン||membre
立|リツ|た(つ)|se lever, debout
開|カイ|あ(ける)・ひら(く)|ouvrir
手|シュ|て|main
力|リョク・リキ|ちから|force
問|モン|と(う)|question
代|ダイ|か(わる)・よ|génération, remplacer
明|メイ|あか(るい)|clair, lumineux
動|ドウ|うご(く)|bouger
京|キョウ||capitale
目|モク|め|œil
通|ツウ|とお(る)・かよ(う)|passer, fréquenter
言|ゲン・ゴン|い(う)・こと|dire
理|リ||raison, logique
体|タイ|からだ|corps
田|デン|た|rizière
主|シュ|ぬし・おも|principal, maître
題|ダイ||sujet, titre
意|イ||idée, intention
不|フ・ブ||non-, négation
作|サク・サ|つく(る)|fabriquer
用|ヨウ|もち(いる)|usage
度|ド|たび|degré, fois
強|キョウ|つよ(い)|fort
公|コウ|おおやけ|public
持|ジ|も(つ)|tenir, avoir
野|ヤ|の|champ, plaine
以|イ||à partir de, par rapport à
思|シ|おも(う)|penser
家|カ・ケ|いえ・うち|maison, famille
世|セ・セイ|よ|monde, génération
多|タ|おお(い)|nombreux
正|セイ・ショウ|ただ(しい)|correct
安|アン|やす(い)|bon marché, tranquille
院|イン||institution
心|シン|こころ|cœur, esprit
界|カイ||monde, frontière
教|キョウ|おし(える)|enseigner
文|ブン・モン|ふみ|phrase, écrit
元|ゲン・ガン|もと|origine
重|ジュウ・チョウ|おも(い)・かさ(ねる)|lourd
近|キン|ちか(い)|proche
考|コウ|かんが(える)|réfléchir
画|ガ・カク||image, trait
海|カイ|うみ|mer
売|バイ|う(る)|vendre
知|チ|し(る)|savoir
道|ドウ|みち|chemin
集|シュウ|あつ(める)|rassembler
別|ベツ|わか(れる)|séparé, autre
物|ブツ・モツ|もの|objet
使|シ|つか(う)|utiliser
品|ヒン|しな|article, qualité
計|ケイ|はか(る)|mesurer, plan
死|シ|し(ぬ)|mort
特|トク||spécial
私|シ|わたし・わたくし|moi, privé
始|シ|はじ(める)|commencer
朝|チョウ|あさ|matin
運|ウン|はこ(ぶ)|transporter, chance
終|シュウ|お(わる)|finir
台|ダイ・タイ||socle, compteur de machines
広|コウ|ひろ(い)|large, vaste
住|ジュウ|す(む)|habiter
真|シン|ま|vrai
有|ユウ・ウ|あ(る)|avoir, exister
口|コウ|くち|bouche
少|ショウ|すく(ない)・すこ(し)|peu
町|チョウ|まち|ville, quartier
料|リョウ||frais, matière
工|コウ・ク||artisanat, construction
建|ケン|た(てる)|construire
空|クウ|そら・あ(く)・から|ciel, vide
急|キュウ|いそ(ぐ)|urgent, se dépêcher
止|シ|と(まる)・と(める)|arrêter
送|ソウ|おく(る)|envoyer
切|セツ|き(る)|couper
転|テン|ころ(ぶ)|tourner, tomber
研|ケン|と(ぐ)|polir, étudier
足|ソク|あし・た(りる)|pied, suffire
究|キュウ|きわ(める)|approfondir
楽|ガク・ラク|たの(しい)|plaisir, musique
起|キ|お(きる)|se lever, survenir
着|チャク|き(る)・つ(く)|porter, arriver
店|テン|みせ|magasin
病|ビョウ|やまい|maladie
質|シツ||qualité, nature
待|タイ|ま(つ)|attendre
試|シ|こころ(みる)・ため(す)|essayer
族|ゾク||famille, tribu
銀|ギン||argent (métal)
早|ソウ|はや(い)|tôt
映|エイ|うつ(る)|refléter, projeter
親|シン|おや・した(しい)|parent, intime
験|ケン||examen, effet
英|エイ||anglais, excellent
医|イ||médecine
仕|シ|つか(える)|servir
去|キョ・コ|さ(る)|partir, passé
味|ミ|あじ|goût
写|シャ|うつ(す)|copier, photographier
字|ジ|あざ|caractère
答|トウ|こた(える)|répondre
夜|ヤ|よる・よ|nuit
音|オン|おと・ね|son
注|チュウ|そそ(ぐ)|verser, attention
帰|キ|かえ(る)|rentrer
古|コ|ふる(い)|vieux
歌|カ|うた・うた(う)|chanson, chanter
買|バイ|か(う)|acheter
悪|アク|わる(い)|mauvais
図|ズ・ト|はか(る)|plan, dessin
週|シュウ||semaine
室|シツ|むろ|pièce, salle
歩|ホ|ある(く)|marcher
風|フウ|かぜ|vent
紙|シ|かみ|papier
黒|コク|くろ(い)|noir
花|カ|はな|fleur
春|シュン|はる|printemps
赤|セキ|あか(い)|rouge
青|セイ|あお(い)|bleu
館|カン|やかた|bâtiment, salle
屋|オク|や|toit, boutique
色|ショク・シキ|いろ|couleur
走|ソウ|はし(る)|courir
秋|シュウ|あき|automne
夏|カ|なつ|été
習|シュウ|なら(う)|apprendre
駅|エキ||gare
洋|ヨウ||océan, occidental
旅|リョ|たび|voyage
服|フク||vêtement
夕|セキ|ゆう|soir
借|シャク|か(りる)|emprunter
曜|ヨウ||jour de la semaine
飲|イン|の(む)|boire
肉|ニク||viande
貸|タイ|か(す)|prêter
堂|ドウ||salle, temple
鳥|チョウ|とり|oiseau
飯|ハン|めし|riz cuit, repas
勉|ベン||effort
冬|トウ|ふゆ|hiver
昼|チュウ|ひる|midi, journée
茶|チャ・サ||thé
弟|ダイ・テイ|おとうと|petit frère
牛|ギュウ|うし|bœuf
魚|ギョ|さかな・うお|poisson
兄|キョウ・ケイ|あに|grand frère
犬|ケン|いぬ|chien
妹|マイ|いもうと|petite sœur
姉|シ|あね|grande sœur
漢|カン||chinois (Han)
`;

export type Kanji = { k: string; on: string; kun: string; sens: string };
const parse = (s: string): Kanji[] =>
  s.trim().split('\n').map((l) => { const [k, on, kun, sens] = l.split('|'); return { k, on, kun, sens }; });

export const LEVELS = [
  { id: 'N5', title: 'N5 · Débutant', kanji: parse(N5) },
  { id: 'N4', title: 'N4 · Élémentaire', kanji: parse(N4) },
  { id: 'N3', title: 'N3 · Intermédiaire', kanji: [] as Kanji[] },
  { id: 'N2', title: 'N2 · Avancé', kanji: [] as Kanji[] },
  { id: 'N1', title: 'N1 · Expert', kanji: [] as Kanji[] },
];
