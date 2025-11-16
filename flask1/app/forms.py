from wtforms import Form, StringField, SubmitField
import re

class PhoneForm(Form):
    phone_number = StringField('Номер телефона') # Поле для ввода номера телефона
    submit = SubmitField('Проверить') # Кнопка отправки формы

    def validate(self):
        if not super().validate():
            return False

        phone_number_str = self.phone_number.data # Получаем значение номера телефона из формы

        # Добавлена проверка на недопустимые символы
        if not re.match(r'^[\d\s()+\-.]+$', phone_number_str):
            self.phone_number.errors.append("Недопустимый ввод. В номере телефона встречаются недопустимые символы.")
            return False

        cleaned_number = re.sub(r'[^\d]', '', phone_number_str) # Удаляем все кроме цифр

        if phone_number_str.startswith('+7'):  # Если номер начинается с +7, он должен содержать 11 цифр
            if len(cleaned_number) != 11:
                self.phone_number.errors.append("Недопустимый ввод. Неверное количество цифр.")
                return False
            else:
                return True
        elif len(cleaned_number) == 10:
            return True  # Валидный короткий номер
        elif len(cleaned_number) == 11 and (cleaned_number.startswith('7') or cleaned_number.startswith('8')):
            return True  # Валидный длинный номер
        else:
            self.phone_number.errors.append("Недопустимый ввод. Неверное количество цифр.")
            return False


    def validate_phone_number(self, phone_number):
        phone_number_str = phone_number.data  # Извлекаем значение из поля
        cleaned_number = re.sub(r'[^\d]', '', phone_number_str)

        if len(cleaned_number) == 11 and cleaned_number.startswith('7'):
            cleaned_number = "8" + cleaned_number[1:]  # Заменяем "7" на "8"
        elif len(cleaned_number) == 10:
            cleaned_number = "8" + cleaned_number  # Добавляем "8" в начале

        formatted_number = f"{cleaned_number[:1]}-{cleaned_number[1:4]}-{cleaned_number[4:7]}-{cleaned_number[7:9]}-{cleaned_number[9:]}"

        return formatted_number