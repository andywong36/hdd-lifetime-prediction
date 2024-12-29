import json
from dataclasses import dataclass
from importlib.resources import files

import numpy as np
from bs4 import BeautifulSoup


@dataclass
class ParsedNode:
    split_feature: str | None
    split_threshold: float | None
    lower_node: int | None
    upper_node: int | None
    expected_lifetime: float
    n_samples: int
    median_lifetime: float
    lower_lifetime: float
    upper_lifetime: float

def find_matching_brace(s, start_index):
    """Finds the position of the matching closing brace for a given opening brace."""
    open_braces = 0
    for i in range(start_index, len(s)):
        if s[i] == '{':
            open_braces += 1
        elif s[i] == '}':
            open_braces -= 1
            if open_braces == 0:
                return i
    return -1

def extract_nodes_from_script(html_content: BeautifulSoup):
    # Iterate over all <script> tags in the HTML
    nodes = []
    for script in html_content.find_all('script'):
        # Extract and strip whitespace from the <script> tag content
        script_content = script.string
        if script_content and 'var treeinfo =' not in script_content:
            continue
        try:
            # Isolate the JSON-like part of the script
            # Find the position after 'var treeinfo ='
            json_start = script_content.index('var treeinfo =') + len('var treeinfo =')

            # Find the start index of the JSON section from there
            json_str_start = script_content.index('{', json_start)

            # Find the matching closing brace
            json_str_end = find_matching_brace(script_content, json_str_start) + 1

            if json_str_end != 0:  # Ensure an end was found
                json_str = script_content[json_str_start:json_str_end]

                # Convert the JSON string into a Python dictionary
                script_data = json.loads(json_str)

                # Extract nodes data
                nodes = script_data.get("lnr", {}).get("tree_", {}).get("nodes", [])

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON from script: {e}")

    # Return empty list if no matching <script> is found
    return nodes

def extract_features_from_script(html_content: BeautifulSoup):
    features = []
    for script in html_content.find_all('script'):
        # Extract and strip whitespace from the <script> tag content
        script_content = script.string
        if script_content and 'var treeinfo =' not in script_content:
            continue
        try:
            # Isolate the JSON-like part of the script
            # Find the position after 'var treeinfo ='
            json_start = script_content.index('var treeinfo =') + len('var treeinfo =')

            # Find the start index of the JSON section from there
            json_str_start = script_content.index('{', json_start)

            # Find the matching closing brace
            json_str_end = find_matching_brace(script_content, json_str_start) + 1

            if json_str_end != 0:  # Ensure an end was found
                json_str = script_content[json_str_start:json_str_end]

                # Convert the JSON string into a Python dictionary
                script_data = json.loads(json_str)

                # Extract nodes data
                features = (
                    script_data
                    .get("lnr", {})
                    .get("prb_", {})
                    .get("data", {})
                    .get("features", {})
                    .get("feature_names", [])
                )

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON from script: {e}")

    return features

def parse_nodes(nodes, features):
    """parse these nodes into a nice dictionary

    :param nodes: list of nodes. each node is a dictionary with the keys
        dict_keys(['id', 'parent', 'lower_child', 'upper_child', 'depth', 'split_type', 'split_mixed',
        'split_hyperplane',  'missingdatamode', 'raw_error', 'baseline_error', 'subtree_complexity',    'n_node_samples',
        'weighted_n_node_samples', 'dirty', 'fit']))]
    :param features: list of features (strings)

    :return: dictionary with the keys being the node id, and the values being a ParsedNode object
    """

    parsed_nodes = {}
    for node in nodes:
        node_id = node.get("id")
        _split_feature_idx: int | None = node.get("split_mixed", {}).get("parallel_split", {}).get("feature") or None
        split_feature_threshold: float | None = node.get("split_mixed", {}).get("parallel_split", {}).get("threshold")
        split_feature_name = features[_split_feature_idx - 1] if _split_feature_idx is not None else None

        _lower_node: int | None = node.get("lower_child")
        _upper_node: int | None = node.get("upper_child")
        # special case - the "-2" node is the None node
        if _lower_node == -2:
            _lower_node = None
        if _upper_node == -2:
            _upper_node = None

        expected_lifetime = node.get('fit', {}).get('curve', {}).get('expected_time')
        n_samples = node.get('n_node_samples')
        lifetimes_x = np.array(node.get('fit', {}).get('curve', {}).get('times'))
        survival_y = np.array(node.get('fit', {}).get('curve', {}).get('coefs'))

        # survival_y should always be between 0 and 1
        assert np.all(survival_y >= 0), "Survival curve should be non-negative"
        assert np.all(survival_y <= 1), "Survival curve should be less than 1000"
        assert np.all(lifetimes_x >= 0), "Lifetimes should be non-negative"

        # get the median - where suvival_y is roughly 0.5, using scipy interp
        median_lifetime = float(np.interp(0.5, survival_y, lifetimes_x))
        # get the upper and lower 5%
        lower_lifetime = float(np.interp(0.025, survival_y, lifetimes_x))
        upper_lifetime = float(np.interp(0.975, survival_y, lifetimes_x))

        parsed_nodes[node_id] = ParsedNode(
            split_feature=split_feature_name,
            split_threshold=split_feature_threshold,
            lower_node=_lower_node,
            upper_node=_upper_node,
            expected_lifetime=expected_lifetime,
            n_samples=n_samples,
            median_lifetime=median_lifetime,
            lower_lifetime=lower_lifetime,
            upper_lifetime=upper_lifetime,
        )

    return parsed_nodes

if __name__ == "__main__":
    from pprint import pprint
    import yaml

    # Example HTML content
    html_content = (
        files('hdd_lifetime_prediction.utils')
        .joinpath("Fig3. Optimal Survival Tree for predicting long-term health.html")
        .read_text()
    )
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    nodes = extract_nodes_from_script(soup)
    pprint([
        (node.get("id"), node.keys())
        for node in nodes
    ])
    features = extract_features_from_script(soup)
    pprint(features)

    parsed_nodes = parse_nodes(nodes, features)
    pprint(parsed_nodes)

    # save these nodes to long-term-params.yaml
    with open("src/hdd_lifetime_prediction/model/long-term-params.yaml", "w") as f:
        # convert the nodes to dicts
        parsed_nodes_dict = {k: v.__dict__ for k, v in parsed_nodes.items()}
        yaml.dump(parsed_nodes_dict, f)


    # Repeat with the short term html
    html_content = (
        files('hdd_lifetime_prediction.utils')
        .joinpath("Fig6. Optimal Survival Tree predicting short-term health.html")
        .read_text()
    )
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    nodes = extract_nodes_from_script(soup)
    features = extract_features_from_script(soup)
    parsed_nodes = parse_nodes(nodes, features)
    with open("src/hdd_lifetime_prediction/model/short-term-params.yaml", "w") as f:
        # convert the nodes to dicts
        parsed_nodes_dict = {k: v.__dict__ for k, v in parsed_nodes.items()}
        yaml.dump(parsed_nodes_dict, f)
