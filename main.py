from collections import UserDict
from datetime import datetime
import csv

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
    
#Name: Клас для зберігання імені контакту. Обов'язкове поле.
class Name(Field):
    def __str__(self):
        return super().__str__()


#Phone: Клас для зберігання номера телефону. Має валідацію формату (10 цифр). 
class Phone(Field):
    
    @staticmethod
    def validate_phone(value): # Додамо функціонал перевірки на правильність наведених значень для полів Phone, Birthday 
        new_phone = (
        value.strip()
            .removeprefix("+380")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
            )
        
        if len(new_phone) == 10 and new_phone.isdigit():
            return new_phone
        else:
            raise ValueError("Invalid phone number format")
             
    def __init__(self, value):
        super().__init__(self.validate_phone(value))

    @Field.value.setter
    def value(self, value):
        self._Field__value = self.validate_phone(value)
    

#Додамо поле для дня народження Birthday. Це поле не обов'язкове, але може бути тільки одне.  
#Клас Record приймає ще один додатковий (опціональний) аргумент класу Birthday
class Birthday(Field):
    def __init__(self, value):
        self.validate_birthday(value)
        self._Field__value = datetime.strptime(value, '%Y-%m-%d').date()

# Додамо функціонал перевірки на правильність наведених значень для полів Phone, Birthday
    @Field.value.setter
    def value(self, value):
        self.validate_birthday(value)
        self._Field__value = datetime.strptime(value, '%Y-%m-%d').date()
    
    def validate_birthday(self, value):
        pass

# Record: Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
# Відповідає за логіку додавання/видалення/редагування необов'язкових полів та зберігання 
# Реалізовано зберігання об'єкта Name в окремому атрибуті.
# Реалізовано зберігання списку об'єктів Phone в окремому атрибуті.
class Record:

    def __init__(self, name, birthday = None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None # ???

    def add_phone(self, phone_number):
        
        phone = Phone(phone_number)
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]
        # for phone in self.phones:
        #     if phone.value == phone_number:
        #         self.phones.remove(phone)
        #         break

    def edit_phone(self, old_phone, new_phone):
        phone_exists = False
        for index, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[index] = Phone(new_phone)
                #phone_exists = True
                break
            else:
                raise ValueError(f"The phone number {old_phone} does not exist.")
        # if not phone_exists:
        #     raise ValueError(f"The phone number {old_phone} does not exist.")
        

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
            
    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones if p is not None)
        return f"Contact name: {self.name.value}, phones: {phones_str}"
        #return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    #Додамо функціонал роботи з Birthday у клас Record, а саме функцію days_to_birthday, 
    #Клас Record реалізує метод days_to_birthday, який повертає кількість днів до наступного 
    # дня народження контакту, якщо день народження заданий.
    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_to = (next_birthday - today).days
            return days_to # яка повертає кількість днів до наступного дня народження
        else:
            return None

    
        
#Додамо пагінацію (посторінковий висновок) для AddressBook для ситуацій, 
# коли книга дуже велика і треба показати вміст частинами, а не все одразу. 
# Реалізуємо це через створення ітератора за записами.
class AddressBookIterator:
    def __init__(self, info, writing_item_pr_page=5):
        self.info = info
        self.keys = list(info.keys())
        self.writing_item_pr_page = writing_item_pr_page
        self.page = 0

    def __iter__(self):
        return self

    def __next__(self):
        start = self.page * self.writing_item_pr_page
        end = (self.page + 1) * self.writing_item_pr_page
        items = self.keys[start:end]

        if not items:
            raise StopIteration

        self.page += 1
        return {key: self.info[key] for key in items}

#AddressBook: Клас для зберігання та управління записами. 
# Успадковується від UserDict, та містить логіку пошуку за записами до цього класу
# Записи Record у AddressBook зберігаються як значення у словнику. 
# В якості ключів використовується значення Record.name.value.

class AddressBook(UserDict):

#Додавання записів.
# Реалізовано метод add_record, який додає запис до self.data.
    def add_record(self, record: Record):
        self.data[record.name.value] = record

#Пошук записів за іменем.
# Реалізовано метод find, який знаходить запис за ім'ям.
    def find(self,name):
        return self.data.get(name)

#Видалення записів за іменем.
# Реалізовано метод delete, який видаляє запис за ім'ям.
    def delete(self, name):
        if name in self.data:
            del self.data[name]

#AddressBook реалізує метод iterator, який повертає генератор за записами AddressBook 
# і за одну ітерацію повертає уявлення для N записів.
    def iterator(self, writing_item_pr_page):
        return AddressBookIterator(self.data, writing_item_pr_page)
    

    def record_to_file(self, filename):
        with open(filename, "w", newline="") as fh:
            field_names = ["name", "phone"]
            writer = csv.writer(fh)
            writer.writerow(field_names)
            for name, record in self.data.items():
                for phone in record.phones:
                    validated_phone = Phone.validate_phone(phone.value)
                    if validated_phone:
                        writer.writerow([name, validated_phone])

    def load_from_file(self, filename):
        with open(filename, "r", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name, phone = row.get("name"), row.get("phone")
                if name and phone:
                    if name not in self.data:
                        self.data[name] = Record(name)
                    validated_phone = Phone.validate_phone(phone)
                    if validated_phone:
                        self.data[name].add_phone(validated_phone)


    def search(self, query):
        results = {}
        for name, record in self.data.items():
            if query.lower() in name.lower():
                results[name] = record
            else:
                for phone in record.phones:
                    if query in phone.value:
                        results[name] = record
                        break
        return results


if __name__ == "__main__":
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("+3805555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")

    john_record = Record("John", "1990-05-15")
    print(john_record.days_to_birthday())


    filename_csv = "address_book.csv"
    
    # Створення та наповнення адресної книги
    # ...

    # Збереження адресної книги в CSV-файл
    book.record_to_file(filename_csv)

    # Відновлення адресної книги з CSV-файлу
    new_book = AddressBook()
    new_book.load_from_file(filename_csv)

    # Пошук та виведення результатів
    search_query = "111"
    search_results = new_book.search(search_query)
    print(f"Search results for '{search_query}':")
    for name, record in search_results.items():
        print(record)