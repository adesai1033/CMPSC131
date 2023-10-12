import sys
import copy

class Book:
    def __init__(self, name, is_restricted, amount):
        self.amount = amount
        self.borrowed_amount = 0
        self.borrowed_count = 0
        self.book = BookItem(name, is_restricted)
    
    def addBook(self, amt=1):
        self.amount += amt

    def getAvailableAmount(self):
        return self.amount - self.borrowed_amount

    def borrowBook(self):
        self.borrowed_amount += 1
        self.borrowed_count += 1
        return self.book
    
    def returnBook(self):
        self.borrowed_amount -= 1

class BookItem:
    def __init__(self, name, is_restricted):
        self.name = name
        self.is_restricted = is_restricted

class BorrowedBookItem:
    def __init__(self, book, borrow_date, borrow_days):
        self.book = book
        self.borrow_date = borrow_date
        self.borrow_days = borrow_days
    
    def calculateFines(self, date_returned):
        fines = 0
        days_exceeded = (date_returned - (self.borrow_date + self.borrow_days))
        if self.book.is_restricted:
            fines = max(0, 5 * days_exceeded)
        else:
            fines = max(0, 3 * days_exceeded)
        return fines

class Log:
    def __init__(self, type, student=None, book=None, days_borrowed=None, amount_owed=None):
        self.type = type
        self.student = student
        self.book = book
        self.days_borrowed = days_borrowed
        self.amount_owed = amount_owed

class DayLog:
    def __init__(self, day, student=None, book=None, days_borrowed=None, amount_owed=None):
        self.day = day
        self.logs = []
        #self.addLog(student=student, book=book, days_borrowed=days_borrowed, amount_owed=amount_owed)

    def addLog(self, type, student=None, book=None, days_borrowed=None, amount_owed=None):
        self.logs.append(Log(type, student=student, book=book, days_borrowed=days_borrowed, amount_owed=amount_owed))

class Student:
    def __init__(self, name):
        self.name = name
        self.books = {}
        self.fines = 0

    def borrowBook(self, book, day, borrow_days):
        self.books[book.name] = BorrowedBookItem(book, borrow_date=day, borrow_days=borrow_days)
    
    def returnBook(self, book_name, day):
        book = self.books.pop(book_name)
        self.fines += book.calculateFines(day)
    
    def pay_fines(self, payment):
        self.fines -= payment
        
    
def parse_booklist_file(filename="Booklist.txt"):
    booklist_dict = {}
    with open(filename) as file:
        for line in file:
            name, amount, is_restricted = line.replace("\n", "").split("#")
            booklist_dict[name] = Book(name, is_restricted == "TRUE", int(amount))
    return booklist_dict

def parse_librarylog_file(filename="librarylog.txt"):
    days_len = -1
    liblog = []
    curr_day = -1
    with open(filename) as file:
        for line in file:
            line = line.replace("\n", "")
            if line.isnumeric():
                days_len = int(line)
            else:
                log_lst = line.split("#")
                type = log_lst[0]
                day = int(log_lst[1])
                student = None
                book = None
                days_borrowed = None
                amount_owed = None
                if type == "B":
                    student = log_lst[2]
                    book = log_lst[3]
                    days_borrowed = int(log_lst[4])
                elif type == "R":
                    student = log_lst[2]
                    book = log_lst[3]
                elif type == "A":
                    book = log_lst[2]
                else:
                    student = log_lst[2]
                    amount_owed = int(log_lst[3])

                if day != curr_day:
                    liblog.append(DayLog(day))
                    curr_day = day
                liblog[-1].addLog(type, student=student,book=book,days_borrowed=days_borrowed,amount_owed=amount_owed)
                
    return days_len, liblog

def update_logs_upto(liblog, bookdict, studentdict={}, day=float("inf")):
    for day_log in liblog:
        curr_day = day_log.day
        if day < curr_day:
            break
        for log in day_log.logs:
            if log.type == "B":
                if log.student not in studentdict:
                    studentdict[log.student] = Student(log.student)
                studentdict[log.student].borrowBook(bookdict[log.book].borrowBook(), day, log.days_borrowed)
            elif log.type == "R":
                studentdict[log.student].returnBook(log.book, day)
                bookdict[log.book].returnBook()
            elif log.type == "A":
                if log.book not in bookdict:
                    bookdict[log.book] = Book(log.book, False, 1)
                bookdict[log.book].addBook()
            else:
                studentdict[log.student].pay_fines(log.amount_owed)

def can_borrow(liblog, bookdict, student, book, day, days_borrow):
    studentdict = {}
    update_logs_upto(liblog, bookdict, studentdict, day)

    has_book = False
    is_legal_days_borrow = False
    if book in bookdict:
        has_book = bookdict[book].getAvailableAmount() > 0
        is_legal_days_borrow = days_borrow <= 7 if bookdict[book].book.is_restricted else days_borrow <= 28
    has_legal_amt_borrowed = True
    has_no_fines = True
    if student in studentdict:
        has_legal_amt_borrowed = len(studentdict[student].books) < 3
        has_no_fines = studentdict[student].fines <= 0
    return has_book and is_legal_days_borrow and has_legal_amt_borrowed and has_no_fines

def get_highest_borrow_ratio_book(liblog, bookdict, days_len):
    update_logs_upto(liblog, bookdict, day=days_len)
    highest_borrow_ratio = 0
    highest_borrow_ratio_book = None 
    for book in bookdict:
        ratio = bookdict[book].borrowed_count / bookdict[book].amount
        if ratio > highest_borrow_ratio:
            highest_borrow_ratio = ratio
            highest_borrow_ratio_book = book
    return highest_borrow_ratio_book

def get_pending_fines(liblog, bookdict, day):
    studentdict = {}
    fines = 0
    update_logs_upto(liblog, bookdict, studentdict, day)
    for student in studentdict:
        fines += studentdict[student].fines
    return fines


if __name__ == "__main__":
    bookdict = parse_booklist_file()
    days_len, liblog = parse_librarylog_file()
    studentdict = {}
    x = get_highest_borrow_ratio_book(liblog, bookdict, days_len)
    y = get_pending_fines(liblog, bookdict, days_len)
    print(x)
    print(y)
