# F-16C Kılavuz Kapsam Matrisi

## Kullanım

Bu dosya, `DCS F-16C Early Access Guide EN.pdf` (16 Ağustos 2026, 774 sayfa) içindeki yetenekleri JSBSim tabanlı RL müfredatına bağlar. Her satır ayrı bir kapsam maddesidir. FlightGear yalnız görselleştirme/debug aracıdır ve bir özelliği `native` veya `adapted` yapamaz.

Durum alanları JSBSim/Block 50 capability audit’i tamamlandıkça doldurulur:

- `native`: simülatör özelliği doğrudan sağlıyor;
- `adapted`: eşdeğer davranış bir adaptörle sağlanıyor;
- `missing`: özellik yok, bağlı ders eğitilemez;
- `knowledge`: ajanın eylem üretmediği fakat görev bağlamı/değerlendirme için kullanılan bilgi;
- `reference`: başka bir satırın test/oracle/veri sözlüğü.

Bir özellik yalnız şu dört koşulla **tam** sayılır: headless JSBSim veya repo uzantısında temsil, müfredatta ders, otomatik ölçüm ve dondurulmuş kabul testi. `TBD`, simülatör seçilmediği anlamına gelmez; JSBSim/Block 50 capability audit’inin henüz yapılmadığını gösterir.

Sağlayıcı önceliği:

1. JSBSim FDM/FCS ve model property’leri;
2. headless çalışabilen repo-native sistem uzantıları;
3. FlightGear görsel/property debug eşlemesi - yalnız inceleme, kapsam kanıtı değil.

### Eğitim sınıfı kuralları

Kapsam envanteri ile aktif RL curriculum aynı şey değildir. Her feature ID aşağıdaki sıralı kurallarla sınıflandırılır; üstteki özel kural alttaki genel kuralı geçersiz kılar.

| Sınıf | Feature ID kuralı | Eğitim kararı |
|---|---|---|
| REFERENCE_ONLY | `REF-*`, `STO-020`, `STO-021`, `CPT-026`, `CPT-032`, `CPT-040`, `CPT-045`, `CPT-046`, `CPT-050`-`CPT-053`, `CPT-056` | Ortam/oracle/dokümantasyon kapsamıdır; bağımsız RL dersi açılmaz. |
| CORE | `FLT-*`; `PRC-001`-`PRC-014`; `NAV-016`, `NAV-028`-`NAV-030`; `CPT-007`, `CPT-009`-`CPT-016`, `CPT-019`-`CPT-023`, `CPT-028`, `CPT-030`, `CPT-033`, `CPT-036`-`CPT-039`, `CPT-042`, `CPT-048`, `CPT-049`; `HOT-001`, `HOT-002`, `HUD-001`, `HUD-002` özelliklerinin yalnız temel uçuş bağlamı | L1 Aviator eğitimini ve mezuniyetini bloklar. |
| ADVANCED | `AAR-*`, `STO-001`-`STO-019`, `FCR-*`, `DLK-*`, `TGP-*`, `HTS-*`, `HMC-*`, `AA-*`, `AG-*`, `DEF-*`, `FRM-*`, `TAC-010`-`TAC-018`; HOTAS/HUD’nin bu sistemlere ait bağlamsal işlevleri | L2/L3 dalları açılınca eğitilir. |
| OPTIONAL | Yukarıdaki kurallara girmeyen `CPT-*`, `UFC-*`, `MFD-*`, `DTE-*`, `APL-*`, `INS-*`, `NAV-*`, `TAC-*`, `ILS-*`, `COM-*`, `MPS-*`, `AVI-*` ve kalan prosedürler | İhtiyaca göre FSM/BC/hybrid olarak eklenir; L1’i bloklamaz. |

`HOT-001`, `HOT-002`, `HUD-001` ve `HUD-002` birleşik satırlardır: temel uçuş alt işlevleri CORE, sensör/sanal görev alt işlevleri ilgili tüketici modül kadar ADVANCED kabul edilir.

### Yöntem yönlendirme kuralları

| Feature ailesi | Varsayılan yöntem |
|---|---|
| `FLT-*`, `AAR-*`, `FRM-*` | RL |
| `PRC-*` ve checklist ağırlıklı cockpit işleri | behavior cloning + FSM; belirsiz abort/continue kararı RL |
| `UFC-*`, `DTE-*`, veri girişi ve mode initialization | deterministik FSM/script |
| `FCR-*`, `TGP-*`, `HTS-*`, `DLK-*`, `DEF-*` | deterministik konfigürasyon + RL tracking/decision |
| `AA-*`, `AG-*`, `TAC-*` | hiyerarşik hybrid; safety/ROE hard constraint |

