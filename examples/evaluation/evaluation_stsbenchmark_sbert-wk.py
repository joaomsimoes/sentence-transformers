"""
Performs the pooling described in the paper:
SBERT-WK: A Sentence Embedding Method by Dissecting BERT-based Word Models, 2020, https://arxiv.org/abs/2002.06652

Note: WKPooling improves the performance only for certain models. Further, WKPooling requires QR-decomposition,
for which there is so far not efficient implementation in pytorch for GPUs (see https://github.com/pytorch/pytorch/issues/22573).
Hence, WKPooling runs on the GPU, which makes it rather in-efficient.
"""
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer,  SentencesDataset, LoggingHandler, models
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.readers import STSDataReader
import logging
import torch

#Limit torch to 4 threads, as this example runs on the CPU
torch.set_num_threads(4)

#### Just some code to print debug information to stdout
logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[LoggingHandler()])
#### /print debug information to stdout



word_embedding_model = models.Transformer('bert-base-uncased', model_args={'output_hidden_states': True})
pooling_model = models.WKPooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

sts_reader = STSDataReader('../datasets/stsbenchmark')

test_data = SentencesDataset(examples=sts_reader.get_examples("sts-test.csv"), model=model)
test_dataloader = DataLoader(test_data, shuffle=False, batch_size=8)
evaluator = EmbeddingSimilarityEvaluator(test_dataloader)

model.evaluate(evaluator)