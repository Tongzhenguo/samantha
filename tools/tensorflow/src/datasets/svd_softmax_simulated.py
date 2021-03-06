
import random
import logging
import json
import numpy as np

from src.dataset import DataSet

logger = logging.getLogger('simulated')


class SVDSoftmaxSimulatedDataSet(DataSet):

    def __init__(self, config=None):
        self._config = {
            'embedding_dim': 5,
            'user_vocab': 8,
            'item_vocab': 100,
            'attr_vocab': 10,
            'max_seq_len': 10,
            'min_seq_len': 2,
            'batch_size': 4,
            'page_size': 1,
            'hierarchical': False,
            'json_file': 'json_file.json',
            'item_attr_file': 'item_attr.txt',
            'item_weights_file': 'item_weights.txt',
            'user_weights_file': 'user_weights.txt',
            'attr_weights_file': 'attr_weights.txt',
            'attr_items_gamma_shape': 100.0,
            'user_gamma_shape': 1.0,
            'cluster_weight': 0.0,
        }
        if config is not None:
            self._config.update(config)
        self._user_idx = 0
        self._item2attr = None
        self._item2attr, self._attr2items, self._non_empty_attrs = self._generate_item_attr()
        self._weights = {
            'attr': np.random.rand(self._config['attr_vocab'], self._config['embedding_dim']),
        }
        self._weights['item'] = self._generate_item_weights(self._weights['attr'], self._item2attr)
        self._weights['user'] = self._generate_user_weights(self._weights['attr'])
        with open(self._config['user_weights_file'], 'w') as fout:
            for weight in self._weights['user']:
                fout.write(' '.join([str(x) for x in list(weight)]) + '\n')
        with open(self._config['attr_weights_file'], 'w') as fout:
            for weight in self._weights['attr']:
                fout.write(' '.join([str(x) for x in list(weight)]) + '\n')

    def _generate_user_weights(self, attr_weights):
        weights = []
        for i in range(self._config['user_vocab']):
            ps = np.random.dirichlet(
                np.random.gamma(
                    self._config['user_gamma_shape'], 1.0, size=[self._config['attr_vocab']]))
            weight = None
            for j in range(len(ps)):
                if ps[j] > 0.0:
                    if weight is None:
                        weight = ps[j] * attr_weights[j]
                    else:
                        weight += ps[j] * attr_weights[j]
            weights.append(list(weight))
        return np.array(weights)

    def _generate_item_weights(self, attr_weights, item2attr):
        cluster_weights = []
        for attr_idx in item2attr:
            cluster_weights.append(
                list(np.random.standard_normal(size=[self._config['embedding_dim']]) * 0.01 + attr_weights[attr_idx]))
        cluster_weights = np.array(cluster_weights)
        random_weights = np.random.rand(self._config['item_vocab'], self._config['embedding_dim'])
        item_weights = ((1.0 - self._config['cluster_weight']) * random_weights +
                        self._config['cluster_weight'] * cluster_weights)
        with open(self._config['item_weights_file'], 'w') as fout:
            for weight in item_weights:
                fout.write(' '.join([str(x) for x in list(weight)]) + '\n')
        return item_weights

    def _generate_item_attr(self):
        p = np.random.dirichlet(
            np.random.gamma(self._config['attr_items_gamma_shape'], 1.0, size=[self._config['attr_vocab']]))
        item2attr = np.random.choice(range(self._config['attr_vocab']), size=[self._config['item_vocab']], p=p)
        attr2items = [[] for _ in range(self._config['attr_vocab'])]
        for item_idx in range(len(item2attr)):
            attr_idx = item2attr[item_idx]
            attr2items[attr_idx].append(item_idx)
        non_empty_attrs = []
        for attr_idx in range(len(attr2items)):
            if len(attr2items[attr_idx]) > 0:
                non_empty_attrs.append(attr_idx)
        with open(self._config['item_attr_file'], 'w') as fout:
            fout.write(' '.join([str(x) for x in item2attr]) + '\n')
        return item2attr, attr2items, non_empty_attrs

    def _generate_from_full_softmax(self, input, weights, size):
        logits = np.matmul(input, np.transpose(weights))
        exp_logits = np.exp(logits)
        probs = np.divide(exp_logits, np.sum(exp_logits))
        dices = np.random.choice(range(len(probs)), size=[size], p=probs)
        return list(dices)

    def _generate_from_sub_softmax(self, input, weights, size, includes):
        part_weights = []
        for idx in includes:
            part_weights.append(weights[idx])
        logits = np.matmul(input, np.transpose(part_weights))
        exp_logits = np.exp(logits)
        probs = np.divide(exp_logits, np.sum(exp_logits))
        dices = np.random.choice(range(len(probs)), size=[size], p=probs)
        return [includes[x] for x in dices]

    def _generate_user_item_attr(self, user_idx, size):
        if self._config['hierarchical']:
            attr_indices = self._generate_from_sub_softmax(
                self._weights['user'][user_idx],
                self._weights['attr'], size, self._non_empty_attrs)
            item_indices = []
            for attr_idx in attr_indices:
                item_idx = self._generate_from_sub_softmax(
                    self._weights['attr'][attr_idx],
                    self._weights['item'], 1, self._attr2items[attr_idx])[0]
                item_indices.append(item_idx)
        else:
            item_indices = self._generate_from_full_softmax(
                self._weights['user'][user_idx],
                self._weights['item'], size)
            attr_indices = []
            for item_idx in item_indices:
                attr_indices.append(self._item2attr[item_idx])
        return item_indices, attr_indices

    def generate(self):
        with open(self._config['json_file'], 'w') as fout:
            num_batches = self._config['user_vocab'] / self._config['batch_size']
            for i in range(num_batches):
                seq_len = random.randint(self._config['min_seq_len'], self._config['max_seq_len'])
                seq_len *= self._config['page_size']
                batch = {'user_idx': [], 'item_idx': [], 'sequence_length_val': [], 'attr_idx': []}
                for l in range(self._config['batch_size']):
                    batch['user_idx'].append([self._user_idx])
                    batch['sequence_length_val'].append([seq_len])
                    item_indices, attr_indices = self._generate_user_item_attr(self._user_idx, seq_len)
                    batch['item_idx'].append(item_indices)
                    batch['attr_idx'].append(attr_indices)
                    self._user_idx += 1
                json.dump(batch, fout)
                fout.write('\n')