## 1. Ortam ve temel uçuş

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| FLT-001 | Pitch kontrolü | 25-26 | M01.2/M01.5-M01.8 | TBD |
| FLT-002 | Roll kontrolü | 25-27 | M01.1/M01.3-M01.4 | TBD |
| FLT-003 | Yaw/rudder kontrolü | 25-27 | M01.4/M01.8 | TBD |
| FLT-004 | Throttle ve afterburner/idle detent | 25-26 | M01.5-M01.9/M02.6 | TBD |
| FLT-005 | Güçle hız değiştirme | 26 | M01.6/M01.9 | TBD |
| FLT-006 | Pitch/AoA ile hız değiştirme | 26 | M01.6/M01.9-M01.10 | TBD |
| FLT-007 | Speedbrake ile hız değiştirme | 26 | M01.9 | TBD |
| FLT-008 | Gear sürüklemesi ve 300 knot limiti | 26 | M01.9/M01.12 | TBD |
| FLT-009 | Tırmanış ve irtifa artırma | 26 | M01.7 | TBD |
| FLT-010 | Alçalış ve irtifa azaltma | 26 | M01.7 | TBD |
| FLT-011 | Heading/bank/koordineli dönüş | 27 | M01.4 | TBD |
| FLT-012 | Enerji, turn rate ve stall marjı yönetimi | 27, 276-278 | M01.9-M01.10/M18.2 | TBD |

