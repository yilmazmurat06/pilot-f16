# Kurulum ve ilk eğitim

Bu repo ilk aşamada müfredattaki `M00` ve `M01.1` hattını çalıştırır. Kullanılan
JSBSim `f16` modeli bir **F-16-like baseline** modelidir; doğrulanmış F-16C Block
50 modeli değildir. FlightGear yalnız görselleştirme/debug aracıdır.

## Windows kurulumu

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev,train]"
.\.venv\Scripts\python.exe -m pip install --force-reinstall --no-deps torch==2.13.0 `
  --index-url https://download.pytorch.org/whl/cu126
```

CUDA kurulumu:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Kabul ve smoke testleri

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\matplotlib"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts\smoke_env.py
```

## M01.1 eğitimini başlatma

Önce kısa doğrulama:

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\matplotlib"
.\.venv\Scripts\python.exe scripts\train_m01.py --steps 2048 `
  --output artifacts\m01_1_smoke
```

Ardından başlangıç eğitimi:

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\matplotlib"
.\.venv\Scripts\python.exe scripts\train_m01.py --steps 100000 `
  --output artifacts\m01_1_ppo
```

M01'in küçük vektör gözlemi ve MLP politikası için CPU varsayılandır. İleride
CNN veya daha büyük ağ kullanılırsa komuta `--device cuda` eklenebilir.

`artifacts/` deney çıktıları Git'e alınmaz. Frozen değerlendirme seti ve K1/K2
kapıları eklenmeden üretilen politika müfredat mezuniyeti sayılmaz.

## Değerlendirme ve FlightGear replay

```powershell
$env:MPLCONFIGDIR = "$PWD\.cache\matplotlib"
.\.venv\Scripts\python.exe scripts\evaluate_m01.py --episodes 200
.\.venv\Scripts\python.exe scripts\replay_flightgear.py
```

İlk komut `artifacts/evaluation_m01_1/report.json`, `telemetry.csv`,
`telemetry.png` ve deterministik episode eylemlerini taşıyan `replay.json`
dosyalarını üretir. Eğitilmiş politika aynı 200 senaryoda sıfır-eylem ve rastgele
politikalarla karşılaştırılır. İkinci komut
FlightGear'ı dış FDM modunda açar, aynı episode'u gerçek zamanlı yayınlar ve
replay bitince FlightGear'ı açık tutar.

Replay, tam FlightGear 2024.1.6 veri paketini
`external/flightgear-data/fgdata_2024_1` altında bekler. Yalnız Windows çekirdek
kurucusunun yüklenmesi yeterli değildir; script eşleşen `version` dosyasını
başlamadan önce kontrol eder.
Replay varsayılan olarak pencereyi inceleyebilmeniz için Enter'a basılana kadar
açık kalır. Otomatik kapanması istenirse komuta `--auto-close` eklenebilir.

## M01.2 pitch stabilization

```powershell
.\.venv\Scripts\python.exe scripts\train_m01.py --lesson M01.2 --steps 100000 `
  --output artifacts\m01_2_ppo
.\.venv\Scripts\python.exe scripts\evaluate_m01_2.py --episodes 200
.\.venv\Scripts\python.exe scripts\replay_flightgear.py `
  --replay artifacts\evaluation_m01_2\replay.json
```
