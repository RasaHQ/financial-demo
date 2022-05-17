from typing import Any, Dict, List, Optional, Text, Tuple, Union, TypeVar, Type
from rasa.nlu.classifiers.diet_classifier import DIETClassifier
from rasa.utils.tensorflow.model_data import (
    RasaModelData,
    FeatureSignature,
    FeatureArray,
)
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.classifiers import LABEL_RANKING_LENGTH
from rasa.shared.nlu.constants import (
    SPLIT_ENTITIES_BY_COMMA_DEFAULT_VALUE,
    TEXT,
    INTENT,
    INTENT_RESPONSE_KEY,
    ENTITIES,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_GROUP,
    ENTITY_ATTRIBUTE_ROLE,
    NO_ENTITY_TAG,
    SPLIT_ENTITIES_BY_COMMA,
)
from rasa.nlu.constants import TOKENS_NAMES, DEFAULT_TRANSFORMER_SIZE
from rasa.utils.tensorflow.constants import (
    LABEL,
    IDS,
    HIDDEN_LAYERS_SIZES,
    RENORMALIZE_CONFIDENCES,
    SHARE_HIDDEN_LAYERS,
    TRANSFORMER_SIZE,
    NUM_TRANSFORMER_LAYERS,
    NUM_HEADS,
    BATCH_SIZES,
    BATCH_STRATEGY,
    EPOCHS,
    RANDOM_SEED,
    LEARNING_RATE,
    RANKING_LENGTH,
    LOSS_TYPE,
    SIMILARITY_TYPE,
    NUM_NEG,
    SPARSE_INPUT_DROPOUT,
    DENSE_INPUT_DROPOUT,
    MASKED_LM,
    ENTITY_RECOGNITION,
    TENSORBOARD_LOG_DIR,
    INTENT_CLASSIFICATION,
    EVAL_NUM_EXAMPLES,
    EVAL_NUM_EPOCHS,
    UNIDIRECTIONAL_ENCODER,
    DROP_RATE,
    DROP_RATE_ATTENTION,
    CONNECTION_DENSITY,
    NEGATIVE_MARGIN_SCALE,
    REGULARIZATION_CONSTANT,
    SCALE_LOSS,
    USE_MAX_NEG_SIM,
    MAX_NEG_SIM,
    MAX_POS_SIM,
    EMBEDDING_DIMENSION,
    BILOU_FLAG,
    KEY_RELATIVE_ATTENTION,
    VALUE_RELATIVE_ATTENTION,
    MAX_RELATIVE_POSITION,
    AUTO,
    BALANCED,
    CROSS_ENTROPY,
    TENSORBOARD_LOG_LEVEL,
    CONCAT_DIMENSION,
    FEATURIZERS,
    CHECKPOINT_MODEL,
    SEQUENCE,
    SENTENCE,
    SEQUENCE_LENGTH,
    DENSE_DIMENSION,
    MASK,
    CONSTRAIN_SIMILARITIES,
    MODEL_CONFIDENCE,
    SOFTMAX,
)
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