## 2. Stores, kokpit ve insan-makine arayüzü

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| STO-001 | M61A1 Vulcan 20 mm | 34 | M14.2/M15.2 | TBD |
| STO-002 | AIM-9 Sidewinder ailesi | 34 | M14.3-M14.5 | TBD |
| STO-003 | AIM-120 AMRAAM | 35 | M14.6-M14.10 | TBD |
| STO-004 | AGM-88 HARM | 35 | M15.10-M15.11 | TBD |
| STO-005 | AGM-65 Maverick | 36 | M15.12-M15.14 | TBD |
| STO-006 | Mark 80 genel maksat bombaları | 36 | M15.4-M15.5 | TBD |
| STO-007 | BDU-50 eğitim mühimmatı | 37 | M15.4-M15.5 | TBD |
| STO-008 | BDU-33 eğitim mühimmatı | 37 | M15.4-M15.5 | TBD |
| STO-009 | CBU-87 | 37 | M15.4-M15.5 | TBD |
| STO-010 | CBU-97 | 38 | M15.4-M15.5 | TBD |
| STO-011 | Paveway II | 38 | M15.6 | TBD |
| STO-012 | Paveway III | 39 | M15.6 | TBD |
| STO-013 | JDAM | 39 | M15.7 | TBD |
| STO-014 | AGM-154 JSOW | 40 | M15.8 | TBD |
| STO-015 | WCMD | 40 | M15.9 | TBD |
| STO-016 | 2.75-inch unguided rocket | 40 | M15.3 | TBD |
| STO-017 | External fuel tanks | 41 | M01.12/M00.4 | TBD |
| STO-018 | Targeting/sensor pods | 41 | M10/M12 | TBD |
| STO-019 | ALQ-131/184 ECM pods | 42 | M17.5 | TBD |
| STO-020 | AN/ASQ-T50 TCTS pod | 42 | M00.4 | TBD |
| STO-021 | MXU-648 travel pod | 42 | M00.4 | TBD |
| CPT-001 | AoA indexer | 44 | M02.1 | TBD |
| CPT-002 | Air-refuel status/NWS indicator | 45 | M02.1/M04.5 | TBD |
| CPT-003 | Sol eyebrow ikaz ışıkları | 45 | M02.1 | TBD |
| CPT-004 | Sağ eyebrow ikaz ışıkları | 46 | M02.1 | TBD |
| CPT-005 | MISC panel | 47 | M02.1 | TBD |
| CPT-006 | RF switch | 48 | M02.1/M09.1 | TBD |
| CPT-007 | Standby attitude indicator | 49 | M02.1 | TBD |
| CPT-008 | Fuel flow indicator | 50 | M02.1 | TBD |
| CPT-009 | Engine instruments | 50 | M02.1/M03.1 | TBD |
| CPT-010 | Airspeed/Mach indicator | 51 | M02.1 | TBD |
| CPT-011 | Altimeter | 51 | M02.1 | TBD |
| CPT-012 | AoA indicator | 52 | M02.1 | TBD |
| CPT-013 | Vertical velocity indicator | 52 | M02.1 | TBD |
| CPT-014 | Attitude director indicator | 53 | M02.1/M06.4 | TBD |
| CPT-015 | FUEL QTY SEL panel | 54 | M02.1 | TBD |
| CPT-016 | Landing gear panel | 55-56 | M02.2/M04 | TBD |
| CPT-017 | HMCS control panel | 57 | M02.2/M13 | TBD |
| CPT-018 | Alternate landing gear handle | 57 | M02.2/M04 | TBD |
| CPT-019 | Magnetic compass | 58 | M02.2/M05 | TBD |
| CPT-020 | Fuel quantity indicator | 58 | M02.2 | TBD |
| CPT-021 | Pilot Fault List Display | 59 | M02.2/M03.6 | TBD |
| CPT-022 | Caution light panel | 59-60 | M02.2/M03.6 | TBD |
| CPT-023 | Hydraulic pressure A/B | 61 | M02.2 | TBD |
| CPT-024 | EPU fuel quantity | 61 | M02.2 | TBD |
| CPT-025 | Cabin pressure | 61 | M02.2 | TBD |
| CPT-026 | Mechanical clock | 61 | M02.2 | TBD |
| CPT-027 | Manual pitch override | 62 | M02.3 | TBD |
| CPT-028 | Engine & jet start panel | 63 | M02.3/M03.1 | TBD |
| CPT-029 | EPU control panel | 64 | M02.3 | TBD |
| CPT-030 | Electrical control panel | 64 | M02.3/M03.1 | TBD |
| CPT-031 | AUDIO 1/AUDIO 2 panels | 65 | M02.3/M06.5 | TBD |
| CPT-032 | AVTR control panel | 66 | M02.3 | TBD |
| CPT-033 | Fuel control panel | 67 | M02.3 | TBD |
| CPT-034 | IFF control panel | 67-68 | M02.3/M09.8 | TBD |
| CPT-035 | Exterior lighting panel | 69-70 | M02.3/M03 | TBD |
| CPT-036 | Flight control panel | 71 | M02.3 | TBD |
| CPT-037 | Manual trim panel | 72 | M02.3 | TBD |
| CPT-038 | Test panel | 72-73 | M02.3/M03.1 | TBD |
| CPT-039 | Canopy switch/handle | 73 | M02.3/M03.1 | TBD |
| CPT-040 | Canopy jettison T-handle | 74 | M02.3/M03.6 | TBD |
| CPT-041 | Defog lever | 74 | M02.3 | TBD |
| CPT-042 | Sensor power panel | 75 | M02.4/M09-M12 | TBD |
| CPT-043 | Interior lighting panel | 76 | M02.4 | TBD |
| CPT-044 | Air-conditioning panel | 76 | M02.4 | TBD |
| CPT-045 | KY-58 secure voice panel | 77 | M02.4/M06.5 | TBD |
| CPT-046 | Plain/cipher switch | 77 | M02.4/M06.5 | TBD |
| CPT-047 | Oxygen regulator | 77-78 | M02.4 | TBD |
| CPT-048 | Anti-ice ve antenna select | 78 | M02.4 | TBD |
| CPT-049 | Avionics power panel | 78-79 | M02.4/M03.1 | TBD |
| CPT-050 | Voice message switch | 80 | M02.4 | TBD |
| CPT-051 | Zeroize switch | 80 | M02.4/M03.6 | TBD |
| CPT-052 | Seat adjustment | 80 | M02.4 | TBD |
| CPT-053 | Nuclear consent switch - güvenli/no-action kapsamı | 80 | M02.4 | knowledge |
| CPT-054 | Ejection handle | 81 | M02.5 | TBD |
| CPT-055 | Ejection seat arming lever | 81 | M02.5 | TBD |
| CPT-056 | Emergency manual chute lever | 82 | M02.5 | TBD |
| HOT-001 | Side Stick Controller üzerindeki bütün bağlamsal işlevler | 83-85, 755-761 | M02.6 | TBD |
| HOT-002 | Throttle üzerindeki bütün bağlamsal işlevler | 86-89, 755-761 | M02.6 | TBD |
| HUD-001 | HUD uçuş/navigasyon/taktik sembolleri | 90-93 | M02.7 | TBD |
| HUD-002 | HUD control panel | 94-97 | M02.7 | TBD |
| UFC-001 | ICP veri girişi | 99-100 | M02.8 | TBD |
| UFC-002 | CNI DED page | 103 | M02.8 | TBD |
| UFC-003 | UHF DED page | 104 | M02.8/M06.5 | TBD |
| UFC-004 | VHF DED page | 104 | M02.8/M06.5 | TBD |
| UFC-005 | IFF DED page | 105 | M02.8/M09.8 | TBD |
| UFC-006 | LIST DED page | 105 | M02.8 | TBD |
| UFC-007 | ALOW DED page | 107 | M02.8 | TBD |
| UFC-008 | CRUS TOS page | 108-109 | M02.8 | TBD |
| UFC-009 | CRUS RNG page | 110-111 | M02.8 | TBD |
| UFC-010 | CRUS HOME page | 112-113 | M02.8 | TBD |
| UFC-011 | CRUS EDR page | 114-115 | M02.8 | TBD |
| UFC-012 | TIME DED page | 116 | M02.8 | TBD |
| UFC-013 | BNGO DED page | 118 | M02.8 | TBD |
| UFC-014 | MAN DED page | 119 | M02.8 | TBD |
| UFC-015 | MODE DED page | 120 | M02.8 | TBD |
| UFC-016 | MISC DED pages | 121 | M02.8 | TBD |
| MFD-001 | MFD master menu/format selection | 122-125 | M02.9 | TBD |
| MFD-002 | MFD format reassignment | 126 | M02.9 | TBD |
| DTE-001 | DTE MFD format ve data transfer | 127-128 | M02.10/M07 | TBD |
| APL-001 | Autopilot controls/settings | 129-131 | M02.11/M06.7 | TBD |
| APL-002 | Autopilot engage/disengage | 131-132 | M02.11/M06.7 | TBD |

