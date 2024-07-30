from collections import UserDict
import re
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    def _validate(self, phone_number):
        return bool(re.match(r'^\d{10}$', phone_number))


class Birthday(Field):
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def _validate(self, birthday):
        try:
            datetime.strptime(birthday, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    def to_date(self):
        return datetime.strptime(self.value, '%d.%m.%Y').date()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone_number, new_phone_number):
        phone_to_edit = self.find_phone(old_phone_number)
        if phone_to_edit:
            self.remove_phone(old_phone_number)
            self.add_phone(new_phone_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.to_date().replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = "; ".join(str(phone) for phone in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.to_date()
                birthday = birthday.replace(year=today.year)

                # Check next year if birthday is already passed
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)

                days_until_birthday = (birthday - today).days
                if days_until_birthday <= 7:
                    if birthday.weekday() == 5:  # Saturday
                        days_until_birthday += 2
                    if birthday.weekday() == 6:  # Sunday
                        days_until_birthday += 1
                    congratulation_date = today + timedelta(days=days_until_birthday)
                    upcoming_birthdays.append(
                        {"name": record.name.value, "congratulation_date": congratulation_date.strftime("%Y.%m.%d")})

        return upcoming_birthdays


# Testing the system

# Creating a new address book
book = AddressBook()

# Creating a record for John
john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
john_record.add_birthday("23.01.1985")

# Adding John's record to the address book
book.add_record(john_record)

# Creating and adding a new record for Jane
jane_record = Record("Jane")
jane_record.add_phone("9876543210")
jane_record.add_birthday("02.08.1990")
book.add_record(jane_record)

# Printing all records in the book
for name, record in book.data.items():
    print(record)

# Finding and editing John's phone number
john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john)  # Output: Contact name: John, phones: 1112223333; 5555555555

# Finding a specific phone in John's record
found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")  # Output: 5555555555

# Deleting Jane's record
book.delete("Jane")

# Printing all records in the book after deleting Jane
for name, record in book.data.items():
    print(record)

# Finding upcoming birthdays
upcoming_birthdays = book.get_upcoming_birthdays()
for user in upcoming_birthdays:
    print(f"Upcoming birthday: {user['name']}, on {user['congratulation_date']}")