from collections import Counter
import logging

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=True
)
class SelectiveDIET(DIETClassifier):
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config (see parent class for full docstring)."""
        # please make sure to update the docs when changing a default parameter
        return {
            # ## Architecture of the used neural network
            # Hidden layer sizes for layers before the embedding layers for user message
            # and labels.
            # The number of hidden layers is equal to the length of the corresponding
            # list.
            HIDDEN_LAYERS_SIZES: {TEXT: [], LABEL: []},
            # Whether to share the hidden layer weights between user message and labels.
            SHARE_HIDDEN_LAYERS: False,
            # Number of units in transformer
            TRANSFORMER_SIZE: DEFAULT_TRANSFORMER_SIZE,
            # Number of transformer layers
            NUM_TRANSFORMER_LAYERS: 2,
            # Number of attention heads in transformer
            NUM_HEADS: 4,
            # If 'True' use key relative embeddings in attention
            KEY_RELATIVE_ATTENTION: False,
            # If 'True' use value relative embeddings in attention
            VALUE_RELATIVE_ATTENTION: False,
            # Max position for relative embeddings. Only in effect if key- or value
            # relative attention are turned on
            MAX_RELATIVE_POSITION: 5,
            # Use a unidirectional or bidirectional encoder.
            UNIDIRECTIONAL_ENCODER: False,
            # ## Training parameters
            # Initial and final batch sizes:
            # Batch size will be linearly increased for each epoch.
            BATCH_SIZES: [64, 256],
            # Strategy used when creating batches.
            # Can be either 'sequence' or 'balanced'.
            BATCH_STRATEGY: BALANCED,
            # Number of epochs to train
            EPOCHS: 300,
            # Set random seed to any 'int' to get reproducible results
            RANDOM_SEED: None,
            # Initial learning rate for the optimizer
            LEARNING_RATE: 0.001,
            # ## Parameters for embeddings
            # Dimension size of embedding vectors
            EMBEDDING_DIMENSION: 20,
            # Dense dimension to use for sparse features.
            DENSE_DIMENSION: {TEXT: 128, LABEL: 20},
            # Default dimension to use for concatenating sequence and sentence features.
            CONCAT_DIMENSION: {TEXT: 128, LABEL: 20},
            # The number of incorrect labels. The algorithm will minimize
            # their similarity to the user input during training.
            NUM_NEG: 20,
            # Type of similarity measure to use, either 'auto' or 'cosine' or 'inner'.
            SIMILARITY_TYPE: AUTO,
            # The type of the loss function, either 'cross_entropy' or 'margin'.
            LOSS_TYPE: CROSS_ENTROPY,
            # Number of top intents for which confidences should be reported.
            # Set to 0 if confidences for all intents should be reported.
            RANKING_LENGTH: LABEL_RANKING_LENGTH,
            # Indicates how similar the algorithm should try to make embedding vectors
            # for correct labels.
            # Should be 0.0 < ... < 1.0 for 'cosine' similarity type.
            MAX_POS_SIM: 0.8,
            # Maximum negative similarity for incorrect labels.
            # Should be -1.0 < ... < 1.0 for 'cosine' similarity type.
            MAX_NEG_SIM: -0.4,
            # If 'True' the algorithm only minimizes maximum similarity over
            # incorrect intent labels, used only if 'loss_type' is set to 'margin'.
            USE_MAX_NEG_SIM: True,
            # If 'True' scale loss inverse proportionally to the confidence
            # of the correct prediction
            SCALE_LOSS: False,
            # ## Regularization parameters
            # The scale of regularization
            REGULARIZATION_CONSTANT: 0.002,
            # The scale of how important is to minimize the maximum similarity
            # between embeddings of different labels,
            # used only if 'loss_type' is set to 'margin'.
            NEGATIVE_MARGIN_SCALE: 0.8,
            # Dropout rate for encoder
            DROP_RATE: 0.2,
            # Dropout rate for attention
            DROP_RATE_ATTENTION: 0,
            # Fraction of trainable weights in internal layers.
            CONNECTION_DENSITY: 0.2,
            # If 'True' apply dropout to sparse input tensors
            SPARSE_INPUT_DROPOUT: True,
            # If 'True' apply dropout to dense input tensors
            DENSE_INPUT_DROPOUT: True,
            # ## Evaluation parameters
            # How often calculate validation accuracy.
            # Small values may hurt performance.
            EVAL_NUM_EPOCHS: 20,
            # How many examples to use for hold out validation set
            # Large values may hurt performance, e.g. model accuracy.
            # Set to 0 for no validation.
            EVAL_NUM_EXAMPLES: 0,
            # ## Model config
            # If 'True' intent classification is trained and intent predicted.
            INTENT_CLASSIFICATION: True,
            # If 'True' named entity recognition is trained and entities predicted.
            ENTITY_RECOGNITION: True,
            # If 'True' random tokens of the input message will be masked and the model
            # should predict those tokens.
            MASKED_LM: False,
            # 'BILOU_flag' determines whether to use BILOU tagging or not.
            # If set to 'True' labelling is more rigorous, however more
            # examples per entity are required.
            # Rule of thumb: you should have more than 100 examples per entity.
            BILOU_FLAG: True,
            # If you want to use tensorboard to visualize training and validation
            # metrics, set this option to a valid output directory.
            TENSORBOARD_LOG_DIR: None,
            # Define when training metrics for tensorboard should be logged.
            # Either after every epoch or for every training step.
            # Valid values: 'epoch' and 'batch'
            TENSORBOARD_LOG_LEVEL: "epoch",
            # Perform model checkpointing
            CHECKPOINT_MODEL: False,
            # Specify what features to use as sequence and sentence features
            # By default all features in the pipeline are used.
            FEATURIZERS: [],
            # Split entities by comma, this makes sense e.g. for a list of ingredients
            # in a recipie, but it doesn't make sense for the parts of an address
            SPLIT_ENTITIES_BY_COMMA: True,
            # If 'True' applies sigmoid on all similarity terms and adds
            # it to the loss function to ensure that similarity values are
            # approximately bounded. Used inside cross-entropy loss only.
            CONSTRAIN_SIMILARITIES: False,
            # Model confidence to be returned during inference. Currently, the only
            # possible value is `softmax`.
            MODEL_CONFIDENCE: SOFTMAX,
            # Determines whether the confidences of the chosen top intents should be
            # renormalized so that they sum up to 1. By default, we do not renormalize
            # and return the confidences for the top intents as is.
            # Note that renormalization only makes sense if confidences are generated
            # via `softmax`.
            RENORMALIZE_CONFIDENCES: False,
            "intents_to_train": [],
            "classifier_name": "",
        }

    def preprocess_train_data(self, training_data: TrainingData) -> RasaModelData:

        intents_to_train = self.component_config["intents_to_train"]
        filtered_training_data = training_data
        if intents_to_train:
            filtered_training_data = filtered_training_data.filter_training_examples(
                lambda ex: ex.get("intent") in intents_to_train
            )
            logger.debug(self.component_config["classifier_name"])
            logger.debug(intents_to_train)
            logger.debug(Counter([ex.get("intent") for ex in filtered_training_data.training_examples]))

        return super().preprocess_train_data(filtered_training_data)

    def process(self, messages: List[Message]) -> List[Message]:
        """Augments the message with intents, entities, and diagnostic data."""
        for message in messages:
            out = self._predict(message)

            if self.component_config[INTENT_CLASSIFICATION]:
                label, label_ranking = self._predict_label(out)
                output = {INTENT: label, "intent_ranking": label_ranking}
                # message.set(INTENT, label, add_to_output=True)
                message.set(
                    self.component_config["classifier_name"], output, add_to_output=True
                )

            if self.component_config[ENTITY_RECOGNITION]:
                entities = self._predict_entities(out, message)

                message.set(ENTITIES, entities, add_to_output=True)

        return messages
