from collections import deque
from itertools import chain, tee
from math import sqrt
from random import choice

class Puzzle:
    HOLE = 0

    """
    Bulmacayi temsil eden bir sinif.Kare liste olmali.
    """
    def __init__(self, tahta, hole_location=None, genislik=None):
        self.tahta = list(chain.from_iterable(tahta)) if hasattr(tahta[0], '__iter__') else tahta
        self.hole = hole_location if hole_location is not None else self.tahta.index(Puzzle.HOLE)
        self.genislik = genislik or int(sqrt(len(self.tahta)))

    @property
    def cozum(self):
        """
        Tahtanin uzerine dogru numaralar yazilmissa cozum yapilir. 0 tahtadaki son pozisyona gelir.
        """
        return self.tahta == list(range(1, self.genislik * self.genislik)) + [Puzzle.HOLE]

    @property
    def olabilecek_hareketler(self):
        """
        0 icin olası hareketler için, burada
        tahta satır ana düzeninde doğrusallaştırılır. Olasılıklar
        -1 (sol), +1 (sağ), - genişlik (yukarı) veya + genişlik (aşağı).
        """
        for hedef in (self.hole - self.genislik, self.hole + self.genislik):
            if 0 <= hedef < len(self.tahta):
                yield hedef
        
        for hedef in (self.hole - 1, self.hole + 1):
            if hedef // self.genislik == self.hole // self.genislik:
                yield hedef

    def move(self, hedef):
        """
        0'i belirtilen dizeye tasir.
        """
        tahta = self.tahta[:]
        tahta[self.hole], tahta[hedef] = tahta[hedef], tahta[self.hole]
        return Puzzle(tahta, hedef, self.genislik)

    def karistir(self, hareketler=1000):
        """
        Return a new puzzle that has been shuffled with random moves
        """
        p = self
        for _ in range(hareketler):
            p = p.move(choice(list(p.olabilecek_hareketler)))
        return p

    @staticmethod
    def yon(a, b):
        """
        0 Sag sol yukari ve asagi hareketleri.
        """
        if a is None:
            return None
        return {
                     -a.genislik: 'Yukari',-1: 'Sola',    0: None,    +1: 'Saga',+a.genislik: 'Asagi',
        }[b.hole - a.hole]

    def __str__(self):
        return "\n".join(str(self.tahta[start : start + self.genislik])
                         for start in range(0, len(self.tahta), self.genislik))

    def __eq__(self, other):
        return self.tahta == other.tahta

    def __hash__(self):
        h = 0
        for value, i in enumerate(self.tahta):
            h ^= value << i
        return h

class SiraylaTasi:
    """
    Birbiri ardina gelen ardasik durumlar.
    """
    def __init__(self, son, onceki_holes=None):
        self.son = son
        self.onceki_holes = onceki_holes or []

    def dallar(self, yon):
        """
    Daha once ayni hareket yapilissa kontrol eder.
        """
        return SiraylaTasi(self.son.move(yon),
                            self.onceki_holes + [self.son.hole])

    def __iter__(self):
        """
        İlk yapılandırmadan başlayarak bulmaca durumlarinin olusturucusu.
        """
        states = [self.son]
        for hole in reversed(self.onceki_holes):
            states.append(states[-1].move(hole))
        yield from reversed(states)

class Solver:
    """
    Cozum baslangici.
    """
    def __init__(self, start):
        self.start = start

    def solve(self):
        """
        Genişlik öncelikli arama gerçekleştirir, SiraylaTasi'yi döndürür,
        eğer varsa 
        """
        queue = deque([SiraylaTasi(self.start)])
        seen  = set([self.start])
        if self.start.cozum:
            return queue.pop()

        for seq in iter(queue.pop, None):
            for hedef in seq.son.olabilecek_hareketler:
                attempt = seq.dallar(hedef)
                if attempt.son not in seen:
                    seen.add(attempt.son)
                    queue.appendleft(attempt)
                    if attempt.son.cozum:
                        return attempt



def pairwise(iterable):
    
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

if __name__ == '__main__':
    tahta = [[1,2,3],
             [4,0,6],
             [7,5,8]]

    puzzle = Puzzle(tahta).karistir()
    print(puzzle)
    move_seq = iter(Solver(puzzle).solve())
    for from_state, to_state in pairwise(move_seq):
        print()
        print(Puzzle.yon(from_state, to_state))
        print(to_state)
        
