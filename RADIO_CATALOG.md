# Radio song catalog

IGN could not be accessed (HTTP 403). This is a fallback extraction of the song lists published by [Dot Esports](https://dotesports.com/cyberpunk/news/all-cyberpunk-2077-radio-stations-and-song-lists), not an IGN extract.

Contains 196 song entries across 14 stations. This captures that article’s lists, not a claim of independently verified or exhaustive game coverage. Source spellings and credits may need review when matching Spotify.

Each JSON record includes a station frequency, station name, song title, real artist credit where the source supplies it, in-game artist alias, and source URL. Existing playback data in `stations.json` was left intact.

## Spotify lookup

```sh
.venv/bin/python scripts/lookup_tracks.py tracks.catalog.json -o stations.resolved.json
```

Review missing and low-confidence matches before replacing `stations.json` with the resolved file. The source credits “I Really Want to Stay at Your House” to Let’s Eat Grandma; Spotify credits Rosa Walton and Hallie Coggins, so use that artist name when resolving it. The source also has spelling variations that can reduce matching confidence.

## 88.9 PACIFIC DREAMS

| Song | Artist | In-game artist |
| --- | --- | --- |
| Isometric Air | Brian Aspey | Quantum Lovers |
| Practical Heart | Brian Aspey | Quantum Lovers |
| Real Window | Brian Aspey | Quantum Lovers |
| Antagonistic | Sebastian Roberston and Chris Cardena | Pacific Avenue |
| Simple Pleasures | Kid Moxie | Jänsens |
| Lithium | SLG | Flatlander Woman |
| Slag | SLG | Flatlander Woman |
| Chooze | Mchy I Porosty | Muchomorr |
| Midnight Eye | Earth Trax | Lick Switch |
| Blurred | Earth Trax | Lick Switch |
| The Other Room | Earth Trax | Lick Switch |
| La Stessa Causa | Eltron | Sonoris Causa |
| Retrogenesis | Private Press | Left Unsaid |
| Miami Suicide | Chino | Talk To Us |
| Slippery Stabs | Chino | Talk To Us |
| Ashes and Diamonds | Hatti Vatti | Wormview |
| Ice Maddox | FOQL | Mona Mitchell |
## 89.3 RADIO VEXELSTROM

| Song | Artist | In-game artist |
| --- | --- | --- |
| Resist and Disorder | Rezodrone | The Cartesian Duelists |
| Kill the Messenger | Rezodrone | The Cartesian Duelists |
| Makes Me Feel Better | OnenO | Slavoj McAllister |
| Dead Pilot | Sebastian Robertson and Daniel Davies | Keine |
| Come Close | Sebastian Robertson and Daniel Davies | Keine |
| Black Terminal | Black Terminal | Upgrade |
| Reaktion | Rezodrone | Alexei Brayko |
| With Her | Steven Richard Davis | Ego Affliction |
| Never Stop Me | Steven Richard Davis | Den of Degenerates |
| Violence | Le Destroy | The Red Glare |
| Pain | Le Destroy | The Red Glare |
| Night City Aliens | The Armed | Homeschool Dropouts |
| Selva Pulsátil | Deafkids | Tainted Overlord |
| A Caça | Deafkids | Tainted Overlord |
## 89.7 GROWL FM

| Song | Artist | In-game artist |
| --- | --- | --- |
| Let The Stars Die | Coeur Noir | Coeur Noir |
| Flatline | Red Dead Roadkill | Red Dead Roadkill |
| Candy Shell | Spirit Machines | Spirit Machines |
| Do or Die | NoWorld | NoWorld |
| LIT | Entolim | Entolim |
| El Tiempo | Skin on Flesh | Skin on Flesh |
| Killshot | Frost, Justtjokay, Dubbygotbars, and Knyvez | Frost, Justtjokay, Dubbygotbars, and Knyvez |
| Let It Go As If You Wander | HARU NEMURI | HARU NEMURI |
| Slipstream | Kiba | Kiba |
| Fumes | Aleyna Moon and Shrinjay Ghosh | Aleyna Moon and Shrinjay Ghosh |
| Look Through My Kiroshi’s (The Solo Life) | D.O.H. Dollahz Ova Hoez | D.O.H. Dollahz Ova Hoez |
| Going to Heaven | St. Aurora | St. Aurora |
| Nebula | ESAI and Pure 100% | ESAI and Pure 100% |
| Afterlife | Thai McGrath ft. JustCosplaySings | Thai McGrath ft. JustCosplaySings |
## 91.9 ROYAL BLUE RADIO

| Song | Artist | In-game artist |
| --- | --- | --- |
| Black Satin | Miles Davis | Miles Davis |
| What If | Miles Davis | Miles Davis |
| Agharta Prelude Dub | Miles Davis | Miles Davis |
| Bitches Brew | Miles Davis | Miles Davis |
| Générique (from Ascenseur pour L’Échafaud) | Miles Davis | Miles Davis |
| Impressions | John Coltrane | John Coltrane |
| Solo Dancer | Charles Mingus | Charles Mingus |
| Laura | Dexter Gordon | Dexter Gordon |
| You Don’t Know What Love Is | Chet Baker | Chet Baker |
| Round Midnight | Thelonious Monk | Thelonious Monk |
| Dark Prince | Trio of Doom | Trio of Doom |
## 92.9 NIGHT FM

| Song | Artist | In-game artist |
| --- | --- | --- |
| Dirty Roses | OnenO | Perilous Futur |
| Worlds | Sebastian Robertson and Daniel Davies | The Unresolved |
| X | Sebastian Robertson and Daniel Davies | The Unresolved |
| Maniak | Picasso | Doctor Berserk |
| Me Machine | Poly Face | Generating Dependencies |
| Like a Miracle | Earth Trax | Lick Switch |
| Run | Steven Richard Davis | Kings of Collapse |
| Glitched Revelation | Procesor Plus | Reviscerator |
| Yellow Box | Procesor Plus | Reviscerator |
| Kill Kill | Le Destroy | The Bait |
| Flying Heads | Kid Moxie | Ashes Potts |
| Volcano The Sailor | Połoz | Yards of the Moon |
| Brain-Damaged | Nikola Nikita Jeremic | Cyber Coorayber |
## 95.2 SAMIZDAT RADIO

| Song | Artist | In-game artist |
| --- | --- | --- |
| Pilling in My Head | Bara Nova | Bara Nova |
| Delirium 2 | Bara Nova | Bara Nova |
| Harm Sweaty Pit | Bara Nova | Bara Nova |
| My Lullaby for You | Bara Nova | Bara Nova |
| Surprise Me, I’m Surprised Today | Bara Nova | Bara Nova |
## 96.1 RITUAL FM

| Song | Artist | In-game artist |
| --- | --- | --- |
| Finis | Drivealone | V3RM1N |
| The Accursed | Antre | Dread Soul |
| Adaptive Manipulator | Tomb Mold | Bacillus |
| March 30 | Tomb Mold | Bacillus |
| Acid Breather | Mastiff | Forlorn Scourge |
| Witches of the Harz Mountains | Marcin Rybicki | Nuclear Aura |
| The Loop | Deszcz | Weles |
| Scrum | Totenmesse | Hysteria |
| Fuelled By Poison | Antigama | Inferno Crops |
| Kevin | Antigama | Inferno Crops |
| Future Drugs | Mord’A’Stigmata | Hexxxer |
| Żurawie | Ugory | Wydech |
| Abandoned Land | Arthur Rumiński and Haldor Grunberg | Fist of Satan |
| Black Concrete | Arthur Rumiński and Haldor Grunberg | Fist of Satan |
| I Won’t Let You Go | Converge | Shattered Void |
## 98.7 BODY HEAT RADIO

| Song | Artist | In-game artist |
| --- | --- | --- |
| BM | SOPHIE and Shygirl | Clockwork Venus |
| Circus Minimus | Jvzel | Neon Haze |
| Major Crimes | HEALTH | Window Weather |
| Night City | R E L | Artemis Delta |
| I Really Want to Stay at Your House | Let’s Eat Grandma | Hallie Coggins |
| Hole In The Sun | Raney Shockne ft. COS and Conway | Point Break Candy |
| Blind | Raney Shockne | American Medical Association |
| History | Gazelle Twin | Trash Generation |
| 4ÆM | Grimes | Lizzy Wizzy |
| Delicate Weapon | Grimes | Lizzy Wizzy |
| Ponpon Sh*t | Namakopuri | Us Cracks |
| User Friendly cover | Namakopuri | Us Cracks |
| Off the Leash | Namakopuri and Damian Ukeje | Us Cracks ft. Kerry Eurodyne |
| Crustpunk | RAT BOY | IBDY |
| Here’s a Thought | RAT BOY | IBDY |
## 99.9 IMPULSE

| Song | Artist | In-game artist |
| --- | --- | --- |
| Walk Of Shame | Idris Elba | Mr. Kipper |
| Dreamy | Adam Brocki and Jan Wóycicki | Private Press |
| DEEEEEEP | Adam Brocki and Jan Wóycicki | Private Press |
| Black Labyrinth | Adam Brocki and Jan Wóycicki | Private Press |
| Feed Your Soul | Adam Brocki and Jan Wóycicki | Private Press |
| Liquid Disco | Adam Brocki and Jan Wóycicki | Private Press |
| Sleepy Dust | Adam Brocki and Jan Wóycicki | Private Press |
| Sparkling Frequency | Adam Brocki and Jan Wóycicki | Private Press |
| Undeniably Changes | Adam Brocki and Jan Wóycicki | Private Press |
| Void | Adam Brocki and Jan Wóycicki | Private Press |
| Woozee | Adam Brocki and Jan Wóycicki | Private Press |
| GREEEEEENHOUSE | Adam Brocki and Jan Wóycicki | Private Press |
| BESTPL | Adam Brocki and Jan Wóycicki | Private Press |
| ENERGEEHOUSE | Adam Brocki and Jan Wóycicki | Private Press |
## 101.9 THE DIRGE

| Song | Artist | In-game artist |
| --- | --- | --- |
| The God Machines | Sebastian Roberston, Kill the Computer, and Indijinouz | Kill Trigger ft. Paul Senai and Krakow |
| Blouses Blue | Konrad OldMoney ft. Cidro Onetoo and Perry Porter | NC3 |
| Problem Kids | Konrad OldMoney ft. Taelor Yung | Young Kenny |
| Bigger Man | Konrad OldMoney ft. Taelor Yung | Droox |
| Go Blaze | Konrad OldMoney ft. Chanarah and Cidro Onetoo | DNE ft. G’Natt |
| Dishonor | Konrad OldMoney ft. Brevner | Ichibanchi |
| Frost | Konrad OldMoney ft. Frawst | Yamete |
| High School Bully | Konrad OldMoney ft. Cidro Onetoo and Perry Porter | UMVN ft. IMP RA |
| NBOM | Konrad OldMoney ft. Cidro Onetoo and Perry Porter | Dapxflem |
| Suicide | Geno Lenardo ft. Zeale | Code 137 |
| Day of Dead | Konrad OldMoney ft. Taelor Yung | Haps |
| Bruzez | Konrad OldMoney ft. Johnny GR4VES | Knixit |
| Clip Boss | Konrad OldMoney ft. Johnny GR4VES | Sugarcoob ft. Anak Konda |
| Pluck U | Konrad OldMoney ft. Ded Stark | Triple-B ft. Gun-Fu |
| Hello Good Morning | Konrad OldMoney ft. S-God | Pazoozu |
| Run The Block | Konrad OldMoney ft. Taelor Yung | Bez Tatami ft. Gully Foyle |
| GR4VES | Konrad OldMoney ft. Johnny GR4VES | Kyubik |
| Warning Shots | Konrad OldMoney ft. Perry Porter and Cidro Onetoo | Laputan Machine |
| Metamorphosis | Yugen Blakrok | Gorgon Madonna |
| No Save Point | Run The Jewels | Yankee and the Brave |
| Flacko Locko | A$AP Rocky | Telo$ |
## 103.5 RADIO PEBKAC

| Song | Artist | In-game artist |
| --- | --- | --- |
| Bios | Louve | Error |
| Drained | Rhys Fulber | Sao Mai |
| Subvert | Rhys Fulber | Spoon Eater |
| Follow the White Crow | Kid Moxie | Nablus |
| Fake Spook | Poly Face | IOshrine |
| Move Dat | Poly Face | [flesh]reactor |
| CANNIBALISMUS | Lutto Lento | Bullet in the Head |
| La Canopée | Private Press | culteX |
| Undertow Velocity | Private Press | Skin<>Drifter |
| IIOI Break | Private Press | Yards of the Moon |
| Across the Floor | Private Press | Retinal Scam |
| Gridflow | Private Press | Retinal Scam |
| Vascular | Speed Dating ft. Horrid Charme | Tar Hawk |
| On My Way to Hell | Połoz | Tinnitus |
| Stackoverflow | Dos Era | Clockwork OS |
| Darkretro | Count | Dukes of Azure |
## 106.9 30 PRINCIPALES

| Song | Artist | In-game artist |
| --- | --- | --- |
| Bamo | Konrad OldMoney ft. Frawst | Kartel Sonoro |
| Dagga | Konrad OldMoney ft. Cerbeus and Johnny GR4VES | Kartel Sonoro |
| Dinero | Konrad OldMoney ft. Cerbeus | 7 Facas |
| Serpant | Konrad OldMoney ft. Cerbeus and Johnny GR4VES | 7 Facas |
| Tatted on my Face | Konrad OldMoney ft. 37 Heartbreak | Don Mara |
| Barrio | Konrad OldMoney | Big Machete |
| Hood | Konrad OldMoney ft. Awrath | Chickychickas |
| Only Son | Konrad OldMoney ft. 37 Heartbreak | Chickychickas |
| Muévelo | David Rolas | Papito Gringo |
| Cumbia | David Rolas | Papito Gringo |
| Muerto Trash | Konrad OldMoney ft. Blackheart NC | FKXU |
| Westcoast Til I Die | Konrad OldMoney ft. Cerbeus | DJ Choloz |
## 107.3 MORRO ROCK RADIO

| Song | Artist | In-game artist |
| --- | --- | --- |
| Suffer Me | The Cold Stares | Brutus Backlash |
| Heave Ho | Konrad OldMoney ft. Frawst | XerzeX |
| I Will Follow | Snot Abundance | Beached Tarantula |
| Who’s Ready for Tomorrow | RAT BOY | IBDY |
| Likewise | RAT BOY | IBDY |
| Friday Night Fire Fight | Aligns | Rubicones |
| Trauma | Aligns | Rubicones |
| Summer of 2069 | Metz | Blood and Ice |
| Testmaster | Pissed Jeans | Krushchev’s Ghosts |
| Sustain/Decay | Drivealone | Cutthroat |
| To the Fullest | The Unfit | Artificial Kids |
| So It Goes | Man Man | Fingers and The Outlaws |
| Never Fade Away | Refused | Samurai |
| Black Dog | Refused | Samurai |
| Chippin’ In | Refused | Samurai |
| The Ballad of Buck Ravers | Refused | Samurai |
## 107.5 DARK STAR

| Song | Artist | In-game artist |
| --- | --- | --- |
| Choke Hold | Idris Elba | Mr. Kipper |
| Headrush | Backxwash | BADPANNINI |
| Orbital Insertion | Hagop Tchaparian | No Strings Attached |
| Cyko Arctic | Lord Spikeheart and Chrisman | BWANA MUNGU |
| Pierwszy raz naprawdę | 27.Fuckdemons | OLO Y |
| NUCLEAR DREAMLAND | julek ploski | DJ papergekko |
| Rolla Coaster | Idris Elba | Mr. Kipper |
| IKARI | Ecko Bazz, Silkback | ECKO FREQUENCY |
| fabrica KOSMOS | Kuba Wandacjpwocz | Her Mashewsky |
| dRk | Krzysztof Freeze Ostrowski | Walt Air |
| Minion Sex | T’len Lai | Mightonauts |
| Bigger Crimes | julek ploski | DJ papergekko |
| Memories of Mzuzu | Połoz | Łotr |
