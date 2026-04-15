# 🏗️ AI-SafeBuild: Yapay Zeka Destekli Akıllı İSG İzleme Sistemi

Bu proje, inşaat sahalarında iş sağlığı ve güvenliğini (İSG) artırmak amacıyla geliştirilmiş **yapay zeka tabanlı bir görsel analiz ve izleme sisteminin prototipidir**.

Sistem, yüklenen görseller üzerinde **çalışan (person), baret (helmet) ve yelek (vest) tespiti** yaparak sahadaki güvenlik durumunu analiz eder ve sonuçları kullanıcıya **etkileşimli bir panel üzerinden sunar**.

---

## 🎯 Projenin Amacı

İnşaat sektöründe meydana gelen iş kazalarını azaltmak ve sahadaki güvenlik ihlallerini erken tespit etmek amacıyla:

* 👷 Çalışan tespiti yapmak
* 🪖 Kişisel koruyucu ekipman (KKE) kullanımını analiz etmek
* ⚠️ Risk seviyesini belirlemek
* 📊 Kullanıcıya hızlı ve anlaşılır geri bildirim sağlamak

Bu proje, TÜBİTAK 2209-A başvurusu kapsamında önerilen:

👉 **“Kubernetes Tabanlı Dijital İkiz Destekli Akıllı İş Sağlığı ve Güvenliği Yönetimi”**

başlıklı çalışmanın ilk teknik adımını oluşturmaktadır.

---

## 🧠 Proje Vizyonu (İSG 4.0)

Bu çalışma, geleneksel denetim yöntemlerinin yetersiz kaldığı dinamik şantiye ortamlarında:

* proaktif risk analizi yapmayı
* güvenlik ihlallerini erken tespit etmeyi
* veri odaklı karar destek sistemleri geliştirmeyi

hedeflemektedir.

Bu doğrultuda proje, aşağıdaki teknolojilerin birleşimini amaçlamaktadır:

* 🧠 Yapay Zeka (YOLOv8)
* 🧩 Mikroservis Mimarisi (MSP yaklaşımı)
* ☁️ Kubernetes tabanlı ölçeklenebilir altyapı
* 🧬 Dijital İkiz (Digital Twin)

---


## 🛠️ Kullanılan Teknolojiler

### Mevcut Sistem

* Python
* YOLOv8 (Ultralytics)
* OpenCV
* Streamlit
* Pandas & NumPy

---

### Hedeflenen Sistem Mimarisi

Bu prototip, aşağıdaki mimariye evrilecek şekilde tasarlanmıştır:

* Docker ile konteynerleştirme
* Kubernetes (K8s) ile orkestrasyon
* Mikroservis tabanlı modüler yapı
* API tabanlı entegrasyon katmanı

---

## 🧩 Entegrasyon Kullanım Alanları

Bu sistem yalnızca inşaat sahaları ile sınırlı değildir ve farklı alanlara uyarlanabilir:

* 🏗️ Şantiye izleme sistemleri
* 🏭 Endüstriyel güvenlik çözümleri
* 🖥️ MSP (Managed Service Provider) tabanlı izleme sistemleri
* 📹 Akıllı kamera ve gözetim uygulamaları

---

## 📊 Sistem Nasıl Çalışır?

1. Kullanıcı bir şantiye görseli yükler
2. Model görüntü üzerinde:

   * çalışanları (person)
   * baretleri (helmet)
   * yelekleri (vest) tespit eder
3. Tespit edilen nesneler analiz edilir
4. Eksik KKE durumları belirlenir
5. Risk seviyesi hesaplanır
6. Sonuçlar arayüzde gösterilir ve kayıt altına alınır

---

## ⚠️ Not

Bu proje, **sentetik veri ve görsel analiz teknikleri kullanılarak geliştirilmiş bir prototiptir**.

Gerçek saha verileri, IoT cihazları ve canlı sistem entegrasyonları, projenin ilerleyen aşamalarında planlanmaktadır.

---

## 🎯 Genel Amaç

👉 **Akıllı, otonom ve proaktif iş güvenliği sistemleri geliştirmek**

---
