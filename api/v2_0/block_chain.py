from flask import jsonify
import schemas
from api import APIBase
from common.logging_config import applogger
from common import exceptions
from . import blockchain_list



class BlockChainAPI(APIBase):
    '''API for working with Block Chain'''
    # response_schema   = schemas.api_tracker.BlockchainSchema
    request_schema    = schemas.blockchain.BlockchainSchema
    api_rate_limit  = '10/second'
    api_url         = '/mine_block'
    api_endpoint    = 'mine_block'

    def get(self):
        last_block = blockchain_list.get_last_block()
        prev_proof = last_block.data.get("proof")
        new_proof = blockchain_list.proof_of_work(prev_proof)
        prev_hash = blockchain_list.hash_block(last_block)
        new_block = blockchain_list.insertBlock(prev_hash,new_proof)
        return jsonify(new_block.data)
    
class FullBlockChainAPI(APIBase):
    '''API for working with the Full BlockChain '''
    
    request_schema    = schemas.blockchain.BlockchainSchema
    api_rate_limit  = '1/second'
    api_url         = '/get_chain'
    api_endpoint    = 'get_chain'

    def get(self):
        result = []
        test_node = blockchain_list.head
        while(test_node is not None):
            result.append(test_node.data)
            test_node = test_node.next            
        return jsonify(result)
      