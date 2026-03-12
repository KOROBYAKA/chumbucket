from pubkeys import create_pubkeys
from structs import Node, Bucket

def main():

    algs_to_test = ["random"] #check algorithms.py for available algs to use
    buckets = {}
    bastard_percentage = 30
    #Spawn buckets
    for alg in algs_to_test:
        # Spawn nodes
        pubkeys = create_pubkeys(20)
        nodes = []
        for pubkey in pubkeys:
            node = Node(pubkey)
            nodes.append(node)

        bucket = Bucket(nodes, alg, bastard_percentage)
        buckets[alg] = bucket

    for bucket in buckets.values():
        for i in range(0, bucket.batch_size):
            bucket.spread_batch()

    for alg, bucket in buckets.items():
        print(f"Algorithm: {alg}\n"
              f" Bucket stats\n"
              f"Total shreds: {bucket.total_shreds}\n"
              f"Successful shreds: {bucket.successful_shreds}\n"
              f"Failed shreds: {bucket.failed_shreds}\n"
              )



if __name__ == "__main__":
    main()