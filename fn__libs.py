from specklepy.transports.server import ServerTransport
from specklepy.api import operations

def get_objects_list(client, project_id, model_id):
    """
    Fetch all unique object IDs from a Speckle model using SpecklePy.
    """
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

    return list(set(object_list))  # return unique IDs

def extract_tekla_fields(client, stream_id, object_id):
    """
    Extract Tekla-specific fields and ifcType from a Speckle object.
    """
    server_transport = ServerTransport(stream_id, client)
    obj = operations.receive(object_id, remote_transport=server_transport)

    props = getattr(obj, "properties", {})
    tekla_common = props.get("Tekla Common", {})
    tekla_quantity = props.get("Tekla Quantity", {})

    return {
        "object_id": object_id,
        "name": getattr(obj, "name", "n/a"),
        "ifcType": getattr(obj, "ifcType", "n/a"),
        "Class": tekla_common.get("Class", "n/a"),
        "Phase": tekla_common.get("Phase", "n/a"),
        "Volume": tekla_quantity.get("Volume", "n/a"),
        "Weight": tekla_quantity.get("Weight", "n/a"),
        "Width": tekla_quantity.get("Width", "n/a"),
        "Length": tekla_quantity.get("Length", "n/a"),
        "Height": tekla_quantity.get("Height", "n/a")
    }
