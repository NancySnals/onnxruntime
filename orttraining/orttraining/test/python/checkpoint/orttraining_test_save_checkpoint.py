#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

################################################################################
# Refer to orttraining_test_checkpoint.py for an overview about Checkpoint tests
################################################################################

import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _test_helpers import distributed_setup, create_orttrainer_and_save_checkpoint

def single_node_full_precision(device = 'cuda', checkpoint_dir = 'checkpoint_dir/single_node/full_precision/'):
    opts = {'device' : {'id' : device},
            'debug' : {'deterministic_compute': True}}
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir)

def single_node_mixed_precision(device = 'cuda', checkpoint_dir = 'checkpoint_dir/single_node/mixed_precision/'):
    opts = {
                'device' : {'id' : device},
                'mixed_precision':
                {
                    'enabled': True
                },
                'debug' : {'deterministic_compute': True}
            }
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir)

@distributed_setup
def data_parallelism_full_precision(world_rank, world_size, device, checkpoint_dir = 'checkpoint_dir/data_parallelism/full_precision/'):
    opts = {
                'device' : {'id' : device},
                'distributed' :
                {
                    'world_rank' : world_rank,
                    'world_size' : world_size,
                    'allreduce_post_accumulation' : True
                },
                'debug' : {'deterministic_compute': True}
            }
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir if world_rank == 0 else None)

@distributed_setup
def data_parallelism_mixed_precision(world_rank, world_size, device, checkpoint_dir = 'checkpoint_dir/data_parallelism/mixed_precision/'):
    opts = {
                'device' : {'id' : device},
                'mixed_precision':
                {
                    'enabled': True
                },
                'distributed' :
                {
                    'world_rank' : world_rank,
                    'world_size' : world_size,
                    'allreduce_post_accumulation' : True
                },
                'debug' : {'deterministic_compute': True}
            }
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir if world_rank == 0 else None)

@distributed_setup
def distributed_zero_full_precision(world_rank, world_size, device, checkpoint_dir = 'checkpoint_dir/distributed_zero/full_precision/'):
    opts = {
                'device' : {'id' : device},
                'distributed' :
                {
                    'world_rank' : world_rank,
                    'world_size' : world_size,
                    'allreduce_post_accumulation' : True,
                    'deepspeed_zero_optimization':
                    {
                        'stage': 1
                    }
                },
                'debug' : {'deterministic_compute': True}
            }
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir, state_dict_key_name='state_dict_'+str(world_rank))

@distributed_setup
def distributed_zero_mixed_precision(world_rank, world_size, device, checkpoint_dir = 'checkpoint_dir/distributed_zero/mixed_precision/'):
    opts = {
                'device' : {'id' : device},
                'mixed_precision':
                {
                    'enabled': True
                },
                'distributed' :
                {
                    'world_rank' : world_rank,
                    'world_size' : world_size,
                    'allreduce_post_accumulation' : True,
                    'deepspeed_zero_optimization':
                    {
                        'stage': 1
                    }
                },
                'debug' : {'deterministic_compute': True}
            }
    create_orttrainer_and_save_checkpoint(device, opts, checkpoint_dir, state_dict_key_name='state_dict_'+str(world_rank))

function_map = {
    'single_node_full_precision': single_node_full_precision,
    'single_node_mixed_precision': single_node_mixed_precision,
    'data_parallelism_full_precision': data_parallelism_full_precision,
    'data_parallelism_mixed_precision': data_parallelism_mixed_precision,
    'distributed_zero_full_precision': distributed_zero_full_precision,
    'distributed_zero_mixed_precision': distributed_zero_mixed_precision
}
parser = argparse.ArgumentParser(description='Save states of trainers')
parser.add_argument('--scenario', choices=function_map.keys(), help='training scenario to save states', required=True)
parser.add_argument('--checkpoint_dir', help='path to the directory where checkpoints can be saved', required=True)
args = parser.parse_args()
function_map[args.scenario](checkpoint_dir = args.checkpoint_dir)
