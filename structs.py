import algorithms as algs
import hashlib
import random

ALG_MAP = {
    "random": algs.select_root_random,
}

class Node:
    def __init__(self, pubkey:str, forward:bool=True):
            self.pubkey = pubkey
            self.bucket_id = hash(pubkey)
            self.forward = forward


    def send(self) -> bool:
        return self.forward



    def get_id(self):
        self.node_id = hash(self.pubkey)

class Bucket:
    def __init__(self, nodes: list, bucket_alg:str, batch_size:int=64):
        self.nodes = nodes
        self.alg = ALG_MAP[bucket_alg]
        self.bucket_root = None
        self.successful_shreds = 0
        self.failed_shreds = 0
        self.total_shreds = 0
        self.batch_size = batch_size
        self.failed_blocks = 0
        self.id = None

    def spread_batch(self, batch_size:int):
        for _ in range(0, batch_size):
            self.bucket_root = self.alg(self.nodes)
            if self.nodes[self.bucket_root].send():
                self.successful_shreds += 1
            else:
                self.failed_shreds += 1
            self.total_shreds += 1