import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime

# --- Test: odstępy między kolejnymi zapisami pojedynczego bajtu ---

LICZBA_BAJTOW = 10000
WYSYLANY_BAJT = b"\xC4"
PORT_SZEREGOWY = "COM5"
PREDKOSC = 115200

BIT_TIME = 1 / PREDKOSC
ZNAK_TIME = 11 * BIT_TIME
ZNAK_TIME_US = ZNAK_TIME * 1_000_000
MAX_ALLOWED_GAP = 1.5 * ZNAK_TIME_US


def uruchom_test_single_byte():
    print(f"Rozpoczynam test na porcie {PORT_SZEREGOWY} z prędkością {PREDKOSC} b/s")
    print(f"Teoretyczny czas transmisji jednego znaku: {ZNAK_TIME_US:.2f} mikrosekund")
    print(
        f"Maksymalny dopuszczalny odstęp wg MODBUS RTU (1.5T): "
        f"{MAX_ALLOWED_GAP:.2f} mikrosekund"
    )

    try:
        ser = serial.Serial(
            port=PORT_SZEREGOWY,
            baudrate=PREDKOSC,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
        )

        if ser.is_open:
            print(f"Port {PORT_SZEREGOWY} został otwarty pomyślnie")
        else:
            print(f"Nie udało się otworzyć portu {PORT_SZEREGOWY}")
            return

        odstepy_czasowe = []

        ser.write(WYSYLANY_BAJT)
        ostatni_czas = time.perf_counter()

        for i in range(1, LICZBA_BAJTOW):
            ser.write(WYSYLANY_BAJT)

            teraz = time.perf_counter()
            odstep = (teraz - ostatni_czas) * 1_000_000
            odstepy_czasowe.append(odstep)
            ostatni_czas = teraz

            if i % 1000 == 0:
                print(f"Wysłano {i} bajtów ({i/LICZBA_BAJTOW*100:.1f}%)")

        ser.close()
        print("Port szeregowy został zamknięty")

        analizuj_wyniki_single_byte(odstepy_czasowe)

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


def analizuj_wyniki_single_byte(odstepy):
    sredni_odstep = np.mean(odstepy)
    min_odstep = np.min(odstepy)
    max_odstep = np.max(odstepy)
    mediana_odstep = np.median(odstepy)
    std_dev = np.std(odstepy)

    przekroczenia = [odstep > MAX_ALLOWED_GAP for odstep in odstepy]
    liczba_przekroczen = sum(przekroczenia)
    procent_przekroczen = (liczba_przekroczen / len(odstepy)) * 100

    print("\nWyniki analizy:")
    print(f"Liczba zmierzonych odstępów: {len(odstepy)}")
    print(
        f"\u015aredni odst\u0119p mi\u0119dzy bajtami: "
        f"{sredni_odstep:.2f} mikrosekund"
    )
    print(f"Minimalny odstęp: {min_odstep:.2f} mikrosekund")
    print(f"Maksymalny odstęp: {max_odstep:.2f} mikrosekund")
    print(f"Mediana odstępów: {mediana_odstep:.2f} mikrosekund")
    print(f"Odchylenie standardowe: {std_dev:.2f} mikrosekund")
    print(
        f"Odchylenie od teoretycznego czasu: "
        f"{sredni_odstep - ZNAK_TIME_US:.2f} mikrosekund "
        f"({(sredni_odstep - ZNAK_TIME_US) / ZNAK_TIME_US * 100:.2f}%)"
    )
    print(
        f"Liczba przekroczeń maksymalnego dopuszczalnego odstępu: "
        f"{liczba_przekroczen} ({procent_przekroczen:.2f}%)"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"intervals_single_byte_{timestamp}.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Indeks", "Odstęp (µs)"])
        for i, odstep in enumerate(odstepy):
            writer.writerow([i, odstep])
    print(f"Dane odstępów zapisano do pliku: {csv_filename}")

    histogram_filename = f"histogram_single_byte_{timestamp}.png"
    utworz_histogram_single_byte(odstepy, histogram_filename)
    print(f"Histogram zapisany do pliku: {histogram_filename}")

    stats_filename = f"stats_single_byte_{timestamp}.txt"
    with open(stats_filename, "w") as f:
        f.write("Analiza odstępów między zapisami pojedynczego bajtu (Modbus RTU)\n")
        f.write(f"Data i czas testu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Parametry testu:\n")
        f.write(f"Port: {PORT_SZEREGOWY}\n")
        f.write(f"Prędkość: {PREDKOSC} b/s\n")
        f.write("Bajt: 0xC4\n")
        f.write(f"Liczba wysłanych bajtów: {LICZBA_BAJTOW}\n\n")

        f.write(f"Teoretyczny czas transmisji jednego znaku: {ZNAK_TIME_US:.2f} µs\n")
        f.write(
            f"Maksymalny dopuszczalny odstęp (1.5T): {MAX_ALLOWED_GAP:.2f} µs\n\n"
        )

        f.write("Wyniki:\n")
        f.write(f"Liczba zmierzonych odstępów: {len(odstepy)}\n")
        f.write(
            f"\u015aredni odst\u0119p mi\u0119dzy bajtami: "
            f"{sredni_odstep:.2f} \u00b5s\n"
        )
        f.write(f"Minimalny odstęp: {min_odstep:.2f} µs\n")
        f.write(f"Maksymalny odstęp: {max_odstep:.2f} µs\n")
        f.write(f"Mediana odstępów: {mediana_odstep:.2f} µs\n")
        f.write(f"Odchylenie standardowe: {std_dev:.2f} µs\n")
        f.write(
            f"Odchylenie od teoretycznego czasu: "
            f"{sredni_odstep - ZNAK_TIME_US:.2f} µs "
            f"({(sredni_odstep - ZNAK_TIME_US) / ZNAK_TIME_US * 100:.2f}%)\n"
        )
        f.write(
            f"Liczba przekroczeń maksymalnego dopuszczalnego odstępu: "
            f"{liczba_przekroczen} ({procent_przekroczen:.2f}%)\n"
        )

    print(f"Statystyki zapisano do pliku: {stats_filename}")


