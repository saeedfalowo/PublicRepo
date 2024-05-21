import glob
import os
import subprocess
import json
import pandas as pd
import numpy as np
import datetime
from tabula import read_pdf
import psycopg2


def collect_files():
    base_dir = f"{os.path.abspath('')}/statements"
    file_paths = []
    pattern = f"{base_dir}/*.pdf"
    file_paths = [path for path in glob.glob(pattern)]

    return file_paths


def read_log_json():
    f = open(f"{os.path.abspath('')}/statements/log/history.json", "r")
    file_content = f.read()
    f.close()
    data = json.loads(file_content) if file_content else []
    return data


def connect_to_db():
    conn = psycopg2.connect(
        host="ep-curly-limit-741542.eu-central-1.aws.neon.tech",
        database="neondb",
        user="tyslogo",
        password="Go6cKQkmbOl8"
    )
    conn.autocommit = True
    return conn


def query_table(query):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query)
    print("The number of rows: ", cur.rowcount)

    row = cur.fetchone()
    cnt = 0

    while row is not None:
        print(row)
        row = cur.fetchone()
        cnt += 1

        if cnt >= 5:
            break

    cur.close()
    conn.close()


def insert_into_bank_statement_table(dict_list: list, bank: str, file_path):
    insert_values_list = []
    for row in dict_list:

        value = f"('{row['Date']}', '{row['Description']}', '{row['Money_out']}', '{row['Money_in']}', '{row['Balance']}', '{file_path}', current_timestamp)"
        insert_values_list.append(value)

    insert_str = ",\n".join(insert_values_list)
    # print(insert_str)

    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("CREATE SCHEMA IF NOT EXISTS statement")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS statement.{bank}_raw (
        id              serial primary key,
        date            text,
        description     text,
        money_out       text,
        money_in        text,
        balance         text,
        file_path       text,
        time_inserted   timestamp
    );""")
    
    cur.execute(f"""
        INSERT INTO statement.{bank}_raw (date, description, money_out, money_in, balance, file_path, time_inserted)
        VALUES {insert_str};
    """)

    cur.close()
    # conn.commit()
    conn.close()
    return


def process_test_statement(path: str):
    df_list = read_pdf(path, stream=True, guess=True, pages='all',
                       multiple_tables=True,
                       pandas_options={'header': None}
                       )
    # df_list = read_pdf(path)

    df = pd.concat(df_list)
    # drop first row
    df = df.drop([0])

    # Assign row as column headers
    df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)
    df["Date"] = df["Date Details"].str.split(" ").str[:2]
    df["Date"] = df["Date"].str.join(" ")
    df["Details"] = df["Date Details"].str.split(" ").str[2:]
    df["Details"] = df["Details"].str.join(" ")

    df = df.drop(["Date Details"], axis=1)

    df = df.rename(columns={'Details': 'Description', 'Withdrawals': 'Money_out', "Deposits": "Money_in"})
    df = df[["Date", "Description", "Money_out", "Money_in", "Balance"]]

    return df


def retrieve_barclays_transactions(df: pd.DataFrame, indx: int):
    transaction_df = df
    transaction_df = transaction_df.rename(columns=transaction_df.iloc[0]).drop(
        transaction_df.index[0]
    ).reset_index(drop=True)

    def _extract_date(df: pd.DataFrame, target_col: str):
        return df[target_col].str.split(" ").apply(
            lambda ls: " ".join(ls[:2])
            if len(ls[0]) > 1 and ls[0].isnumeric()
            else " ".join(
                [
                    el for el in [
                        "".join(ls[:2]), ls[2] if len(ls) > 2 else np.nan
                    ]
                    if "".join(ls[:2]).isnumeric()
                ]
            )
        )
    
    def _remove_date(df: pd.DataFrame, target_col: str):
        return transaction_df[target_col].str.split(" ").apply(
            lambda ls: " ".join(ls) if not ls[0].isnumeric() else
            " ".join(ls[2:]) if len(ls) > 2 and not ls[1].isnumeric() else " ".join(ls[3:])
        )

    if indx == 0:
        transaction_df["Date"] = _extract_date(transaction_df, "Date Description Money out")
        transaction_df["Description Money out"] = _remove_date(transaction_df, "Date Description Money out")
        transaction_df["Description"] = transaction_df["Description Money out"].str.split(" ").apply(
            lambda ls: " ".join(ls) if "." not in ls[-1] else " ".join(ls[:-1])
        )
        transaction_df["Money out"] = transaction_df["Description Money out"].str.split(" ").apply(
            lambda ls: ls[-1] if "." in ls[-1] else np.nan
        )
        transaction_df = transaction_df.drop(["Date Description Money out", "Description Money out"], axis=1)
    else:
        transaction_df["Date"] = _extract_date(transaction_df, "Date Description")
        # transaction_df["Description"] = transaction_df["Date Description"].str.split(" ").apply(
        #     lambda ls: " ".join(ls) if not ls[0].isnumeric() else
        #     " ".join(ls[2:]) if len(ls) > 2 and not ls[1].isnumeric() else " ".join(ls[3:])
        # )
        transaction_df["Description"] = _remove_date(transaction_df, "Date Description")
        transaction_df = transaction_df.drop(["Date Description"], axis=1)
        # print(transaction_df)

    transaction_df.columns = transaction_df.columns.str.replace(" ", "_")
    transaction_df = transaction_df[["Date", "Description", "Money_out", "Money_in", "Balance"]]
    
    return transaction_df


def process_barclays_statement(path: str):
    transaction_df_list = []
    df_list = read_pdf(path, stream=True, guess=True, pages='all',
                       multiple_tables=True,
                       pandas_options={'header': None}
                       )
    # df_list = read_pdf(path)

    for i in range(len(df_list)):
        el = df_list[i]
        if i == 0:
            address_n_isa_df = el.iloc[:10]
            # print(address_n_isa_df)
            address_df = address_n_isa_df.iloc[:4, [0]]
            address_df = address_df.rename(columns={0: 'address'})
            # print(address_df)
            acc_summary_df = address_n_isa_df.iloc[:9, [3]]
            acc_summary_df = acc_summary_df.rename(columns={3: 'acc_summary'})
            # print(acc_summary_df)
            transaction_df = retrieve_barclays_transactions(el.iloc[17:], i)
            
            # print(transaction_df)

        else:
            # print(el.head(50))
            # print(el.iloc[1:])
            transaction_df = retrieve_barclays_transactions(el.iloc[1:], i)
        
        print(f"num row in df: {len(transaction_df)}")
        # print(transaction_df)
        transaction_df_list.append(transaction_df)
    
    print(f"length of df_list: {len(df_list)}")


    df = pd.concat(transaction_df_list, ignore_index=True)
    # print(f"num row in df: {len(df)}")
    # print(df)
    # drop first row

    return df


def retrieve_santander_transactions(df: pd.DataFrame, indx: int):
    transaction_df = df[[0, 1, 3, 4]] if indx == 0 else df
    transaction_df = transaction_df.rename(columns=transaction_df.iloc[0]).drop(
        transaction_df.index[0]
    ).reset_index(drop=True)
    # print(transaction_df)

    def _extract_date(df: pd.DataFrame, target_col: str):
        return df[target_col].str.split(" ").apply(
            lambda ls: " ".join(ls[:2])
            if len(ls[0]) > 2 and ls[0][:-2].isnumeric() else np.nan
        )
    
    def _remove_date(df: pd.DataFrame, target_col: str):
        return transaction_df[target_col].str.split(" ").apply(
            lambda ls: " ".join(ls) if not len(ls[0]) > 2 or not ls[0][:-2].isnumeric() else
            " ".join(ls[2:])
        )

    if indx == 0:
        transaction_df["Date"] = _extract_date(transaction_df, "Date Description")
        transaction_df["Description"] = _remove_date(transaction_df, "Date Description")
        transaction_df = transaction_df.drop(["Date Description"], axis=1)
        # print(transaction_df)
    else:
        # print(transaction_df)
        pass

    transaction_df.columns = transaction_df.columns.str.replace("£ ", "").str.replace(" ", "_")
    transaction_df = transaction_df[["Date", "Description", "Money_out", "Money_in", "Balance"]]
    # print(transaction_df)
    
    return transaction_df


def process_santander_statement(path: str):
    if "santander" not in path:
        return None
    
    transaction_df_list = []
    df_list = read_pdf(path, stream=True, guess=True, pages='all',
                       multiple_tables=True,
                       pandas_options={'header': None}
                       )
    # df_list = read_pdf(path)

    for i in range(len(df_list)):
        el = df_list[i]
        # print(el)
        if i == 0:
            acc_summary_df = el.iloc[:3, [0, 4]]
            acc_summary_df = acc_summary_df.rename(columns={0: 'Description', 4: "Amount"})
            # print(acc_summary_df)
            transaction_df = retrieve_santander_transactions(el.iloc[3:], i)
            # print(transaction_df)

        else:
            # print(el.head(50))
            transaction_df = retrieve_santander_transactions(el, i)
        
        print(f"num row in df: {len(transaction_df)}")
        # print(transaction_df.head())
        transaction_df_list.append(transaction_df)
    
    print(f"length of df_list: {len(df_list)}")
    # print(f"col names: {transaction_df_list[0].columns}")
    # print(f"col names: {transaction_df_list[1].columns}")
    # print(f"row count: {len(transaction_df_list[0])}")
    # print(f"row count: {len(transaction_df_list[1])}")


    df = pd.concat(transaction_df_list, ignore_index=True)
    print(f"num row in df: {len(df)}")
    # print(df[["Date", "Money in", "Money out", "£ Balance"]])
    # drop first row

    return df


def main():
    pd.set_option('display.max_colwidth', None)
    # pd.set_option('max_columns', 10)
    pd.options.display.max_columns = 10
    log = read_log_json()
    # log = []
    file_paths = collect_files()
    print(file_paths)

    for path in file_paths:
        try:
            bank = path.split("/")[-1].split("_")[0]
            print(f"BANK: {bank}\n")
            if bank == "test":
                df = process_test_statement(path)
            elif bank == "barclays":
                df = process_barclays_statement(path)
            elif bank == "santander":
                df = process_santander_statement(path)
            else:
                df = None

            df_dict_list = json.loads(df.to_json(orient="records"))
            insert_into_bank_statement_table(df_dict_list, bank, path)

            # log processed file
            log.append({
                "file_name": path.split("/")[-1],
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print(e)
            print(f"file not processed:\n{path}")

    log_df = pd.DataFrame.from_dict(log)
    # print(log_df)
    log_json = log_df.to_json(orient="records", indent=4)
    # print(log_json)
    f = open(f"{os.path.abspath('')}/statements/log/history.json", "w")
    f.write(log_json)
    f.close()
    # subprocess.run(["cat", f"{os.path.abspath('')}/statements/log/history.json"])


if __name__ == "__main__":
    main()
