from pubkeys import create_pubkeys
from structs import Node, Bucket
import random
import statistics

NODES = 1238
BUCKETS = 32
BASTARD_PERCENTAGE = 30
BATCH_SIZE = 64

def main():
    random.seed(BUCKETS)
    algs_to_test = ["random"] #check algorithms.py for available algs to use
    #Simulation
    for alg in algs_to_test:
        buckets = []

        # Spawn nodes
        pubkeys = create_pubkeys(NODES)
        nodes = []
        for pubkey in pubkeys:
            node = Node(pubkey)
            node.bucket_id = node.bucket_id%(BUCKETS)
            nodes.append(node)

        #Set bastards nodes
        bad_nodes = random.sample(nodes, k=int(NODES*BASTARD_PERCENTAGE/100))
        for node in bad_nodes:
            node.forward = False


        for i in range (0,BUCKETS):
            local_nodes = []
            for node in nodes:
                if node.bucket_id == i:
                    local_nodes.append(node)
            bucket = Bucket(local_nodes, alg)
            bucket.id = i
            buckets.append(bucket)



        for bucket in buckets:
            bucket.spread_batch(BATCH_SIZE)


        failed_shreds = []
        success_shreds = []
        failed_batches = 0
        for bucket in buckets:
            failed_shreds.append(bucket.failed_shreds)
            if bucket.failed_shreds > BATCH_SIZE/2:
                failed_batches += 1
            success_shreds.append(bucket.successful_shreds)

        print("SIMULATION COMPLETE\n"
              f"Algorithm: {alg}\n"
              f"Success shreds: Mean:{statistics.mean(success_shreds)}    Median:{statistics.median(success_shreds)}\n"
              f"Failed shreds: Mean:{statistics.mean(failed_shreds)}    Median:{statistics.median(failed_shreds)}\n"
              f"Failed batches: {failed_batches}")


if __name__ == "__main__":
    main()