## 3. Prosedürler, seyrüsefer ve haberleşme

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| PRC-001 | Before engine start | 135 | M03.1 | TBD |
| PRC-002 | Engine start | 136 | M03.1 | TBD |
| PRC-003 | After engine start | 137-140 | M03.1 | TBD |
| PRC-004 | Before taxi | 142 | M03.3 | TBD |
| PRC-005 | Taxi/NWS/braking | 142 | M03.3 | TBD |
| PRC-006 | Before takeoff | 144-145 | M04.1 | TBD |
| PRC-007 | Normal takeoff | 146 | M04.1 | TBD |
| PRC-008 | Crosswind takeoff | 147 | M04.2 | TBD |
| PRC-009 | Descent/before landing | 149 | M04.3 | TBD |
| PRC-010 | Overhead break | 150-152 | M04.3 | TBD |
| PRC-011 | Normal landing | 153 | M04.3 | TBD |
| PRC-012 | Crosswind landing | 154 | M04.4 | TBD |
| PRC-013 | After landing | 156 | M03.4 | TBD |
| PRC-014 | Engine shutdown | 157 | M03.4 | TBD |
| PRC-015 | Ground support | 158 | M03.5 | TBD |
| PRC-016 | Hot refuel/rearm | 159 | M03.5 | TBD |
| AAR-001 | Tanker approach/rendezvous | 161 | M04.5 | TBD |
| AAR-002 | Pre-refueling checklist | 161 | M04.5 | TBD |
| AAR-003 | Pre-contact position | 162 | M04.5 | TBD |
| AAR-004 | Contact position ve transfer | 163-164 | M04.6 | TBD |
| AAR-005 | Breakaway | 165 | M04.7 | TBD |
| AAR-006 | Post-refueling checklist | 165 | M04.7 | TBD |
| INS-001 | INS initialization/DED ve coarse-fine kalite | 169-171 | M05.1 | TBD |
| INS-002 | INFLT ALGN DED | 172 | M05.4 | TBD |
| INS-003 | MAGV DED | 173 | M05.2 | TBD |
| INS-004 | Normal gyrocompass alignment | 174-175 | M05.2 | TBD |
| INS-005 | AUTO-NAV/NARF/resume/accept | 175 | M05.2 | TBD |
| INS-006 | Stored heading alignment/interruption/accept | 176 | M05.3 | TBD |
| INS-007 | GPS-aided inflight alignment | 177 | M05.4 | TBD |
| INS-008 | GPS-denied inflight alignment | 178 | M05.4 | TBD |
| INS-009 | Attitude mode ve kalite | 179 | M05.4 | TBD |
| NAV-001 | NAV STATUS DED | 181 | M05.5 | TBD |
| NAV-002 | NAV COMMANDS DED | 182 | M05.5 | TBD |
| NAV-003 | System altitude/DTS | 183-185 | M05.5 | TBD |
| NAV-004 | AUTO ACAL | 186-187 | M05.5 | TBD |
| NAV-005 | Cursor-slew navigation correction | 189 | M05.6 | TBD |
| NAV-006 | Position fix / FIX DED | 190, 192-193 | M05.6 | TBD |
| NAV-007 | Altitude calibration / MAN ACAL | 191, 198-199 | M05.6 | TBD |
| NAV-008 | HUD position fix | 194 | M05.7 | TBD |
| NAV-009 | FCR position fix | 195 | M05.7 | TBD |
| NAV-010 | TGP position fix | 196 | M05.7 | TBD |
| NAV-011 | OFLY position fix | 197 | M05.7 | TBD |
| NAV-012 | RALT altitude calibration | 200 | M05.7 | TBD |
| NAV-013 | FCR altitude calibration | 201 | M05.7 | TBD |
| NAV-014 | HUD altitude calibration | 202 | M05.7 | TBD |
| NAV-015 | TGP altitude calibration | 203 | M05.7 | TBD |
| NAV-016 | Navigation/mark/threat/datalink/destination/SEAD steerpoint türleri | 205-206 | M05.8 | TBD |
| NAV-017 | STPT DED ve MGRS format | 207-208 | M05.8 | TBD |
| NAV-018 | UTM DEST / DEST DIR / OA1-OA2 | 209-211 | M05.8 | TBD |
| NAV-019 | Steerpoint edit | 212-213 | M05.9 | TBD |
| NAV-020 | Offset aimpoint edit | 214 | M05.9 | TBD |
| NAV-021 | MGRS -> latitude/longitude dönüşümü | 215-218 | M05.9 | TBD |
| NAV-022 | MARK DED | 219-220 | M05.10 | TBD |
| NAV-023 | HUD markpoint | 221 | M05.10 | TBD |
| NAV-024 | HMCS markpoint | 222 | M05.10 | TBD |
| NAV-025 | FCR markpoint | 223 | M05.10 | TBD |
| NAV-026 | TGP markpoint | 224 | M05.10 | TBD |
| NAV-027 | OFLY markpoint ve manual edit | 225 | M05.10 | TBD |
| NAV-028 | Rota oluşturma | 227 | M05.11/M07 | TBD |
| NAV-029 | HUD/HSD/EHSI route navigation | 228-233 | M05.11 | TBD |
| NAV-030 | Steerpoint selection | 234 | M05.11 | TBD |
| TAC-001 | TACAN tuning/identification | 236-237 | M06.1 | TBD |
| TAC-002 | TACAN radial/EHSI TCN navigation | 238-239 | M06.1 | TBD |
| TAC-003 | Air-to-air TACAN | 240 | M06.2 | TBD |
| ILS-001 | ILS localizer tuning/identification | 242-243 | M06.3 | TBD |
| ILS-002 | Glideslope intercept/descent | 244-245 | M06.3 | TBD |
| ILS-003 | Decision height | 246 | M06.3 | TBD |
| ILS-004 | EHSI PLS / ADI / HUD low-visibility approach | 246-248 | M06.4 | TBD |
| COM-001 | Communications management | 251-252 | M06.5 | TBD |
| COM-002 | UHF preset tuning/edit/manual tuning | 253-259 | M06.5 | TBD |
| COM-003 | VHF preset tuning/edit/manual tuning | 255-259 | M06.5 | TBD |
| COM-004 | UHF backup preset/manual tuning | 260-262 | M06.6 | TBD |
| COM-005 | HOTAS radio controls | 263 | M06.5 | TBD |
| COM-006 | Easy communication eşdeğeri | 263 | M06.6 | TBD |

