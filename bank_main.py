from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import pandas as pd
import datetime

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/Create_Account")
def create_account(first_name:str,last_name:str,address:str,pin_code:int,phone_number:int,pin:str, balance:int):
    
    if len(str(phone_number)) != 10:
        return {"Message": "Invalid Phone Number Provided"}
    else:
        data = pd.read_csv('bank.csv')
        acc_num = random.randint(100000, 1000000)
        while acc_num in data['Account Number']:
            acc_num = random.randint(100000, 1000000)

        print(data.columns)

        df = {'Account Number': acc_num, 'First Name': first_name, 'Last Name': last_name, 'Address': address,'Phone Number': phone_number, 'Account Pin': pin, 'Account Balance': balance}
        data = data.append(df, ignore_index = True)
        data.drop(data.columns[data.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
        data.to_csv('bank.csv')
        
        return {"Account Number" : acc_num, 'Message' : 'Successful'}


@app.post("/Check_Account")
def check_account(account_number:int,pin:str):
    data = pd.read_csv('bank.csv',header=0)
    if account_number in data['Account Number'].values:
        x = data[data['Account Number']==account_number]['Account Pin'].values
        if str(x[0]) != pin:
            return{'Message':'Wrong Pin, Try Again!!'}
        else:
            df = data[data['Account Number']==account_number].to_dict(orient='records')
            df = df[0]
            return {'Account Number': df['Account Number'], 'First Name': df['First Name'], 'Last Name': df['Last Name'], 'Address': df['Address'],'Phone Number': df['Phone Number'], 'Account Pin': df['Account Pin'], 'Account Balance': df['Account Balance'],'Message':'Succesful!!'}
    else:
        return {'Message':'User Not Registered !!'}


@app.get("/Deposit")
def deposit(account_number:int,pin:str,deposit_money:int):
    data = pd.read_csv('bank.csv',header=0)  
    if account_number in data['Account Number'].values:
        x = data[data['Account Number']==account_number]['Account Pin'].values
        if str(x[0]) != pin:
            return{'Message':'Wrong Pin, Try Again!!'}
        else:
            data.loc[data['Account Number'].isin([account_number]), 'Account Balance'] += deposit_money
            data.drop(data.columns[data.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
            data.to_csv('bank.csv')

            df = data[data['Account Number']==account_number].to_dict(orient='records')
            df = df[0]

            trans = pd.read_csv('transaction.csv',header=0)
            df_trans = {'Account Number': account_number, 'Deposit / Withdraw': 'Deposit', 'Amount': deposit_money, 'Account Balance': df['Account Balance'], 'TimeStamp': datetime.datetime.now() }
            trans = trans.append(df_trans, ignore_index = True)
            trans.drop(trans.columns[trans.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
            trans.to_csv('transaction.csv')

            return {'Message':'Amount succesfully deposited', 'Account Balance': df['Account Balance']}

    else:
        return {'Message':'User Not Registered !!'}


@app.get("/Withdraw")
def withdraw(account_number:int,pin:str,withdraw_money:int):
    data = pd.read_csv('bank.csv',header=0)  
    if account_number in data['Account Number'].values:
        x = data[data['Account Number']==account_number]['Account Pin'].values
        if str(x[0]) != pin:
            return{'Message':'Wrong Pin, Try Again!!'}
        else:
            if (data.loc[data['Account Number'].isin([account_number]), 'Account Balance'] < withdraw_money).any():
                return {'Message':'Sufficient Balance Not Available'}
            else:
                data.loc[data['Account Number'].isin([account_number]), 'Account Balance'] -= withdraw_money
            
            data.drop(data.columns[data.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
            data.to_csv('bank.csv')

            df = data[data['Account Number']==account_number].to_dict(orient='records')
            df = df[0]

            trans = pd.read_csv('transaction.csv',header=0)
            df_trans = {'Account Number': account_number, 'Deposit / Withdraw': 'Withdraw', 'Amount': withdraw_money, 'Account Balance': df['Account Balance'], 'TimeStamp': datetime.datetime.now() }
            trans = trans.append(df_trans, ignore_index = True)
            trans.drop(trans.columns[trans.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
            trans.to_csv('transaction.csv')

            return {'Message':'Amount succesfully withdrawed', 'Account Balance': df['Account Balance']}

    else:
        return {'Message':'User Not Registered !!'}



@app.post("/Transaction_report")
def report(account_number:int,pin:str,num_days:int):
    data = pd.read_csv('bank.csv',header=0)  
    if account_number in data['Account Number'].values:
        x = data[data['Account Number']==account_number]['Account Pin'].values
        if str(x[0]) != pin:
            return{'Message':'Wrong Pin, Try Again!!'}
        else:
            trans = pd.read_csv('transaction.csv',header=0)
            start_date = datetime.datetime.now() - datetime.timedelta(days=num_days)
            trans['TimeStamp'] = pd.to_datetime(trans['TimeStamp'])
            trans.drop(trans.columns[trans.columns.str.contains('Unnamed',case = False)],axis = 1, inplace = True)
            df = trans[(trans['Account Number'] == account_number) & (trans['TimeStamp'] > start_date)].to_dict(orient='records')
            return {'Message': 'Succesful!!', 'Report': df}
    else:
        return {'Message':'User Not Registered !!'}


if __name__ == '__main__':
    pass