def utworz_histogram_single_byte(odstepy, nazwa_pliku):
    plt.figure(figsize=(10, 6))
    plt.hist(odstepy, bins=50, alpha=0.75, color="blue", edgecolor="black")
    plt.yscale("log")
    plt.axvline(
        x=ZNAK_TIME_US,
        color="r",
        linestyle="--",
        label=f"Teoretyczny czas ({ZNAK_TIME_US:.2f} µs)",
    )
    plt.axvline(
        x=MAX_ALLOWED_GAP,
        color="g",
        linestyle="--",
        label=f"Max dopuszczalny ({MAX_ALLOWED_GAP:.2f} µs)",
    )
    plt.title("Histogram odstępów między zapisami kolejnych bajtów")
    plt.xlabel("Odstęp czasowy (mikrosekundy)")
    plt.ylabel("Liczba wystąpień")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.savefig(nazwa_pliku)


# --- Test: wiele pełnych ramek Modbus RTU ---

LICZBA_RAMEK = 500
RAMKA_MODBUS = b"\x01\x03\x00\x00\x00\x02\xC4\x0B"
PORT_SZEREGOWY = "COM5"
PREDKOSC = 115200

BIT_TIME = 1 / PREDKOSC
ZNAK_TIME = 11 * BIT_TIME
ZNAK_TIME_US = ZNAK_TIME * 1_000_000
MAX_ALLOWED_GAP = 1.5 * ZNAK_TIME_US


def uruchom_test_modbus_frame():
    print(f"Test ramki Modbus RTU na porcie {PORT_SZEREGOWY}")
    print(f"Ramka: {[hex(b) for b in RAMKA_MODBUS]}")

    try:
        ser = serial.Serial(
            port=PORT_SZEREGOWY,
            baudrate=PREDKOSC,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
        )

        if not ser.is_open:
            print("Nie udało się otworzyć portu!")
            return

        print("Port został otwarty pomyślnie")
        odstepy = []

        for i in range(LICZBA_RAMEK):
            start_time = time.perf_counter()
            ser.write(RAMKA_MODBUS)
            ser.flush()
            end_time = time.perf_counter()

            czas_transmisji = (end_time - start_time) * 1_000_000
            sredni_na_bajt = czas_transmisji / len(RAMKA_MODBUS)
            odstepy.append(sredni_na_bajt)

            if (i + 1) % 50 == 0:
                print(f"Wysłano {i + 1} ramek ({(i + 1) / LICZBA_RAMEK * 100:.1f}%)")

        ser.close()
        print("Port został zamknięty")
        analizuj_wyniki_modbus_frame(odstepy)

    except Exception as e:
        print(f"Błąd: {e}")


