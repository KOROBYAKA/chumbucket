import random
import algorithms as algs

def pubkey_to_id(pubkey: str) -> int:
    print("no yet")
    return 0


class Node:
    def __init__(self, pubkey:str, forwarding_probability:int, bucket_id:int=None):
            self.pubkey = pubkey
            self.node_id = None
            self.bucket_id = bucket_id
            self.forwarding_probability = forwarding_probability

    def send(self) -> bool:
        if random.randint(1,100) > self.forwarding_probability:
            return False
        return True

    def get_id(self):
        self.node_id = pubkey_to_id(self.pubkey)
class Bucket:
    def __init__(self, nodes: list, bucket_id:int, batch_size:int=64):
        self.nodes = self.map_nodes(nodes)
        self.bucket_id = bucket_id
        self.bucket_root = None
        self.succeed_shreds = 0
        self.failed_shreds = 0

    def map_nodes(self, nodes):
        print(nodes)

    def spread_batch(self):
        self.bucket_root = algs.select_root_1(self.nodes)
        if self.nodes[self.bucket_root].send():
            self.succeed_shreds += 1
        else:
            self.failed_shreds += 1