## 4. Taktik arayüz, görev planlama ve FCR

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| TAC-010 | BVR detection/commit/engagement/defense | 266-272 | M18.1 | TBD |
| TAC-011 | WVR positional/attack geometry | 273-275 | M18.2 | TBD |
| TAC-012 | Turn rate vs turn radius ve merge | 276-281 | M18.2 | TBD |
| TAC-013 | Engaged/supporting fighter rolleri | 282-283 | M16.3 | TBD |
| TAC-014 | A-G objective/threat/terrain/weather analizi | 284-285 | M18.3 | TBD |
| TAC-015 | High-altitude level/dive profilleri | 285-286 | M18.4 | TBD |
| TAC-016 | Low-altitude level-retarded/pop-up profilleri | 287-288 | M18.5 | TBD |
| TAC-017 | Toss ve missile/glide-bomb standoff profilleri | 288-289 | M18.6 | TBD |
| TAC-018 | Ingress/egress ve fence check | 290-292 | M18.7 | TBD |
| FRM-001 | Line abreast | 293 | M16.1 | TBD |
| FRM-002 | Trail | 294 | M16.1 | TBD |
| FRM-003 | Wedge | 294 | M16.1 | TBD |
| FRM-004 | Echelon left/right | 294 | M16.1 | TBD |
| FRM-005 | Finger four | 295 | M16.1 | TBD |
| FRM-006 | Spread four | 295 | M16.1 | TBD |
| MPS-001 | DTC Manager/Mission Editor/load-to-group/DTC tab | 297-301 | M07.1 | TBD |
| MPS-002 | MPD NAV PTS | 302-304 | M07.2 | TBD |
| MPS-003 | GEO LINES | 305-306 | M07.2 | TBD |
| MPS-004 | THREAT PTS | 307-308 | M07.2 | TBD |
| MPS-005 | DEST PTS | 309-310 | M07.2 | TBD |
| MPS-006 | ROE | 311 | M07.2 | TBD |
| MPS-007 | CMDS | 312-313 | M07.2 | TBD |
| MPS-008 | NAV RTE 1-3 | 314-315 | M07.3 | TBD |
| MPS-009 | VIP/VRP planlama | 316-317 | M07.3 | TBD |
| MPS-010 | COMM 1/2 | 318-319 | M07.4 | TBD |
| MPS-011 | RWR threat table | 320-321 | M07.5 | TBD |
| MPS-012 | MFD/FCR, HSD/HAD, MISC renk/sembol ayarları | 322-324 | M07.6 | TBD |
| AVI-001 | NAV/A-A/A-G master modes | 326-328 | M08.1 | TBD |
| AVI-002 | MSL/DGFT override modes | 328-329 | M08.1 | TBD |
| AVI-003 | Selective/emergency JETT modes | 329-330 | M08.1/M08.11 | TBD |
| AVI-004 | SSC ile MFD format cycling | 330 | M08.2 | TBD |
| AVI-005 | Sensor of Interest | 331 | M08.2 | TBD |
| AVI-006 | SPI: preplanned/visual/pipper/airborne target | 332-334 | M08.3 | TBD |
| AVI-007 | PRE/VIS delivery submodes | 335-343 | M08.4 | TBD |
| AVI-008 | STP/TGT, OA1/OA2, IP, RP sighting points | 338-339 | M08.4 | TBD |
| AVI-009 | Navigation/VIP/VRP/mark/HMCS/visual/snowplow cursors | 340-341 | M08.5 | TBD |
| AVI-010 | Cursor Zero / hands-on CZ | 341 | M08.5 | TBD |
| AVI-011 | Snowplow pre/post-designate | 342-343 | M08.6 | TBD |
| AVI-012 | VRP, TGT-to-VRP/PUP, overflight/cursor alignment | 344-350 | M08.7 | TBD |
| AVI-013 | VIP, VIP-to-TGT/PUP ve overflight | 351-355 | M08.8 | TBD |
| AVI-014 | Bullseye/BULL DED | 356-357 | M08.9 | TBD |
| AVI-015 | HSD format/CNTL/EXP/zoom | 358-365 | M08.10 | TBD |
| AVI-016 | SMS inventory ve store codes | 366-368 | M08.11 | TBD |
| AVI-017 | SMS selective jettison | 369-371 | M08.11 | TBD |
| AVI-018 | SMS emergency jettison | 372 | M08.11 | TBD |
| FCR-001 | Activation/STBY/OVRD/RF switch | 375, 407 | M09.1 | TBD |
| FCR-002 | Slew/track/display/bar scan/mini-search | 377-380 | M09.2 | TBD |
| FCR-003 | Azimuth/range/elevation/spotlight | 381-383 | M09.2 | TBD |
| FCR-004 | Space/body stabilization | 384 | M09.3 | TBD |
| FCR-005 | Pulse/pulse-Doppler/detection/scan frame/jamming | 385-393 | M09.3 | TBD |
| FCR-006 | A-A/A-G format, menu, CNTL, symbols, TOI | 394-405 | M09.4 | TBD |
| FCR-007 | RWS | 410-411 | M09.5 | TBD |
| FCR-008 | VSR | 412 | M09.5 | TBD |
| FCR-009 | TWS system/cursor/bugged targets ve TMS | 413-416 | M09.5 | TBD |
| FCR-010 | SAM/DT SAM/DTT/STT/EXP | 417-422 | M09.6 | TBD |
| FCR-011 | ACM 30x20 | 425 | M09.7 | TBD |
| FCR-012 | ACM 10x60 | 426 | M09.7 | TBD |
| FCR-013 | BORE/HMCS-cued BORE | 427-428 | M09.7/M13.4 | TBD |
| FCR-014 | ACM SLEW | 429-430 | M09.7 | TBD |
| FCR-015 | NCTR symbols/codes | 431-432 | M09.8 | TBD |
| FCR-016 | AIFF | 433-435 | M09.8 | TBD |
| FCR-017 | GM/EXP/DBS1/DBS2/freeze/FTT | 437-444 | M09.9 | TBD |
| FCR-018 | GMT/GMTT | 445-447 | M09.10 | TBD |
| FCR-019 | SEA | 448 | M09.10 | TBD |
| FCR-020 | AGR | 449 | M09.10 | TBD |