def analizuj_wyniki_modbus_frame(odstepy):
    srednia = np.mean(odstepy)
    minimum = np.min(odstepy)
    maksimum = np.max(odstepy)
    odch_std = np.std(odstepy)
    mediana = np.median(odstepy)

    przekroczenia = [t > MAX_ALLOWED_GAP for t in odstepy]
    liczba_przekroczen = sum(przekroczenia)
    procent = (liczba_przekroczen / len(odstepy)) * 100

    print("\n--- Wyniki: średni czas na bajt (transmisja ramki) ---")
    print(f"Liczba ramek: {len(odstepy)}")
    print(f"\u015aredni czas na bajt: {srednia:.2f} \u00b5s")
    print(f"Min: {minimum:.2f} µs")
    print(f"Max: {maksimum:.2f} µs")
    print(f"Mediana: {mediana:.2f} µs")
    print(f"Odchylenie standardowe: {odch_std:.2f} µs")
    print(
        f"Przekroczenia limitu (1.5T = {MAX_ALLOWED_GAP:.2f} µs): "
        f"{liczba_przekroczen} ({procent:.2f}%)"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"intervals_modbus_frame_{timestamp}.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Indeks", "\u015aredni czas na bajt (\u00b5s)"]
        )
        for i, val in enumerate(odstepy):
            writer.writerow([i, val])
    print(f"Zapisano dane do: {csv_filename}")

    histogram_filename = f"histogram_modbus_frame_{timestamp}.png"
    utworz_histogram_modbus_frame(odstepy, histogram_filename)
    print(f"Zapisano histogram do: {histogram_filename}")

    stats_filename = f"stats_modbus_frame_{timestamp}.txt"
    with open(stats_filename, "w") as f:
        f.write("Analiza czasu na bajt przy wysyłaniu ramki Modbus RTU\n\n")
        f.write(f"Liczba ramek: {len(odstepy)}\n")
        f.write(f"\u015aredni czas na bajt: {srednia:.2f} \u00b5s\n")
        f.write(f"Min: {minimum:.2f} µs\n")
        f.write(f"Max: {maksimum:.2f} µs\n")
        f.write(f"Mediana: {mediana:.2f} µs\n")
        f.write(f"Odchylenie standardowe: {odch_std:.2f} µs\n")
        f.write(f"Przekroczenia limitu 1.5T: {liczba_przekroczen} ({procent:.2f}%)\n")
    print(f"Zapisano statystyki do: {stats_filename}")


def utworz_histogram_modbus_frame(odstepy, plik):
    plt.figure(figsize=(10, 6))
    plt.hist(odstepy, bins=50, alpha=0.75, color="green", edgecolor="black")
    plt.yscale("log")
    plt.axvline(
        ZNAK_TIME_US,
        color="r",
        linestyle="--",
        label=f"Teoretyczny czas ({ZNAK_TIME_US:.2f} µs)",
    )
    plt.axvline(
        MAX_ALLOWED_GAP,
        color="orange",
        linestyle="--",
        label=f"Max dopuszczalny ({MAX_ALLOWED_GAP:.2f} µs)",
    )
    plt.title("Histogram średniego czasu na bajt (ramka Modbus RTU)")
    plt.xlabel("Czas (mikrosekundy)")
    plt.ylabel("Liczba wystąpień")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plik)


if __name__ == "__main__":
    print("Analiza odstępów czasowych w transmisji szeregowej (Modbus RTU)")
    print("1) Pojedynczy bajt — odstępy między kolejnymi zapisami")
    uruchom_test_single_byte()
    print("2) Pełna ramka — średni czas na bajt przy wysyłaniu ramki")
    uruchom_test_modbus_frame()
