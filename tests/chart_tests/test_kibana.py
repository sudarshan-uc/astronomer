import pytest

from tests import supported_k8s_versions, get_containers_by_name
from tests.chart_tests.helm_template_generator import render_chart


def common_kibana_cronjob_test(docs):
    """Test common asserts for kibana index cronjob."""
    assert len(docs) == 1
    doc = docs[0]
    assert doc["kind"] == "Job"
    assert doc["apiVersion"] == "batch/v1"
    assert doc["metadata"]["name"] == "release-name-kibana-default-index"


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
class TestKibana:
    def test_kibana_defaults(self, kube_version):
        """Test kibana deployment defaults."""
        docs = render_chart(
            kube_version=kube_version,
            values={},
            show_only=[
                "charts/kibana/templates/kibana-deployment.yaml",
            ],
        )
        doc = docs[0]
        assert doc["kind"] == "Deployment"
        assert doc["metadata"]["name"] == "release-name-kibana"
        c_by_name = get_containers_by_name(doc)
        assert c_by_name["kibana"]
        assert c_by_name["kibana"]["resources"] == {
            "limits": {"cpu": "500m", "memory": "1024Mi"},
            "requests": {"cpu": "250m", "memory": "512Mi"},
        }

        assert {
            "name": "SERVER_PUBLICBASEURL",
            "value": "https://kibana.example.com",
        } in c_by_name["kibana"]["env"]

    def test_kibana_index_defaults(self, kube_version):
        """Test kibana Service with index defaults."""
        docs = render_chart(
            kube_version=kube_version,
            values={},
            show_only=[
                "charts/kibana/templates/kibana-default-index-cronjob.yaml",
            ],
        )
        common_kibana_cronjob_test(docs)
        doc = docs[0]
        assert (
            "fluentd.*"
            in doc["spec"]["template"]["spec"]["containers"][0]["command"][2]
        )

    def test_kibana_index_with_logging_sidecar(self, kube_version):
        """Test kibana Service with logging sidecar index."""
        docs = render_chart(
            kube_version=kube_version,
            values={"global": {"loggingSidecar": {"enabled": True}}},
            show_only=[
                "charts/kibana/templates/kibana-default-index-cronjob.yaml",
            ],
        )
        common_kibana_cronjob_test(docs)
        doc = docs[0]
        assert (
            "vector.*" in doc["spec"]["template"]["spec"]["containers"][0]["command"][2]
        )

    def test_kibana_index_disabled(self, kube_version):
        """Test kibana Service with index creation disabled."""
        docs = render_chart(
            kube_version=kube_version,
            values={"kibana": {"createDefaultIndex": False}},
            show_only=[
                "charts/kibana/templates/kibana-default-index-cronjob.yaml",
            ],
        )

        assert len(docs) == 0

    def test_kibana_index_network_policy_enabled(self, kube_version):
        """Test network policy for kibana index service."""
        docs = render_chart(
            kube_version=kube_version,
            values={"kibana": {"createDefaultIndex": True}},
            show_only=[
                "charts/kibana/templates/kibana-networkpolicy.yaml",
            ],
        )

        assert len(docs) == 1
        doc = docs[0]
        assert "NetworkPolicy" == doc["kind"]
        assert [
            {
                "podSelector": {
                    "matchLabels": {
                        "component": "kibana-default-index",
                        "release": "release-name",
                        "tier": "logging",
                    }
                },
            }
        ] == [doc["spec"]["ingress"][1]["from"][0]]

        assert [{"port": 5601, "protocol": "TCP"}] == doc["spec"]["ingress"][1]["ports"]

    def test_kibana_index_securitycontext_defaults(self, kube_version):
        """Test kibana Service with index defaults."""
        docs = render_chart(
            kube_version=kube_version,
            values={},
            show_only=[
                "charts/kibana/templates/kibana-default-index-cronjob.yaml",
            ],
        )
        common_kibana_cronjob_test(docs)
        doc = docs[0]
        assert {"runAsNonRoot": True, "runAsUser": 1000} == doc["spec"]["template"][
            "spec"
        ]["containers"][0]["securityContext"]

    def test_kibana_index_securitycontext_with_openshiftEnabled(self, kube_version):
        """Test kibana Service with index defaults."""
        docs = render_chart(
            kube_version=kube_version,
            values={"global": {"openshiftEnabled": True}},
            show_only=[
                "charts/kibana/templates/kibana-default-index-cronjob.yaml",
            ],
        )
        common_kibana_cronjob_test(docs)
        doc = docs[0]
        assert {"runAsNonRoot": True} == doc["spec"]["template"]["spec"]["containers"][
            0
        ]["securityContext"]
