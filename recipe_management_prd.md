# PRD - Aplikacja do Zarządzania Recepturami

## 1. Przegląd Produktu

### 1.1 Cel Produktu
Aplikacja webowa umożliwiająca zarządzanie recepturami produktów, pozwalająca na dodawanie, modyfikowanie i wyszukiwanie receptur wraz z kalkulacją składników dla określonych mas produktu.

### 1.2 Grupa Docelowa
Przedsiębiorstwa produkcyjne, laboratoria, kuchnie przemysłowe oraz inne organizacje zarządzające recepturami i składem produktów.

### 1.3 Kluczowe Korzyści
- Centralne zarządzanie recepturami produktów
- Hierarchiczne przeglądanie składu produktów
- Automatyczne przeliczanie ilości składników
- Intuicyjne wyszukiwanie produktów
- Kontrola poprawności receptur (suma 100%)

## 2. Wymagania Funkcjonalne

### 2.1 Model Danych

#### 2.1.1 Encja: Produkt
- **ID produktu** (identyfikator)
- **Nazwa produktu** (string)
- **Typ produktu** (enum):
  - Produkt standardowy
  - Komplet
  - Półprodukt
- **Jednostka produktu** (enum):
  - sztuka (szt)
  - gram (g)
- **Opis produktu** (string, opcjonalny)

#### 2.1.2 Encja: Receptura
- **ID receptury** (identyfikator)
- **ID produktu** (foreign key)
- **Lista składników**

#### 2.1.3 Encja: Składnik Receptury
- **ID produktu składnika** (foreign key)
- **Ilość** (float, > 0)
- **Jednostka** (enum):
  - sztuka (szt)
  - gram (g)
- **Kolejność** (integer)

### 2.2 Funkcjonalności Główne

#### 2.2.1 Dodawanie Nowej Receptury

**Przepływ użytkownika:**
1. Użytkownik wyszukuje istniejący produkt (sekcja 2.2.2)
2. Użytkownik otwiera szczegóły produktu bez receptury
3. Użytkownik klika przycisk "Dodaj recepturę"
4. System przekierowuje do strony definicji nowej receptury
5. System prezentuje dynamiczną tabelę do dodawania składników z podstawowymi informacjami o produkcie

**Strona definicji receptury:**
- Wyświetlenie informacji o produkcie (nazwa, ID)
- Edytowalny typ produktu (dropdown: standardowy/komplet/półprodukt)
- Edytowalna jednostka produktu (dropdown: sztuka/gram)
- Dynamiczną tabelę składników:
  - Kolumny: Składnik | Ilość | Jednostka | Akcje
  - Dodawanie wierszy: przycisk "Dodaj składnik"
  - Wyszukiwanie składników: fuzzy search z podpowiedziami
  - Pole ilości z walidacją (liczba > 0)
  - Wybór jednostki: sztuki lub gramy
  - Przycisk usuwania wiersza

**Walidacje:**
- Ilość > 0
- Minimum jeden składnik w recepturze
- Dla produktów z jednostką gram: suma składników powinna być logiczna (np. dla 1kg produktu)

**Przykłady receptur:**

*Przykład 1 - Ciasteczka do chrupania (jednostka: sztuka):*
- 1 szt - kubek papierowy
- 1 szt - przykrywka papierowa do kubka  
- 1 szt - opaska z logo firmy
- 1 szt - naklejka na wieczka ciastek
- 120 g - ciasteczka w luzie (półprodukt)

*Przykład 2 - Ciasteczka w luzie (jednostka: gram, dla 1kg produktu):*
- 400 g - mąka pszenna
- 200 g - masło
- 150 g - cukier
- 100 g - jajka
- 100 g - czekolada
- 50 g - przyprawy

#### 2.2.2 Wyszukiwanie Produktów/Receptur

**Interfejs wyszukiwania:**
- Pole tekstowe z fuzzy search
- Podpowiedzi w czasie rzeczywistym
- Wyszukiwanie po:
  - Nazwie produktu
  - Identyfikatorze produktu
  - Częściowych dopasowaniach

**Wyniki wyszukiwania:**
- Lista produktów z podstawowymi informacjami
- Oznaczenie czy produkt ma już recepturę
- Kliknięcie otwiera szczegóły produktu

#### 2.2.3 Przeglądanie Szczegółów Produktu

**Widok produktu bez receptury:**
- Identyfikator produktu
- Nazwa produktu
- Typ produktu
- Jednostka produktu
- Opis produktu
- Przycisk "Dodaj recepturę"

**Widok produktu z recepturą:**
- Podstawowe informacje o produkcie (w tym jednostka produktu)
- Tabelka składników:
  - Identyfikator składnika
  - Nazwa składnika
  - Ilość składnika
  - Jednostka (szt/g)
  - Typ składnika
  - Link/przycisk do rozwinięcia (dla półproduktów)

#### 2.2.4 Hierarchiczne Przeglądanie Składu

**Funkcjonalność:**
- Kliknięcie na półprodukt rozwija jego skład
- Wielopoziomowa hierarchia składników
- Wizualne oznaczenie poziomów zagnieżdeń
- Opcja zwijania/rozwijania węzłów

#### 2.2.5 Kalkulator Receptury

