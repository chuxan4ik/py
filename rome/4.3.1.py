class Roman:
    """Класс Roman реализует работу с римскими числами.
    Внутри класс работает с обычными арабскими числами (int),
    которые преобразуются в римские при необходимости (например, при выводе).
    """

    # Константы класса
    ARABIC_MIN = 1
    ARABIC_MAX = 3999
    ROMAN_MIN = "I"
    ROMAN_MAX = "MMMCMXCIX"

    LETTERS = ["M", "CM", "D", "CD", "C", "XC", "L",
               "XL", "X", "IX", "V", "IV", "I"]
    NUMBERS = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]

    def __init__(self, value):
        if not isinstance(value, (int, str)):
            raise TypeError("Не могу создать римское число из {0}".format(type(value)))

        if isinstance(value, int):
            self.__check_arabic(value)
            self._arabic = value
        elif isinstance(value, str):
            self._arabic = self.to_arabic(value)

    def __add__(self, other):
        if not isinstance(other, (Roman, int)):
            raise TypeError('Нельзя складывать числа и не числа')

        if isinstance(other, int):
            return Roman(self.arabic + other)
        elif isinstance(other, Roman):
            return Roman(self.arabic + other.arabic)

    def __sub__(self, other):
        if not isinstance(other, (Roman, int)):
            raise TypeError('Нельзя складывать числа и не числа')

        if isinstance(other, int):
            return Roman(self.arabic - other)
        elif isinstance(other, Roman):
            return Roman(self.arabic - other.arabic)

    def __mul__(self, other):
        if not isinstance(other, (Roman, int)):
            raise TypeError('Нельзя складывать числа и не числа')

        if isinstance(other, int):
            return Roman(self.arabic * other)
        elif isinstance(other, Roman):
            return Roman(self.arabic * other.arabic)

    def __floordiv__(self, other):
        if not isinstance(other, (Roman, int)):
            raise TypeError('Нельзя складывать числа и не числа')

        if isinstance(other, int):
            return Roman(self.arabic // other)
        elif isinstance(other, Roman):
            return Roman(self.arabic // other.arabic)

    def __truediv__(self, other):
        # Любое деление для римского числа считается делением нацело,
        # поэтому необходимо передать "работу" реализованному методу
        # целочисленного деления
        return self.__floordiv__(other)

    def __str__(self):
        """Вернуть строковое представление класса."""
        return Roman.to_roman(self._arabic)

    @staticmethod
    def __check_arabic(value):
        """Возбудить исключение ValueError, если 'value' не принадлежит
        [ARABIC_MIN; ARABIC_MIN]."""
        if not Roman.ARABIC_MIN <= value <= Roman.ARABIC_MAX:
            raise ValueError(f'Число должно лежать на отрезке [{Roman.ARABIC_MIN}; {Roman.ARABIC_MAX}]')

    @staticmethod
    def __check_roman(value):
        """Возбудить исключение ValueError, если 'value' содержит
        недопустимые символы (не входящие в LETTERS)."""
        if any(i not in Roman.LETTERS for i in value):
            raise ValueError(f'Римское число должно содержать только символы из набора {Roman.LETTERS}')

    @property
    def arabic(self):
        """Вернуть арабское представление числа."""
        return self._arabic

    @staticmethod
    def to_arabic(roman):
        def letter_to_number(letter):
            """Вернуть арабское значение римской цифры 'letter'.

            Регистр не учитывается."""
            return Roman.NUMBERS[Roman.LETTERS.index(letter)]
        Roman.__check_roman(roman)

        i = 0  # Позиция в строке roman
        value = 0  # Преобразованное число

        while i < len(roman):

            number = letter_to_number(roman[i])

            i += 1

            if i == len(roman):
                # В строке roman больше не осталось символов, добавляем number
                value += number
            else:
                # Если символы остались, необходимо посмотреть на следующий.
                # Если следующий символ "больше", считаем их за одну цифру.
                # Это необходимо, например, для того,
                # чтобы IV преобразовать в 4, а не 15.
                next_number = letter_to_number(roman[i])
                if next_number > number:
                    # Комбинируем цифры и перемещаем i к следующей
                    value += next_number - number
                    i += 1
                else:
                    # Просто добавляем следующую цифру
                    value += number

        Roman.__check_arabic(value)
        return value

    @staticmethod
    def to_roman(arabic):
        Roman.__check_arabic(arabic)

        roman = ""
        # n - часть arabic, которую осталось преобразовать
        n = arabic

        for i, number in enumerate(Roman.NUMBERS):
            while n >= number:
                roman += Roman.LETTERS[i]
                n -= Roman.NUMBERS[i]

        return roman