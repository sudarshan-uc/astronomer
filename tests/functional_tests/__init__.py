from kubernetes import client, config


def get_core_v1_client(in_cluster=False):
    """Return a Core v1 API client."""
    if in_cluster:
        print("Using in cluster kubernetes configuration")
        config.load_incluster_config()
    else:
        print("Using kubectl kubernetes configuration")
        config.load_kube_config()

    return client.CoreV1Api()


def delete_pod(*, namespace: str, name: str):
    """Delete an arbitrary pod."""

    core_v1_client = get_core_v1_client()

    return core_v1_client.delete_namespaced_pod(namespace=namespace, name=name)


def create_pod(
    *,
    namespace: str,
    pod_name: str,
    container_name: str,
    image: str | None = None,
    command: list | None = None,
    labels: dict | None = None,
):
    """Create a pod with a single container and return it. This will also create the namespace if it does not exist."""

    if image is None:
        image = "quay.io/astronomer/ap-base:latest"
    if command is None:
        command = ["sleep", "300"]
    if labels is None:
        labels = {}

    core_v1_client = get_core_v1_client()

    try:
        core_v1_client.create_namespace(
            client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    annotations={
                        "description": "Automated test namespace. This can safely be deleted if it is more than a few hours old."
                    },
                )
            )
        )
    except Exception as e:
        if "AlreadyExists" in e.body:
            print("Namespace already exists")
        else:
            print(f"{e=}")
            raise

    v1container = client.V1Container(name=container_name)
    v1container.command = command
    v1container.image = image

    v1podspec = client.V1PodSpec(containers=[v1container], restart_policy="Never")
    v1objectmeta = client.V1ObjectMeta(
        name=pod_name,
        labels=labels,
        annotations={
            "description": "Automated test pod. This can safely be deleted if it is more than a few hours old."
        },
    )
    v1pod = client.V1Pod(spec=v1podspec, metadata=v1objectmeta)

    return core_v1_client.create_namespaced_pod(namespace, v1pod)
