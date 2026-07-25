import heapq
import json
import os


class Member:
    def __init__(self, member_id, name, balance=0.0):
        self.member_id = member_id
        self.name = name
        self.balance = balance

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "balance": self.balance,
        }


class FinCoop:
    def __init__(self):
        self.members = {}          # member_id -> Member object
        self.transactions = {}     # tx_id -> dict
        self.transaction_queue = []
        self.undo_stack = []
        self.loan_heap = []
        self.loan_counter = 0      # Tie-breaker for heapq

    # ---------------- HELPERS ----------------

    def _get_float_input(self, prompt):
        """Safely prompt the user for a floating-point number."""
        while True:
            try:
                val = float(input(prompt))
                if val <= 0:
                    print("Amount must be greater than zero.")
                    continue
                return val
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def _get_int_input(self, prompt):
        """Safely prompt the user for an integer."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    def save_data(self):
        """Placeholder persistence method - extend as needed."""
        # For demonstration, state is maintained in memory.
        pass

    # ---------------- MEMBER REGISTRATION ----------------

    def register_member(self):
        member_id = input("Enter Member ID: ").strip()

        if not member_id:
            print("Member ID cannot be empty.\n")
            return

        if member_id in self.members:
            print("Member already exists.\n")
            return

        name = input("Enter Member Name: ").strip()

        self.members[member_id] = Member(member_id, name)
        self.save_data()

        print("Member registered successfully.\n")

    # ---------------- DEPOSIT ----------------

    def deposit(self):
        member_id = input("Member ID: ").strip()

        if member_id not in self.members:
            print("Member not found.\n")
            return

        amount = self._get_float_input("Deposit Amount: ")
        tx_id = input("Transaction ID: ").strip()

        if not tx_id:
            print("Transaction ID cannot be empty.\n")
            return

        if tx_id in self.transactions:
            print("Duplicate transaction detected!\n")
            return

        self.members[member_id].balance += amount

        self.transactions[tx_id] = {
            "Type": "Deposit",
            "Member": member_id,
            "Amount": amount,
        }

        self.transaction_queue.append(tx_id)
        self.undo_stack.append(("deposit", member_id, amount))
        self.save_data()

        print("Deposit successful.\n")

    # ---------------- WITHDRAW ----------------

    def withdraw(self):
        member_id = input("Member ID: ").strip()

        if member_id not in self.members:
            print("Member not found.\n")
            return

        amount = self._get_float_input("Withdrawal Amount: ")

        if amount > self.members[member_id].balance:
            print("Insufficient funds.\n")
            return

        tx_id = input("Transaction ID: ").strip()

        if not tx_id:
            print("Transaction ID cannot be empty.\n")
            return

        if tx_id in self.transactions:
            print("Duplicate transaction detected.\n")
            return

        self.members[member_id].balance -= amount

        self.transactions[tx_id] = {
            "Type": "Withdrawal",
            "Member": member_id,
            "Amount": amount,
        }

        self.transaction_queue.append(tx_id)
        self.undo_stack.append(("withdraw", member_id, amount))
        self.save_data()

        print("Withdrawal successful.\n")

    # ---------------- LOANS ----------------

    def apply_loan(self):
        member_id = input("Member ID: ").strip()

        if member_id not in self.members:
            print("Member not found.\n")
            return

        amount = self._get_float_input("Loan Amount: ")
        priority = self._get_int_input("Priority (1 = Highest): ")

        # Counter breaks ties if two applications share the exact same priority
        self.loan_counter += 1
        heapq.heappush(
            self.loan_heap, (priority, self.loan_counter, member_id, amount)
        )
        self.save_data()

        print("Loan application submitted.\n")

    def process_loan(self):
        if not self.loan_heap:
            print("No pending loans.\n")
            return

        priority, _, member_id, amount = heapq.heappop(self.loan_heap)

        # Deposit loan funds directly to the member's balance
        if member_id in self.members:
            self.members[member_id].balance += amount
            self.save_data()

            print("\nLoan Approved & Disbursed")
            print("----------------")
            print("Member   :", member_id)
            print("Amount   :", amount)
            print("Priority :", priority)
            print()
        else:
            print(f"\nLoan popped, but member {member_id} no longer exists.\n")

    # ---------------- SEARCH ----------------

    def search_transaction(self):
        tx_id = input("Enter Transaction ID: ").strip()

        if tx_id in self.transactions:
            tx = self.transactions[tx_id]
            print(f"\nType: {tx['Type']} | Member: {tx['Member']} | Amount: {tx['Amount']}")
        else:
            print("Transaction not found.")

        print()

    # ---------------- UNDO ----------------

    def undo(self):
        if not self.undo_stack:
            print("Nothing to undo.\n")
            return

        action, member_id, amount = self.undo_stack.pop()

        if member_id not in self.members:
            print("Member associated with this action no longer exists.\n")
            return

        if action == "deposit":
            self.members[member_id].balance -= amount
        elif action == "withdraw":
            self.members[member_id].balance += amount

        self.save_data()  # Persist changes for ALL undo types
        print(f"Last transaction ('{action}' of ${amount}) reversed.\n")

    # ---------------- REPORT ----------------

    def report(self):
        print("\n========== MEMBER REPORT ==========")

        if not self.members:
            print("No members registered.\n")
            return

        for member in self.members.values():
            print("-----------------------------------")
            print("Member ID :", member.member_id)
            print("Name      :", member.name)
            print(f"Balance   : ${member.balance:,.2f}")

        print("-----------------------------------\n")


# ================= MAIN MENU =================

def main():
    system = FinCoop()

    while True:
        print("========== FINCOOP ==========")
        print("1. Register Member")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Apply Loan")
        print("5. Process Loan")
        print("6. Search Transaction")
        print("7. Undo Transaction")
        print("8. Reports")
        print("9. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            system.register_member()
        elif choice == "2":
            system.deposit()
        elif choice == "3":
            system.withdraw()
        elif choice == "4":
            system.apply_loan()
        elif choice == "5":
            system.process_loan()
        elif choice == "6":
            system.search_transaction()
        elif choice == "7":
            system.undo()
        elif choice == "8":
            system.report()
        elif choice == "9":
            print("\nThank you for using FinCoop.")
            break
        else:
            print("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    main()1