## 5. Datalink, TGP, HTS ve HMCS

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| DLK-001 | Fighter/Mission channel | 453-455 | M11.1 | TBD |
| DLK-002 | Fighter-to-fighter ve surveillance/C2 mesajları | 456-457 | M11.1 | TBD |
| DLK-003 | MIDS initialization; NET STATUS/TNDL/STN DED | 458-461 | M11.2 | TBD |
| DLK-004 | Manuel sync ve ownship/flight-team settings | 462-466 | M11.3 | TBD |
| DLK-005 | PPLI | 468 | M11.4 | TBD |
| DLK-006 | STF ve onboard/offboard/TN correlation | 469-470 | M11.4 | TBD |
| DLK-007 | ATDT/fighter/surveillance tracks | 471-475 | M11.4-M11.5 | TBD |
| DLK-008 | PDLT ve FCR declutter | 476-478 | M11.5 | TBD |
| DLK-009 | Steerpoint veya FCR/TGP SPI markpoint gönderme/alma | 479-481 | M11.6 | TBD |
| DLK-010 | SEAD target gönderme/alma | 482-483 | M11.7 | TBD |
| TGP-001 | Activation/STBY/OVRD | 486, 504 | M10.1 | TBD |
| TGP-002 | FLIR/TV/PIP/variable-XR zoom | 487-488 | M10.1 | TBD |
| TGP-003 | Area/point/inertial track | 489-491 | M10.2 | TBD |
| TGP-004 | Sensor management/XR processing/orientation | 492-494 | M10.3 | TBD |
| TGP-005 | TGP format/menu/CNTL/LASR DED | 495-503 | M10.3-M10.4 | TBD |
| TGP-006 | A-G multi-target add/select/slew/delete | 505-509 | M10.5 | TBD |
| TGP-007 | Manual/automatic laser range/designate | 510-511 | M10.4 | TBD |
| TGP-008 | Laser Spot Tracker/acquisition | 512-515 | M10.6 | TBD |
| TGP-009 | IR pointer | 516 | M10.7 | TBD |
| TGP-010 | MASK/CHECK ATTITUDE advisory | 517 | M10.8 | TBD |
| TGP-011 | A-A mode, MT, laser range, AIM-9 slave | 518-522 | M10.9 | TBD |
| HTS-001 | Activation/slew/designate | 525-526 | M12.1 | TBD |
| HTS-002 | Radio direction finding/triangulation/AOA | 527-528 | M12.2 | TBD |
| HTS-003 | TDOA geolocation/master/slave | 529 | M12.3 | TBD |
| HTS-004 | HAD/THRT/CNTL/EXP/HTS DED | 530-538 | M12.4 | TBD |
| HTS-005 | AOA/TDOA ranging ve SEAD DED | 539-544 | M12.5 | TBD |
| HTS-006 | TDOA sub-team/master/slave procedure | 545-546 | M12.6 | TBD |
| HMC-001 | HMCS activation ve symbology | 549-551 | M13.1 | TBD |
| HMC-002 | HMCS display/align settings | 552-554 | M13.2 | TBD |
| HMC-003 | HMCS alignment | 555 | M13.3 | TBD |

