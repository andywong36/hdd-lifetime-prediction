from abc import ABC, abstractmethod

from hdd_lifetime_prediction.utils.node import ParsedNode
from .smartctl import SMARTAttributes
import yaml
from pathlib import Path


class Model(ABC):
    @abstractmethod
    def predict(self, smart_attributes: SMARTAttributes):
        pass

class TreeModel(Model):
    def __init__(self, config_yaml: Path):
        self.config = {}
        with open(config_yaml) as f:
            # load the yaml config and change the config items to ParsedNode
            _config = yaml.safe_load(f)
            for key, value in _config.items():
                self.config[key] = ParsedNode(**value)

    @staticmethod
    def get_attribute(attr_name, smart_attributes: SMARTAttributes) -> str | None:
        """ from an attr_name like "smart_5_raw" or "smart_7_normalized" get the value from the SMARTAttributes object
        """
        smart_flag_id = attr_name.split("_")[1]
        smart_flag_key = attr_name.split("_")[2]
        for attr in smart_attributes.attributes:
            if attr.id == smart_flag_id:
                return getattr(attr, smart_flag_key)
        return None


    def predict(self, smart_attributes: SMARTAttributes):
        # Initialize the lifetime prediction to the root node
        current_node: ParsedNode = self.config[1]

        # Traverse the tree until a leaf node is reached
        while current_node.split_feature is not None:
            # Get the attribute value from the SMART attributes
            attr_value = self.get_attribute(current_node.split_feature, smart_attributes)
            if not attr_value:
                return current_node.expected_lifetime
            # Determine which child node to traverse to
            if float(attr_value) < current_node.split_threshold:
                current_node = self.config[current_node.lower_node]
            else:
                current_node = self.config[current_node.upper_node]

        # Return the predicted lifetime
        return current_node.expected_lifetime

    def predict_full(self, smart_attributes: SMARTAttributes):
        # Initialize the lifetime prediction to the root node
        current_node: ParsedNode = self.config[1]

        # Traverse the tree until a leaf node is reached
        while current_node.split_feature is not None:
            # Get the attribute value from the SMART attributes
            attr_value = self.get_attribute(current_node.split_feature, smart_attributes)
            if not attr_value:
                return current_node
            # Determine which child node to traverse to
            if float(attr_value) < current_node.split_threshold:
                current_node = self.config[current_node.lower_node]
            else:
                current_node = self.config[current_node.upper_node]

        # Return the predicted lifetime
        return current_node
