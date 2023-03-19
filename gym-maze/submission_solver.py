import sys
import numpy as np
import math
import random
import json
import requests

from riddle_solvers import *

### the api calls must be modified by you according to the server IP communicated with you
#### students track --> 16.170.85.45
#### working professionals track --> 13.49.133.141
server_ip = '13.49.133.141'
prize = 0
learning_rate = 0.1
discount = 0.95
cur_state = None 
next_state = None
done = False
pre_action = 0
q_table = np.random.uniform(low=-100, high=100, size=[10,10,4])
epislon = 0.2
history = {}

def select_action(state):
    #implementation of Q learning algorithm
    if(not done and cur_state!=None and next_state!=None ):
        a=next_state+(np.argmax(q_table[next_state]))
        if cur_state==next_state:
            q_table[cur_state+(pre_action,)]=-np.inf
        elif(history[a]==True):
            q_table[a]+=-1000
        else:   
            q_cur=q_table[cur_state+(pre_action,)]
            max_fur=np.max(q_table[next_state])
            q_new=(1-learning_rate)*q_cur+learning_rate*(prize+discount*max_fur)
            q_table[cur_state+(pre_action,)]=q_new
    if(np.random.rand() > 0.4 and (not done and cur_state!=None and next_state!=None)):     
        actions = ['N', 'S', 'E', 'W']
        action_index=np.argmax(q_table[tuple(state[0])])
        action = actions[action_index]
        return action, action_index
    else:
        actions = ['N', 'S', 'E', 'W']
        random_action = random.choice(actions)
        action_index = actions.index(random_action)
        return random_action, action_index


def move(agent_id, action):
    response = requests.post(f'http://{server_ip}:5000/move', json={"agentId": agent_id, "action": action})
    return response

def solve(agent_id,  riddle_type, solution):
    response = requests.post(f'http://{server_ip}:5000/solve', json={"agentId": agent_id, "riddleType": riddle_type, "solution": solution}) 
    print(response.json()) 
    return response

def get_obv_from_response(response):
    print('Response:', response)
    directions = response.json()['directions']
    distances = response.json()['distances']
    position = response.json()['position']
    obv = [position, distances, directions] 
    return obv

        
def submission_inference(riddle_solvers):

    response = requests.post(f'http://{server_ip}:5000/init', json={"agentId": agent_id})
    obv = get_obv_from_response(response)

    while(True):
        # Select an action
        state_0 = obv
        action, action_index = select_action(state_0) # Random action
        response = move(agent_id, action)
        if not response.status_code == 200:
            print(response)
            break

        obv = get_obv_from_response(response)
        cur_state = tuple(state_0[0])
        next_state = tuple(obv)
        pre_action = action_index
        if(response.json()['riddleType'] == None):
          prize = 0
        else:
          prize = 0
        flag=cur_state+(action_index,)
        history[flag]=True
        print(response.json())

        if not response.json()['riddleType'] == None:
            solution = riddle_solvers[response.json()['riddleType']](response.json()['riddleQuestion'])
            response = solve(agent_id, response.json()['riddleType'], solution)


        # THIS IS A SAMPLE TERMINATING CONDITION WHEN THE AGENT REACHES THE EXIT
        # IMPLEMENT YOUR OWN TERMINATING CONDITION
        if np.array_equal(response.json()['position'], (9,9)):
            response = requests.post(f'http://{server_ip}:5000/leave', json={"agentId": agent_id})
            break


if __name__ == "__main__":
    agent_id = "bdZUAAFqkJ"
    riddle_solvers = {'cipher': cipher_solver, 'captcha': captcha_solver, 'pcap': pcap_solver, 'server': server_solver}
    submission_inference(riddle_solvers)
    
