import re
import pandas as pd


class StatementParser:
    def __init__(self):
        pass

    def _filter_regex_transaction(self, raw_data):

        # last segment of regex is Cr\ which is common in UBI statement as credit balance, but it might differ
        regex = r"(\d+ \d{2}/\d{2}/\d{4}.*?\(Cr\))"
        return re.findall(regex, raw_data, re.DOTALL)

    def _convert_transaction_to_dict(self, transactions):
        statements = []
        for transaction in transactions:
            clean_line = transaction.replace("\n", " ")

            # Combine debit and credit regex patterns
            regex = r"(\d+) (\d{2}/\d{2}/\d{4}) ([A-Z0-9]+) (.*?) (\d+\.\d+) \((Dr|Cr)\)"

            match = re.search(regex, clean_line)

            if match:
                groups = match.groups()
                transaction_data = {
                    "serial": groups[0],
                    "date": groups[1],
                    "transid": groups[2],
                    "summary": groups[3],
                    "debit": groups[-2] if groups[-1] == "Dr" else "",
                    "credit": groups[-2] if groups[-1] == "Cr" else ""
                }
                statements.append(transaction_data)

        return statements

    def parse_statement(self, filename):
        with open(filename, 'r') as file:
            raw_statement = file.read()

        transactions = self._filter_regex_transaction(raw_statement)
        statements = self._convert_transaction_to_dict(transactions)

        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(statements)
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        df['debit'] = pd.to_numeric(df['debit'], errors='coerce')
        df['credit'] = pd.to_numeric(df['credit'], errors='coerce')
        df['serial'] = pd.to_numeric(df['serial'], errors='coerce')

        df = df.drop_duplicates(subset='transid', keep='first')
        df['serial'] = range(1, len(df) + 1)
        # Save the DataFrame to an Excel file
        df.to_excel('output1.xlsx', index=False)














