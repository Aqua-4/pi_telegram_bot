# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 00:42:21 2022

@author: parashar
"""

# AUTHORIZATION:
from fyers_api import fyersModel
from fyers_api import accessToken
from datetime import date
import pandas as pd
from urllib.parse import urlparse, parse_qsl
import time
from dotenv import load_dotenv
import os
# import webbrowser

load_dotenv('fyers.env')


today = date.today()
date_str = today.strftime("%d-%m-%Y")


class FyersUtils:
    def __init__(self, print_to_bot=None):

        # in the next iteration get these from user
        redirect_url = os.environ['redirect_url']
        # The app id we get after creating the app
        self.appId = os.environ['app_id']
        # The app secret we got after creating the app.
        app_secret = os.environ['app_secret']

        self.session = accessToken.SessionModel(client_id=self.appId, secret_key=app_secret,
                                                redirect_uri=redirect_url, response_type="code", grant_type='authorization_code')

        self.session_response = None

        self.bot_print = print
        if print_to_bot:
            self.bot_print = print_to_bot

        data = {'symbol': [], 'timestamp': [], 'open': [],
                'high': [], 'low': [], 'close': [], 'volume': []}

        self.df = pd.DataFrame.from_dict(data)

    def __extract_auth_code(self, auth_str):
        try:
            result = urlparse(auth_str)
            query_params = dict(parse_qsl(result.query))
            return query_params['auth_code']
        except:
            return auth_str

    def _get_auth_url(self):
        auth_code_gen_url = self.session.generate_authcode()
        self.bot_print('login to the url to generate auth code')
        # return response url asking user to paste the auth_code
        self.bot_print(auth_code_gen_url)
        self.bot_print('enter the auth_code')
        return auth_code_gen_url

    def _set_auth_code(self, auth_code):
        auth_file = open(f"{date_str}.secure", "w")
        auth_code = self.__extract_auth_code(auth_code)
        auth_file.write(auth_code)
        auth_file.close()
        return auth_code

    def auth_code_gen(self, force_new_code=False):

        if force_new_code:
            self.auth_code_gen_url = self._get_auth_url()
            #webbrowser.open(auth_code_gen_url, new=1)
            _auth_code = input()
            auth_code = self._set_auth_code(_auth_code)
            # get input here
            return auth_code

        print('force_new_code', force_new_code)
        try:
            auth_file = open(f"{date_str}.secure", "r")
            auth_code = auth_file.read()
            auth_file.close()
            if not force_new_code:
                print("using pre-existing auth code")
                return auth_code
        except:
            self.bot_print('error')
            return None

    def is_bot_session_active(self):

        auth_code = self.auth_code_gen()
        self.session.set_token(auth_code)
        self.session_response = self.session.generate_token()
        response = self.session_response

        if response.get('code') == 200:
            self.bot_print('success')
            a_t = response['access_token']
            self.fyers = fyersModel.FyersModel(
                token=a_t, is_async=False, client_id=self.appId, log_path="./")
            self.bot_print('access token has been set')
            return True
        return False

    def get_session(self):

        auth_code = self.auth_code_gen()
        self.session.set_token(auth_code)
        self.session_response = self.session.generate_token()
        response = self.session_response

        if response.get('code') == 200:
            self.bot_print('success')
            a_t = response['access_token']
            self.fyers = fyersModel.FyersModel(
                token=a_t, is_async=False, client_id=self.appId, log_path="./")
            self.bot_print('access token has been set')
        elif response.get('message') == 'Your auth code has expired. Please generate a new auth code':
            self.auth_code_gen(True)
            self.get_session()
        else:
            self.auth_code_gen(True)
            self.get_session()
            self.bot_print(response.get('message'))

    def __xform_cmd(self, cmd):
        result = {}
        result['timestamp'] = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(cmd['t']))
        result['open'] = cmd['o']
        result['high'] = cmd['h']
        result['low'] = cmd['l']
        result['close'] = cmd['c']
        result['volume'] = cmd['v']
        return result

    def get_quote_data(self, symbol_name="NSE:NIFTYBANK-INDEX"):
        meta_data = {"symbols": symbol_name}
        quote_data = self.fyers.quotes(meta_data)
        raw_data = quote_data.get('d')[0].get('v')
        cmd = raw_data.get('cmd')
        polished_data = self.__xform_cmd(cmd)
        polished_data['symbol'] = raw_data.get('short_name')
        return polished_data

    def save_df(self, data):
        new_row = pd.Series(data)
        self.df = pd.concat([self.df, new_row.to_frame().T], ignore_index=True)
        self.df.to_csv(f'./data_store/{date_str}.csv')

    def is_quote_sideways(self, symbol_name="NSE:NIFTYBANK-INDEX"):
        delta = self.df[['high', 'low', 'open', 'close']].tail().std()
        for i in delta:
            if i > 0:
                return False
        return True

    def is_low_broken(self, data, symbol_name="NSE:NIFTYBANK-INDEX"):
        if data.get('low') < self.df['low'].min():
            return True
        return False

    def is_high_broken(self, data, symbol_name="NSE:NIFTYBANK-INDEX"):
        if data.get('high') > self.df['high'].max():
            return True
        return False


"""
fu = FyersUtils()
fu.get_session()
fyers = fu.fyers


data = {"symbol": "NSE:SBIN-EQ", "resolution": "D", "date_format": "0",
        "range_from": "1622097600", "range_to": "1622097685", "cont_flag": "1"}


fyers.history(data)


data = {"symbols": "NSE:NIFTYBANK-INDEX"}
quote_data = fyers.quotes(data)

quote_data.get('d')[0].get('v')
"""
