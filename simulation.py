import argparse

from pubkeys import create_pubkeys
from structs import Node, Bucket
import random
import statistics
import argparse
import json

NODES = 128
BUCKETS = 32
BASTARD_PERCENTAGE = 80
BATCH_SIZE = 64
SEED_CONTS = 228
SIMULATIONS = 10

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, help="Simulation ID", default=1)
    parser.add_argument("--bastard_percentage", type=int, help="Bastard percentage", default=BASTARD_PERCENTAGE)
    parser.add_argument("-n", "--nodes", type=int, help="Number of nodes", default=NODES)
    parser.add_argument("-b","--buckets", type=int, help="Number of buckets", default=BUCKETS)
    parser.add_argument("--batch_size", type=int, help="Batch size", default=BATCH_SIZE)
    parser.add_argument("-s","--simulations", type=int, help="Seed", default=SIMULATIONS)
    args = parser.parse_args()
    random.seed(SEED_CONTS)
    for x in range(0, args.simulations):
        algs_to_test = ["random"] #check algorithms.py for available algs to use
        #Simulation
        for alg in algs_to_test:
            buckets = []
            empty_buckets = 0
            # Spawn nodes
            pubkeys = create_pubkeys(args.nodes, args.id)
            nodes = []
            for pubkey in pubkeys:
                node = Node(pubkey)
                node.bucket_id = node.bucket_id%(args.buckets)
                nodes.append(node)

            #Set bastards nodes
            bad_nodes = random.sample(nodes, k=int(args.nodes * args.bastard_percentage/100))
            for node in bad_nodes:
                node.forward = False


            for i in range (0,args.buckets):
                local_nodes = []
                for node in nodes:
                    if node.bucket_id == i:
                        local_nodes.append(node)
                bucket = Bucket(local_nodes, alg)
                bucket.id = i
                buckets.append(bucket)

            print(f"buckets_len: {len(buckets)}")

            for bucket in buckets:
                if len(bucket.nodes) == 0:
                    empty_buckets += 1
                    continue
                bucket.spread_batch(args.batch_size)


            failed_shreds = []
            success_shreds = []
            failed_batches = 0
            for bucket in buckets:
                failed_shreds.append(bucket.failed_shreds)
                if bucket.failed_shreds > BATCH_SIZE/2:
                    failed_batches += 1
                success_shreds.append(bucket.successful_shreds)

            '''print("SIMULATION COMPLETE\n"
                  f"Algorithm: {alg}\n"
                  f"Success shreds: Mean:{statistics.mean(success_shreds)}    Median:{statistics.median(success_shreds)}\n"
                  f"Failed shreds: Mean:{statistics.mean(failed_shreds)}    Median:{statistics.median(failed_shreds)}\n"
                  f"Failed batches: {failed_batches}    "
                  f"Empty buckets: {empty_buckets}")'''

            # Save the result
            save_data = json.dumps(
                {'bastard_percentage': args.bastard_percentage, 'success_shreds': success_shreds,
                  'failed_shreds': failed_shreds, 'batch_size': args.batch_size, 'empty_buckets': empty_buckets,
                  'alg': alg, 'buckets': len(buckets)}
            )

            with open("results.jsonl", "a") as json_file:
                json_file.write(f"{save_data}\n")
                json_file.close()





if __name__ == "__main__":
    main()