## 6. Hava-hava ve hava-yer sanal kullanım

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| AA-001 | Air-combat preparation/master mode | 558-559 | M14.1 | TBD |
| AA-002 | M61 EEGS symbology/SMS | 560-566 | M14.2 | TBD |
| AA-003 | Gun Level 5 FCR solution | 567 | M14.2 | TBD |
| AA-004 | Gun Level 2 visual solution | 568 | M14.2 | TBD |
| AA-005 | AIM-9P/P3, L/M/P5, X varyantları | 569-570 | M14.3 | TBD |
| AA-006 | AIM-9 SLAVE/BORE cueing | 571 | M14.3 | TBD |
| AA-007 | SRM HUD/HMCS/MFD/audio/SMS | 572-581 | M14.4 | TBD |
| AA-008 | AIM-9 SLAVE FCR cue | 582-583 | M14.5 | TBD |
| AA-009 | AIM-9 SLAVE TGP cue | 584-585 | M14.5 | TBD |
| AA-010 | AIM-9 BORE HMCS cue | 586-587 | M14.5 | TBD |
| AA-011 | AIM-9 BORE no cue | 588-589 | M14.5 | TBD |
| AA-012 | AIM-120 guidance ve SLAVE/BORE | 590-592 | M14.6 | TBD |
| AA-013 | MRM HUD/HMCS/MFD/SMS | 593-600 | M14.6 | TBD |
| AA-014 | AIM-120 single-target SAM/STT | 601-602 | M14.7 | TBD |
| AA-015 | AIM-120 dual-target DT SAM/DTT | 603-604 | M14.8 | TBD |
| AA-016 | AIM-120 multi-target TWS | 605-606 | M14.9 | TBD |
| AA-017 | AIM-120 visual BORE | 607 | M14.10 | TBD |
| AG-001 | Attack preparation | 609 | M15.1 | TBD |
| AG-002 | M61 strafe/in-range cue | 610-613 | M15.2 | TBD |
| AG-003 | 2.75-inch rocket CCIP | 614-616 | M15.3 | TBD |
| AG-004 | GP/cluster/training bomb ve SMS | 617-622 | M15.4 | TBD |
| AG-005 | Unguided bomb CCIP | 623-625 | M15.5 | TBD |
| AG-006 | CCIP post-designate | 626-627 | M15.5 | TBD |
| AG-007 | Unguided bomb CCRP | 628-630 | M15.5 | TBD |
| AG-008 | Laser code/SMS/Paveway CCRP | 631-638 | M15.6 | TBD |
| AG-009 | JDAM SMS/CNTL/HUD/PRE/VIS | 639-645 | M15.7 | TBD |
| AG-010 | JSOW SMS/HUD/PRE/VIS | 646-650 | M15.8 | TBD |
| AG-011 | WCMD SMS/HUD/CNTL/PRE/VIS | 651-656 | M15.9 | TBD |
| AG-012 | HARM preparation/DED/SMS/WPN/HUD | 657-664 | M15.10 | TBD |
| AG-013 | HARM HAS | 665-667 | M15.11 | TBD |
| AG-014 | HARM POS EOM/PB/RUK | 668-670 | M15.11 | TBD |
| AG-015 | Maverick operation/limitations/SMS/CNTL/WPN | 671-674 | M15.12 | TBD |
| AG-016 | Maverick automatic power-on/boresight | 675-680 | M15.12-M15.13 | TBD |
| AG-017 | Maverick PRE | 681-682 | M15.13 | TBD |
| AG-018 | Maverick VIS | 683-684 | M15.13 | TBD |
| AG-019 | Maverick BORE | 685-686 | M15.13 | TBD |
| AG-020 | Maverick TGP handoff | 687 | M15.14 | TBD |
| AG-021 | Maverick ripple fire | 687-689 | M15.14 | TBD |
| AG-022 | Maverick force correlate | 690-691 | M15.14 | TBD |

