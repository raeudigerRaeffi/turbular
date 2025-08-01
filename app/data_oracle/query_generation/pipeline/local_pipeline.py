from .basepipeline import PipelineSqlGen
from ...connectors import BaseDBConnector


class Local_Pipeline(PipelineSqlGen):
    def __init__(self,
                 _connection: BaseDBConnector,
                 _lm_model,
                 _lm_tokenizer):
        super().__init__(_connection)
        self.lm_model = _lm_model
        self.tokenizer = _lm_tokenizer
