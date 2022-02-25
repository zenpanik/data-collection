import os
import json
import requests
import unicodedata
from pathlib import Path
import pandas as pd


class uniswapCollector():

    def __init__(
        self,
        version=3,
        url=None,
        headers=None
    ):
        """
        """
        self.result = {}
        if type(headers) == dict:
            self.headers = headers
        else:
            self.headers = {'content-type': 'application/json'}
        
        self.version = version

        if version == 2:
            self.url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
        elif version == 3:
            self.url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

    
    @staticmethod
    def remove_control_characters(s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

    @staticmethod
    def to_epoch(**kwargs):
        """returns: NumPy ndarray."""
        stamps = pd.date_range(**kwargs)
        return stamps.view('int64') // 1000000000

    def query2payload(self, query):
        """
        return subgraph payload from input GraphQL query
        """

        payload = f"""
            {{"query" : "{query}"}}

            """

        return self.remove_control_characters(payload)

    @staticmethod
    def read_query(version, qry_name):
        """
        """
        path = f"v{version}/utils/queries/{qry_name}.thegraph"

        query = Path(path).read_text()

        return query


    def execute(self, name, query=None, verbose=False, debug=False):
        """
        Execute single query
        Used where the result is less than 1000 size
        """

        if not query:
            query = self.read_query(self.version, name)

        error = None
        result = None

        payload = self.query2payload(query)
        
        if debug:
            print("payload")
            print(payload)
            
        r = requests.post(self.url, data=payload, headers=self.headers)
        if verbose:
            print(f'Status code: {r.status_code}')

        if r.status_code > 200:
            if verbose:
                print(r.content)
        else:
            r_json = json.loads(r.content)
            if 'data' in r_json.keys():
                n = len(r_json['data'][name])
                result = pd.DataFrame(r_json['data'][name])
            elif 'errors' in r_json.keys():
                n = 0
                error = r_json['errors']

            if verbose:
                print("Total rows fetched from the query", n)
                if error:
                    print(error)

        return result, error



    def execute_many(
        self, 
        name,  
        base_query=None, 
        offset=0, 
        chunksize=1000, 
        verbose=False, 
        debug=False, 
        pool_id=None, 
        tick_id=None):
        """
        Execute many queries 
        Used where the result is more than 1000 size and need to iterate with offeset and chunksize parameters
        if querying for tickDayDatas provide **pool_id** as well

        """

        if not base_query:
            base_query = self.read_query(self.version, name)

        # for tickDayDatas need to replace pool_id with corresponding pool_id
        if name == "ticks":
            base_query = base_query.replace('POOL_ID', str(pool_id))

        if name == "tickDayDatas":
            base_query = base_query.replace('TICK_ID', str(tick_id))
        
        if debug:
            print("base_query")
            print(base_query)

        errors = []
        results = []
        while True:
            
            result = None
            error = None

            query = base_query.replace('CHUNKSIZE', str(chunksize)).replace('OFFSET', str(offset))
            if debug:    
                print("query")
                print(query)

            result, error = self.execute(name=name, query=query, verbose=verbose, debug=debug)
            
            if debug:
                print("result")
                print(result)
                print("error")
                print(error)

            if not error and not isinstance(result, pd.DataFrame):
                break
            
            if not error:
                n = len(result)
                results.append(result)
            else:
                n = 0
                errors.append(error)

            if n < chunksize:
                break
            else:
                offset += chunksize
            
            if verbose:
                print("Total rows fetched from the query", n)
                print('Offset ', offset)
                if errors:
                    print(errors)

        return results, errors

