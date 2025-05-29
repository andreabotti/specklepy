import streamlit as st
import os
import pandas as pd
from specklepy.api.client import SpeckleClient
from specklepy.transports.server import ServerTransport
from specklepy.api.credentials import get_default_account
from specklepy.api import operations





def get_objects_list(client, project_id, model_id):
    model = client.model.get_with_versions(model_id, project_id).versions
    root_object_id = model.items[0].referencedObject
    server_transport = ServerTransport(project_id, client)
    data = operations.receive(root_object_id, remote_transport=server_transport)

    object_list = []
    objects_to_process = [data]

    while objects_to_process:
        current = objects_to_process.pop()
        if current and hasattr(current, "id"):
            object_list.append(current.id)

            elements = getattr(current, "elements", getattr(current, "@elements", None))
            if elements:
                objects_to_process.extend(elements)

    return list(set(object_list))  # unique IDs



def extract_tekla_fields(client, stream_id, object_id):
    server_transport = ServerTransport(stream_id, client)
    obj = operations.receive(object_id, remote_transport=server_transport)

    props = getattr(obj, "properties", {})
    tekla_common = props.get("Tekla Common", {})
    tekla_quantity = props.get("Tekla Quantity", {})

    return {
        "object_id": object_id,
        "name": getattr(obj, "name", "n/a"),
        "Class": tekla_common.get("Class", "n/a"),
        "Phase": tekla_common.get("Phase", "n/a"),
        "Volume": tekla_quantity.get("Volume", "n/a"),
        "Weight": tekla_quantity.get("Weight", "n/a")
    }






def load_mapping_dict(file_path):
    """
    Reads a text file with 'key: value' pairs and returns a dictionary.
    Parameters:     file_path (str): Path to the text file.
    Returns:        dict: Dictionary with int keys and string values.
    """
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key_str, value = line.strip().split(':', 1)
                try:
                    key = int(key_str.strip())
                    mapping[key] = value.strip()
                except ValueError:
                    print(f"Skipping invalid key: {key_str}")
    return mapping



def add_mapping_column(df, source_column, mapping_dict, new_column_name='Mapped_Name'):
    """
    Adds a new column to the DataFrame by mapping values from the source_column using mapping_dict.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame.
        source_column (str): The name of the column in df to map from (must contain keys from mapping_dict).
        mapping_dict (dict): Dictionary to map values.
        new_column_name (str): The name of the new column to add.
        
    Returns:
        pd.DataFrame: The DataFrame with the new mapped column added.
    """
    df[new_column_name] = df[source_column].map(mapping_dict).fillna('Unknown')
    return df

