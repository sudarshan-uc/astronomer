import pytest

urls = [
    ("http://astrodev-elasticsearch-nginx.development:9200/_search", "401"),
    ("http://astrodev-elasticsearch-nginx.development:9200/_count", "401"),
    ("http://astrodev-elasticsearch-nginx.development:9200/_bulk", "401"),
]


pod_data = {
    "pod_name": "nginx-es-test-mock-webserver",
    "namespace": "danielh-test-2023-02-28",
    "container_name": "nginx-es-tester",
    "image": "curlimages/curl:7.88.1",
    "labels": {
        "component": "webserver",
        "platform": "astronomer",
        "tier": "airflow",
    },
}


@pytest.mark.pod_data(**pod_data)
@pytest.mark.parametrize("url,expected_result", urls)
def test_nginx_es_from_worker(url, expected_result, pod):
    data = pod.check_output(
        'curl --connect-timeout 5 --max-filesize 1 -s -w "%{http_code}\n" -o /dev/null '
        + url
        + " || /bin/true"
    )

    assert data == expected_result


# TODO
# - handle authentication for queries we expect to succeed (those 401's up there should not be 401's)
# - make a non-webserver-ish pod and its tests
