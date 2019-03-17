from flask import jsonify
import schemas
from api import APIBase
from common.logging_config import applogger
from common import exceptions
import requests
from . import blockchain_list,node_address




class TransactionAPI(APIBase):
    '''API for adding a transaction in the blockchain'''
    request_schema    = schemas.transaction.TransactionAPISchema
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


class AddNodeAPI(APIBase):
    '''API for adding a transaction in the blockchain'''
    request_schema    = schemas.transaction.AddNodeAPISchema
    api_rate_limit  = '10/second'
    api_url         = '/connect_node'
    api_endpoint    = 'connect_node'

    def post(self):
        args = self.get_parsed_request_data()
        node_addresses = args.get("nodes")
        if not node_addresses:
            for node in node_addresses:
                blockchain_list.add_node(node)
        else:
            raise exceptions.BadRequest("Please enter some node addresses in the request list")
        result = {"message":"The nodes were successfully added", "nodes":list(blockchain_list.nodes)}
        return jsonify(result)
    



class ReplaceChainAPI(APIBase):
    '''API for adding a transaction in the blockchain'''
    # request_schema    = schemas.blockchain.BlockchainSchema
    api_rate_limit  = '10/second'
    api_url         = '/replace_chain'
    api_endpoint    = 'replace_chain'

    def get(self):
        chain_replaced = blockchain_list.replace_chain()
        test_node = blockchain_list.head
        chain = []
        while(test_node is not None):
            chain.append(test_node.data)
            test_node = test_node.next
        if(chain_replaced):
            result = {"message":"The chain has been replaced","chain":chain}
        else:
            result = {"message":"The chain is the largest chain at present","chain":chain}
        return jsonify(result)
    