## 7. Savunma ve referans ekleri

| Feature ID | Kılavuz özelliği | Sayfa | Müfredat | Durum |
|---|---|---:|---|---|
| DEF-001 | RWR/TWAI | 693-694 | M17.1 | TBD |
| DEF-002 | Threat Warning Prime panel | 695 | M17.1 | TBD |
| DEF-003 | Threat Warning Auxiliary panel/handoff | 696 | M17.1 | TBD |
| DEF-004 | CMDS control panel | 697-699 | M17.3 | TBD |
| DEF-005 | CMDS BINGO | 700 | M17.3-M17.4 | TBD |
| DEF-006 | CMDS CHAFF/FLARE DED | 701 | M17.3-M17.4 | TBD |
| DEF-007 | CMDS OTHER1/OTHER2 DED | 702 | M17.3 | TBD |
| DEF-008 | Radar jamming/noise/deception | 703-704 | M17.5 | TBD |
| DEF-009 | Burnthrough ve ECM uygulama kararı | 705 | M17.5-M17.6 | TBD |
| DEF-010 | ECM control panel | 706-707 | M17.5 | TBD |
| DEF-011 | HOTAS chaff/flare dispense | 708 | M17.4 | TBD |
| REF-001 | Kısaltılmış start/taxi/takeoff/landing/shutdown checklistleri | 712-719 | M03/M04 | reference |
| REF-002 | Kısaltılmış navigation/INS/TACAN/ILS checklistleri | 720-729 | M05/M06 | reference |
| REF-003 | Kısaltılmış radio checklistleri | 730-731 | M06 | reference |
| REF-004 | Kısaltılmış datalink/SEAD checklistleri | 732-736 | M11/M12 | reference |
| REF-005 | Kısaltılmış combat checklistleri | 737-748 | M14/M18 | reference |
| REF-006 | ALIC air-defense radar symbols | 749 | M17.2 | reference |
| REF-007 | ALIC naval radar symbols | 750 | M17.2 | reference |
| REF-008 | ALIC airborne radar symbols | 751 | M17.2 | reference |
| REF-009 | Other threat symbols | 752 | M17.2 | reference |
| REF-010 | HAD threat classes | 753 | M12.4/M17.2 | reference |
| REF-011 | AGM-88 WPN threat tables | 754 | M15.10-M15.11 | reference |
| REF-012 | HOTAS A-A/MSL/DGFT, SOI=FCR | 755 | M02.6/M09/M14 | reference |
| REF-013 | HOTAS A-G SOI=FCR | 756 | M02.6/M09/M15 | reference |
| REF-014 | HOTAS A-G SOI=HUD | 757 | M02.6/M08/M15 | reference |
| REF-015 | HOTAS A-G SOI=HSD | 758 | M02.6/M08/M11 | reference |
| REF-016 | HOTAS A-G SOI=HAD | 759 | M02.6/M12/M15 | reference |
| REF-017 | HOTAS A-G SOI=TGP | 760 | M02.6/M10/M15 | reference |
| REF-018 | HOTAS A-G SOI=WPN | 761 | M02.6/M15 | reference |
| REF-019 | Glossary | 762-772 | Tüm modüller | knowledge |
| REF-020 | Formulas | 773-774 | M00/Metrikler | reference |

## 8. Kapsam dışı olmayan, fakat politika eylemi olmayan bölümler

Kılavuzdaki Introduction, Aircraft History ve DCS’ye özgü kurulum/destek bağlantıları silinmemiştir. Bunlar sırasıyla kapsam/provenans ve ortam kurulumu bilgisi olarak izlenir; ajanın uçuş politikasında ayrı motor becerisi değildir. Çok oyunculu kullanım, görev/campaign editor ve harita çeşitliliği, belirli DCS ürün özellikleri olarak değil M00 senaryo üretimi, M16 çok-ajan ve M19 genelleme gereksinimlerine dönüştürülmüştür.

## 9. JSBSim capability audit sonrası kapanış kontrolü

1. Her `TBD` satırını `native`, `adapted` veya `missing` yap.
2. `missing` satırları için eşdeğer davranış ekleme maliyeti ve gerçekçilik sınırı çıkar.
3. Her `native/adapted` satırı bir gözlem, eylem ve ölçüm alanına bağla.
4. Her feature ID için en az bir tek-beceri testi ve bir bileşik görev testi oluştur.
5. Kılavuzdaki prosedür/checklist ile test oracle’ını karşılaştır.
6. Tüm satırlar kapanmadan “kılavuz kapsamı tamam” iddiasında bulunma.
7. Yalnız FlightGear’da görünen hiçbir satırı `native/adapted` olarak kapatma.
