import json
import socket
from itertools import product
import re
from itertools import product, chain
from collections import deque
import heapq

def apply_gate(gate, bits, indices):
    new_bits = bits[:]
    if gate == "NOT":
        new_bits[indices[0]] ^= 1
    elif gate == "CNOT":
        if new_bits[indices[0]] == 1:
            new_bits[indices[1]] ^= 1
    elif gate == "TOFFOLI":
        if new_bits[indices[0]] == 1 and new_bits[indices[1]] == 1:
            new_bits[indices[2]] ^= 1
    return new_bits

def generate_truth_table(gates, num_bits):
    truth_table = {}
    for i in range(2**num_bits):
        input_bits = [(i >> j) & 1 for j in range(num_bits)]
        output_bits = input_bits[:]
        for gate, indices in gates:
            output_bits = apply_gate(gate, output_bits, indices)
        truth_table[tuple(input_bits)] = tuple(output_bits)
    return truth_table

def is_equivalent(truth_table1, truth_table2):
    return truth_table1 == truth_table2

def bruteforce_optimal_circuit(original_gates, num_bits, max_depth):
    original_truth_table = generate_truth_table(original_gates, num_bits)
    best_circuit = original_gates
    best_size = len(original_gates)
    gates = ["NOT", "CNOT", "TOFFOLI"]
    indices_options = {
        "NOT": [[i] for i in range(num_bits)],
        "CNOT": [[i, j] for i in range(num_bits) for j in range(num_bits) if i != j],
        "TOFFOLI": [[i, j, k] for i in range(num_bits) for j in range(num_bits) for k in range(num_bits) if i != j and j != k and i != k]
    }

    # Using a priority queue to prioritize shorter circuits first
    circuits_queue = []
    heapq.heappush(circuits_queue, (0, []))  # (circuit length, circuit definition)

    while circuits_queue:
        current_size, current_gates = heapq.heappop(circuits_queue)
        if current_size > best_size:
            continue

        current_truth_table = generate_truth_table(current_gates, num_bits)
        if is_equivalent(current_truth_table, original_truth_table) and current_size < best_size:
            best_circuit = current_gates
            best_size = current_size

        if current_size + 1 > max_depth or current_size + 1 >= best_size:
            continue

        for gate in gates:
            for indices in indices_options[gate]:
                new_gates = current_gates + [(gate, indices)]
                heapq.heappush(circuits_queue, (current_size + 1, new_gates))

    return best_circuit


buffer = ""
cpt = 0

while cpt < 5:
    cpt = 0
    host, port = 'challenges.404ctf.fr', 32274
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    try:
        while True:
            
            part = sock.recv(4096)
            print(part)
            if not part:
                break
            buffer += part.decode()

            # Attempt to extract and process JSON when we have complete chunks.
            try:
                while '{' in buffer and '}' in buffer:
                    start = buffer.index('{')
                    end = buffer.index('}', start) + 1
                    data = buffer[start:end]
                    buffer = buffer[end:]

                    # Parsing the given circuit
                    original_circuit = json.loads(data)['gates']

                    # Finding the optimal circuit
                    optimal_circuit = bruteforce_optimal_circuit(original_circuit, 3, 3)

                    # Sending the solution to the server
                    solution = json.dumps({'gates': optimal_circuit, 'bits': 3})
                    cpt = cpt+1
                    print(cpt)
                    sock.sendall(f"{solution}\n".encode())
                    
            except json.JSONDecodeError as e:
                print("JSON decoding failed, waiting for more data...", e)

    finally:
        sock.close()
