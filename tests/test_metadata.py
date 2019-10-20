from pkg_resources import get_distribution


def test_metadata():
    metadata_name = "airflow-declarative"
    pkg = get_distribution(metadata_name)
    assert pkg.version
    assert pkg.project_name == metadata_name


def test_package_import():
    import airflow_declarative

    assert airflow_declarative