**Sekcja kalkulatora:**
- Pole wprowadzania ilości docelowej
- Jednostka przeliczenia automatycznie pobrana z definicji produktu (szt/g)
- Przycisk "Przelicz"

**Logika przeliczania:**

*Dla produktów w sztukach (jednostka produktu = szt):*
- Użytkownik wprowadza liczbę sztuk (np. 100 szt ciasteczek)
- System przelicza proporcjonalnie wszystkie składniki
- Przykład: receptura na 1 szt → 100 szt = 100× każdy składnik
- Wynik: 100 kubków + 100 przykrywek + 12kg ciasteczek w luzie

*Dla produktów w gramach (jednostka produktu = g):*
- Użytkownik wprowadza masę docelową (np. 5 kg = 5000g)
- System przelicza wszystkie składniki proporcjonalnie względem receptury bazowej
- Przykład: receptura na 1000g → 5000g = 5× każdy składnik
- Wynik: 2000g mąki + 1000g masła + 750g cukru...

**Wyniki kalkulacji:**
- Tabelka z przeliczonymi ilościami
- Kolumny: Składnik | Ilość bazowa | Jednostka | Ilość przeliczona
- Automatyczne przeliczenie po zmianie ilości
- Precyzja do 2 miejsc po przecinku dla gramów, liczby całkowite dla sztuk

#### 2.2.6 Modyfikacja Receptury

**Funkcjonalności:**
- Edycja istniejącej receptury
- Edycja typu produktu (dropdown: standardowy/komplet/półprodukt)
- Edycja jednostki produktu (dropdown: sztuka/gram)
- Dodawanie/usuwanie składników
- Zmiana ilości składników
- Zmiana jednostek składników
- Walidacja poprawności ilości (> 0)

## 3. Wymagania Niefunkcjonalne

### 3.1 Wydajność
- Czas odpowiedzi wyszukiwania: < 300ms
- Obsługa do 1000 produktów bez degradacji wydajności
- Responsywny interfejs na urządzeniach mobilnych

### 3.2 Użyteczność
- Intuicyjny interfejs użytkownika
- Minimalna liczba kliknięć do wykonania zadań
- Błędy walidacji wyświetlane w czasie rzeczywistym
- Potwierdzenia dla akcji destrukcyjnych

### 3.3 Techniczne
- Kompatybilność z przeglądarkami: Chrome, Firefox, Safari, Edge
- Responsywny design (Bootstrap/CSS Grid)
- Frontend: JavaScript/TypeScript
- Obsługa importu istniejącej bazy produktów

## 4. Interfejs Użytkownika

### 4.1 Struktura Nawigacji
- Strona główna/Dashboard
- Wyszukiwanie produktów
- Szczegóły produktu
- Definicja receptury
- Lista wszystkich produktów
- Import danych

### 4.2 Kluczowe Komponenty UI
- Pole wyszukiwania z autocomplete
- Dynamiczna tabela składników
- Modal do dodawania składników
- Hierarchiczny widok drzewa składników
- Kalkulator receptury
- Formularze walidacji

## 5. Import Danych

### 5.1 Wymagania
- Import istniejącej bazy produktów
- Obsługiwane formaty: CSV, JSON
- Mapowanie pól podczas importu
- Walidacja danych importowanych
- Raport z błędów importu

### 5.2 Struktura Importu
```json
{
  "products": [
    {
      "id": "string",
      "name": "string", 
      "type": "standard|kit|semi-product",
      "unit": "piece|gram",
      "description": "string"
    }
  ]
}
```

## 6. Walidacja i Kontrola Błędów

### 6.1 Walidacje Biznesowe
- Ilość składników > 0
- Unikalność identyfikatorów produktów
- Niepuste wymagane pola
- Poprawne jednostki (szt/g)
- Brak cyklicznych zależności w składnikach
- Logiczna suma składników (szczególnie dla produktów w gramach)

### 6.2 Komunikaty Błędów
- Jasne komunikaty walidacji
- Podświetlanie błędnych pól
- Sugestie naprawy błędów
- Podsumowanie błędów przed zapisem

## 7. Przyszłe Rozszerzenia

### 7.1 Planowane Funkcjonalności
- Eksport receptur do PDF/Excel
- Wersjonowanie receptur
- Komentarze i notatki do receptur
- Zarządzanie kosztami składników
- API dla integracji z innymi systemami
- Zarządzanie użytkownikami i uprawnieniami

### 7.2 Integracje
- Systemy ERP
- Bazy danych składników
- Systemy zarządzania magazynem

## 8. Kryteria Akceptacji

### 8.1 Podstawowe
- [x] Dodawanie nowych receptur z jednostkami (szt/g)
- [x] Wyszukiwanie produktów po nazwie i ID
- [x] Hierarchiczne przeglądanie składu półproduktów
- [x] Kalkulator przeliczający recepturę dla zadanej ilości/masy
- [x] Import istniejącej bazy produktów
- [x] Obsługa mieszanych jednostek w recepturach

### 8.2 Zaawansowane
- [x] Modyfikacja istniejących receptur
- [x] Responsywny design
- [x] Obsługa fuzzy search
- [x] Dynamiczne dodawanie składników
- [x] Walidacja w czasie rzeczywistym