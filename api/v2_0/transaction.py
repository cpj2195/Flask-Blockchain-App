from flask import jsonify
import schemas
from api import APIBase
from common.logging_config import applogger
from common import exceptions
import requests
from . import blockchain_list,node_address




class TransactionAPI(APIBase):
    '''API for adding a transaction in the blockchain'''
    # response_schema   = schemas.api_tracker.BlockchainSchema
    request_schema    = schemas.blockchain.BlockchainSchema
    api_rate_limit  = '10/second'
    api_url         = '/add_transaction'
    api_endpoint    = 'add_transaction'

    def post(self):
        args = self.get_parsed_request_data()
        transaction_keys = ["sender","receiver","amount"]
        if not all(key in args for key in transaction_keys):
            raise exceptions.BadRequest("Please include only sender,receiver and amount parameters")
        index = blockchain_list.add_transaction(args.get("sender"),args.get("receiver"),args.get("amount"))
        result = {"message":"The Transaction has been successfully added"}
        return jsonify(result)
    