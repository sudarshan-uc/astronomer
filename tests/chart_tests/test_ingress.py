from tests.chart_tests.helm_template_generator import render_chart
import pytest
from tests import supported_k8s_versions
import json


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
class TestIngress:
    def test_basic_ingress(self, kube_version):
        # sourcery skip: extract-duplicate-method
        docs = render_chart(
            kube_version=kube_version,
            show_only=[
                "charts/astronomer/templates/ingress.yaml",
                "charts/astronomer/templates/ingress_class.yaml",
            ],
        )

        assert len(docs) == 2

        ing_obj = docs[0]
        ing_cl_obj = docs[1]

        assert ing_obj["kind"] == "Ingress"

        assert len(ing_obj["metadata"]["annotations"]) >= 4
        assert (
            ing_obj["metadata"]["annotations"]["kubernetes.io/ingress.class"]
            == "release-name-nginx"
        )

        expected_rules_v1 = json.loads(
            """
        [{"host":"example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"release-name-astro-ui","port":{"name":"astro-ui-http"}}}}]}},
        {"host":"app.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"release-name-astro-ui","port":{"name":"astro-ui-http"}}}}]}},
        {"host":"registry.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"release-name-registry","port":{"name":"registry-http"}}}}]}},
        {"host":"install.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"release-name-cli-install","port":{"name":"install-http"}}}}]}}]
        """
        )

        assert ing_obj["apiVersion"] == "networking.k8s.io/v1"
        assert ing_obj["spec"]["rules"] == expected_rules_v1

        assert False
