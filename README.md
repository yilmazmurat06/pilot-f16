# pilot-f16

F-16C Block 50 yeteneklerini JSBSim üzerinde eğitilen bir RL ajanına öğretmek için hazırlanan çalışma alanı. FlightGear yalnız görselleştirme ve debug içindir.

## Eğitim tasarımı

- [F-16C RL Eğitim Müfredatı](docs/F16C_RL_EGITIM_MUFREDATI.md)
- [Kılavuz Kapsam Matrisi](docs/F16C_KILAVUZ_KAPSAM_MATRISI.md)
- [JSBSim - FlightGear RL Mimarisi](docs/JSBSIM_FLIGHTGEAR_MIMARISI.md)

JSBSim tek yetkili fizik ve eğitim state’i kaynağıdır. FlightGear açık veya kapalıyken aynı seed/action dizisi aynı JSBSim sonucunu üretmelidir. İlk hedef, atomik uçuş kontrolünden kalkış-rota-inişe ilerleyen `L1 Aviator` modelidir; ileri aviyonik ve görev sistemleri daha sonraki `L2 Advanced Aviator` ve `L3 Mission Agent` dallarındadır.

## Başlangıç

Yerel ortam, kabul testleri ve ilk M01.1 PPO koşusu için
[kurulum ve ilk eğitim](docs/KURULUM_VE_ILK_EGITIM.md) belgesini izleyin.
