############### CODIGO RUIM

class Wallet:

    def __init__(self, money):
        self.money = money

    def subtract(self, amount):
        self.money -= amount

    def add(self, amount):
        self.money += amount


class Customer:

    def __init__(self, name, wallet):
        self.name = name
        self.wallet = wallet


class Paperboy:

    def __init__(self, num_of_papers, newspaper_price):
        self.num_of_papers = num_of_papers
        self.newspaper_price = newspaper_price

    def deliver_paper(self, customer):
        self.num_of_papers -= 1

        wallet = customer.wallet
        if wallet.money >= self.newspaper_price:
            wallet.money.subtract(self.newspaper_price)
            print("Thanks!")
        else:
            print("Show me the money!!!")

############### REFATORAÇÃO 1

class Wallet:

    def __init__(self, money):
        self.money = money

    def subtract(self, amount):
        self.money -= amount

    def add(self, amount):
        self.money += amount


class Customer:

    def __init__(self, name, wallet):
        self.name = name
        self.wallet = wallet

    def pay_for_something(self, payment):
        if self.wallet:
            if self.wallet.money >= payment:
                self.wallet.subtract(payment)
                return payment

        return 0


class Paperboy:

    def __init__(self, num_of_papers, newspaper_price):
        self.num_of_papers = num_of_papers
        self.newspaper_price = newspaper_price

    def deliver_paper(self, customer):
        self.num_of_papers -= 1

        payment = customer.pay_for_something(self.newspaper_price)
        if payment == self.newspaper_price:
            print("Thanks!")
        else:
            print("Show me the money!!!")

############### REFATORAÇÃO 2 - com moedas


class Wallet:

    def __init__(self, money):
        self.money = money

    def subtract(self, amount):
        self.money -= amount

    def add(self, amount):
        self.money += amount

    def empty(self):
        self.subtract(self.money)

class Customer:

    def __init__(self, name, wallet, coins_in_pocket):
        self.name = name
        self.wallet = wallet
        self.coins_in_pocket = coins_in_pocket

    def pay_for_something(self, payment):
        total_money = self.coins_in_pocket
        if self.wallet:
            total_money += self.wallet.money

        if payment > total_money:
            return 0

        to_pay = payment
        if to_pay > self.wallet.money:
            to_pay -= self.wallet.money
            self.wallet.empty()
        else:
            to_pay = 0
            self.wallet.subtract(payment)

        if to_pay > 0:
            self.coins_in_pocket -= to_pay

        return payment


class Paperboy:

    def __init__(self, num_of_papers, newspaper_price):
        self.num_of_papers = num_of_papers
        self.newspaper_price = newspaper_price

    def deliver_paper(self, customer):
        self.num_of_papers -= 1

        payment = customer.pay_for_something(self.newspaper_price)
        if payment == self.newspaper_pricezz:
            print("Thanks!")
        else:
            print("Show me the money!!!")
