import numpy as np
import gdal
from osgeo import gdal
import sys
import gdalnumeric
from osgeo.gdalnumeric import *
from gdalconst import *
gdal.UseExceptions()

def filtrace(hodnoty, radky, sloupce):
    for radek in range(1, radky - 1):
        for sloupec in range(1, sloupce - 1):
            # zjisti se hodnoty aktualni zpracovavane bunky a hodnoty bunek v osmi/sousedstvi
            stredBunka = hodnoty[radek][sloupec]
            lhBunka = hodnoty[radek - 1][sloupec - 1]  # leva-horni bunka
            hBunka = hodnoty[radek - 1][sloupec]  # horni bunka
            phBunka = hodnoty[radek - 1][sloupec + 1]  # prava-horni bunka
            pBunka = hodnoty[radek][sloupec + 1]
            pdBunka = hodnoty[radek + 1][sloupec + 1]
            dBunka = hodnoty[radek + 1][sloupec]
            ldBunka = hodnoty[radek + 1][sloupec - 1]
            lBunka = hodnoty[radek][sloupec - 1]
            # vypocet prumeru ze vsech 9 hodnot - vyhlazovaci filtr
            novaHodnota = (stredBunka + lhBunka + hBunka + phBunka + pBunka + pdBunka + dBunka + ldBunka + lBunka) / 9
            # vypocitana hodnota pro aktualne zpracovavanou bunku rastru se zapise do pole noveHodnoty (na totoznou pozici)
            noveHodnoty[radek][sloupec] = novaHodnota
    return noveHodnoty

try:
    # otevreni rastru - GDAL sam rozpozna, o ktery z podporovanych formatu
    # se jedna a podle toho pouzije prislusny driver
    dataset = gdal.Open(r"D:\temp\cvicna_data\teren")
except RuntimeError:
    # pokud soubor nelze otevrit, program se ukonci
    print('Zadany soubor nelze otevrit')
    sys.exit(1)

# vyber pasma z datasetu (rastru), pasma jsou ocislovane od 1 (ne od 0)
# vice pasem obsahuji obvykle hyperspektralni a multispektralni snimky
band = dataset.GetRasterBand(1)
# print(str(dataset.RasterCount)) # vypis poctu pasem v rastru/datasetu
# nacteni hodnost z rastru/pasma do pole
hodnoty = band.ReadAsArray()
# print(hodnoty)
# print(hodnoty.shape)
# zjisteni poctu sloupcu a radku rastru/datasetu
sloupce = dataset.RasterXSize
radky = dataset.RasterYSize
# vytvoreni pole o stejnem poctu sloupcu a radku, jako ma vstup - bude obsahovat same 0
noveHodnoty = np.zeros((radky, sloupce))
# cykly pro prochazeni rastru od leveho horniho okraje po radcich a sloupcich
# cykly vynechavaji okrajove radky a sloupce (zacinaji az od 1, ne 0 a konci na predposlednim radku/sloupci)
#   - aby se pri vymezeni okoli (3x3 bunky) zpracovavanych bunek nedostal za okraj rastru

noveHodnoty = filtrace(hodnoty, radky, sloupce)
## ulozeni vyfiltrovaneho rastru (pole noveHodnoty) do GeoTiffu
# urceni driver podle formatu, do ktereho se bude ukladat
driver = gdal.GetDriverByName("GTiff")
# vytvoreni (prazdneho) datasetu s parametry kam se bude ukladat, jakou bude mit velikost, kolik pasem a datovy typ hodnot
# posledni parametr lze zadat i v podobe: band.DataType - prevezme se datovy typ ze vstupni vrstvy
dsOut = driver.Create(r"D:\temp\teren2.tiff", sloupce, radky, 1, gdal.GDT_Float32)
# zkopirovani prostorove reference rastu ze vstupniho datasetu do vystupniho
gdalnumeric.CopyDatasetInfo(dataset,dsOut)
# ziskani pasma vystupu
bandOut=dsOut.GetRasterBand(1)
# zapis hodnot z pole noveHodnoty do vystupniho pasma
BandWriteArray(bandOut, noveHodnoty)
# dokonceni zapisu
bandOut.FlushCache()